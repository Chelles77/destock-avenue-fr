# app/analytics/routes.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
from app.extensions import db
from app.models import Sale, StockItem, PurchaseLot

bp = Blueprint('analytics', __name__)


@bp.route('/analytics')
@login_required
def index():
    """Tableau de bord analytique avec stats et diagrammes."""

    # Stats globales
    sales = Sale.query.filter_by(user_id=current_user.id).all()
    total_sales = len(sales)
    total_revenue = sum(s.sale_price for s in sales) if sales else 0.0
    total_fees = sum(s.fees for s in sales) if sales else 0.0
    total_shipping = sum(s.shipping_cost for s in sales) if sales else 0.0
    total_costs = sum(s.stock_item.buy_price for s in sales if s.stock_item) if sales else 0.0

    total_profit = total_revenue - total_costs - total_fees - total_shipping
    avg_profit = round(total_profit / total_sales, 2) if total_sales > 0 else 0.0
    margin_percent = round((total_profit / total_revenue * 100), 1) if total_revenue > 0 else 0.0

    # Ventes par mois (derniers 12 mois)
    months_data = _get_sales_by_month(current_user.id)

    # Ventes par plateforme
    platform_data = _get_sales_by_platform(current_user.id)

    # Stocks actifs
    active_stocks = StockItem.query.filter_by(
        user_id=current_user.id, status='available'
    ).count()

    # Articles vendus
    sold_count = StockItem.query.filter_by(
        user_id=current_user.id, status='sold'
    ).count()

    return render_template('analytics/index.html',
                           total_sales=total_sales,
                           total_revenue=round(total_revenue, 2),
                           total_profit=round(total_profit, 2),
                           avg_profit=avg_profit,
                           margin_percent=margin_percent,
                           total_fees=round(total_fees, 2),
                           total_shipping=round(total_shipping, 2),
                           months_data=months_data,
                           platform_data=platform_data,
                           active_stocks=active_stocks,
                           sold_count=sold_count)


def _get_sales_by_month(user_id):
    """Ventes par mois pour les 12 derniers mois."""
    months = []
    data = []

    for i in range(11, -1, -1):
        date = datetime.now() - timedelta(days=30 * i)
        month_key = date.strftime('%Y-%m')
        months.append(date.strftime('%b %Y'))

        count = db.session.query(func.count(Sale.id)).filter(
            Sale.user_id == user_id,
            func.strftime('%Y-%m', Sale.sale_date) == month_key
        ).scalar()
        data.append(count or 0)

    return {'months': months, 'data': data}


def _get_sales_by_platform(user_id):
    """Ventes par plateforme."""
    result = db.session.query(
        Sale.platform,
        func.count(Sale.id).label('count'),
        func.sum(Sale.sale_price).label('total')
    ).filter(Sale.user_id == user_id).group_by(Sale.platform).all()

    platforms = []
    counts = []
    for platform, count, total in result:
        platforms.append(platform or 'Autre')
        counts.append(count or 0)

    return {'platforms': platforms, 'counts': counts}
