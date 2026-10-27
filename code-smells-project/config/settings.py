import os
import secrets


def _flag(name):
    return os.environ.get(name, "0") == "1"


SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
DEBUG = _flag("FLASK_DEBUG")
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "5000"))
DB_PATH = os.environ.get("DB_PATH", "loja.db")
APP_ENV = os.environ.get("APP_ENV", "producao")
APP_VERSION = "1.0.0"

# Endpoints /admin/* ficam desabilitados salvo opt-in explícito com token.
ENABLE_ADMIN_ENDPOINTS = _flag("ENABLE_ADMIN_ENDPOINTS")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")
