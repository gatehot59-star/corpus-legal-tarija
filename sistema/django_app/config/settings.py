"""sistema/django_app/config/settings.py: fail-closed runtime settings."""
import os
import sys
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
TESTING = os.environ.get("CORPUS_TEST_PROFILE") == "synthetic"
SECRET_KEY = os.environ.get("CORPUS_SECRET_KEY", "")
if TESTING:
    SECRET_KEY = SECRET_KEY or "synthetic-only-not-a-production-secret-key"
if len(SECRET_KEY) < 40:
    raise ImproperlyConfigured("CORPUS_SECRET_KEY must contain at least 40 characters")
DEBUG = False
ALLOWED_HOSTS = os.environ.get("CORPUS_HOSTS", "localhost,127.0.0.1,testserver" if TESTING else "").split(",")
if not all(ALLOWED_HOSTS) or "*" in ALLOWED_HOSTS:
    raise ImproperlyConfigured("Explicit CORPUS_HOSTS required")
DB_PATH = os.environ.get("CORPUS_DB", "")
if not DB_PATH or not Path(DB_PATH).is_absolute():
    raise ImproperlyConfigured("Absolute CORPUS_DB required")
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": DB_PATH,
                         "OPTIONS": {"timeout": 10}}}
INSTALLED_APPS = ["django.contrib.auth", "django.contrib.contenttypes",
                  "django.contrib.sessions", "corpus"]
MIDDLEWARE = ["django.middleware.security.SecurityMiddleware",
              "django.contrib.sessions.middleware.SessionMiddleware",
              "django.middleware.common.CommonMiddleware",
              "django.middleware.csrf.CsrfViewMiddleware",
              "django.contrib.auth.middleware.AuthenticationMiddleware",
              "corpus.tracking.PilotTrackingMiddleware",
              "corpus.views.BoundaryMiddleware"]
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates",
              "APP_DIRS": True, "OPTIONS": {"context_processors": [
                  "django.template.context_processors.request",
                  "django.contrib.auth.context_processors.auth"]}}]
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
TIME_ZONE = "America/La_Paz"
LANGUAGE_CODE = "es"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = not TESTING
CSRF_COOKIE_SECURE = not TESTING
SESSION_COOKIE_AGE = 1800
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = False
SECURE_SSL_REDIRECT = not TESTING
SECURE_REDIRECT_EXEMPT = [r"^corpus/live/$"]
SECURE_PROXY_SSL_HEADER = (("HTTP_X_FORWARDED_PROTO", "https")
                           if os.environ.get("CORPUS_TRUST_PROXY") == "yes" else None)
SECURE_HSTS_SECONDS = 31536000 if not TESTING else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = False
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
DATA_UPLOAD_MAX_MEMORY_SIZE = 16384
DATA_UPLOAD_MAX_NUMBER_FIELDS = 12
FILE_UPLOAD_MAX_MEMORY_SIZE = 0
LOGIN_URL = "/corpus/login/"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
EMAIL_BACKEND = ("django.core.mail.backends.locmem.EmailBackend" if TESTING
                 else "django.core.mail.backends.dummy.EmailBackend")
# Real email remains explicitly disabled until separately configured/approved.
DEFAULT_FROM_EMAIL = "corpus@example.invalid"
PASSWORD_RESET_TIMEOUT = 900
CORPUS_ORIGIN = os.environ.get("CORPUS_ORIGIN", "http://testserver" if TESTING else "")
if not TESTING and (not CORPUS_ORIGIN.startswith("https://") or CORPUS_ORIGIN.endswith("/")):
    raise ImproperlyConfigured("Explicit HTTPS CORPUS_ORIGIN required, without trailing slash")
CSRF_TRUSTED_ORIGINS = [CORPUS_ORIGIN] if CORPUS_ORIGIN.startswith("https://") else []
_extra = [origin.strip() for origin in os.environ.get("CORPUS_EXTRA_ORIGINS", "").split(",")]
for origin in _extra:
    if not origin:
        continue
    if not origin.startswith("https://") or origin.endswith("/"):
        raise ImproperlyConfigured("CORPUS_EXTRA_ORIGINS must be HTTPS origins without trailing slash")
    if origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)
LOGGING = {"version": 1, "disable_existing_loggers": False,
           "handlers": {"discard": {"class": "logging.NullHandler"}},
           "loggers": {"django.request": {"handlers": ["discard"], "propagate": False},
                       "django.server": {"handlers": ["discard"], "propagate": False}}}
