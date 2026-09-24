"""sistema/django_app/corpus/access.py: current request-local authorization."""
import re
from uuid import UUID
from django.contrib.auth import get_user_model
from django.utils import timezone
from contracts.corpus_django import Principal, DocumentLocator, AccessDecision, ErrorCode
from .models import PolicyState, Membership, AccessGrant, Locator, PilotAccount

EMPLOYEES_GROUP = "corpus-empleados"


class CorpusError(Exception):
    """Bounded public error with no account or document contents."""
    def __init__(self, code: ErrorCode) -> None:
        self.code = code
        super().__init__(code.value)


def state_for(principal: Principal) -> PolicyState:
    """Reject absent identity, stale epoch, inactive account or quarantine."""
    state = PolicyState.objects.filter(pk=1, quarantined=False).first()
    if (state is None or type(principal.user_id) is not int
            or not get_user_model().objects.filter(pk=principal.user_id, is_active=True).exists()
            or principal.session_epoch != state.session_epoch):
        raise CorpusError(ErrorCode.ACCESS_DENIED)
    return state


def validate_locator(locator: DocumentLocator) -> None:
    """Validate the full untrusted locator; no implicit current-version fallback."""
    if (not isinstance(locator.collection_id, UUID) or not isinstance(locator.uid, str)
            or not 1 <= len(locator.uid) <= 200
            or not re.fullmatch("[0-9a-f]{64}", locator.version_sha256)):
        raise CorpusError(ErrorCode.INVALID_INPUT)


def eligible(principal: Principal):
    """Filter policy before any text or snippet is read, including empty catalogs."""
    state_for(principal)
    now = timezone.now()
    groups = Membership.objects.filter(user_id=principal.user_id, enabled=True).values("group_id")
    grants = AccessGrant.objects.filter(
        user_id=principal.user_id, group_id__in=groups, revoked_at__isnull=True,
        valid_from__lte=now, valid_until__gt=now).exclude(evidence_id="").values("collection_id")
    return Locator.objects.filter(
        collection_id__in=grants, collection__enabled=True, withdrawn_at__isnull=True
    ).exclude(collection__approval_evidence="").select_related("collection")


def require(principal: Principal, locator: DocumentLocator) -> Locator:
    """Reauthorize exact version on every read/write; staff is not a bypass."""
    validate_locator(locator)
    row = eligible(principal).filter(collection_id=locator.collection_id, uid=locator.uid,
                                     version_sha256=locator.version_sha256).first()
    if row is None:
        raise CorpusError(ErrorCode.ACCESS_DENIED)
    return row


def is_employee(principal: Principal) -> bool:
    """An employee is an enabled member of the employees group and never a pilot lawyer."""
    if PilotAccount.objects.filter(lawyer_id=principal.user_id).exists():
        return False
    return Membership.objects.filter(user_id=principal.user_id, enabled=True,
                                     group__name=EMPLOYEES_GROUP).exists()


def require_employee(principal: Principal) -> None:
    """Only employees operate the pilot desk; lawyers and staff-as-such are denied."""
    state_for(principal)
    if not is_employee(principal):
        raise CorpusError(ErrorCode.ACCESS_DENIED)


def authorize(principal: Principal, locator: DocumentLocator) -> AccessDecision:
    """Return a request-local decision, not a reusable capability."""
    try:
        require(principal, locator)
        return AccessDecision(True, state_for(principal).revision, timezone.now())
    except CorpusError:
        state = PolicyState.objects.filter(pk=1).first()
        return AccessDecision(False, state.revision if state else 0, timezone.now())
