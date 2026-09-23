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
        Membership.objects.create(user=user or self.ana, group=group, enabled=True)

    def test_pilot_page_requires_authentication(self):
        self.assertEqual(Client().get("/corpus/piloto/").status_code, 403)

    def test_pilot_page_denies_non_employee(self):
        """A reader without the employee group cannot open the desk."""
        self.login()
        self.assertEqual(self.client.get("/corpus/piloto/").status_code, 403)

    def test_pilot_page_denies_pilot_lawyer(self):
        """A created lawyer is denied even if someone adds them to the group."""
        self.make_employee()
        self.login()
        token = self.client.cookies["csrftoken"].value
        self.client.post("/corpus/piloto/", {
            "first_name": "María", "last_name": "Suárez", "bar_number": "",
            "csrfmiddlewaretoken": token})
        lawyer = PilotAccount.objects.get().lawyer
        Membership.objects.create(user=lawyer, group=Group.objects.get(name=EMPLOYEES_GROUP))
        lawyer_client = self.login(Client(enforce_csrf_checks=True), "fixture-ben")
        self.assertEqual(lawyer_client.get("/corpus/piloto/").status_code, 403)
        lawyer_client2 = Client(enforce_csrf_checks=True)
        lawyer_client2.get("/corpus/login/")
        body = self.client.post("/corpus/piloto/", {
            "first_name": "Ana", "last_name": "Otra", "bar_number": "",
            "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value}).content.decode()
        creds = [p.split("</code>")[0] for p in body.split("<code>")[1:]]
        username = PilotAccount.objects.order_by("-created_at").first().lawyer.username
        password = [c for c in creds if c != username][0]
        login = lawyer_client2.post("/corpus/login/", {"username": username, "password": password,
            "csrfmiddlewaretoken": lawyer_client2.cookies["csrftoken"].value})
        self.assertEqual(login.status_code, 302)
        self.assertEqual(lawyer_client2.get("/corpus/piloto/").status_code, 403)

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
