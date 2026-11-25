"""Konfigurasi utama NusaTani.

Seluruh nilai yang sensitif atau bergantung lingkungan dibaca dari
environment variable. File `.env` hanya dipakai untuk pengembangan lokal.
"""

import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _env_list(name, default=""):
    return [item.strip() for item in os.environ.get(name, default).split(",") if item.strip()]


def _env_bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-development-only-key-ganti-di-produksi"
)
DEBUG = _env_bool("DEBUG", True)
ALLOWED_HOSTS = _env_list("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver")
CSRF_TRUSTED_ORIGINS = _env_list("CSRF_TRUSTED_ORIGINS")

# PythonAnywhere tidak memakai SECURE_SSL_REDIRECT karena HTTPS ditangani platform,
# tetapi secret key bawaan tidak boleh sampai terpakai di alamat publik.
if (
    not DEBUG
    and any("pythonanywhere.com" in host for host in ALLOWED_HOSTS)
    and SECRET_KEY.startswith("django-insecure-")
):
    raise ImproperlyConfigured(
        "SECRET_KEY bawaan tidak boleh dipakai di produksi. Isi SECRET_KEY di file .env."
    )

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "accounts",
    "products",
    "orders",
    "quality_control",
    "deliveries",
    "assets",
    "mentorship",
    "bankku",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "accounts.context_processors.role_navigation",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600),
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "accounts.CustomUser"
AUTHENTICATION_BACKENDS = ["accounts.backends.ForgivingModelBackend"]
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:dashboard"
LOGOUT_REDIRECT_URL = "accounts:login"

LANGUAGE_CODE = "id-id"
TIME_ZONE = "Asia/Jakarta"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        # Saat DEBUG, pakai URL static apa adanya supaya perubahan CSS langsung
        # terlihat di runserver tanpa perlu collectstatic. Di produksi tetap
        # memakai nama file ber-hash + kompresi dari WhiteNoise.
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = _env_bool("SECURE_SSL_REDIRECT", not DEBUG)
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "0" if DEBUG else "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_HSTS_PRELOAD = SECURE_HSTS_SECONDS > 0
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

# Demo login - bisa dimatikan via env var untuk produksi
DEMO_LOGIN_ENABLED = _env_bool("DEMO_LOGIN_ENABLED", True)
