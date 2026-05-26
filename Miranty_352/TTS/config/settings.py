import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-in-production")

DEBUG = os.environ.get("DEBUG", "True").lower() in ("1", "true", "yes")

# Hôtes locaux + sous-domaines Render (.onrender.com = wildcard Django)
_DEFAULT_ALLOWED_HOSTS = ("127.0.0.1", "localhost", "tts-mg.onrender.com")
_env_hosts = [
    h.strip()
    for h in os.environ.get("ALLOWED_HOSTS", "").split(",")
    if h.strip()
]
ALLOWED_HOSTS = list(dict.fromkeys((*_DEFAULT_ALLOWED_HOSTS, *_env_hosts)))

# Render expose RENDER_EXTERNAL_URL=https://votre-app.onrender.com
_csrf_origins = [
    o.strip()
    for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if o.strip()
]
_render_url = os.environ.get("RENDER_EXTERNAL_URL", "").strip().rstrip("/")
if _render_url and _render_url not in _csrf_origins:
    _csrf_origins.append(_render_url)
CSRF_TRUSTED_ORIGINS = _csrf_origins

# HTTPS derrière le proxy Render
if os.environ.get("RENDER") or _render_url:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "tts.apps.TtsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "tts.context_processors.vox_synth",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Indian/Antananarivo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MODEL_ID = "Nelchael/tts-malagasy"
DEFAULT_SEED = 555
DEFAULT_RITMA = 0.75
DEFAULT_FIOVAN_RITMA = 0.40
DEFAULT_ANGOLO = 0.40
