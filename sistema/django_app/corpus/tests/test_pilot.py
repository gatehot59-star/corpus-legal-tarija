"""Pilot desk tests: employee-only role, and created accounts must work."""
from django.contrib.auth.models import Group
from django.test import Client
from corpus.access import EMPLOYEES_GROUP
from corpus.models import PilotAccount, Membership
from .test_access import FixtureBase


class PilotTests(FixtureBase):
    """The pilot desk is for employees; pilot lawyers can only read the corpus."""

    def make_employee(self, user=None) -> None:
        """Grant the employee role explicitly, as an operator would."""
        group, _ = Group.objects.get_or_create(name=EMPLOYEES_GROUP)
        Membership.objects.get_or_create(user=user or self.ana, group=group,
                                         defaults={"enabled": True})

    def _issued_credentials(self, body: str) -> tuple[str, str]:
        """Extract the one-time credentials from the desk response."""
        creds = [p.split("</code>")[0] for p in body.split("<code>")[1:]]
        username = PilotAccount.objects.order_by("-created_at").first().lawyer.username
        password = [c for c in creds if c != username][0]
        return username, password

    def _login_as(self, client: Client, username: str, password: str) -> Client:
        """Real CSRF login for a freshly created account."""
        client.get("/corpus/login/")
        login = client.post("/corpus/login/", {"username": username, "password": password,
            "csrfmiddlewaretoken": client.cookies["csrftoken"].value})
        self.assertEqual(login.status_code, 302)
        return client

    def test_pilot_page_requires_authentication(self):
        self.assertEqual(Client().get("/corpus/piloto/").status_code, 403)

    def test_pilot_page_denies_non_employee(self):
        """A reader without the employee group cannot open the desk."""
        self.login()
        self.assertEqual(self.client.get("/corpus/piloto/").status_code, 403)

    def test_pilot_page_denies_pilot_lawyer(self):
        """A created lawyer is denied even with a valid session and grant."""
        self.make_employee()
        self.login()
        token = self.client.cookies["csrftoken"].value
        response = self.client.post("/corpus/piloto/", {
            "first_name": "Ana", "last_name": "Otra", "bar_number": "",
            "csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 200)
        username, password = self._issued_credentials(response.content.decode())
        lawyer_client = self._login_as(Client(enforce_csrf_checks=True), username, password)
        self.assertEqual(lawyer_client.get("/corpus/piloto/").status_code, 403)
        self.assertContains(lawyer_client.get("/corpus/"), "Buscar. Leer. Verificar.")

    def test_pilot_creation_flow_and_login(self):
        self.make_employee()
        self.login()
        token = self.client.cookies["csrftoken"].value
        response = self.client.post("/corpus/piloto/", {
            "first_name": "María", "last_name": "Suárez", "bar_number": "12345",
            "csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 200)
        account = PilotAccount.objects.get()
        self.assertEqual(account.first_name, "María")
        self.assertEqual(account.bar_number, "12345")
        username, password = self._issued_credentials(response.content.decode())
        lawyer_client = self._login_as(Client(enforce_csrf_checks=True), username, password)
        self.assertContains(lawyer_client.get("/corpus/"), "Buscar. Leer. Verificar.")

    def test_pilot_page_lists_reports_from_lawyers(self):
        self.make_employee()
        self.login()
        self.app.report_error(self.p, self.locator, "metadata", "El título no coincide con la fuente.")
        response = self.client.get("/corpus/piloto/")
        self.assertContains(response, "fixture-ana")
        self.assertContains(response, "El título no coincide")

    def test_pilot_form_rejects_empty_names(self):
        self.make_employee()
        self.login()
        token = self.client.cookies["csrftoken"].value
        response = self.client.post("/corpus/piloto/", {
            "first_name": "", "last_name": "", "bar_number": "",
            "csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PilotAccount.objects.count(), 0)

    def test_pilot_password_is_never_stored_in_plain_text(self):
        """The stored credential is a hash, and the PilotAccount keeps no password."""
        self.make_employee()
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

    def test_workspace_shows_pilot_link_only_to_employees(self):
        """The desk link appears for employees and stays hidden for readers."""
        self.login()
        self.assertNotContains(self.client.get("/corpus/"), "Prueba piloto")
        self.make_employee()
        self.assertContains(self.client.get("/corpus/"), "Prueba piloto")
