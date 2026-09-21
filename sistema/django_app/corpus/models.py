"""sistema/django_app/corpus/models.py: operational policy, never legal text."""
import uuid
from django.conf import settings
from django.db import models
from django.db.models import Q, F


class PolicyState(models.Model):
    """Singleton current authority; absence and quarantine deny service."""
    id = models.PositiveSmallIntegerField(primary_key=True, default=1)
    revision = models.PositiveBigIntegerField(default=1)
    session_epoch = models.PositiveBigIntegerField(default=1)
    quarantined = models.BooleanField(default=True)

    class Meta:
        constraints = [models.CheckConstraint(condition=Q(id=1), name="policy_singleton")]


class Collection(models.Model):
    """Approved immutable snapshot path assigned only by an operator."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    enabled = models.BooleanField(default=False)
    approval_evidence = models.CharField(max_length=200)
    snapshot_path = models.TextField()
    snapshot_digest = models.CharField(max_length=64)


class Membership(models.Model):
    """Explicit enabled membership; Django staff grants no corpus access."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey("auth.Group", on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "group"], name="membership_unique")]


class Locator(models.Model):
    """Server catalog of precise versions, with persistent withdrawal."""
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    uid = models.CharField(max_length=200)
    version_sha256 = models.CharField(max_length=64)
    title = models.CharField(max_length=240)
    withdrawn_at = models.DateTimeField(null=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["collection", "uid", "version_sha256"],
                                               name="locator_unique")]


class AccessGrant(models.Model):
    """Time-bounded attributable permission, not implied by membership."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="corpus_grants")
    group = models.ForeignKey("auth.Group", on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    origin = models.CharField(max_length=30)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True)
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                 related_name="issued_corpus_grants")
    evidence_id = models.CharField(max_length=200)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(valid_until__gt=F("valid_from")), name="grant_interval"),
            models.CheckConstraint(condition=~Q(evidence_id=""), name="grant_evidence"),
        ]
        indexes = [models.Index(fields=["user", "collection", "valid_until"], name="grant_lookup")]


class SavedReference(models.Model):
    """Owned locator only; no copied content, password or bearer token."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    locator = models.ForeignKey(Locator, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["owner", "locator"], name="reference_unique")]


class PrivateFeedback(models.Model):
    """Private bounded report, never mirrored to third parties."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    locator = models.ForeignKey(Locator, on_delete=models.PROTECT)
    category = models.CharField(max_length=16)
    description = models.CharField(max_length=2000)
    status = models.CharField(max_length=16, default="received")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(category__in=["extraction", "metadata", "access", "other"]),
                                   name="feedback_category"),
            models.CheckConstraint(condition=Q(status="received"), name="feedback_initial_status"),
        ]


class AttemptBudget(models.Model):
    """Persistent per-IP/purpose/window budget, stored as keyed digest."""
    key = models.CharField(primary_key=True, max_length=64)
    attempts = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField()
