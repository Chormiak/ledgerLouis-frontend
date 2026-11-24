from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR.parent / ".env")

DEBUG = env.bool("DEBUG", default=True)
# shortcut: chave fixa só para desenvolvimento local; em produção SECRET_KEY é obrigatória.
SECRET_KEY = env("SECRET_KEY", default="dev-only-insecure-key" if DEBUG else environ.Env.NOTSET)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "ledgerlouis.market",
    "ledgerlouis.portfolio",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]
WSGI_APPLICATION = "config.wsgi.application"

# shortcut: SQLite quando DATABASE_URL não existe; use o Postgres do docker-compose no dia a dia.
DATABASES = {"default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_TZ = True
STATIC_URL = "static/"

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost:5173"])
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": None,
    # Só JSON: um formulário de outro site (sem preflight de CORS) não consegue aprovar nada em localhost.
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
}

BRAPI_TOKEN = env("BRAPI_TOKEN", default="")

# Chat do dashboard: Gemini via API do Google (chave em https://aistudio.google.com/apikey)
GEMINI_API_KEY = env("GEMINI_API_KEY", default="")
GEMINI_CHAT_MODEL = env("GEMINI_CHAT_MODEL", default="gemini-3.5-flash")
