# app/dashboard/routes.py
# -----------------------------------------------------------------------------
# Blueprint tableau de bord : statistiques de l'utilisateur connecte.
# -----------------------------------------------------------------------------

from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Sale, StockItem, PurchaseLot, RexInsight, Expense, RawProduct, LotInspection

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@login_required
def index():
    uid = current_user.id
    # Naive UTC : SQLite renvoie sale_date sans timezone, on compare donc en naive.
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)

    # Toutes les ventes de l'utilisateur (calcul des stats en Python).
    sales = Sale.query.filter_by(user_id=uid).all()

    ca_month = 0.0
    net_margin = 0.0
    ca_net = 0.0
    cout_achat_produits = 0.0
    frais_variables = 0.0
    ranking = {}  # nom article -> {count, revenue}

    for s in sales:
        buy = s.stock_item.buy_price if s.stock_item else 0.0
        name = s.stock_item.name if s.stock_item else "(article supprime)"

        # CA du mois en cours.
        if s.sale_date and s.sale_date >= month_start:
            ca_month += s.sale_price

        # Marge nette globale.
        net_margin += (s.sale_price - s.fees - s.shipping_cost - buy)

        # ---- Cartes du tableau de bord (vue d'ensemble) ----
        ca_net += s.sale_price
        cout_achat_produits += buy
        frais_variables += (s.fees or 0.0) + (s.shipping_cost or 0.0)

        # Agregation pour le top produits.
        entry = ranking.setdefault(name, {"name": name, "count": 0, "revenue": 0.0})
        entry["count"] += 1
        entry["revenue"] += s.sale_price

    # Charges fixes du mois en cours (loyer, logiciels, etc.).
    fixed_expenses_month = Expense.query.filter_by(user_id=uid, is_fixed=True).filter(
        Expense.date >= month_start
    ).all()
    charges_fixes_mois = sum(e.amount for e in fixed_expenses_month)

    marge_nette_reelle = ca_net - cout_achat_produits - frais_variables - charges_fixes_mois

    # Top 5 : tri par nombre de ventes puis CA.
    top_products = sorted(
        ranking.values(), key=lambda e: (e["count"], e["revenue"]), reverse=True
    )[:5]

    # Compteurs de stock.
    nb_available = StockItem.query.filter_by(user_id=uid, status="available").count()
    nb_sold = StockItem.query.filter_by(user_id=uid, status="sold").count()

    # ---- ANALYSE DECISIONNELLE (par lot d'achat) ----
    lots = PurchaseLot.query.filter_by(user_id=uid, is_purchased=True).all()
    by_source = {}   # source -> agregats
    by_combo = {}    # (source, category) -> agregats
    lot_performance = []  # cartes "Performance par Lot"

    for lot in lots:
        inv = lot.total_investment
        rev = lot.generated_revenue
        qty = lot.quantity or 0
        sold = 0
        for rp in lot.raw_products:
            for it in rp.stock_items:
                if it.sale is not None:
                    sold += 1

        margin_amount = round(rev - inv, 2)
        margin_pct = round(margin_amount / inv * 100, 1) if inv else 0.0
        lot_performance.append({
            "lot_number": lot.lot_number,
            "total_cost": lot.total_cost,
            "remaining_qty": max(qty - sold, 0),
            "unit_cost": lot.unit_cost,
            "margin_amount": margin_amount,
            "margin_pct": margin_pct,
        })

        src = lot.source_platform or "Non renseigne"
        cat = lot.category or "Non renseigne"

        s = by_source.setdefault(src, {"source": src, "invest": 0.0, "revenue": 0.0,
                                        "qty": 0, "sold": 0})
        s["invest"] += inv; s["revenue"] += rev; s["qty"] += qty; s["sold"] += sold

        key = (src, cat)
        c = by_combo.setdefault(key, {"source": src, "category": cat,
                                      "invest": 0.0, "revenue": 0.0})
        c["invest"] += inv; c["revenue"] += rev

    # Analyse par source : marge % + rotation (taux d'ecoulement).
    source_analysis = []
    for d in by_source.values():
        margin = ((d["revenue"] - d["invest"]) / d["invest"] * 100) if d["invest"] else 0.0
        rotation = (d["sold"] / d["qty"] * 100) if d["qty"] else 0.0
        source_analysis.append({
            "source": d["source"],
            "margin": round(margin, 1),
            "rotation": round(rotation, 1),
        })
    source_analysis.sort(key=lambda x: x["margin"], reverse=True)

    # Top combinaisons Source + Categorie (par profit absolu).
    top_combos = []
    for d in by_combo.values():
        top_combos.append({
            "source": d["source"],
            "category": d["category"],
            "profit": round(d["revenue"] - d["invest"], 2),
        })
    top_combos.sort(key=lambda x: x["profit"], reverse=True)
    top_combos = top_combos[:5]

    # ---- ANALYSE PAR PROVENANCE (REX) ----
    by_country = {}
    for lot in lots:
        pays = lot.source_country or "Non renseigne"
        d = by_country.setdefault(pays, {"pays": pays, "nb": 0,
                                         "dmg_sum": 0.0, "dmg_n": 0,
                                         "margin_sum": 0.0})
        d["nb"] += 1
        d["margin_sum"] += lot.net_margin_percent
        if lot.inspection is not None:
            d["dmg_sum"] += lot.inspection.rate_damaged
            d["dmg_n"] += 1

    provenance_analysis = []
    for d in by_country.values():
        provenance_analysis.append({
            "pays": d["pays"],
            "nb": d["nb"],
            "avg_damage": round(d["dmg_sum"] / d["dmg_n"], 1) if d["dmg_n"] else None,
            "avg_margin": round(d["margin_sum"] / d["nb"], 1) if d["nb"] else 0.0,
        })
    provenance_analysis.sort(key=lambda x: x["avg_margin"], reverse=True)

    # ---- LECONS APPRISES (insights REX recents) ----
    lessons = RexInsight.query.filter_by(user_id=uid).order_by(
        RexInsight.date_created.desc()
    ).limit(10).all()

    return render_template(
        "dashboard/index.html",
        ca_month=round(ca_month, 2),
        net_margin=round(net_margin, 2),
        ca_net=round(ca_net, 2),
        cout_achat_produits=round(cout_achat_produits, 2),
        frais_variables=round(frais_variables, 2),
        charges_fixes_mois=round(charges_fixes_mois, 2),
        marge_nette_reelle=round(marge_nette_reelle, 2),
        lot_performance=lot_performance,
        nb_available=nb_available,
        nb_sold=nb_sold,
        top_products=top_products,
        source_analysis=source_analysis,
        top_combos=top_combos,
        provenance_analysis=provenance_analysis,
        lessons=lessons,
    )


@bp.route("/reset", methods=["GET", "POST"])
@login_required
def reset():
    """Réinitialiser toutes les données de l'utilisateur."""
    if request.method == "POST":
        password = request.form.get("password")

        # Vérifier le mot de passe
        if not password or not current_user.check_password(password):
            flash("❌ Mot de passe incorrect", "danger")
            return render_template("dashboard/reset.html")

        uid = current_user.id

        # Supprimer toutes les données liées à l'utilisateur
        Sale.query.filter_by(user_id=uid).delete()
        StockItem.query.filter_by(user_id=uid).delete()
        RawProduct.query.filter_by(user_id=uid).delete()

        # Supprimer les inspections et insights des lots
        lots = PurchaseLot.query.filter_by(user_id=uid).all()
        for lot in lots:
            if lot.inspection:
                db.session.delete(lot.inspection)
            RexInsight.query.filter_by(lot_id=lot.id).delete()

        PurchaseLot.query.filter_by(user_id=uid).delete()
        Expense.query.filter_by(user_id=uid).delete()
        RexInsight.query.filter_by(user_id=uid).delete()

        db.session.commit()
        flash("✅ Toutes les données ont été réinitialisées", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("dashboard/reset.html")
