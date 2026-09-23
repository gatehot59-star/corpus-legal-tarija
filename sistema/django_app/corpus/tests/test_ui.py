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

    def test_reader_shell_keeps_provenance_actions_and_human_title(self):
        """The reading view keeps verification, private actions and the real title."""
        self.login()
        response = self.client.get("/corpus/read/", self.fields)
        self.assertContains(response, 'Procedencia verificada')
        self.assertContains(response, 'Guardar referencia privada')
        self.assertContains(response, 'Reportar un problema en privado')
        self.assertContains(response, 'data-theme-toggle')
        self.assertContains(response, 'Documento sintético')

    def test_login_shell_exposes_theme_toggle_and_access_links(self):
        """The login page keeps the same design system and recovery links."""
        response = Client(enforce_csrf_checks=True).get("/corpus/login/")
        self.assertContains(response, 'data-theme-toggle')
        self.assertContains(response, 'Recuperar cuenta')
        self.assertContains(response, 'Sin acceso público a documentos')

    def test_theme_toggle_sets_cookie_and_renders_dark(self):
        """Theme switching is a plain POST: no scripts, CSP stays scriptless."""
        self.login()
        token = self.client.cookies["csrftoken"].value
        response = self.client.post("/corpus/theme/", {"theme": "dark", "next": "/corpus/",
                                                       "csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.cookies["corpus_theme"].value, "dark")
        page = self.client.get("/corpus/")
        self.assertContains(page, 'data-theme="dark"')
        self.assertContains(page, 'Modo claro')

    def test_theme_toggle_rejects_bad_values_and_external_redirect(self):
        """Only light/dark/auto are accepted; next must stay on this site."""
        self.login()
        token = self.client.cookies["csrftoken"].value
        bad = self.client.post("/corpus/theme/", {"theme": "evil", "next": "/corpus/",
                                                  "csrfmiddlewaretoken": token})
        self.assertEqual(bad.status_code, 400)
        offsite = self.client.post("/corpus/theme/", {"theme": "light",
                                                      "next": "https://evil.example/",
                                                      "csrfmiddlewaretoken": token})
        self.assertEqual(offsite.status_code, 302)
        self.assertEqual(offsite["Location"], "/corpus/")

    def test_pages_ship_without_inline_scripts(self):
        """CSP forbids scripts; templates must not rely on them at all."""
        self.login()
        for url in ["/corpus/", "/corpus/login/", "/corpus/read/"]:
            target = self.client.get(url, self.fields if url.endswith("read/") else None)
            self.assertNotIn(b"<script", target.content, url)

    def test_search_results_have_no_redundant_badges(self):
        """Result cards show title, snippet and provenance note, not empty badges."""
        self.login()
        response = self.client.get("/corpus/", {"q": "Artículo"})
        self.assertNotContains(response, '>Resultado<')
        self.assertNotContains(response, '>Versión verificada<')

    def test_workspace_report_form_has_glossary_and_target_after_read(self):
        """Reporting is possible from the workspace too, with plain-language categories."""
        self.login()
        self.client.get("/corpus/read/", self.fields)
        self.app.save_reference(self.p, self.locator)
        response = self.client.get("/corpus/")
        self.assertContains(response, 'Reportar un problema')
        self.assertContains(response, 'Metadatos')
        self.assertContains(response, 'Datos del documento mal puestos')
        self.assertContains(response, 'Extracción')
        self.assertContains(response, 'El texto se ve cortado')
        self.assertContains(response, self.locator.uid)

    def test_workspace_report_form_without_target_is_guided(self):
        """Without any seen document, the report card explains how to start."""
        self.login()
        response = self.client.get("/corpus/")
        self.assertContains(response, 'Abrí cualquier documento una vez')
