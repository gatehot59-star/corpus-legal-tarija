"""Pilot desk tests: employee-created accounts must actually work."""
from django.test import Client
from corpus.models import PilotAccount
from .test_access import FixtureBase


class PilotTests(FixtureBase):
    """The pilot desk creates real, working, authorized lawyer accounts."""

    def test_pilot_page_requires_authentication(self):
        self.assertEqual(Client().get("/corpus/piloto/").status_code, 403)

    def test_pilot_creation_flow_and_login(self):
        self.login()
        token = self.client.cookies["csrftoken"].value
        response = self.client.post("/corpus/piloto/", {
            "first_name": "María", "last_name": "Suárez", "bar_number": "12345",
            "csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 200)
        account = PilotAccount.objects.get()
        self.assertEqual(account.first_name, "María")
        self.assertEqual(account.bar_number, "12345")
        username = account.lawyer.username
        body = response.content.decode()
        self.assertIn(username, body)
        lawyer_client = Client(enforce_csrf_checks=True)
        lawyer_client.get("/corpus/login/")
        password = None
        for part in body.split("<code>"):
            if "</code>" in part:
                value = part.split("</code>")[0]
                if value != username:
                    password = value
        self.assertIsNotNone(password)
        login = lawyer_client.post("/corpus/login/", {"username": username, "password": password,
            "csrfmiddlewaretoken": lawyer_client.cookies["csrftoken"].value})
        self.assertEqual(login.status_code, 302)
        self.assertContains(lawyer_client.get("/corpus/"), "Buscar. Leer. Verificar.")

    def test_pilot_page_lists_reports_from_lawyers(self):
        self.login()
        self.app.report_error(self.p, self.locator, "metadata", "El título no coincide con la fuente.")
        response = self.client.get("/corpus/piloto/")
        self.assertContains(response, "fixture-ana")
        self.assertContains(response, "El título no coincide")

    def test_pilot_form_rejects_empty_names(self):
        self.login()
        token = self.client.cookies["csrftoken"].value
        response = self.client.post("/corpus/piloto/", {
            "first_name": "", "last_name": "", "bar_number": "",
            "csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PilotAccount.objects.count(), 0)

    def test_pilot_password_is_never_stored_in_plain_text(self):
        """The stored credential is a hash, and the PilotAccount keeps no password."""
        self.login()
        token = self.client.cookies["csrftoken"].value
        self.client.post("/corpus/piloto/", {
            "first_name": "Juan", "last_name": "Pérez", "bar_number": "",
            "csrfmiddlewaretoken": token})
        account = PilotAccount.objects.get()
        self.assertFalse(hasattr(account, "password"))
        stored = account.lawyer.password
        self.assertIn("$", stored)
        self.assertNotEqual(stored, "")
        self.assertFalse(stored.isalnum())
