# app/social_charges/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Sale, User

bp = Blueprint('social_charges', __name__)

# Taux par défaut pour auto-entrepreneur en achat-revente (versement libératoire)
DEFAULT_SOCIAL_RATE = 12.3


@bp.route('/')
@login_required
def index():
    """Page Charges Sociales avec brut/net."""

    # Récupérer le taux de la session ou utiliser le défaut
    social_rate = session.get(f'social_rate_{current_user.id}', DEFAULT_SOCIAL_RATE)

    # Récupérer toutes les ventes
    sales = Sale.query.filter_by(user_id=current_user.id).order_by(Sale.sale_date.desc()).all()

    # Calculer totals
    total_brut = sum(s.sale_price for s in sales) if sales else 0.0
    total_charges = round(total_brut * social_rate / 100, 2)
    total_net = round(total_brut - total_charges, 2)

    # Transactions avec calcul
    transactions = []
    for s in sales:
        brut = s.sale_price
        charges = round(brut * social_rate / 100, 2)
        net = round(brut - charges, 2)
        transactions.append({
            'date': s.sale_date,
            'platform': s.platform or 'Autre',
            'brut': brut,
            'charges': charges,
            'net': net,
            'fees': s.fees,
        })

    return render_template(
        'social_charges/index.html',
        total_brut=round(total_brut, 2),
        total_charges=total_charges,
        total_net=total_net,
        social_rate=social_rate,
        transactions=transactions,
    )


@bp.route('/update-rate', methods=['POST'])
@login_required
def update_rate():
    """Mettre à jour le taux de charges sociales."""
    new_rate = request.form.get('social_rate')
    if new_rate:
        try:
            new_rate = float(new_rate)
            if 0 <= new_rate <= 100:
                session[f'social_rate_{current_user.id}'] = new_rate
                flash(f"Taux de charges mises à jour: {new_rate}%", "success")
            else:
                flash("Le taux doit être entre 0 et 100", "danger")
        except ValueError:
            flash("Taux invalide", "danger")

    return redirect(url_for('social_charges.index'))
