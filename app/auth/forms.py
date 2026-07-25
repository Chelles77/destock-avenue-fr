# app/auth/forms.py
# -----------------------------------------------------------------------------
# Formulaires Flask-WTF pour l'authentification.
# La protection CSRF est active automatiquement (SECRET_KEY requis dans config).
# -----------------------------------------------------------------------------

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from app.models import User


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    remember_me = BooleanField("Se souvenir de moi")
    submit = SubmitField("Se connecter")


class RegistrationForm(FlaskForm):
    username = StringField("Nom du collaborateur", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField(
        "Mot de passe",
        validators=[DataRequired(), Length(min=8, message="8 caracteres minimum.")],
    )
    confirm = PasswordField(
        "Confirmer le mot de passe",
        validators=[DataRequired(), EqualTo("password", message="Les mots de passe different.")],
    )
    submit = SubmitField("Creer le compte")

    def validate_email(self, field):
        """Validateur "inline" WTForms : verifie l'unicite de l'email en base."""
        if User.query.filter_by(email=field.data.lower().strip()).first():
            raise ValidationError("Un compte existe deja avec cet email.")
