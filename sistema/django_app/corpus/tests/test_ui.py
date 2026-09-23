"""UI polish regression tests for the reading desk templates."""
from django.test import Client
from .test_access import FixtureBase


class UiTests(FixtureBase):
    """The redesigned pages must remain usable, readable and authorized."""

    def test_workspace_shell_exposes_theme_toggle_and_catalog_controls(self):
        """The workspace renders the professional shell, filters and theme control."""
        self.login()
        response = self.client.get("/corpus/")
        self.assertContains(response, 'data-theme-toggle')
        self.assertContains(response, 'Explorar el catálogo')
        self.assertContains(response, 'Tus referencias')
        self.assertContains(response, 'Tus reportes privados')
        self.assertContains(response, 'Buscar. Leer. Verificar.')

    def test_reader_shell_keeps_provenance_and_actions_visible(self):
        """The reading view keeps verification and private actions in a separate rail."""
        self.login()
        response = self.client.get("/corpus/read/", self.fields)
        self.assertContains(response, 'Procedencia verificada')
        self.assertContains(response, 'Guardar referencia privada')
        self.assertContains(response, 'Reportar un problema en privado')
        self.assertContains(response, 'data-theme-toggle')

    def test_login_shell_exposes_theme_toggle_and_access_links(self):
        """The login page keeps the same design system and recovery links."""
        response = Client(enforce_csrf_checks=True).get("/corpus/login/")
        self.assertContains(response, 'data-theme-toggle')
        self.assertContains(response, 'Recuperar cuenta')
        self.assertContains(response, 'Sin acceso público a documentos')
