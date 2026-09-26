"""sistema/django_app/corpus/views.py: session/CSRF boundary and private UI."""
import hashlib
import hmac
import math
import time
from uuid import UUID
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction, DatabaseError
from django.db.models import F
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.http import require_http_methods
from contracts.corpus_django import Principal, DocumentLocator, ErrorCode
from .access import CorpusError, state_for, require_employee, is_employee
from .forms import BrowseForm, PilotForm, QueryForm, PrivateResetForm, strict
from .models import PolicyState, AttemptBudget, PrivateFeedback, Locator, PilotAccount, PilotEvent
from .services import Application, usage_for

app = Application()


class BoundaryMiddleware:
    """Prevent storage, framing and script execution for every application response."""
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Cache-Control"] = "no-store"
        response["X-Frame-Options"] = "DENY"
        response["Content-Security-Policy"] = (
            "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; "
            "base-uri 'none'; frame-ancestors 'none'")
        return response


def guarded(view):
    """Translate bounded domain/DB errors without leaking identifiers or text."""
    def wrapped(request, *args, **kwargs):
        try:
            if request.FILES:
                raise CorpusError(ErrorCode.INVALID_INPUT)
            return view(request, *args, **kwargs)
        except CorpusError as exc:
            if exc.code == ErrorCode.AUTHENTICATION_REQUIRED or (
                    exc.code == ErrorCode.ACCESS_DENIED and needs_fresh_login(request)):
                logout(request)
                return redirect("login")
            status = {ErrorCode.INVALID_INPUT: 400, ErrorCode.RATE_LIMITED: 429,
                      ErrorCode.SERVICE_UNAVAILABLE: 503, ErrorCode.INTEGRITY_FAILED: 503}.get(exc.code, 403)
            return HttpResponse("Solicitud no disponible.", status=status)
        except DatabaseError:
            return HttpResponse("Servicio temporalmente no disponible.", status=503)
    return wrapped


def needs_fresh_login(request) -> bool:
    """True only when re-authenticating is the way forward: no identity, stale
    login-bound epoch, deactivated account or missing/quarantined policy.
    Document-scope denials on a healthy session keep the bounded 403."""
    if not request.user.is_authenticated:
        return True
    try:
        state = PolicyState.objects.filter(pk=1, quarantined=False).first()
    except DatabaseError:
        return False
    return (state is None or not request.user.is_active
            or request.session.get("corpus_epoch", -1) != state.session_epoch)


def principal(request) -> Principal:
    """Only Django server-side identity and login-bound epoch create a principal."""
    if not request.user.is_authenticated:
        raise CorpusError(ErrorCode.AUTHENTICATION_REQUIRED)
    p = Principal(request.user.pk, request.session.get("corpus_epoch", -1))
    state_for(p)
    return p


@transaction.atomic
def consume_budget(request, purpose: str) -> None:
    """Enforce a persistent 10/minute peer budget; never trust forwarded IP."""
    minute = int(time.time() // 60)
    raw = f'{purpose}:{request.META.get("REMOTE_ADDR", "")}:{minute}'.encode()
    key = hmac.new(settings.SECRET_KEY.encode(), raw, hashlib.sha256).hexdigest()
    AttemptBudget.objects.filter(expires_at__lt=timezone.now()).delete()
    AttemptBudget.objects.get_or_create(key=key, defaults={"expires_at": timezone.now() + timedelta(minutes=2)})
    changed = AttemptBudget.objects.filter(pk=key, attempts__lt=10).update(attempts=F("attempts") + 1)
    if not changed:
        raise CorpusError(ErrorCode.RATE_LIMITED)


@require_http_methods(["GET", "POST"])
@guarded
def login_view(request):
    """Authenticate with CSRF, throttle and session rotation; no next-URL redirect."""
    strict(request.GET, set())
    form = AuthenticationForm(request, data=request.POST if request.method == "POST" else None)
    if request.method == "POST":
        strict(request.POST, {"username", "password", "csrfmiddlewaretoken"})
        consume_budget(request, "login")
        if form.is_valid():
            state = PolicyState.objects.filter(pk=1, quarantined=False).first()
            if state is None:
                raise CorpusError(ErrorCode.ACCESS_DENIED)
            login(request, form.get_user())
            request.session["corpus_epoch"] = state.session_epoch
            return redirect("workspace")
    return render(request, "corpus/login.html", {"form": form, "mode": "login"})


@require_http_methods(["POST"])
@guarded
def logout_view(request):
    """Flush server session even if grants or epoch expired."""
    strict(request.GET, set())
    strict(request.POST, {"csrfmiddlewaretoken"})
    logout(request)
    return redirect("login")


@require_http_methods(["POST"])
@guarded
def theme_view(request):
    """Persist the reading theme in a first-party cookie; pages run script-free."""
    strict(request.GET, set())
    strict(request.POST, {"csrfmiddlewaretoken", "theme", "next"})
    theme = request.POST.get("theme", "")
    if theme not in {"light", "dark", "auto"}:
        raise CorpusError(ErrorCode.INVALID_INPUT)
    target = request.POST.get("next", "/corpus/")
    if not target.startswith("/") or target.startswith("//"):
        target = "/corpus/"
    response = redirect(target)
    response.set_cookie("corpus_theme", theme, max_age=365 * 24 * 3600,
                        samesite="Lax", secure=not settings.TESTING, httponly=True)
    return response


@require_http_methods(["GET", "POST"])
@guarded
def reset_request(request):
    """Uniform account-recovery acknowledgement with a persistent peer budget."""
    strict(request.GET, set())
    form = PrivateResetForm(request.POST if request.method == "POST" else None)
    if request.method == "POST":
        strict(request.POST, {"email", "csrfmiddlewaretoken"})
        consume_budget(request, "reset")
        if form.is_valid():
            form.save(use_https=not settings.TESTING, domain_override="unused.invalid",
                      from_email=settings.DEFAULT_FROM_EMAIL)
        return render(request, "corpus/login.html", {"mode": "sent"})
    return render(request, "corpus/login.html", {"form": form, "mode": "reset"})


@require_http_methods(["GET", "POST"])
@guarded
def reset_confirm(request, uid: str, token: str):
    """Django one-use password reset invalidates old authenticated sessions."""
    strict(request.GET, set())
    consume_budget(request, "reset-confirm")
    try:
        user = get_user_model().objects.get(pk=urlsafe_base64_decode(uid).decode(), is_active=True)
    except (ValueError, UnicodeError, get_user_model().DoesNotExist, OverflowError):
        raise CorpusError(ErrorCode.ACCESS_DENIED)
    if not default_token_generator.check_token(user, token):
        raise CorpusError(ErrorCode.ACCESS_DENIED)
    form = SetPasswordForm(user, request.POST if request.method == "POST" else None)
    if request.method == "POST":
        strict(request.POST, {"new_password1", "new_password2", "csrfmiddlewaretoken"})
        if form.is_valid():
            form.save()
            logout(request)
            return redirect("login")
    return render(request, "corpus/login.html", {"form": form, "mode": "confirm"})


def locator_from(data) -> DocumentLocator:
    """Parse a complete locator without accepting client-provided authority."""
    try:
        return DocumentLocator(UUID(data["collection"]), data["uid"], data["version"])
    except (KeyError, ValueError, TypeError):
        raise CorpusError(ErrorCode.INVALID_INPUT)


def _feedback_target(refs, page, catalog):
    """Pick a sane locator for the workspace report form: last reference, else first visible hit."""
    if refs:
        return refs[-1].locator
    if page is not None and page.results:
        return page.results[0].locator
    if catalog is not None and catalog["items"]:
        item = catalog["items"][0]
        return {"collection_id": item["collection_id"], "uid": item["uid"],
                "version_sha256": item["version_sha256"]}
    return None


def _page_context(offset: int, limit: int, next_offset: int | None, visible_count: int) -> dict:
    """Compute pagination metadata: current page, total pages (bounded by next_offset), prev link."""
    page = (offset // max(limit, 1)) + 1
    prev_offset = offset - limit if offset > 0 else None
    next_page = None
    page_total = page
    if next_offset is not None:
        next_page = (next_offset // max(limit, 1)) + 1
        page_total = next_page
    return {"page": page, "page_total": page_total, "next_page": next_page,
            "shown": visible_count, "prev_offset": prev_offset}


@require_http_methods(["GET"])
@guarded
def workspace(request):
    """Render search, authorized catalog navigation, private references and reports."""
    p = principal(request)
    page_ctx = {}
    if "browse" in request.GET:
        strict(request.GET, {"browse", "source", "rubro", "tipo", "offset", "limit"})
        browse_form = BrowseForm(request.GET or None)
        if not browse_form.is_valid():
            raise CorpusError(ErrorCode.INVALID_INPUT)
        data = browse_form.cleaned_data
        offset = int(data.get("offset") or 0)
        limit = int(data.get("limit") or 20)
        catalog = app.browse(p, data.get("source", ""), data.get("rubro", ""), data.get("tipo", ""),
                              offset, limit)
        catalog_facets = catalog
        form = QueryForm(None)
        page = None
        ctx = _page_context(offset, limit, catalog["next_offset"], len(catalog["items"]))
        catalog.update(ctx)
        catalog["prev_offset"] = ctx["prev_offset"]
    else:
        strict(request.GET, {"q", "source", "rubro", "tipo", "offset", "limit"})
        form = QueryForm(request.GET or None)
        page = None
        catalog = None
        if request.GET:
            if not form.is_valid():
                raise CorpusError(ErrorCode.INVALID_INPUT)
            offset = int(form.cleaned_data["offset"] or 0)
            limit = int(form.cleaned_data["limit"] or 10)
            page = app.search(p, form.cleaned_data["q"], offset, limit,
                              form.cleaned_data.get("source", ""),
                              form.cleaned_data.get("rubro", ""),
                              form.cleaned_data.get("tipo", ""))
            page_ctx = _page_context(offset, limit, page.next_offset, len(page.results))
        browse_form = BrowseForm(initial={"browse": "1", "limit": "20"})
        catalog_facets = app.browse(p, offset=0, limit=1)
    refs = app.list_references(p)
    feedback = PrivateFeedback.objects.filter(owner_id=p.user_id).order_by("-created_at")[:20]
    return render(request, "corpus/workspace.html", {"form": form, "page": page,
                  "page_ctx": page_ctx, "catalog": catalog,
                  "catalog_facets": catalog_facets, "browse_form": browse_form,
                  "references": refs, "feedback": feedback, "query": request.GET.get("q", ""),
                  "feedback_target": _feedback_target(refs, page, catalog),
                  "is_employee": is_employee(p)})


@require_http_methods(["GET"])
@guarded
def read_view(request):
    """Exact authorized legal text, escaped by template, never marked official."""
    p = principal(request)
    strict(request.GET, {"collection", "uid", "version", "start", "limit"})
    try:
        start_text, limit_text = request.GET.get("start", "0"), request.GET.get("limit", "10000")
        if not start_text.isascii() or not start_text.isdecimal() or str(int(start_text)) != start_text:
            raise ValueError
        if not limit_text.isascii() or not limit_text.isdecimal() or str(int(limit_text)) != limit_text:
            raise ValueError
        locator = locator_from(request.GET)
        result = app.read(p, locator, int(start_text), int(limit_text))
    except ValueError:
        raise CorpusError(ErrorCode.INVALID_INPUT)
    row = Locator.objects.filter(collection_id=locator.collection_id, uid=locator.uid,
                                 version_sha256=locator.version_sha256).first()
    title = row.title if row and row.title else locator.uid
    next_page_number = min(result.page_total, result.page_number + 1) if result.next_start is not None else result.page_number
    return render(request, "corpus/workspace.html", {"text": result, "doc_title": title,
                                                     "next_page_number": next_page_number,
                                                     "reading_progress_pct": round((result.end / result.total_characters) * 100),
                                                     "is_employee": is_employee(p)})


@require_http_methods(["GET"])
@guarded
def download_view(request):
    """Download the authorized exact text as a plain .txt file."""
    p = principal(request)
    strict(request.GET, {"collection", "uid", "version"})
    locator = locator_from(request.GET)
    result = app.read(p, locator, 0, 10000)
    row = Locator.objects.filter(collection_id=locator.collection_id, uid=locator.uid,
                                 version_sha256=locator.version_sha256).first()
    title = (row.title if row and row.title else locator.uid)
    safe = "".join(c if c.isalnum() or c in " -_." else "" for c in title)[:80].strip() or "documento"
    response = HttpResponse(result.text, content_type="text/plain; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{safe}.txt"'
    return response


@require_http_methods(["POST"])
@guarded
def save_view(request):
    """Save only a locator belonging to the authenticated owner."""
    strict(request.GET, set())
    strict(request.POST, {"collection", "uid", "version", "csrfmiddlewaretoken"})
    app.save_reference(principal(request), locator_from(request.POST))
    return redirect("workspace")


@require_http_methods(["POST"])
@guarded
def feedback_view(request):
    """Create a private report without any external notification."""
    strict(request.GET, set())
    strict(request.POST, {"collection", "uid", "version", "category", "description", "csrfmiddlewaretoken"})
    p = principal(request)
    consume_budget(request, "feedback")
    receipt = app.report_error(p, locator_from(request.POST), request.POST.get("category", ""),
                               request.POST.get("description", ""))
    if request.headers.get("Accept") == "application/json":
        return JsonResponse({"id": str(receipt.id), "created_at": receipt.created_at.isoformat(),
                             "status": receipt.status}, status=201)
    return redirect("workspace")


@require_http_methods(["GET", "POST"])
@guarded
def pilot_view(request):
    """Legacy desk path; the desk is now the independent employee portal."""
    return redirect("portal")


def _portal_context(form, created=None, notice=""):
    """Assemble accounts with usage, recent activity and lawyer reports."""
    accounts = (PilotAccount.objects.select_related("lawyer", "created_by")
                .order_by("-created_at")[:50])
    rows = []
    for account in accounts:
        rows.append({"account": account, "usage": usage_for(account.lawyer),
                     "reports": PrivateFeedback.objects.filter(owner=account.lawyer).count()})
    recent = PilotEvent.objects.select_related("lawyer").order_by("-at")[:50]
    reports = (PrivateFeedback.objects.select_related("owner", "locator")
               .order_by("-created_at")[:100])
    return {"form": form, "created": created, "notice": notice, "rows": rows,
            "recent": recent, "reports": reports}


@require_http_methods(["GET", "POST"])
@guarded
def portal_login(request):
    """Independent employee entrance: same credential store, separate door."""
    strict(request.GET, set())
    if request.user.is_authenticated and is_employee(Principal(request.user.pk, -1)):
        return redirect("portal")
    form = AuthenticationForm(request, data=request.POST if request.method == "POST" else None)
    if request.method == "POST":
        strict(request.POST, {"username", "password", "csrfmiddlewaretoken"})
        consume_budget(request, "portal-login")
        if form.is_valid():
            user = form.get_user()
            if not is_employee(Principal(user.pk, -1)):
                form.add_error(None, "Esta entrada es solo para el equipo de Corpus Tarija.")
            else:
                state = PolicyState.objects.filter(pk=1, quarantined=False).first()
                if state is None:
                    raise CorpusError(ErrorCode.ACCESS_DENIED)
                login(request, user)
                request.session["corpus_epoch"] = state.session_epoch
                return redirect("portal")
    return render(request, "corpus/portal_login.html", {"form": form})


@require_http_methods(["POST"])
@guarded
def portal_logout(request):
    """Close the employee session and return to the independent entrance."""
    strict(request.GET, set())
    strict(request.POST, {"csrfmiddlewaretoken"})
    logout(request)
    return redirect("portal-login")


@require_http_methods(["GET", "POST"])
@guarded
def portal(request):
    """Employee portal: create accounts, review usage and read lawyer reports."""
    if not request.user.is_authenticated:
        return redirect("portal-login")
    p = principal(request)
    require_employee(p)
    created = None
    form = PilotForm(request.POST if request.method == "POST" else None)
    if request.method == "POST":
        strict(request.POST, {"first_name", "last_name", "bar_number", "csrfmiddlewaretoken"})
        consume_budget(request, "pilot")
        if form.is_valid():
            created = app.create_pilot(p, form.cleaned_data["first_name"],
                                       form.cleaned_data["last_name"],
                                       form.cleaned_data.get("bar_number", ""))
            form = PilotForm(None)
    notice = request.session.pop("portal_notice", "")
    if created is None:
        created = request.session.pop("portal_credentials", None)
    return render(request, "corpus/portal.html", _portal_context(form, created, notice))


@require_http_methods(["POST"])
@guarded
def portal_reissue(request, account_id):
    """Re-issue a pilot password and show it once back in the portal."""
    if not request.user.is_authenticated:
        return redirect("portal-login")
    strict(request.GET, set())
    strict(request.POST, {"csrfmiddlewaretoken"})
    consume_budget(request, "pilot")
    result = app.reissue_pilot_password(principal(request), account_id)
    request.session["portal_credentials"] = result
    return redirect("portal")


@require_http_methods(["POST"])
@guarded
def portal_delete(request, account_id):
    """Remove a lawyer's access; usage history and reports stay attributable."""
    if not request.user.is_authenticated:
        return redirect("portal-login")
    strict(request.GET, set())
    strict(request.POST, {"csrfmiddlewaretoken"})
    consume_budget(request, "pilot")
    username = app.deactivate_pilot(principal(request), account_id)
    request.session["portal_notice"] = (
        f"Acceso eliminado: {username}. Sus lecturas e informes quedan registrados.")
    return redirect("portal")


@require_http_methods(["GET"])
@guarded
def health(request, kind: str):
    """Separate process liveness from policy/database readiness; expose no metadata."""
    if kind != "live" and not PolicyState.objects.filter(pk=1, quarantined=False).exists():
        return HttpResponse("not ready", status=503)
    return HttpResponse("ok")
