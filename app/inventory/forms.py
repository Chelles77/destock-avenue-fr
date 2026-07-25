# app/inventory/forms.py
# -----------------------------------------------------------------------------
# Formulaires Flask-WTF pour la preparation des articles de stock (StockItem).
# -----------------------------------------------------------------------------

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length

# Statuts autorises (doit rester coherent avec StockItem.status).
STATUS_CHOICES = [
    ("draft", "Brouillon (preparation)"),
    ("available", "Disponible (pret a vendre)"),
    ("sold", "Vendu"),
    ("archived", "Archive"),
]

CONDITION_CHOICES = [
    ("Neuf", "Neuf"),
    ("Comme neuf", "Comme neuf"),
    ("Tres bon etat", "Tres bon etat"),
    ("Bon etat", "Bon etat"),
    ("Correct", "Correct"),
]

PACKAGING_CHOICES = [
    ("Boite d'origine scellee", "Boite d'origine scellee"),
    ("Boite d'origine ouverte", "Boite d'origine ouverte"),
    ("Boite abimee", "Boite abimee"),
    ("Sans boite", "Sans boite"),
]

PLATFORM_CHOICES = [
    ("", "-- A definir --"),
    ("Vinted", "Vinted"),
    ("Leboncoin", "Leboncoin"),
    ("eBay", "eBay"),
    ("Autre", "Autre"),
]


class StockItemForm(FlaskForm):
    """Fiche de preparation d'un article, orientee vente marketplace."""

    name = StringField("Nom interne", validators=[DataRequired(), Length(max=150)])
    condition = SelectField("Etat du produit (verifie physiquement)",
                            choices=CONDITION_CHOICES, validators=[Optional()])
    packaging_condition = SelectField("Etat de l'emballage",
                                      choices=PACKAGING_CHOICES, validators=[Optional()])
    target_platform = SelectField("Ou le vendre", choices=PLATFORM_CHOICES,
                                  validators=[Optional()])
    status = SelectField("Statut", choices=STATUS_CHOICES, default="draft",
                         validators=[DataRequired()])

    buy_price = FloatField("Prix d'achat impute (EUR)",
                           validators=[Optional(), NumberRange(min=0)])
    sell_price = FloatField("Prix de vente decide (EUR)",
                            validators=[Optional(), NumberRange(min=0)])

    description = TextAreaField("Notes internes", validators=[Optional()])

    # ---- Champs marketplace (type Amazon) ----
    marketplace_title = StringField("Titre marketplace",
                                    validators=[Optional(), Length(max=255)])
    marketplace_description = TextAreaField("Description marketplace",
                                            validators=[Optional()])

    # Photo principale (upload) ; le chemin est stocke dans main_image_path.
    main_image = FileField("Photo principale",
                           validators=[FileAllowed(["jpg", "jpeg", "png", "webp"],
                                                   "Images uniquement.")])

    submit = SubmitField("Enregistrer")
