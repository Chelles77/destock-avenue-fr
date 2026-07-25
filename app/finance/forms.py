# app/finance/forms.py
# -----------------------------------------------------------------------------
# Formulaire Flask-WTF pour les charges (fixes ou variables).
# -----------------------------------------------------------------------------

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length


class ExpenseForm(FlaskForm):
    category = StringField("Categorie", validators=[DataRequired(), Length(max=80)])
    amount = FloatField("Montant (EUR)", validators=[DataRequired(), NumberRange(min=0)])
    is_fixed = BooleanField("Charge fixe (mensuelle, ex: loyer, logiciel)", default=False)
    description = TextAreaField("Note", validators=[Optional()])
    submit = SubmitField("Enregistrer")
