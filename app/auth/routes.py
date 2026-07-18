# app/auth/routes.py
# -----------------------------------------------------------------------------
# Blueprint d'authentification : inscription, connexion, deconnexion.
# Expose l'objet `bp`, enregistre automatiquement par la factory sur /auth.
# -----------------------------------------------------------------------------

from urllib.parse import urlparse

from flask import (
    Blueprint, render_template, redirect, url_for, flash, request,
)
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db
from app.models import User
from app.auth.forms import LoginForm, RegistrationForm

# 1er argument = nom du blueprint -> prefixe des endpoints ("auth.login").
bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Inscription d'un nouvel utilisateur."""
    # Un utilisateur deja connecte n'a rien a faire ici.
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower().strip())
        user.set_password(form.password.data)  # hash werkzeug
        db.session.add(user)
        db.session.commit()
        flash("Compte cree avec succes. Vous pouvez vous connecter.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Connexion utilisateur."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()

        # Message volontairement generique (ne pas reveler si l'email existe).
        if user is None or not user.check_password(form.password.data):
            flash("Email ou mot de passe incorrect.", "danger")
            return redirect(url_for("auth.login"))

        login_user(user, remember=form.remember_me.data)
        flash("Connexion reussie.", "success")

        # Redirection securisee vers ?next= (protection open-redirect :
        # on refuse toute URL absolue / externe).
        next_page = request.args.get("next")
        if not next_page or urlparse(next_page).netloc != "":
            next_page = url_for("dashboard.index")
        return redirect(next_page)

    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    """Deconnexion."""
    logout_user()
    flash("Vous etes deconnecte.", "info")
    return redirect(url_for("auth.login"))
