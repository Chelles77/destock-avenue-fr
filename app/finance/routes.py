# app/finance/routes.py
# -----------------------------------------------------------------------------
# Blueprint Finance : charges fixes/variables (loyer, plateforme, emballage...).
# Enregistre par la factory sur /finance. Requetes isolees par user_id.
# -----------------------------------------------------------------------------

from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Expense, Sale
from app.finance.forms import ExpenseForm

bp = Blueprint("finance", __name__)


@bp.route("/")
@login_required
def index():
    # Entrées (Sales)
    sales = Sale.query.filter_by(user_id=current_user.id).all()
    total_revenue = sum(s.sale_price for s in sales) if sales else 0.0

    # Sorties (Expenses)
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(
        Expense.date.desc()
    ).all()
    total_expenses = sum(e.amount for e in expenses) if expenses else 0.0

    # Trésorerie
    treasury = total_revenue - total_expenses

    # Historique fusionné (entrées + sorties)
    transactions = []
    for s in sales:
        transactions.append({
            'date': s.sale_date,
            'type': 'ENTRÉE',
            'category': s.platform or 'Vente',
            'amount': s.sale_price,
            'description': f"Vente {s.platform}",
        })
    for e in expenses:
        transactions.append({
            'date': e.date,
            'type': 'SORTIE',
            'category': e.category,
            'amount': -e.amount,
            'description': e.description,
        })

    transactions.sort(key=lambda x: x['date'], reverse=True)

    return render_template(
        "finance/index.html",
        total_revenue=round(total_revenue, 2),
        total_expenses=round(total_expenses, 2),
        treasury=round(treasury, 2),
        transactions=transactions,
        form=ExpenseForm(),
    )


@bp.route("/add", methods=["GET", "POST"])
@login_required
def add_expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        expense = Expense(
            category=form.category.data.strip(),
            amount=form.amount.data or 0.0,
            is_fixed=bool(form.is_fixed.data),
            description=(form.description.data or "").strip() or None,
            user_id=current_user.id,
        )
        db.session.add(expense)
        db.session.commit()
        flash("Charge enregistree.", "success")
        return redirect(url_for("finance.index"))

    return render_template("finance/add_expense.html", form=form)


@bp.route("/<int:expense_id>/delete", methods=["POST"])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.filter_by(
        id=expense_id, user_id=current_user.id
    ).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    flash("Charge supprimee.", "success")
    return redirect(url_for("finance.index"))
