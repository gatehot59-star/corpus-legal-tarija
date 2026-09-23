"""sistema/django_app/corpus/views.py: session/CSRF boundary and private UI."""
import hashlib
import hmac
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
from .access import CorpusError, state_for
from .forms import BrowseForm, QueryForm, PrivateResetForm, strict
from .models import PolicyState, AttemptBudget, PrivateFeedback
from .services import Application

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
            status = {ErrorCode.INVALID_INPUT: 400, ErrorCode.RATE_LIMITED: 429,
                      ErrorCode.SERVICE_UNAVAILABLE: 503, ErrorCode.INTEGRITY_FAILED: 503}.get(exc.code, 403)
            return HttpResponse("Solicitud no disponible.", status=status)
        except DatabaseError:
            return HttpResponse("Servicio temporalmente no disponible.", status=503)
    return wrapped


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


@require_http_methods(["GET"])
@guarded
def workspace(request):
    """Render search, authorized catalog navigation, private references and reports."""
    p = principal(request)
    if "browse" in request.GET:
        strict(request.GET, {"browse", "source", "rubro", "tipo", "offset", "limit"})
        browse_form = BrowseForm(request.GET or None)
        if not browse_form.is_valid():
            raise CorpusError(ErrorCode.INVALID_INPUT)
        data = browse_form.cleaned_data
        catalog = app.browse(p, data.get("source", ""), data.get("rubro", ""), data.get("tipo", ""),
                              int(data.get("offset") or 0), int(data.get("limit") or 20))
        catalog_facets = catalog
        form = QueryForm(None)
        page = None
    else:
        strict(request.GET, {"q", "offset", "limit"})
        form = QueryForm(request.GET or None)
        page = None
        catalog = None
        if request.GET:
            if not form.is_valid():
                raise CorpusError(ErrorCode.INVALID_INPUT)
            page = app.search(p, form.cleaned_data["q"],
                              int(form.cleaned_data["offset"] or 0), int(form.cleaned_data["limit"] or 10))
        browse_form = BrowseForm(initial={"browse": "1", "limit": "20"})
        catalog_facets = app.browse(p, offset=0, limit=1)
    refs = app.list_references(p)
    feedback = PrivateFeedback.objects.filter(owner_id=p.user_id).order_by("-created_at")[:20]
    return render(request, "corpus/workspace.html", {"form": form, "page": page, "catalog": catalog,
                  "catalog_facets": catalog_facets, "browse_form": browse_form,
                  "references": refs, "feedback": feedback, "query": request.GET.get("q", "")})


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
        result = app.read(p, locator_from(request.GET), int(start_text), int(limit_text))
    except ValueError:
        raise CorpusError(ErrorCode.INVALID_INPUT)
    return render(request, "corpus/workspace.html", {"text": result})


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


@require_http_methods(["GET"])
@guarded
def health(request, kind: str):
    """Separate process liveness from policy/database readiness; expose no metadata."""
    if kind != "live" and not PolicyState.objects.filter(pk=1, quarantined=False).exists():
        return HttpResponse("not ready", status=503)
    return HttpResponse("ok")
