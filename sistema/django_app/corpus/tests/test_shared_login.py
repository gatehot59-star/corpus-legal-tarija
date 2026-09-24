"""Shared login tests: one entrance, role-specific destination."""
from django.contrib.auth.models import Group
from django.test import Client
from corpus.access import EMPLOYEES_GROUP
from corpus.models import Membership
from corpus.management.commands.provision_fixture import FIXTURE_PASSWORD
from .test_access import FixtureBase


class SharedLoginTests(FixtureBase):
    """The public login link sends each authenticated role to its own window."""

    def test_employee_uses_same_login_and_lands_in_portal(self):
        """An employee does not need a second login URL."""
        group, _ = Group.objects.get_or_create(name=EMPLOYEES_GROUP)
        Membership.objects.create(user=self.ana, group=group, enabled=True)
        client = Client(enforce_csrf_checks=True)
        client.get("/corpus/login/")
        response = client.post("/corpus/login/", {
            "username": "fixture-ana", "password": FIXTURE_PASSWORD,
            "csrfmiddlewaretoken": client.cookies["csrftoken"].value})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/empleados/")
        self.assertContains(client.get("/empleados/"), "Panel de empleados")

    def test_lawyer_uses_same_login_and_lands_in_corpus(self):
        """A pilot lawyer still lands in the legal reading workspace."""
        client = Client(enforce_csrf_checks=True)
        client.get("/corpus/login/")
        response = client.post("/corpus/login/", {
            "username": "fixture-ana", "password": FIXTURE_PASSWORD,
            "csrfmiddlewaretoken": client.cookies["csrftoken"].value})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/corpus/")
        self.assertContains(client.get("/corpus/"), "Buscar. Leer. Verificar.")
