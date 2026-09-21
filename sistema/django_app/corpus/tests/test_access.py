"""sistema/django_app/corpus/tests/test_access.py: causal policy and CSRF tests."""
import tempfile
from pathlib import Path
from datetime import timedelta
from unittest.mock import patch
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from contracts.corpus_django import Principal
from corpus.models import PolicyState, AccessGrant, Membership, Collection, Locator
from corpus.management.commands.provision_fixture import provision, FIXTURE_PASSWORD
from corpus.services import Application, locator_of
from corpus.access import CorpusError


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class FixtureBase(TestCase):
    """Real ORM and snapshot fixture; no production identities or network."""
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.snapshot = Path(self.temp.name) / "snapshot.sqlite3"
        self.fields = provision(self.snapshot)
        self.ana = get_user_model().objects.get(username="fixture-ana")
        self.ben = get_user_model().objects.get(username="fixture-ben")
        self.row = Locator.objects.get()
        self.locator = locator_of(self.row)
        self.p = Principal(self.ana.pk, 1)
        self.app = Application()
        self.client = Client(enforce_csrf_checks=True)

    def login(self, client=None, username="fixture-ana") -> Client:
        """Perform real CSRF login with session rotation, not force_login."""
        client = client or self.client
        client.get("/corpus/login/")
        response = client.post("/corpus/login/", {"username": username, "password": FIXTURE_PASSWORD,
                              "csrfmiddlewaretoken": client.cookies["csrftoken"].value})
        self.assertEqual(response.status_code, 302)
        return client

    def denied(self, p=None) -> None:
        """Require a domain failure, not empty output masquerading as authorization."""
        with self.assertRaises(CorpusError):
            self.app.read(p or self.p, self.locator, 0, 100)


class AccessTests(FixtureBase):
    """Challenge each server-side policy conjunct and the actual HTTP boundary."""
    def test_positive_reader_and_contract(self):
        result = self.app.read(self.p, self.locator, 0, 100)
        self.assertIn("Artículo 1", result.text)
        self.assertEqual(result.authority, "secondary")
        self.assertTrue(self.app.authorize(self.p, self.locator).allowed)

    def test_no_grant_and_staff_never_bypass(self):
        self.ben.is_staff = self.ben.is_superuser = True
        self.ben.save()
        self.denied(Principal(self.ben.pk, 1))

    def test_future_grant_denied(self):
        AccessGrant.objects.update(valid_from=timezone.now() + timedelta(hours=1))
        self.denied()

    def test_expired_grant_denied(self):
        AccessGrant.objects.update(valid_from=timezone.now() - timedelta(days=2),
                                   valid_until=timezone.now() - timedelta(seconds=1))
        self.denied()

    def test_revoked_grant_denied(self):
        AccessGrant.objects.update(revoked_at=timezone.now())
        self.denied()

    def test_disabled_membership_denied(self):
        Membership.objects.update(enabled=False)
        self.denied()

    def test_wrong_group_denied(self):
        wrong = Group.objects.create(name="other")
        AccessGrant.objects.update(group=wrong)
        self.denied()

    def test_withdrawn_version_denied(self):
        Locator.objects.update(withdrawn_at=timezone.now())
        self.denied()

    def test_disabled_collection_denied(self):
        Collection.objects.update(enabled=False)
        self.denied()

    def test_unapproved_collection_denied(self):
        Collection.objects.update(approval_evidence="")
        self.denied()

    def test_inactive_user_denied(self):
        self.ana.is_active = False
        self.ana.save()
        self.denied()

    def test_epoch_and_quarantine_deny(self):
        self.denied(Principal(self.ana.pk, 0))
        PolicyState.objects.update(quarantined=True)
        self.denied()

    def test_empty_catalog_still_requires_valid_identity(self):
        Locator.objects.all().delete()
        with self.assertRaises(CorpusError):
            self.app.search(Principal(999999, 1), "artículo", 0, 10)

    def test_authorization_precedes_reader(self):
        with patch("corpus.services.read_exact", side_effect=AssertionError("Unauthorized read")):
            self.denied(Principal(self.ben.pk, 1))
            self.assertEqual(self.app.search(Principal(self.ben.pk, 1), "artículo", 0, 10).results, ())

    def test_login_csrf_required_and_no_header_identity(self):
        self.assertEqual(self.client.post("/corpus/login/", {
            "username": "fixture-ana", "password": FIXTURE_PASSWORD}).status_code, 403)
        self.assertEqual(self.client.get("/corpus/", HTTP_X_USER=str(self.ana.pk)).status_code, 403)

    def test_write_csrf_required_even_when_authenticated(self):
        self.login()
        self.assertEqual(self.client.post("/corpus/save/", self.fields).status_code, 403)
        self.assertEqual(self.client.get("/corpus/logout/").status_code, 405)

    def test_logout_invalidates_old_cookie(self):
        self.login()
        old = self.client.cookies["sessionid"].value
        response = self.client.post("/corpus/logout/", {
            "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value})
        self.assertEqual(response.status_code, 302)
        stale = Client()
        stale.cookies["sessionid"] = old
        self.assertEqual(stale.get("/corpus/").status_code, 403)

    def test_throttle_is_persistent_across_clients(self):
        for _ in range(10):
            client = Client(enforce_csrf_checks=True)
            client.get("/corpus/login/")
            self.assertEqual(client.post("/corpus/login/", {"username": "unknown", "password": "bad",
                "csrfmiddlewaretoken": client.cookies["csrftoken"].value}).status_code, 200)
        response = self.client.get("/corpus/login/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.post("/corpus/login/", {"username": "unknown", "password": "bad",
            "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value}).status_code, 429)

    def test_wrong_collection_and_invalid_locator(self):
        from dataclasses import replace
        from uuid import uuid4
        for loc in [replace(self.locator, collection_id=uuid4()),
                    replace(self.locator, version_sha256="bad"), replace(self.locator, uid="")]:
            with self.assertRaises(CorpusError):
                self.app.read(self.p, loc, 0, 100)
