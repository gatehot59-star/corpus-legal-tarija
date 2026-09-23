"""Independent employee portal: role management and explicit corpus grants."""
import re
import secrets
import string
from datetime import timedelta
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from contracts.corpus_django import Principal, ErrorCode
from .access import CorpusError, EMPLOYEES_GROUP, is_employee, require_employee
from .forms import PilotForm, strict
from .models import (AccessGrant, EmployeeAccount, Membership, PilotAccount,
                     PilotEvent, PrivateFeedback, Collection)
from .services import usage_for
from .views import consume_budget, guarded, principal


EMPLOYEE_PASSWORD_NOTE = "Una minúscula y cuatro números"
LAWYER_PASSWORD_NOTE = "Una mayúscula y cuatro números"


def _password(role: str) -> str:
    """Create the requested pilot credential shape without storing it in the database."""
    alphabet = string.ascii_lowercase if role == "employee" else string.ascii_uppercase
    return secrets.choice(alphabet) + "".join(secrets.choice(string.digits) for _ in range(4))


def _username(first_name: str, last_name: str, prefix: str) -> str:
    """Build a unique ASCII username for a managed account."""
    base = re.sub(r"[^a-z0-9]", "", f"{first_name}.{last_name}".lower())
    base = f"{prefix}{base}" if prefix else base
    if len(base) < 3:
        raise CorpusError(ErrorCode.INVALID_INPUT)
    candidate, suffix = base, 2
    User = get_user_model()
    while User.objects.filter(username=candidate).exists():
        candidate = f"{base}{suffix}"
        suffix += 1
        if suffix > 200:
            raise CorpusError(ErrorCode.SERVICE_UNAVAILABLE)
    return candidate


def _operator(principal_value):
    """Return the active operator user or deny the operation."""
    User = get_user_model()
    operator = User.objects.filter(pk=principal_value.user_id, is_active=True).first()
    if operator is None:
        raise CorpusError(ErrorCode.ACCESS_DENIED)
    return operator


def _employee_group():
    """Resolve the explicit employee group used by memberships and grants."""
    return Group.objects.filter(name=EMPLOYEES_GROUP).first() or Group.objects.create(name=EMPLOYEES_GROUP)


def _grant(user, operator, origin: str, days: int):
    """Issue an attributable grant on the enabled real collection."""
    collection = Collection.objects.filter(enabled=True).order_by("name").first()
    if collection is None:
        raise CorpusError(ErrorCode.SERVICE_UNAVAILABLE)
    group = _employee_group()
    now = timezone.now()
    AccessGrant.objects.create(user=user, group=group, collection=collection, origin=origin,
                               valid_from=now, valid_until=now + timedelta(days=days),
                               issued_by=operator, evidence_id=f"{origin}:{operator.pk}:{now.date()}")


def _membership(user):
    """Give a managed employee or lawyer the explicit group membership required by grants."""
    Membership.objects.update_or_create(user=user, group=_employee_group(),
                                        defaults={"enabled": True})


@transaction.atomic
def create_employee(operator_principal, first_name: str, last_name: str = "") -> dict:
    """Create an employee operator with a lower-case-letter plus four-digit password."""
    require_employee(operator_principal)
    operator = _operator(operator_principal)
    if not first_name.strip() or len(first_name) > 80 or len(last_name) > 80:
        raise CorpusError(ErrorCode.INVALID_INPUT)
    User = get_user_model()
    username = _username(first_name.strip(), last_name.strip(), "emp-")
    password = _password("employee")
    user = User.objects.create_user(username=username, password=password,
                                   first_name=first_name.strip(), last_name=last_name.strip())
    _membership(user)
    _grant(user, operator, "employee", 365)
    EmployeeAccount.objects.create(employee=user, first_name=first_name.strip(),
                                   last_name=last_name.strip(), created_by=operator)
    return {"username": username, "password": password, "role": "employee"}


@transaction.atomic
def create_lawyer(operator_principal, first_name: str, last_name: str, bar_number: str = "") -> dict:
    """Create a lawyer pilot with an upper-case-letter plus four-digit password."""
    require_employee(operator_principal)
    operator = _operator(operator_principal)
    if not first_name.strip() or not last_name.strip() or len(bar_number) > 40:
        raise CorpusError(ErrorCode.INVALID_INPUT)
    User = get_user_model()
    username = _username(first_name.strip(), last_name.strip(), "")
    password = _password("lawyer")
    user = User.objects.create_user(username=username, password=password,
                                   first_name=first_name.strip(), last_name=last_name.strip())
    _membership(user)
    _grant(user, operator, "pilot", 30)
    PilotAccount.objects.create(lawyer=user, first_name=first_name.strip(),
                                last_name=last_name.strip(), bar_number=bar_number.strip(),
                                created_by=operator)
    return {"username": username, "password": password, "role": "lawyer"}


@transaction.atomic
def reissue(operator_principal, account_id, role: str) -> dict:
    """Reissue a managed password and return it once to the employee."""
    require_employee(operator_principal)
    model = EmployeeAccount if role == "employee" else PilotAccount
    field = "employee" if role == "employee" else "lawyer"
    account = model.objects.select_related(field).filter(pk=account_id, status="activa").first()
    if account is None:
        raise CorpusError(ErrorCode.INVALID_INPUT)
    user = getattr(account, field)
    password = _password(role)
    user.set_password(password)
    user.save(update_fields=["password"])
    return {"username": user.username, "password": password, "role": role}


@transaction.atomic
def deactivate(operator_principal, account_id, role: str) -> str:
    """Deactivate an employee or lawyer, revoke grants, and preserve evidence."""
    require_employee(operator_principal)
    model = EmployeeAccount if role == "employee" else PilotAccount
    field = "employee" if role == "employee" else "lawyer"
    account = model.objects.select_related(field).filter(pk=account_id, status="activa").first()
    if account is None:
        raise CorpusError(ErrorCode.INVALID_INPUT)
    user = getattr(account, field)
    account.status = "eliminada"
    account.save(update_fields=["status"])
    user.is_active = False
    user.save(update_fields=["is_active"])
    AccessGrant.objects.filter(user=user, revoked_at__isnull=True).update(revoked_at=timezone.now())
    Membership.objects.filter(user=user, enabled=True).update(enabled=False)
    return user.username


def _employee_rows():
    """List managed employees plus legacy employee memberships awaiting profile backfill."""
    rows = []
    known = set()
    for account in EmployeeAccount.objects.select_related("employee", "created_by").order_by("-created_at"):
        rows.append({"account": account, "user": account.employee})
        known.add(account.employee_id)
    for membership in Membership.objects.filter(group__name=EMPLOYEES_GROUP, enabled=True).select_related("user"):
        if membership.user_id in known or PilotAccount.objects.filter(lawyer_id=membership.user_id).exists():
            continue
        rows.append({"account": None, "user": membership.user})
    return rows


def _context(form, created=None, notice=""):
    """Assemble the employee panel without exposing password hashes."""
    accounts = PilotAccount.objects.select_related("lawyer", "created_by").order_by("-created_at")[:50]
    lawyers = [{"account": account, "usage": usage_for(account.lawyer),
                "reports": PrivateFeedback.objects.filter(owner=account.lawyer).count()}
               for account in accounts]
    return {"form": form, "created": created, "notice": notice, "lawyers": lawyers,
            "employees": _employee_rows(),
            "recent": PilotEvent.objects.select_related("lawyer").order_by("-at")[:50],
            "reports": PrivateFeedback.objects.select_related("owner", "locator").order_by("-created_at")[:100],
            "employee_password_note": EMPLOYEE_PASSWORD_NOTE,
            "lawyer_password_note": LAWYER_PASSWORD_NOTE}


@require_http_methods(["GET", "POST"])
@guarded
def portal(request):
    """Shared employee panel: manage employees, lawyers, usage and reports."""
    if not request.user.is_authenticated:
        return redirect("portal-login")
    p = principal(request)
    require_employee(p)
    created = None
    form = PilotForm(request.POST if request.method == "POST" and request.POST.get("account_type") == "lawyer" else None)
    if request.method == "POST":
        strict(request.POST, {"account_type", "first_name", "last_name", "bar_number", "csrfmiddlewaretoken"})
        consume_budget(request, "portal-account")
        role = request.POST.get("account_type")
        first = request.POST.get("first_name", "").strip()
        last = request.POST.get("last_name", "").strip()
        if role == "employee":
            created = create_employee(p, first, last)
        elif form.is_valid():
            created = create_lawyer(p, first, last, form.cleaned_data.get("bar_number", ""))
            form = PilotForm(None)
    notice = request.session.pop("portal_notice", "")
    if created is None:
        created = request.session.pop("portal_credentials", None)
    return render(request, "corpus/portal.html", _context(form, created, notice))


@require_http_methods(["GET", "POST"])
@guarded
def portal_login(request):
    """Keep the direct employee URL available while the public login remains shared."""
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
                login(request, user)
                request.session["corpus_epoch"] = 1
                return redirect("portal")
    return render(request, "corpus/portal_login.html", {"form": form})


@require_http_methods(["POST"])
@guarded
def portal_logout(request):
    """Close an employee portal session."""
    strict(request.GET, set())
    strict(request.POST, {"csrfmiddlewaretoken"})
    logout(request)
    return redirect("portal-login")


@require_http_methods(["POST"])
@guarded
def portal_reissue(request, role, account_id):
    """Reissue a lawyer or employee password."""
    if not request.user.is_authenticated:
        return redirect("portal-login")
    strict(request.GET, set())
    strict(request.POST, {"csrfmiddlewaretoken"})
    consume_budget(request, "portal-account")
    request.session["portal_credentials"] = reissue(principal(request), account_id, role)
    return redirect("portal")


@require_http_methods(["POST"])
@guarded
def portal_delete(request, role, account_id):
    """Deactivate a lawyer or employee while preserving activity history."""
    if not request.user.is_authenticated:
        return redirect("portal-login")
    strict(request.GET, set())
    strict(request.POST, {"csrfmiddlewaretoken"})
    consume_budget(request, "portal-account")
    username = deactivate(principal(request), account_id, role)
    request.session["portal_notice"] = f"Acceso eliminado: {username}."
    return redirect("portal")
