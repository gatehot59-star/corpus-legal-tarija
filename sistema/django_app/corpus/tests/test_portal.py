"""Employee portal tests: independent entrance, credential reissue, deletion, telemetry."""
from datetime import timedelta
from django.contrib.auth.models import Group
from django.test import Client
from django.utils import timezone
from corpus.access import EMPLOYEES_GROUP
from corpus.management.commands.provision_fixture import FIXTURE_PASSWORD
from corpus.models import PilotAccount, PilotEvent, Membership, AccessGrant
from corpus.services import usage_for
from .test_access import FixtureBase


class PortalTests(FixtureBase):
    """The portal is a separate door for employees, with full account control."""

    def make_employee(self, user=None) -> None:
        group, _ = Group.objects.get_or_create(name=EMPLOYEES_GROUP)
        Membership.objects.get_or_create(user=user or self.ana, group=group,
                                         defaults={"enabled": True})

    def _create_lawyer(self) -> tuple[str, str]:
        """Create a pilot account through the portal and return its credentials."""
        self.make_employee()
        self.login()
        token = self.client.cookies["csrftoken"].value
        response = self.client.post("/empleados/", {
            "first_name": "María", "last_name": "Suárez", "bar_number": "12345",
            "csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 200)
        account = PilotAccount.objects.order_by("-created_at").first()
        creds = [p.split("</code>")[0] for p in response.content.decode().split("<code>")[1:]]
        password = [c for c in creds if c != account.lawyer.username][0]
        return account.lawyer.username, password

    @staticmethod
    def _login_attempt(username: str, password: str) -> int:
        client = Client(enforce_csrf_checks=True)
        client.get("/corpus/login/")
        response = client.post("/corpus/login/", {
            "username": username, "password": password,
            "csrfmiddlewaretoken": client.cookies["csrftoken"].value})
        return response.status_code

    def test_portal_anonymous_is_sent_to_its_own_login(self):
        response = Client().get("/empleados/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/empleados/login/")

    def test_portal_login_page_is_product_neutral(self):
        response = Client().get("/empleados/login/")
        self.assertContains(response, "Panel de empleados")
        self.assertNotContains(response, "La ley, lista para citar.")

    def test_lawyer_cannot_enter_through_portal_login(self):
        username, password = self._create_lawyer()
        client = Client(enforce_csrf_checks=True)
        client.get("/empleados/login/")
        response = client.post("/empleados/login/", {
            "username": username, "password": password,
            "csrfmiddlewaretoken": client.cookies["csrftoken"].value})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "solo para el equipo")
        redirected = client.get("/empleados/")
        self.assertEqual(redirected.status_code, 302)

    def test_employee_enters_through_portal_login(self):
        self.make_employee()
        client = Client(enforce_csrf_checks=True)
        client.get("/empleados/login/")
        response = client.post("/empleados/login/", {
            "username": "fixture-ana", "password": FIXTURE_PASSWORD,
            "csrfmiddlewaretoken": client.cookies["csrftoken"].value})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/empleados/")
        self.assertContains(client.get("/empleados/"), "Cuentas de abogados")

    def test_reissue_password_shows_new_credentials_and_old_fails(self):
        username, old_password = self._create_lawyer()
        account = PilotAccount.objects.get(lawyer__username=username)
        token = self.client.cookies["csrftoken"].value
        response = self.client.post(f"/empleados/cuentas/{account.pk}/clave/",
                                    {"csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 302)
        page = self.client.get("/empleados/")
        self.assertContains(page, "Credenciales listas para entregar")
        creds = [p.split("</code>")[0] for p in page.content.decode().split("<code>")[1:]]
        new_password = [c for c in creds if c != username][0]
        self.assertNotEqual(new_password, old_password)
        self.assertEqual(self._login_attempt(username, old_password), 200)
        self.assertEqual(self._login_attempt(username, new_password), 302)

    def test_delete_account_blocks_login_and_keeps_history(self):
        username, password = self._create_lawyer()
        lawyer = Client(enforce_csrf_checks=True)
        lawyer.get("/corpus/login/")
        lawyer.post("/corpus/login/", {"username": username, "password": password,
                    "csrfmiddlewaretoken": lawyer.cookies["csrftoken"].value})
        lawyer.get("/corpus/", {"q": "artículo"})
        self.assertTrue(PilotEvent.objects.filter(section="Búsqueda").exists())
        account = PilotAccount.objects.get(lawyer__username=username)
        token = self.client.cookies["csrftoken"].value
        response = self.client.post(f"/empleados/cuentas/{account.pk}/eliminar/",
                                    {"csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 302)
        account.refresh_from_db()
        self.assertEqual(account.status, "eliminada")
        self.assertFalse(account.lawyer.is_active)
        self.assertFalse(AccessGrant.objects.filter(user=account.lawyer,
                                                    revoked_at__isnull=True).exists())
        self.assertEqual(self._login_attempt(username, password), 200)
        self.assertTrue(PilotEvent.objects.filter(lawyer=account.lawyer).exists())
        self.assertContains(self.client.get("/empleados/"), "Eliminada")

    def test_usage_summary_groups_sessions(self):
        username, _ = self._create_lawyer()
        account = PilotAccount.objects.get(lawyer__username=username)
        now = timezone.now()
        for minutes_ago in [100, 20, 10, 0]:
            event = PilotEvent.objects.create(lawyer=account.lawyer, section="Inicio")
            PilotEvent.objects.filter(pk=event.pk).update(at=now - timedelta(minutes=minutes_ago))
        usage = usage_for(account.lawyer)
        self.assertEqual(usage["pages"], 4)
        self.assertEqual(usage["sessions"], 2)
        self.assertEqual(usage["minutes"], 22)

    def test_employee_browsing_is_not_tracked(self):
        self.make_employee()
        self.login()
        self.client.get("/corpus/")
        self.client.get("/corpus/", {"q": "artículo"})
        self.assertEqual(PilotEvent.objects.count(), 0)

    def test_tracking_records_sections_and_details(self):
        username, password = self._create_lawyer()
        lawyer = Client(enforce_csrf_checks=True)
        lawyer.get("/corpus/login/")
        lawyer.post("/corpus/login/", {"username": username, "password": password,
                    "csrfmiddlewaretoken": lawyer.cookies["csrftoken"].value})
        lawyer.get("/corpus/read/", self.fields)
        sections = list(PilotEvent.objects.values_list("section", flat=True))
        self.assertIn("Ingreso", sections)
        self.assertIn("Lectura de documento", sections)
        read = PilotEvent.objects.get(section="Lectura de documento")
        self.assertEqual(read.detail, self.locator.uid)

    def test_legacy_pilot_path_redirects_to_portal(self):
        self.make_employee()
        self.login()
        response = self.client.get("/corpus/piloto/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/empleados/")
