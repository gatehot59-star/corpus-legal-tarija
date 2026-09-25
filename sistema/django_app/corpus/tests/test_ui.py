"""UI regression tests for the corrected reading desk."""
from django.test import Client
from .test_access import FixtureBase


class UiTests(FixtureBase):
    """The redesigned pages must remain usable, readable and authorized."""

    def test_workspace_has_single_filter_panel_and_aligned_search(self):
        """Filters live in one sidebar panel; search button aligns with the query box."""
        self.login()
        response = self.client.get("/corpus/")
        self.assertContains(response, 'data-theme-toggle')
        self.assertContains(response, 'Filtros')
        self.assertContains(response, 'hero-search')
        self.assertContains(response, '<button type="submit">Buscar</button>')
        self.assertContains(response, 'Buscar. Leer. Verificar.')

    def test_search_filters_persist_and_results_show_citation_download_source(self):
        """After searching, filters stay selected and each hit shows citation, download and source."""
        self.login()
        response = self.client.get("/corpus/", {"q": "Artículo"})
        self.assertContains(response, 'value="Artículo"')
        self.assertContains(response, 'name="source"')
        self.assertContains(response, 'name="rubro"')
        self.assertContains(response, 'name="tipo"')
        self.assertContains(response, 'Cita')
        self.assertContains(response, 'Documento sintético')
        self.assertContains(response, 'Descargar texto')
        self.assertContains(response, 'resultado')

    def test_search_zero_results_replaces_previous_results(self):
        """An empty search explicitly says so and does not leave stale hits visible."""
        self.login()
        self.client.get("/corpus/", {"q": "Artículo"})
        response = self.client.get("/corpus/", {"q": "sin-resultado"})
        self.assertContains(response, 'Sin resultados para esta consulta.')
        self.assertNotContains(response, 'Documento sintético')

    def test_reader_has_citation_progress_and_download(self):
        """The reading view shows legal citation, page progress, guide and download."""
        self.login()
        response = self.client.get("/corpus/read/", self.fields)
        self.assertContains(response, 'Procedencia verificada')
        self.assertContains(response, 'Guardar referencia')
        self.assertContains(response, 'Cita interna')
        self.assertContains(response, 'Página ')
        self.assertContains(response, 'progress-shell')
        self.assertContains(response, 'reading-guide')
        self.assertContains(response, 'Documento sintético')

    def test_login_shell_exposes_theme_toggle_and_access_links(self):
        """The login page presents the product and keeps the recovery link."""
        response = Client(enforce_csrf_checks=True).get("/corpus/login/")
        self.assertContains(response, 'data-theme-toggle')
        self.assertContains(response, 'Recuperar cuenta')
        self.assertContains(response, 'La ley, lista para citar.')
        self.assertContains(response, 'Acceso por invitación')

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

    def test_download_view_returns_plain_text_with_filename(self):
        """The download endpoint serves authorized exact text as an attachment."""
        self.login()
        response = self.client.get("/corpus/download/", self.fields)
        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertIn(b"Documento", response.content)
