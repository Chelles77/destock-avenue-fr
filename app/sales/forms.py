# app/sales/forms.py
# -----------------------------------------------------------------------------
# Formulaire Flask-WTF pour l'enregistrement / edition d'une vente.
# -----------------------------------------------------------------------------

from flask_wtf import FlaskForm
from wtforms import (
    FloatField, SelectField, TextAreaField, DateTimeLocalField, SubmitField,
)
from wtforms.validators import DataRequired, Optional, NumberRange

# Plateformes proposees (valeur stockee = libelle affiche).
PLATFORM_CHOICES = [
    ("Vinted", "Vinted"),
    ("Leboncoin", "Leboncoin"),
    ("eBay", "eBay"),
    ("Autre", "Autre"),
]


class SaleForm(FlaskForm):
    sale_price = FloatField("Prix de vente final (EUR)",
                            validators=[DataRequired(), NumberRange(min=0)])
    platform = SelectField("Plateforme", choices=PLATFORM_CHOICES,
                           validators=[DataRequired()])
    fees = FloatField("Frais / commission (EUR)",
                      validators=[Optional(), NumberRange(min=0)])
    shipping_cost = FloatField("Frais de port (EUR)",
                               validators=[Optional(), NumberRange(min=0)])
    # DateTimeLocalField : input HTML5 datetime-local.
    sale_date = DateTimeLocalField("Date de vente", format="%Y-%m-%dT%H:%M",
                                   validators=[Optional()])
    buyer_info = TextAreaField("Infos acheteur", validators=[Optional()])
    submit = SubmitField("Enregistrer la vente")
