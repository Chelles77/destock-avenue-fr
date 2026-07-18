# app/sales/routes.py
# -----------------------------------------------------------------------------
# Blueprint Sales : enregistrement et suivi des ventes.
# Enregistre par la factory sur /sales. Requetes isolees par current_user.id.
# -----------------------------------------------------------------------------

from datetime import datetime

from flask import (
    Blueprint, render_template, redirect, url_for, flash, request,
)
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Sale, StockItem
from app.sales.forms import SaleForm, PLATFORM_CHOICES

bp = Blueprint("sales", __name__)

PER_PAGE = 20


# ===========================================================================
# LISTE + FILTRES
# ===========================================================================
@bp.route("/")
@login_required
def index():
    platform = request.args.get("platform")
    day = request.args.get("date")  # format YYYY-MM-DD
    page = request.args.get("page", 1, type=int)

    query = Sale.query.filter_by(user_id=current_user.id)

    if platform:
        query = query.filter_by(platform=platform)

    if day:
        try:
            d = datetime.strptime(day, "%Y-%m-%d").date()
            # Filtre sur la journee (borne min incluse, max exclue).
            query = query.filter(
                Sale.sale_date >= datetime(d.year, d.month, d.day),
                Sale.sale_date < datetime(d.year, d.month, d.day, 23, 59, 59),
            )
        except ValueError:
            flash("Date invalide (attendu AAAA-MM-JJ).", "warning")

    pagination = query.order_by(Sale.sale_date.desc()).paginate(
        page=page, per_page=PER_PAGE, error_out=False
    )
    return render_template(
        "sales/sales.html",
        pagination=pagination,
        sales=pagination.items,
        platforms=[p[0] for p in PLATFORM_CHOICES],
        current_platform=platform,
        current_date=day,
    )


# ===========================================================================
# CREATION D'UNE VENTE
# ===========================================================================
@bp.route("/add/<int:stock_item_id>", methods=["GET", "POST"])
@login_required
def add(stock_item_id):
    item = StockItem.query.filter_by(
        id=stock_item_id, user_id=current_user.id
    ).first_or_404()

    # Un article deja vendu ne peut pas etre revendu (relation 1-1).
    if item.status == "sold" or item.sale is not None:
        flash("Cet article est deja vendu.", "warning")
        return redirect(url_for("inventory.stock", status="sold"))

    form = SaleForm()
    if request.method == "GET":
        # Pre-remplissage : prix de vente vise comme valeur de depart.
        form.sale_price.data = item.sell_price

    if form.validate_on_submit():
        sale = Sale(
            stock_item_id=item.id,
            sale_price=form.sale_price.data,
            platform=form.platform.data,
            fees=form.fees.data or 0.0,
            shipping_cost=form.shipping_cost.data or 0.0,
            buyer_info=form.buyer_info.data or None,
            user_id=current_user.id,
        )
        # sale_date : seulement si fournie (sinon defaut UTC du modele).
        if form.sale_date.data:
            sale.sale_date = form.sale_date.data

        item.status = "sold"  # bascule le stock en vendu
        db.session.add(sale)
        db.session.commit()
        flash("Vente enregistree.", "success")
        return redirect(url_for("sales.index"))

    return render_template("sales/add_sale.html", form=form, item=item)


# ===========================================================================
# EDITION D'UNE VENTE
# ===========================================================================
@bp.route("/<int:sale_id>/edit", methods=["GET", "POST"])
@login_required
def edit(sale_id):
    sale = Sale.query.filter_by(
        id=sale_id, user_id=current_user.id
    ).first_or_404()

    form = SaleForm(obj=sale)
    if form.validate_on_submit():
        sale.sale_price = form.sale_price.data
        sale.platform = form.platform.data
        sale.fees = form.fees.data or 0.0
        sale.shipping_cost = form.shipping_cost.data or 0.0
        sale.buyer_info = form.buyer_info.data or None
        if form.sale_date.data:
            sale.sale_date = form.sale_date.data
        db.session.commit()
        flash("Vente mise a jour.", "success")
        return redirect(url_for("sales.index"))

    return render_template("sales/add_sale.html", form=form, item=sale.stock_item,
                           edit_mode=True, sale=sale)


# ===========================================================================
# ANNULATION D'UNE VENTE
# ===========================================================================
@bp.route("/<int:sale_id>/cancel")
@login_required
def cancel(sale_id):
    sale = Sale.query.filter_by(
        id=sale_id, user_id=current_user.id
    ).first_or_404()

    item = sale.stock_item
    if item is not None:
        item.status = "available"  # remise en stock

    db.session.delete(sale)
    db.session.commit()
    flash("Vente annulee, article remis en stock.", "info")
    return redirect(url_for("sales.index"))
