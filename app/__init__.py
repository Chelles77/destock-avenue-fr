# app/__init__.py
# -----------------------------------------------------------------------------
# Factory pattern : create_app() construit et configure une instance Flask.
#
# Avantages : configuration injectable (dev/prod/test), pas d'objet app global,
# extensions liees a la demande via init_app().
# -----------------------------------------------------------------------------

import os
import logging

from flask import Flask

from app.config import Config
from app.extensions import db, login_manager


# Blueprints a enregistrer : (chemin du module, nom de l'attribut Blueprint, prefixe URL).
# Convention : chaque module <feature>/routes.py expose un objet nomme `bp`.
# Tant qu'un routes.py est vide, le blueprint est ignore avec un avertissement
# (l'app demarre quand meme).
_BLUEPRINTS = [
    ("app.auth.routes", "bp", "/auth"),
    ("app.dashboard.routes", "bp", "/"),
    ("app.inventory.routes", "bp", "/inventory"),
    ("app.sales.routes", "bp", "/sales"),
    ("app.purchases.routes", "bp", "/purchases"),
    ("app.finance.routes", "bp", "/finance"),
]


def create_app(config_class=Config):
    """Cree, configure et retourne l'application Flask."""
    # templates/ et static/ sont a la RACINE du projet (un niveau au-dessus
    # du package app/), pas dans app/. On pointe Flask dessus explicitement.
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder=os.path.join(project_root, "templates"),
        static_folder=os.path.join(project_root, "static"),
    )
    app.config.from_object(config_class)

    # Le dossier instance/ (base SQLite, secrets locaux) doit exister.
    os.makedirs(app.instance_path, exist_ok=True)
    # Dossier des photos produits (StockItem.image_path).
    os.makedirs(app.config.get("UPLOAD_FOLDER", os.path.join(app.instance_path, "uploads")),
                exist_ok=True)

    # ---- Liaison des extensions a cette instance ----
    db.init_app(app)
    login_manager.init_app(app)

    # ---- Enregistrement des blueprints ----
    _register_blueprints(app)

    # ---- Import des modeles + creation des tables ----
    # Import necessaire pour que SQLAlchemy connaisse les tables avant create_all().
    with app.app_context():
        from app import models  # noqa: F401  (import pour effet de bord)
        db.create_all()

    return app


def _register_blueprints(app):
    """Enregistre chaque blueprint, en ignorant proprement ceux non encore ecrits."""
    for module_path, attr_name, url_prefix in _BLUEPRINTS:
        try:
            module = __import__(module_path, fromlist=[attr_name])
            blueprint = getattr(module, attr_name)
        except (ImportError, AttributeError) as exc:
            # routes.py encore vide ou objet `bp` absent : on continue.
            app.logger.warning("Blueprint '%s' non enregistre (%s).", module_path, exc)
            continue
        app.register_blueprint(blueprint, url_prefix=url_prefix)
        app.logger.info("Blueprint '%s' enregistre sur '%s'.", module_path, url_prefix)


# Configuration minimale des logs (utile en dev).
logging.basicConfig(level=logging.INFO)
