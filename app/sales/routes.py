# app/sales/routes.py
# -----------------------------------------------------------------------------
# Blueprint Sales : enregistrement des ventes d'un StockItem (relation 1-1).
# Enregistre par la factory sur /sales. Requetes isolees par user_id.
# -----------------------------------------------------------------------------

from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Sale, StockItem
from app.sales.forms import SaleForm

bp = Blueprint("sales", __name__)

PER_PAGE = 20


# ===========================================================================
# LISTE (filtres plateforme / date + pagination)
# ===========================================================================
@bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    platform = request.args.get("platform") or None
    date_str = request.args.get("date") or None

    query = Sale.query.filter_by(user_id=current_user.id)
    if platform:
        query = query.filter_by(platform=platform)
    if date_str:
        try:
            day = datetime.strptime(date_str, "%Y-%m-%d").date()
            query = query.filter(db.func.date(Sale.sale_date) == day)
        except ValueError:
            pass

    pagination = query.order_by(Sale.sale_date.desc()).paginate(
        page=page, per_page=PER_PAGE, error_out=False
    )

    all_sales = Sale.query.filter_by(user_id=current_user.id).all()
    platforms = sorted({s.platform for s in all_sales if s.platform})

    return render_template(
        "sales/sales.html",
        sales=pagination.items,
        pagination=pagination,
        platforms=platforms,
        current_platform=platform,
        current_date=date_str,
    )


# ===========================================================================
# ENREGISTREMENT D'UNE VENTE (depuis un StockItem "available")
# ===========================================================================
@bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    stock_item_id = request.args.get("stock_item_id", type=int)
    item = StockItem.query.filter_by(
        id=stock_item_id, user_id=current_user.id
    ).first_or_404()

    if item.sale is not None:
        flash("Cet article a deja une vente enregistree.", "danger")
        return redirect(url_for("inventory.stock"))

    form = SaleForm()
    if form.validate_on_submit():
        sale = Sale(
            sale_price=form.sale_price.data,
            platform=form.platform.data,
            fees=form.fees.data or 0.0,
            shipping_cost=form.shipping_cost.data or 0.0,
            buyer_info=(form.buyer_info.data or None),
            stock_item_id=item.id,
            user_id=current_user.id,
        )
        if form.sale_date.data:
            sale.sale_date = form.sale_date.data

        item.status = "sold"
        db.session.add(sale)
        db.session.commit()
        flash("Vente enregistree.", "success")
        return redirect(url_for("sales.index"))

    return render_template("sales/add_sale.html", form=form, item=item, edit_mode=False)


# ===========================================================================
# EDITION D'UNE VENTE
# ===========================================================================
@bp.route("/<int:sale_id>/edit", methods=["GET", "POST"])
@login_required
def edit(sale_id):
    sale = Sale.query.filter_by(id=sale_id, user_id=current_user.id).first_or_404()

    form = SaleForm(obj=sale)
    if form.validate_on_submit():
        form.populate_obj(sale)
        db.session.commit()
        flash("Vente modifiee.", "success")
        return redirect(url_for("sales.index"))

    return render_template(
        "sales/add_sale.html", form=form, item=sale.stock_item, edit_mode=True
    )


# ===========================================================================
# ANNULATION D'UNE VENTE (remet l'article en stock "available")
# ===========================================================================
@bp.route("/<int:sale_id>/cancel")
@login_required
def cancel(sale_id):
    sale = Sale.query.filter_by(id=sale_id, user_id=current_user.id).first_or_404()
    item = sale.stock_item

    db.session.delete(sale)
    if item is not None:
        item.status = "available"
    db.session.commit()

    flash("Vente annulee, article remis en stock.", "success")
    return redirect(url_for("sales.index"))
