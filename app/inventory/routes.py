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
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, FloatField, IntegerField, SelectField, TextAreaField, SubmitField
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
    name = StringField("Nom du produit", validators=[DataRequired(), Length(max=150)])
    supplier = StringField("Fournisseur", validators=[Optional(), Length(max=150)])
    cost_price = FloatField("Prix / valeur neuf (EUR)",
                            validators=[Optional(), NumberRange(min=0)])
    estimated_resale_value = FloatField("Valeur estimative a la revente (EUR)",
                                        validators=[Optional(), NumberRange(min=0)])
    description = TextAreaField("Description du produit", validators=[Optional()])
    quantity = IntegerField("Quantite", default=1,
                            validators=[DataRequired(), NumberRange(min=1)])
    # coerce=int avec option 0 -> "aucun lot".
    purchase_lot_id = SelectField("Lot d'achat (d'ou vient ce produit)", coerce=int, validators=[Optional()])
    image = FileField("Photo du produit",
                      validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp"],
                                                          "Images uniquement.")])
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
    q = (request.args.get("q") or "").strip()

    # Un produit brut deja prepare (converti en StockItem) n'est plus "brut" :
    # il ne doit apparaitre que dans Stock, pas ici (evite les doublons).
    base_query = RawProduct.query.filter_by(user_id=current_user.id).filter(
        ~RawProduct.stock_items.any()
    )

    if q:
        like = f"%{q}%"
        base_query = base_query.outerjoin(PurchaseLot).filter(
            db.or_(RawProduct.name.ilike(like), PurchaseLot.lot_number.ilike(like))
        )

    pagination = base_query.order_by(
        RawProduct.date_added.asc()
    ).paginate(page=page, per_page=60, error_out=False)

    # Compteurs globaux sur TOUS les produits bruts non encore prepares.
    all_products = RawProduct.query.filter_by(user_id=current_user.id).filter(
        ~RawProduct.stock_items.any()
    ).all()
    total_pieces = sum(p.quantity for p in all_products)
    total_new_value = sum(p.cost_price * p.quantity for p in all_products)
    total_resale_value = sum(p.estimated_resale_value * p.quantity for p in all_products)
    total_real_cost = sum(p.real_unit_cost * p.quantity for p in all_products)
    total_potential_profit = total_resale_value - total_real_cost

    return render_template("inventory/raw_products.html", pagination=pagination,
                           items=pagination.items, total_pieces=total_pieces,
                           total_new_value=total_new_value, total_resale_value=total_resale_value,
                           total_real_cost=total_real_cost, total_potential_profit=total_potential_profit,
                           q=q)


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
            estimated_resale_value=form.estimated_resale_value.data or 0.0,
            description=(form.description.data or "").strip() or None,
            quantity=form.quantity.data or 1,
            purchase_lot_id=form.purchase_lot_id.data or None,  # 0 -> None
            image_path=_save_image(form.image.data),
            user_id=current_user.id,
        )
        db.session.add(raw)
        db.session.commit()
        flash("Produit brut ajoute.", "success")
        return redirect(url_for("inventory.raw_products"))

    return render_template("inventory/add_raw_product.html", form=form)


@bp.route("/raw-product/<int:raw_product_id>/edit", methods=["GET", "POST"])
@login_required
def edit_raw_product(raw_product_id):
    raw = RawProduct.query.filter_by(
        id=raw_product_id, user_id=current_user.id
    ).first_or_404()

    form = RawProductForm(obj=raw)
    form.purchase_lot_id.choices = _lot_choices()
    if request.method == "GET":
        form.purchase_lot_id.data = raw.purchase_lot_id or 0

    if form.validate_on_submit():
        raw.name = form.name.data.strip()
        raw.supplier = (form.supplier.data or "").strip() or None
        raw.cost_price = form.cost_price.data or 0.0
        raw.estimated_resale_value = form.estimated_resale_value.data or 0.0
        raw.description = (form.description.data or "").strip() or None
        raw.quantity = form.quantity.data or 1
        raw.purchase_lot_id = form.purchase_lot_id.data or None
        new_image = _save_image(form.image.data)
        if new_image:
            raw.image_path = new_image
        db.session.commit()
        flash("Produit brut modifie.", "success")
        return redirect(url_for("inventory.raw_products"))

    return render_template("inventory/add_raw_product.html", form=form, edit_mode=True, raw=raw)


@bp.route("/raw-product/<int:raw_product_id>/delete", methods=["POST"])
@login_required
def delete_raw_product(raw_product_id):
    raw = RawProduct.query.filter_by(
        id=raw_product_id, user_id=current_user.id
    ).first_or_404()

    if raw.stock_items.count() > 0:
        flash("Impossible de supprimer : des articles de stock sont deja lies a ce produit.", "danger")
        return redirect(url_for("inventory.raw_products"))

    db.session.delete(raw)
    db.session.commit()
    flash("Produit brut supprime.", "success")
    return redirect(url_for("inventory.raw_products"))


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
        # Pre-remplissage : titre = nom du produit brut, prix d'achat = cout,
        # prix vise = valeur de revente estimee saisie sur le produit brut.
        form.name.data = raw.name
        form.marketplace_title.data = raw.name
        form.buy_price.data = raw.cost_price
        form.sell_price.data = raw.estimated_resale_value
        form.status.data = "draft"

    if form.validate_on_submit():
        item = StockItem(
            name=form.name.data.strip(),
            condition=form.condition.data or None,
            packaging_condition=form.packaging_condition.data or None,
            target_platform=form.target_platform.data or None,
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
    else:
        # Par defaut : uniquement le stock actif (brouillon + disponible).
        # Les articles vendus/archives ne doivent plus encombrer cette vue
        # (ils restent consultables via l'onglet dedie, ou dans Ventes/Archives).
        query = query.filter(StockItem.status.in_(("draft", "available")))

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
