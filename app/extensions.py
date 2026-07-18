# app/extensions.py
# -----------------------------------------------------------------------------
# Instanciation centralisee des extensions Flask.
#
# On cree ici les objets SANS les lier a une application (pas de app en argument).
# La liaison reelle se fait dans la factory create_app() via .init_app(app).
# Ce decouplage est essentiel pour :
#   - eviter les imports circulaires (models.py importe `db` d'ici, pas de app/)
#   - permettre plusieurs instances d'app (tests, prod, dev)
# -----------------------------------------------------------------------------

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# ORM : point d'entree unique vers la base de donnees.
# Tous les modeles heritent de db.Model.
db = SQLAlchemy()

# Gestionnaire de sessions utilisateur (cookies, current_user, @login_required).
login_manager = LoginManager()

# Vue vers laquelle rediriger un visiteur non authentifie.
# Format : "nom_du_blueprint.nom_de_la_fonction_vue".
login_manager.login_view = "auth.login"

# Message flash affiche lors d'une redirection pour cause d'authentification.
login_manager.login_message = "Veuillez vous connecter pour acceder a cette page."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    """
    Callback obligatoire de Flask-Login.

    Flask-Login stocke uniquement l'ID de l'utilisateur dans la session (cookie).
    A chaque requete, il appelle cette fonction pour recharger l'objet User complet.

    Note : l'import est fait a l'interieur de la fonction (import differe) pour
    eviter un import circulaire (extensions -> models -> extensions).
    """
    from app.models import User
    # SQLAlchemy 2.x : db.session.get() remplace l'ancien Query.get().
    return db.session.get(User, int(user_id))
