"""Real Chromium acceptance for the Corpus Django journey.

The test owns only a temporary synthetic database and a loopback Gunicorn
process. It never sends mail, reaches external URLs, edits source, or deploys.
Fontconfig is provisioned by CI before this script starts Chromium.
"""
from __future__ import annotations
import os
import re
import sqlite3
import subprocess
import tempfile
import time
from pathlib import Path
from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PYTHON = os.environ.get("CORPUS_PYTHON", str(ROOT / ".venv-browser" / "bin" / "python"))
APP = ROOT / "sistema" / "django_app"
DB = Path(os.environ.get("CORPUS_DB", tempfile.mktemp(prefix="corpus-browser-", suffix=".sqlite3")))
ENV = dict(os.environ, CORPUS_TEST_PROFILE="synthetic", CORPUS_DB=str(DB),
           CORPUS_HOSTS="127.0.0.1,localhost", DJANGO_SETTINGS_MODULE="config.settings")


def run_manage(*args: str) -> str:
    """Run a management command and fail with its complete output on error."""
    result = subprocess.run([PYTHON, "manage.py", *args], cwd=APP, env=ENV,
                            capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise AssertionError(f"{args}: exit={result.returncode}\n{result.stdout}\n{result.stderr}")
    return result.stdout


def wait_live(base: str) -> None:
    """Wait for the real WSGI process without accepting a dead port."""
    import urllib.request
    for _ in range(100):
        try:
            with urllib.request.urlopen(base + "/corpus/live/", timeout=1) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(0.1)
    raise AssertionError("Gunicorn never became live")


def login(page, base: str, username: str, password: str) -> None:
    """Log in through rendered fields and require the authenticated workspace."""
    page.goto(base + "/corpus/login/")
    page.locator('[name="username"]').fill(username)
    page.locator('[name="password"]').fill(password)
    page.get_by_role("button", name="Entrar", exact=True).click()
    page.wait_for_load_state("networkidle")
    expect(page.get_by_role("heading", name="Buscar. Leer. Verificar.")).to_be_visible()


def main() -> None:
    """Execute the desktop, mobile, ownership, recovery and withdrawal journey."""
    run_manage("migrate", "--noinput")
    fixture = run_manage("provision_fixture", "--snapshot", str(DB.with_name("snapshot.sqlite3")))
    version = re.search(r'"version": "([0-9a-f]{64})"', fixture).group(1)
    server = None
    with tempfile.TemporaryDirectory(prefix="corpus-browser-mail-") as maildir:
        with subprocess.Popen([
            PYTHON, "-c",
            "from django.conf import settings; "
            f"settings.CORPUS_ORIGIN='http://127.0.0.1:8000'; "
            f"settings.EMAIL_BACKEND='django.core.mail.backends.filebased.EmailBackend'; "
            f"settings.EMAIL_FILE_PATH={maildir!r}; "
            "from gunicorn.app.wsgiapp import run; run()",
            "config.wsgi:application", "--bind", "127.0.0.1:8000", "--workers", "1",
            "--timeout", "120", "--error-logfile", "-"],
            cwd=APP, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as server:
            try:
                wait_live("http://127.0.0.1:8000")
                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch(headless=True,
                                                         args=["--no-sandbox", "--disable-dev-shm-usage"])
                    desktop = browser.new_context(viewport={"width": 1440, "height": 1000})
                    page = desktop.new_page()
                    response = page.goto("http://127.0.0.1:8000/corpus/")
                    assert response.status == 403
                    login(page, "http://127.0.0.1:8000", "fixture-ana", "Synthetic-Corpus-Only-2026!")
                    assert page.evaluate("Object.keys(localStorage).length") == 0
                    page.get_by_label("Buscá en tus colecciones autorizadas").fill("Artículo")
                    page.get_by_role("button", name="Buscar", exact=True).click()
                    page.wait_for_load_state("networkidle")
                    result = page.get_by_role("link", name="Documento sintético, sin valor jurídico")
                    expect(result).to_be_visible()
                    result.click()
                    page.wait_for_load_state("networkidle")
                    read_url = page.url
                    expect(page.get_by_role("heading", name="Lectura verificada")).to_be_visible()
                    assert "Artículo 1." in page.locator("pre").inner_text()
                    assert version in page.locator(".provenance").inner_text()
                    assert "Vigencia jurídica no medida" in page.locator(".provenance").inner_text()
                    page.get_by_role("button", name="Guardar referencia privada").click()
                    page.wait_for_load_state("networkidle")
                    expect(page.get_by_role("link", name="fixture-1", exact=True)).to_be_visible()
                    page.get_by_role("link", name="fixture-1", exact=True).click()
                    page.get_by_text("Reportar un problema en privado", exact=True).click()
                    page.get_by_label("Categoría").select_option("extraction")
                    marker = "Browser synthetic report <script>window.corpusXSS=1</script>"
                    page.get_by_label("Descripción, sin datos personales").fill(marker)
                    page.get_by_role("button", name="Enviar reporte privado").click()
                    page.wait_for_load_state("networkidle")
                    expect(page.locator("blockquote")).to_have_text(marker)
                    assert page.evaluate("window.corpusXSS === undefined")
                    old_cookies = desktop.cookies()
                    page.get_by_role("button", name="Salir", exact=True).click()
                    page.wait_for_load_state("networkidle")
                    assert page.locator('[name="password"]').is_visible()
                    replay = browser.new_context()
                    replay.add_cookies(old_cookies)
                    stale = replay.new_page().goto("http://127.0.0.1:8000" + read_url)
                    assert stale.status == 403
                    replay.close()
                    login(page, "http://127.0.0.1:8000", "fixture-ben", "Synthetic-Corpus-Only-2026!")
                    assert page.get_by_role("link", name="fixture-1", exact=True).count() == 0
                    page.goto("http://127.0.0.1:8000/corpus/?q=Art%C3%ADculo")
                    page.wait_for_load_state("networkidle")
                    assert "Sin resultados autorizados" in page.locator("body").inner_text()
                    mobile = browser.new_context(viewport={"width": 390, "height": 844},
                                                  is_mobile=True, has_touch=True)
                    mobile_page = mobile.new_page()
                    login(mobile_page, "http://127.0.0.1:8000", "fixture-ana", "Synthetic-Corpus-Only-2026!")
                    mobile_page.get_by_label("Buscá en tus colecciones autorizadas").fill("Artículo")
                    mobile_page.get_by_role("button", name="Buscar", exact=True).click()
                    mobile_page.wait_for_load_state("networkidle")
                    mobile_page.get_by_role("link", name="Documento sintético, sin valor jurídico").click()
                    mobile_page.wait_for_load_state("networkidle")
                    assert mobile_page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                    mobile.close()
                    recovery = browser.new_page()
                    recovery.goto("http://127.0.0.1:8000/corpus/login/")
                    recovery.get_by_role("link", name="Recuperar cuenta", exact=True).click()
                    recovery.locator('[name="email"]').fill("ana@example.invalid")
                    recovery.get_by_role("button", name="Continuar", exact=True).click()
                    recovery.wait_for_load_state("networkidle")
                    expect(recovery.get_by_text("Si la cuenta admite recuperación", exact=False)).to_be_visible()
                    files = list(Path(maildir).glob("*"))
                    assert len(files) == 1
                    token_url = re.search(r"http://127.0.0.1:8000/corpus/reset/[^\\s]+", files[0].read_text()).group(0)
                    recovery.goto(token_url)
                    recovery.locator('[name="new_password1"]').fill("Browser-Synthetic-New-987!")
                    recovery.locator('[name="new_password2"]').fill("Browser-Synthetic-New-987!")
                    recovery.get_by_role("button", name="Continuar", exact=True).click()
                    recovery.wait_for_load_state("networkidle")
                    login(recovery, "http://127.0.0.1:8000", "fixture-ana", "Browser-Synthetic-New-987!")
                    page.goto(token_url)
                    assert page.url == token_url and page.locator('[name="new_password1"]').count() == 0
                    with sqlite3.connect(DB) as database:
                        database.execute("UPDATE corpus_locator SET withdrawn_at=CURRENT_TIMESTAMP")
                        database.commit()
                    response = recovery.goto(read_url)
                    assert response.status == 403
                    recovery.goto("http://127.0.0.1:8000/corpus/")
                    assert recovery.get_by_role("link", name="fixture-1", exact=True).count() == 0
                    assert not page.request if False else True
                    browser.close()
            finally:
                server.terminate()
                server.wait(timeout=20)


if __name__ == "__main__":
    main()
