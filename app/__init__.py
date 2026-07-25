# app/__init__.py
import os
import logging
from flask import Flask, redirect, url_for, send_from_directory
from flask_cors import CORS
from app.extensions import db, login_manager, migrate
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(config_class)

    # Dossier uploads
    os.makedirs(app.config.get("UPLOAD_FOLDER",
              os.path.join(app.instance_path, "uploads")), exist_ok=True)

    # CORS pour permettre aux requêtes cross-origin (ecommerce site)
    CORS(app, resources={r"/uploads/*": {"origins": "*"}})

    # Extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Les modeles doivent etre importes pour qu'Alembic les detecte (autogenerate).
    with app.app_context():
        from app import models  # noqa: F401

    # Blueprints
    _register_blueprints(app)

    @app.route("/")
    def root():
        return redirect(url_for("dashboard.index"))

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    return app

def _register_blueprints(app):
    """Enregistrement sécurisé avec détection de doublons."""
    _BLUEPRINTS = [
        ("app.auth.routes", "bp", "/auth"),
        ("app.dashboard.routes", "bp", "/dashboard"),
        ("app.inventory.routes", "bp", "/inventory"),
        ("app.purchases.routes", "bp", "/purchases"),  # ⚠️ UNIQUEMENT ICI
        ("app.sales.routes", "bp", "/sales"),
        ("app.finance.routes", "bp", "/finance"),
        ("app.analytics.routes", "bp", "/analytics"),
        ("app.social_charges.routes", "bp", "/charges"),
        ("app.ecommerce.routes", "bp", ""),
    ]

    for module_path, attr_name, url_prefix in _BLUEPRINTS:
        try:
            module = __import__(module_path, fromlist=[attr_name])
            blueprint = getattr(module, attr_name)
            
            # Vérification anti-doublon critique
            if blueprint.name in app.blueprints:
                app.logger.warning(f"Blueprint '{blueprint.name}' déjà enregistré, ignoré.")
                continue
                
            app.register_blueprint(blueprint, url_prefix=url_prefix)
            app.logger.info(f"✅ Blueprint '{module_path}' enregistré sur '{url_prefix}'.")
            
        except (ImportError, AttributeError) as exc:
            app.logger.warning(f"️ Blueprint '{module_path}' ignoré ({exc}).")
            continue

logging.basicConfig(level=logging.INFO)