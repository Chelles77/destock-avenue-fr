# app/inventory/routes.py
# -----------------------------------------------------------------------------
# Blueprint Inventory : produits bruts (RawProduct) et stock (StockItem).
# Enregistre par la factory sur /inventory. Toutes les requetes sont isolees
# par current_user.id.
# -----------------------------------------------------------------------------

import os
import uuid

from flask import (
    Blueprint, render_template, redirect, url_for, flash, request,
    current_app,
)
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import RawProduct, StockItem, PurchaseLot
from app.inventory.forms import StockItemForm

bp = Blueprint("inventory", __name__)

PER_PAGE = 20


# ---------------------------------------------------------------------------
# Formulaire d'ajout de produit brut (local a ce blueprint).
# ---------------------------------------------------------------------------
class RawProductForm(FlaskForm):
    name = StringField("Nom", validators=[DataRequired(), Length(max=150)])
    supplier = StringField("Fournisseur", validators=[Optional(), Length(max=150)])
    cost_price = FloatField("Prix coutant unitaire (EUR)",
                            validators=[Optional(), NumberRange(min=0)])
    quantity = IntegerField("Quantite", default=1,
                            validators=[DataRequired(), NumberRange(min=1)])
    # coerce=int avec option 0 -> "aucun lot".
    purchase_lot_id = SelectField("Lot d'achat", coerce=int, validators=[Optional()])
    submit = SubmitField("Enregistrer")


class EditStockForm(FlaskForm):
    marketplace_title = StringField("Titre marketplace",
                                    validators=[DataRequired(), Length(max=255)])
    sell_price = FloatField("Prix de vente (EUR)",
                            validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField("Enregistrer")


def _lot_choices():
    """Liste des lots de l'utilisateur pour le SelectField (0 = aucun)."""
    lots = PurchaseLot.query.filter_by(user_id=current_user.id).order_by(
        PurchaseLot.date.desc()
    ).all()
    return [(0, "-- Aucun lot --")] + [(l.id, l.name) for l in lots]


def _save_image(file_storage):
    """Sauvegarde une image uploadee et retourne son nom de fichier, ou None."""
    if not file_storage or not file_storage.filename:
        return None
    filename = secure_filename(file_storage.filename)
    ext = os.path.splitext(filename)[1].lower()
    unique = f"{uuid.uuid4().hex}{ext}"
    folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    file_storage.save(os.path.join(folder, unique))
    return unique  # on stocke seulement le nom de fichier


# ===========================================================================
# PRODUITS BRUTS
# ===========================================================================
@bp.route("/raw-products")
@login_required
def raw_products():
    page = request.args.get("page", 1, type=int)
    pagination = RawProduct.query.filter_by(user_id=current_user.id).order_by(
        RawProduct.date_added.desc()
    ).paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template("inventory/raw_products.html", pagination=pagination,
                           items=pagination.items)


@bp.route("/raw-product/add", methods=["GET", "POST"])
@login_required
def add_raw_product():
    form = RawProductForm()
    form.purchase_lot_id.choices = _lot_choices()

    if form.validate_on_submit():
        raw = RawProduct(
            name=form.name.data.strip(),
            supplier=(form.supplier.data or "").strip() or None,
            cost_price=form.cost_price.data or 0.0,
            quantity=form.quantity.data or 1,
            purchase_lot_id=form.purchase_lot_id.data or None,  # 0 -> None
            user_id=current_user.id,
        )
        db.session.add(raw)
        db.session.commit()
        flash("Produit brut ajoute.", "success")
        return redirect(url_for("inventory.raw_products"))

    return render_template("inventory/add_raw_product.html", form=form)


# ===========================================================================
# PREPARATION -> StockItem
# ===========================================================================
@bp.route("/prepare/<int:raw_product_id>", methods=["GET", "POST"])
@login_required
def prepare(raw_product_id):
    raw = RawProduct.query.filter_by(
        id=raw_product_id, user_id=current_user.id
    ).first_or_404()

    form = StockItemForm()

    if request.method == "GET":
        # Pre-remplissage : titre = nom du produit brut, prix d'achat = cout.
        form.name.data = raw.name
        form.marketplace_title.data = raw.name
        form.buy_price.data = raw.cost_price
        form.status.data = "draft"

    if form.validate_on_submit():
        item = StockItem(
            name=form.name.data.strip(),
            condition=form.condition.data or None,
            status="draft",  # toujours en brouillon a la creation
            buy_price=form.buy_price.data or 0.0,
            sell_price=form.sell_price.data or 0.0,
            description=form.description.data or None,
            marketplace_title=(form.marketplace_title.data or raw.name).strip(),
            marketplace_description=form.marketplace_description.data or None,
            main_image_path=_save_image(form.main_image.data),
            raw_product_id=raw.id,
            user_id=current_user.id,
        )
        db.session.add(item)
        db.session.commit()
        flash("Article cree en brouillon.", "success")
        return redirect(url_for("inventory.stock"))

    return render_template("inventory/prepare_product.html", form=form, raw=raw)


# ===========================================================================
# STOCK
# ===========================================================================
@bp.route("/stock")
@login_required
def stock():
    status = request.args.get("status")  # draft / available / sold / archived
    page = request.args.get("page", 1, type=int)

    query = StockItem.query.filter_by(user_id=current_user.id)
    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(StockItem.date_entry.desc()).paginate(
        page=page, per_page=PER_PAGE, error_out=False
    )
    return render_template("inventory/stock.html", pagination=pagination,
                           items=pagination.items, current_status=status)


@bp.route("/stock/<int:stock_item_id>/edit", methods=["GET", "POST"])
@login_required
def edit_stock(stock_item_id):
    item = StockItem.query.filter_by(
        id=stock_item_id, user_id=current_user.id
    ).first_or_404()

    form = EditStockForm(obj=item)  # pre-remplit depuis l'objet
    if form.validate_on_submit():
        item.marketplace_title = form.marketplace_title.data.strip()
        item.sell_price = form.sell_price.data or 0.0
        db.session.commit()
        flash("Article mis a jour.", "success")
        return redirect(url_for("inventory.stock", status=request.args.get("status")))

    return render_template("inventory/edit_stock.html", form=form, item=item)


@bp.route("/stock/<int:stock_item_id>/publish")
@login_required
def publish(stock_item_id):
    item = StockItem.query.filter_by(
        id=stock_item_id, user_id=current_user.id
    ).first_or_404()

    if item.status != "draft":
        flash("Seul un brouillon peut etre publie.", "warning")
    else:
        item.status = "available"
        db.session.commit()
        flash("Article publie (disponible a la vente).", "success")

    return redirect(url_for("inventory.stock", status=request.args.get("status")))
