"""sistema/django_app/corpus/tests/test_workflow.py: whole private HTTP workflow."""
import hashlib
import re
import time
from unittest.mock import patch
from django.test import Client
from django.core import mail
from django.utils import timezone
from contracts.corpus_django import Principal
from corpus.models import Locator, SavedReference, PrivateFeedback, Collection, PolicyState
from corpus.access import CorpusError
from .test_access import FixtureBase


class WorkflowTests(FixtureBase):
    """Exercise auth, search, read, save, report, reset and failure paths."""
    def test_real_http_journey_and_private_ownership(self):
        self.login()
        result = self.client.get("/corpus/", {"q": "Artículo"})
        self.assertContains(result, "Documento sintético")
        self.assertEqual(result["Cache-Control"], "no-store")
        self.assertIn("frame-ancestors 'none'", result["Content-Security-Policy"])
        self.assertContains(self.client.get("/corpus/read/", self.fields), "Artículo 1")
        fields = dict(self.fields, csrfmiddlewaretoken=self.client.cookies["csrftoken"].value)
        self.assertEqual(self.client.post("/corpus/save/", fields).status_code, 302)
        self.assertEqual(SavedReference.objects.get().owner_id, self.ana.pk)
        response = self.client.post("/corpus/feedback/", dict(fields, category="extraction",
                                                               description="<script>private</script>"),
                                    HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(set(response.json()), {"id", "created_at", "status"})
        self.assertEqual(PrivateFeedback.objects.get().owner_id, self.ana.pk)
        self.assertContains(self.client.get("/corpus/"), "&lt;script&gt;private&lt;/script&gt;")
        ben = self.login(Client(enforce_csrf_checks=True), "fixture-ben")
        self.assertNotContains(ben.get("/corpus/"), "private")
        self.assertEqual(ben.get("/corpus/read/", self.fields).status_code, 403)
        self.assertEqual(len(mail.outbox) if hasattr(mail, "outbox") else 0, 0)

    def test_withdrawal_after_page_blocks_read_save_report_and_reference(self):
        self.login()
        self.app.save_reference(self.p, self.locator)
        Locator.objects.update(withdrawn_at=timezone.now())
        self.assertEqual(self.app.list_references(self.p), ())
        self.assertEqual(self.client.get("/corpus/read/", self.fields).status_code, 403)
        fields = dict(self.fields, csrfmiddlewaretoken=self.client.cookies["csrftoken"].value)
        self.assertEqual(self.client.post("/corpus/save/", fields).status_code, 403)
        self.assertEqual(self.client.post("/corpus/feedback/", dict(fields, category="other",
                                                                  description="x")).status_code, 403)

    def test_reference_deduplication_and_no_content_columns(self):
        self.app.save_reference(self.p, self.locator)
        self.app.save_reference(self.p, self.locator)
        self.assertEqual(SavedReference.objects.count(), 1)
        self.assertEqual({f.name for f in SavedReference._meta.fields},
                         {"id", "owner", "locator", "created_at"})
        self.assertEqual(self.app.list_references(Principal(self.ben.pk, 1)), ())

    def test_strict_query_duplicate_unknown_and_invalid_ranges(self):
        self.login()
        for query in ["q=a&q=b", "q=a&admin=1", "q=a&offset=-1", "q=a&offset=01",
                      "q=a&limit=21", "q=" + "x" * 129, "q=" + "界" * 100]:
            self.assertEqual(self.client.get("/corpus/?" + query).status_code, 400, query)
        for start in ["-1", "01", "x"]:
            self.assertEqual(self.client.get("/corpus/read/", dict(self.fields, start=start)).status_code, 400)

    def test_service_range_and_feedback_validation(self):
        for start, limit in [(-1, 1), (0, 0), (0, 10001), (True, 1)]:
            with self.assertRaises(CorpusError):
                self.app.read(self.p, self.locator, start, limit)
        for category, description in [("bad", "ok"), ("other", ""), ("other", "x" * 2001)]:
            with self.assertRaises(CorpusError):
                self.app.report_error(self.p, self.locator, category, description)
        for query, offset, limit in [("", 0, 10), ("a", -1, 1), ("a", 0, 21)]:
            with self.assertRaises(CorpusError):
                self.app.search(self.p, query, offset, limit)

    def test_hash_failure_never_returns_text(self):
        Collection.objects.update(snapshot_digest="0" * 64)
        self.login()
        response = self.client.get("/corpus/read/", self.fields)
        self.assertEqual(response.status_code, 503)
        self.assertNotIn(b"Documento", response.content)

    def test_snapshot_symlink_rejected(self):
        link = self.snapshot.with_name("link")
        link.symlink_to(self.snapshot)
        Collection.objects.update(snapshot_path=str(link))
        with self.assertRaises(CorpusError):
            self.app.read(self.p, self.locator, 0, 100)

    def test_search_budget_failure_not_partial_success(self):
        with patch("corpus.services.time.monotonic", side_effect=[0, 6]):
            with self.assertRaises(CorpusError):
                self.app.search(self.p, "Artículo", 0, 10)

    def test_synthetic_search_latency_and_pagination(self):
        start = time.monotonic()
        found = self.app.search(self.p, "Artículo", 0, 1)
        self.assertEqual(len(found.results), 1)
        self.assertIsNone(found.next_offset)
        self.assertEqual(self.app.search(self.p, "absent", 0, 1).results, ())
        self.assertLess(time.monotonic() - start, 5)

    def test_password_reset_uniform_and_old_session_invalidated(self):
        self.login()
        session = self.client.cookies["sessionid"].value
        token = self.client.cookies["csrftoken"].value
        exists = self.client.post("/corpus/reset/", {"email": "ana@example.invalid",
                                                     "csrfmiddlewaretoken": token})
        missing = self.client.post("/corpus/reset/", {"email": "nobody@example.invalid",
                                                      "csrfmiddlewaretoken": token})
        self.assertEqual(exists.content, missing.content)
        self.assertEqual(len(mail.outbox), 1)
        url = re.search(r"http://testserver(\S+)", mail.outbox[0].body).group(1)
        response = self.client.post(url, {"new_password1": "New-Synthetic-Password-987!",
            "new_password2": "New-Synthetic-Password-987!", "csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 302)
        stale = Client()
        stale.cookies["sessionid"] = session
        self.assertEqual(stale.get("/corpus/").status_code, 403)
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_health_distinguishes_process_from_policy(self):
        PolicyState.objects.update(quarantined=True)
        self.assertEqual(self.client.get("/corpus/live/").status_code, 200)
        self.assertEqual(self.client.get("/corpus/ready/").status_code, 503)
        self.assertEqual(self.client.get("/corpus/health/").status_code, 503)
