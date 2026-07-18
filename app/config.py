# app/config.py
# -----------------------------------------------------------------------------
# Configuration de l'application. La classe Config contient les valeurs par
# defaut ; DevConfig / ProdConfig peuvent la specialiser.
#
# Les secrets se lisent via les variables d'environnement (jamais en dur).
# -----------------------------------------------------------------------------

import os

_BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    # Clef de signature des sessions/CSRF. A DEFINIR en prod via l'environnement.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me-en-prod")

    # Base SQLite par defaut dans instance/. Surchargeable via DATABASE_URL.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(_BASE_DIR, "instance", "reventepro.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload des photos produits.
    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER", os.path.join(_BASE_DIR, "instance", "uploads"),
    )
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 Mo max par fichier


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False
