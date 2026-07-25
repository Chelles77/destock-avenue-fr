# app/purchases/forms.py
# -----------------------------------------------------------------------------
# Simulateur d'achat B-Stock : saisie des donnees brutes.
# Un lot peut etre sauvegarde en simulation (is_purchased=False) ou achete.
# Les metriques (CA reel, prix de revient, marge nette) sont calculees cote
# modele + en live cote JS.
# -----------------------------------------------------------------------------

from flask_wtf import FlaskForm
from wtforms import (
    StringField, FloatField, IntegerField, BooleanField, TextAreaField, DateField, SubmitField,
)
from wtforms.validators import DataRequired, Optional, NumberRange, Length


class LotInspectionForm(FlaskForm):
    """Checklist de tri physique au depot. Le total recu = somme des 4 quantites."""

    qty_new = IntegerField("Neuf scelle", default=0,
                           validators=[Optional(), NumberRange(min=0)])
    qty_good = IntegerField("Bon etat (fonctionnel)", default=0,
                            validators=[Optional(), NumberRange(min=0)])
    qty_damaged = IntegerField("Casse / HS", default=0,
                               validators=[Optional(), NumberRange(min=0)])
    qty_parts = IntegerField("Pieces detachees", default=0,
                             validators=[Optional(), NumberRange(min=0)])
    notes = TextAreaField("Observations", validators=[Optional()])
    submit = SubmitField("Valider le REX")


class PurchaseLotForm(FlaskForm):
    lot_number = StringField("Numero de lot", validators=[DataRequired(), Length(max=80)])

    purchase_date = DateField("Date d'achat", validators=[Optional()])
    estimated_retail_total = FloatField("Prix neuf total affiche (EUR)",
                                        validators=[DataRequired(), NumberRange(min=0)])
    quantity = IntegerField("Nombre de pieces", default=1,
                            validators=[DataRequired(), NumberRange(min=1)])
    pallet_count = IntegerField("Nombre de palettes", validators=[Optional(), NumberRange(min=0)])
    bid_price = FloatField("Prix d'enchere (EUR)",
                           validators=[DataRequired(), NumberRange(min=0)])
    auction_fee_percent = FloatField("Frais d'encheres (%)", default=5.0,
                                     validators=[Optional(), NumberRange(min=0, max=100)])
    shipping_cost = FloatField("Frais de port totaux (EUR)",
                               validators=[Optional(), NumberRange(min=0)])

    # Coche = lot reellement achete ; decoche = simple simulation.
    is_purchased = BooleanField("Lot achete", default=False)

    submit = SubmitField("Enregistrer")
