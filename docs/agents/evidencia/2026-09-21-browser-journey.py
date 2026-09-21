"""Real Chromium acceptance of immutable Corpus PR22, synthetic loopback only.

Run with Python and playwright==1.63.0. CORPUS_BROWSER_ROOT is a scratch
directory; CORPUS_SOURCE is a clean archive of the tested commit; CORPUS_PYTHON
points to a venv with that commit's pinned application requirements installed.
No application source changes, real mail, deployment, or external credentials.
"""
import hashlib
import json
import os
import pathlib
import re
import socket
import sqlite3
import subprocess
import time
import traceback
import urllib.request
from playwright.sync_api import sync_playwright, expect

ROOT = pathlib.Path(os.environ["CORPUS_BROWSER_ROOT"])
SOURCE = pathlib.Path(os.environ["CORPUS_SOURCE"])
PYTHON = os.environ["CORPUS_PYTHON"]
SHA = "ba9646bf89fecb2a2431e9708f876dd0966afe81"
APP = SOURCE / "sistema/django_app"
DB = ROOT / "runtime.sqlite3"
ENV = dict(os.environ, CORPUS_TEST_PROFILE="synthetic", CORPUS_DB=str(DB),
           DJANGO_SETTINGS_MODULE="config.settings")
RESULT = {"commit": SHA, "checks": [], "http": [], "console": [], "pageerrors": [],
          "processes": [], "screenshots": [], "source_manifest": {},
          "settings_override": "Only EMAIL_BACKEND=filebased and EMAIL_FILE_PATH=scratch; synthetic .invalid mail, no SMTP."}
for file in sorted((SOURCE / "sistema/django_app").rglob("*")):
    if file.is_file():
        RESULT["source_manifest"][str(file.relative_to(SOURCE))] = hashlib.sha256(file.read_bytes()).hexdigest()


def persist():
    """Write observations after each checkpoint, including partial failures."""
    (ROOT / "result.json").write_text(json.dumps(RESULT, ensure_ascii=False, indent=2))


def check(name, actual, expected=True):
    """Persist an actual observation and fail when the asserted contract is broken."""
    passed = actual == expected
    RESULT["checks"].append({"name": name, "actual": actual, "expected": expected, "pass": passed})
    persist()
    assert passed, (name, actual, expected)


def command(args):
    """Run real CLI and preserve complete stdout/stderr and exit."""
    run = subprocess.run([PYTHON] + args, cwd=APP, env=ENV, capture_output=True, text=True, timeout=90)
    RESULT["processes"].append({"command": [PYTHON] + args, "exit": run.returncode,
                                "stdout": run.stdout, "stderr": run.stderr})
    persist()
    assert run.returncode == 0
    return run.stdout


def capture(page, name):
    """Save the actual rendered page and DOM, not a mocked illustration."""
    file = ROOT / (name + ".png")
    page.screenshot(path=str(file), full_page=True)
    (ROOT / (name + ".html")).write_text(page.content())
    RESULT["screenshots"].append({"file": file.name, "sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
                                   "viewport": page.viewport_size, "url": page.url})
    persist()


def attach(page):
    """Collect responses, browser console and uncaught JavaScript exceptions."""
    page.on("response", lambda response: RESULT["http"].append({
        "method": response.request.method, "url": response.url,
        "status": response.status, "resource_type": response.request.resource_type}))
    page.on("request", lambda request: RESULT.setdefault("request_origins", []).append({
        "method": request.method, "url": request.url, "origin": request.headers.get("origin"),
        "referer": request.headers.get("referer")}))
    page.on("console", lambda message: RESULT["console"].append({"type": message.type, "text": message.text}))
    page.on("pageerror", lambda error: RESULT["pageerrors"].append(str(error)))


def login(page, base, username, password="Synthetic-Corpus-Only-2026!"):
    """Enter credentials via actual browser fields and click submit."""
    page.goto(base + "/corpus/login/")
    page.locator('[name="username"]').fill(username)
    page.locator('[name="password"]').fill(password)
    page.get_by_role("button", name="Entrar", exact=True).click()
    expect(page.get_by_role("heading", name="Buscar. Leer. Verificar.")).to_be_visible()


command(["manage.py", "migrate", "--noinput"])
fixture = json.loads(command(["manage.py", "provision_fixture", "--snapshot", str(ROOT / "corpus.sqlite3")]))
with socket.socket() as sock:
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
base = f"http://127.0.0.1:{port}"
ENV["CORPUS_ORIGIN"] = base
maildir = ROOT / "mail"
maildir.mkdir()
# Real Gunicorn worker, unchanged Django application. Only test mail capture differs.
boot = ("import os; from django.conf import settings; "
        "settings.EMAIL_BACKEND='django.core.mail.backends.filebased.EmailBackend'; "
        f"settings.EMAIL_FILE_PATH={str(maildir)!r}; "
        "import django; django.setup(); import logging; "
        "logger=logging.getLogger('django.security.csrf'); logger.handlers=[logging.StreamHandler()]; logger.setLevel(logging.WARNING); "
        "from gunicorn.app.wsgiapp import run; run()")
if os.environ.get("CORPUS_DIAGNOSTIC_REFERRER") == "same-origin":
    boot = "from django.conf import settings; settings.SECURE_REFERRER_POLICY='same-origin'; " + boot
    RESULT["diagnostic_only_override"] = "SECURE_REFERRER_POLICY=same-origin; not the unchanged product configuration"
server_args = [PYTHON, "-c", boot, "config.wsgi:application", "--bind", f"127.0.0.1:{port}",
               "--workers", "1", "--timeout", "30", "--error-logfile", "-"]
server = subprocess.Popen(server_args, cwd=APP, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
try:
    for _ in range(100):
        try:
            urllib.request.urlopen(base + "/corpus/live/", timeout=1).read()
            break
        except OSError:
            time.sleep(.1)
    else:
        raise AssertionError("Server failed readiness")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        RESULT["browser"] = {"name": "Chromium", "version": browser.version,
                             "playwright": "1.63.0", "headless": True}
        desktop = browser.new_context(viewport={"width": 1440, "height": 1000})
        desktop.tracing.start(screenshots=True, snapshots=True, sources=False)
        page = desktop.new_page()
        attach(page)
        check("anonymous workspace denied", page.goto(base + "/corpus/").status, 403)
        login(page, base, "fixture-ana")
        check("Django session HttpOnly", next(c for c in desktop.cookies() if c["name"] == "sessionid")["httpOnly"])
        check("no localStorage identity", page.evaluate("Object.keys(localStorage).length"), 0)
        page.get_by_label("Buscá en tus colecciones autorizadas").fill("Artículo")
        page.get_by_role("button", name="Buscar", exact=True).click()
        result_link = page.get_by_role("link", name="Documento sintético, sin valor jurídico")
        expect(result_link).to_be_visible()
        capture(page, "desktop-search")
        result_link.click()
        expect(page.get_by_role("heading", name="Lectura verificada")).to_be_visible()
        read_url = page.url
        check("exact text visible", "Artículo 1." in page.locator("pre").inner_text())
        check("exact SHA visible", fixture["version"] in page.locator(".provenance").inner_text())
        check("secondary/legal-validity warning visible", "Vigencia jurídica no medida" in page.locator(".provenance").inner_text())
        capture(page, "desktop-read")
        page.get_by_role("button", name="Guardar referencia privada").click()
        expect(page.get_by_role("link", name="fixture-1", exact=True)).to_be_visible()
        page.get_by_role("link", name="fixture-1", exact=True).click()
        page.get_by_text("Reportar un problema en privado", exact=True).click()
        page.get_by_label("Categoría").select_option("extraction")
        marker = "Browser-only synthetic report <script>window.corpusXSS=1</script>"
        page.get_by_label("Descripción, sin datos personales").fill(marker)
        page.get_by_role("button", name="Enviar reporte privado").click()
        expect(page.locator("blockquote")).to_have_text(marker)
        check("report text escaped not executed", page.evaluate("window.corpusXSS === undefined"))
        check("report persisted owned", sqlite3.connect(DB).execute(
            "SELECT COUNT(*) FROM corpus_privatefeedback f JOIN auth_user u ON u.id=f.owner_id WHERE u.username='fixture-ana'").fetchone()[0], 1)
        capture(page, "desktop-saved-report")
        # Reload and fresh session prove server persistence, not DOM-only state.
        page.reload()
        expect(page.locator("blockquote")).to_have_text(marker)
        old_session = next(c for c in desktop.cookies() if c["name"] == "sessionid")
        page.get_by_role("button", name="Salir", exact=True).click()
        check("logout returns login form", page.locator('[name="password"]').is_visible())
        check("logout denied old deep link", page.goto(read_url).status, 403)
        replay = browser.new_context()
        replay.add_cookies([old_session])
        check("old session replay denied", replay.new_page().goto(read_url).status, 403)
        replay.close()
        login(page, base, "fixture-ben")
        check("other owner has no reference", page.get_by_role("link", name="fixture-1", exact=True).count(), 0)
        check("other owner has no report", page.locator("blockquote").count(), 0)
        check("other owner deep link denied", page.goto(read_url).status, 403)
        page.goto(base + "/corpus/?q=Art%C3%ADculo")
        check("other owner search empty", "Sin resultados autorizados" in page.locator("body").inner_text())
        capture(page, "denied-user")
        desktop.tracing.stop(path=str(ROOT / "desktop-trace.zip"))
        # Independent mobile-sized context drives the same real app.
        mobile = browser.new_context(viewport={"width": 390, "height": 844},
                                     is_mobile=True, has_touch=True, device_scale_factor=1)
        m = mobile.new_page()
        attach(m)
        login(m, base, "fixture-ana")
        check("saved reference persists across sessions", m.get_by_role("link", name="fixture-1", exact=True).count(), 1)
        m.get_by_role("link", name="fixture-1", exact=True).click()
        check("mobile read no horizontal overflow", m.evaluate(
            "document.documentElement.scrollWidth <= window.innerWidth"))
        capture(m, "mobile-read")
        m.get_by_role("link", name="Mesa de lectura", exact=True).click()
        capture(m, "mobile-workspace")
        # Browser recovery request, captured .invalid mail, reset form, prior-session invalidation.
        recovery = browser.new_context()
        r = recovery.new_page()
        attach(r)
        r.goto(base + "/corpus/login/")
        r.get_by_role("link", name="Recuperar cuenta", exact=True).click()
        r.locator('[name="email"]').fill("ana@example.invalid")
        r.get_by_role("button", name="Continuar", exact=True).click()
        expect(r.get_by_text("Si la cuenta admite recuperación", exact=False)).to_be_visible()
        files = list(maildir.glob("*"))
        check("only synthetic reset mail captured", len(files), 1)
        email = files[0].read_text()
        token_url = re.search(re.escape(base) + r"/corpus/reset/[^\s]+", email).group(0)
        r.goto(token_url)
        r.locator('[name="new_password1"]').fill("Browser-Synthetic-New-987!")
        r.locator('[name="new_password2"]').fill("Browser-Synthetic-New-987!")
        r.get_by_role("button", name="Continuar", exact=True).click()
        expect(r.locator('[name="password"]')).to_be_visible()
        check("password reset invalidates existing browser session", m.goto(read_url).status, 403)
        check("reset link cannot be reused", r.goto(token_url).status, 403)
        login(r, base, "fixture-ana", "Browser-Synthetic-New-987!")
        check("new password works with retained references", r.get_by_role("link", name="fixture-1", exact=True).count(), 1)
        # Policy revocation acts on the disposable database only, not application source.
        with sqlite3.connect(DB) as db:
            db.execute("UPDATE corpus_locator SET withdrawn_at=CURRENT_TIMESTAMP")
        check("withdrawal blocks already-seen URL", r.goto(read_url).status, 403)
        r.goto(base + "/corpus/")
        check("withdrawn reference hidden on next request", r.get_by_role("link", name="fixture-1", exact=True).count(), 0)
        check("no uncaught browser exception", RESULT["pageerrors"], [])
        check("no off-loopback application requests", [
            x["url"] for x in RESULT["http"] if not x["url"].startswith(base)], [])
        RESULT["outcome"] = "PASS"
        recovery.close()
        mobile.close()
        desktop.close()
        browser.close()
except Exception:
    RESULT["outcome"] = "FAIL"
    RESULT["exception"] = traceback.format_exc()
    # Keep the failure DOM if the browser has not yet been torn down.
    if "page" in globals():
        try:
            RESULT["failure_page_url"] = page.url
        except Exception as exc:
            RESULT["failure_capture_error"] = str(exc)
    raise
finally:
    server.terminate()
    stdout, stderr = server.communicate(timeout=20)
    RESULT["processes"].append({"command": server_args, "exit": server.returncode,
                                "stdout": stdout, "stderr": stderr})
    RESULT["server_stopped"] = server.poll() is not None
    persist()
    print(json.dumps({k: RESULT[k] for k in ("outcome", "checks", "server_stopped")}, ensure_ascii=False))
