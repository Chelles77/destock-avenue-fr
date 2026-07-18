# app/purchases/routes.py
# -----------------------------------------------------------------------------
# Blueprint Purchases : simulateur decisionnel B-Stock + historique comparatif.
# Enregistre par la factory sur /purchases. Requetes isolees par user_id.
# -----------------------------------------------------------------------------

from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, jsonify,
)
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import Optional, Length

from app.extensions import db
from app.models import PurchaseLot, PurchaseTag, LotInspection
from app.purchases.forms import PurchaseLotForm, LotInspectionForm
from app.purchases.rex_engine import analyze_rex

COUNTRY_CHOICES = [
    ("", "-- Non renseigne --"),
    ("IT", "Italie"), ("ES", "Espagne"), ("DE", "Allemagne"),
    ("FR", "France"), ("Autre", "Autre"),
]


class LotInfoForm(FlaskForm):
    """Infos post-reception (recommandees pour un REX precis)."""
    source_country = SelectField("Provenance", choices=COUNTRY_CHOICES,
                                 validators=[Optional()])
    category = StringField("Categorie", validators=[Optional(), Length(max=120)])
    source_platform = StringField("Source / Plateforme",
                                  validators=[Optional(), Length(max=120)])
    submit = SubmitField("Enregistrer")

bp = Blueprint("purchases", __name__)

PER_PAGE = 20
VALID_TAG_TYPES = ("source", "category", "condition")

# ---------------------------------------------------------------------------
# Scoreur pondere par quantite.
# NOTE : en attendant les tables UserBrandPreference / ProductScoreConfig, la
# note de base par marque est definie ici (mot-cle detecte dans le nom).
# ---------------------------------------------------------------------------
SCORE_CONFIG = {
    "dyson": 8, "apple": 9, "samsung": 7, "bosch": 7, "philips": 6,
    "rowenta": 5, "dreame": 4, "cecotec": 3,
}
DEFAULT_NOTE = 5


def _score_group(name, unit_price):
    """Note individuelle 0-10 : marque + ajustement par tranche de prix."""
    n = (name or "").lower()
    note = DEFAULT_NOTE
    for kw, base in SCORE_CONFIG.items():
        if kw in n:
            note = base
            break
    if unit_price > 500:
        note += 2
    elif unit_price > 200:
        note += 1
    elif unit_price < 30:
        note -= 1
    return max(0, min(note, 10))


def _analyze_lot(lot):
    """Note globale /20 ponderee par quantite + badges de concentration risque.

    Les groupes de produits proviennent des RawProduct du lot, regroupes par nom.
    """
    groups = {}
    for rp in lot.raw_products:
        g = groups.setdefault(rp.name, {"name": rp.name, "qty": 0,
                                        "unit_price": rp.cost_price or 0.0})
        g["qty"] += rp.quantity or 0

    total = sum(g["qty"] for g in groups.values())
    rows, weighted = [], 0.0
    heavy_qty = 0        # produits notes < 4/10
    high_ticket_qty = 0  # produits > 500 EUR (top tier)

    for g in groups.values():
        note = _score_group(g["name"], g["unit_price"])
        qty = g["qty"]
        weighted += note * qty
        if note < 4:
            heavy_qty += qty
        if g["unit_price"] > 500:
            high_ticket_qty += qty
        rows.append({
            "name": g["name"],
            "qty": qty,
            "unit_price": round(g["unit_price"], 2),
            "note": note,
            "pct": round(qty / total * 100, 1) if total else 0.0,
            "color": "green" if note >= 6 else ("red" if note < 4 else "neutral"),
        })

    # Note globale : SOMME(note * qty) / qty_totale, ramenee sur /20.
    global_score = round(weighted / total * 2, 1) if total else 0.0

    badges = []
    if total and heavy_qty / total > 0.5:
        badges.append(("LOT LOURD", "warning"))
    if total and high_ticket_qty / total > 0.3:
        badges.append(("POTENTIEL HIGH TICKET", "positive"))

    rows.sort(key=lambda r: r["qty"], reverse=True)
    return rows, global_score, badges, total


# ===========================================================================
# LISTE
# ===========================================================================
@bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    pagination = PurchaseLot.query.filter_by(user_id=current_user.id).order_by(
        PurchaseLot.date.desc()
    ).paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template("purchases/purchases.html", pagination=pagination,
                           lots=pagination.items)


# ===========================================================================
# AUTO-COMPLETION (JSON)
# ===========================================================================
@bp.route("/tags/<tag_type>")
@login_required
def tags(tag_type):
    if tag_type not in VALID_TAG_TYPES:
        return jsonify([])
    rows = PurchaseTag.query.filter_by(
        user_id=current_user.id, tag_type=tag_type
    ).order_by(PurchaseTag.label.asc()).all()
    return jsonify([t.label for t in rows])


# ===========================================================================
# SIMULATEUR / AJOUT (achete OU simule)
# ===========================================================================
@bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    form = PurchaseLotForm()
    if form.validate_on_submit():
        lot_number = form.lot_number.data.strip()

        if PurchaseLot.query.filter_by(lot_number=lot_number).first():
            flash("Ce numero de lot existe deja.", "danger")
            return render_template("purchases/add_purchase.html", form=form)

        lot = PurchaseLot(
            lot_number=lot_number,
            name=lot_number,
            estimated_retail_total=form.estimated_retail_total.data or 0.0,
            quantity=form.quantity.data or 1,
            bid_price=form.bid_price.data or 0.0,
            auction_fee_percent=(form.auction_fee_percent.data
                                 if form.auction_fee_percent.data is not None else 5.0),
            shipping_cost=form.shipping_cost.data or 0.0,
            is_purchased=bool(form.is_purchased.data),
            user_id=current_user.id,
        )
        db.session.add(lot)
        db.session.commit()
        etat = "achete" if lot.is_purchased else "simule"
        flash(f"Lot {etat} enregistre.", "success")
        return redirect(url_for("purchases.detail", lot_id=lot.id))

    return render_template("purchases/add_purchase.html", form=form)


# ===========================================================================
# DETAIL / VERDICT
# ===========================================================================
@bp.route("/<int:lot_id>/detail")
@login_required
def detail(lot_id):
    lot = PurchaseLot.query.filter_by(
        id=lot_id, user_id=current_user.id
    ).first_or_404()

    # ---- CALCUL UNIQUE (ratio fixe 30%) ----
    ca_revente = lot.real_sales_total                 # estimated_retail_total * 0.30
    total_cost = lot.total_cost
    unit_sale = lot.unit_real_sales                   # ca_revente / quantity
    gross_margin = round(ca_revente - total_cost, 2)  # marge brute
    roi = round(gross_margin / total_cost * 100, 1) if total_cost else 0.0
    coeff = lot.coefficient                           # ca_revente / total_cost
    # Part du neuf que coute le lot (pour le message decisionnel).
    cost_ratio = round(total_cost / lot.estimated_retail_total * 100, 1) if lot.estimated_retail_total else 0.0

    # Verdict lisible base sur le coefficient.
    if coeff >= 3.0:
        verdict_label = "✅ OPPORTUNITE MASSIVE (x3 ou plus)"
    elif coeff >= 2.0:
        verdict_label = "✅ BON LOT"
    else:
        verdict_label = "⚠️ MARGE INSUFFISANTE"

    message = (f"Ce lot te coute {cost_ratio}% du neuf. Tu revends a 30%. "
               f"Ton coefficient est x{coeff}.")

    return render_template(
        "purchases/lot_detail.html",
        lot=lot,
        ca_revente=ca_revente,
        unit_sale=unit_sale,
        gross_margin=gross_margin,
        roi=roi,
        coeff=coeff,
        cost_ratio=cost_ratio,
        verdict_label=verdict_label,
        message=message,
    )


# ===========================================================================
# HISTORIQUE COMPARATIF (analyse decisionnelle)
# ===========================================================================
@bp.route("/comparative")
@login_required
def comparative():
    source = request.args.get("source") or None
    category = request.args.get("category") or None
    price_min = request.args.get("price_min", type=float)
    price_max = request.args.get("price_max", type=float)

    query = PurchaseLot.query.filter_by(user_id=current_user.id)
    if source:
        query = query.filter_by(source_platform=source)
    if category:
        query = query.filter_by(category=category)
    # Tranche de prix appliquee sur le prix d'enchere (colonne).
    if price_min is not None:
        query = query.filter(PurchaseLot.bid_price >= price_min)
    if price_max is not None:
        query = query.filter(PurchaseLot.bid_price <= price_max)

    lots = query.order_by(PurchaseLot.date.desc()).all()

    # Valeurs distinctes pour les filtres (uniquement les non vides).
    all_lots = PurchaseLot.query.filter_by(user_id=current_user.id).all()
    sources = sorted({l.source_platform for l in all_lots if l.source_platform})
    categories = sorted({l.category for l in all_lots if l.category})

    return render_template(
        "purchases/comparative.html",
        lots=lots,
        sources=sources,
        categories=categories,
        current_source=source,
        current_category=category,
        price_min=price_min,
        price_max=price_max,
    )


# ===========================================================================
# INFOS POST-RECEPTION (provenance / categorie / source)
# ===========================================================================
@bp.route("/<int:lot_id>/edit-info", methods=["GET", "POST"])
@login_required
def edit_info(lot_id):
    lot = PurchaseLot.query.filter_by(
        id=lot_id, user_id=current_user.id
    ).first_or_404()

    form = LotInfoForm(obj=lot)
    if form.validate_on_submit():
        lot.source_country = form.source_country.data or None
        lot.category = (form.category.data or "").strip() or None
        lot.source_platform = (form.source_platform.data or "").strip() or None

        # Memoire intuitive : on retient categorie et source.
        _remember_tag("category", form.category.data)
        _remember_tag("source", form.source_platform.data)

        db.session.commit()
        flash("Infos du lot enregistrees.", "success")
        return redirect(url_for("purchases.detail", lot_id=lot.id))

    return render_template("purchases/edit_info.html", form=form, lot=lot)


# ===========================================================================
# TRI PHYSIQUE (inspection) + DECLENCHEMENT REX
# ===========================================================================
@bp.route("/<int:lot_id>/inspect", methods=["GET", "POST"])
@login_required
def inspect(lot_id):
    lot = PurchaseLot.query.filter_by(
        id=lot_id, user_id=current_user.id
    ).first_or_404()

    # Reutilise l'inspection existante (re-tri) ou en cree une nouvelle.
    insp = lot.inspection or LotInspection(lot_id=lot.id)
    form = LotInspectionForm(obj=insp if lot.inspection else None)

    if form.validate_on_submit():
        insp.qty_new = form.qty_new.data or 0
        insp.qty_good = form.qty_good.data or 0
        insp.qty_damaged = form.qty_damaged.data or 0
        insp.qty_parts = form.qty_parts.data or 0
        insp.notes = form.notes.data or None
        # Total recu = somme des 4 categories.
        insp.qty_total_received = (insp.qty_new + insp.qty_good
                                   + insp.qty_damaged + insp.qty_parts)

        if lot.inspection is None:
            db.session.add(insp)
        db.session.commit()

        # Declenchement de l'analyse REX (genere les RexInsight).
        analyze_rex(lot.id)
        flash("Tri enregistre, analyse REX generee.", "success")
        return redirect(url_for("purchases.detail", lot_id=lot.id))

    return render_template("purchases/inspect.html", form=form, lot=lot)


# ===========================================================================
# ANALYSE / SCOREUR PONDERE
# ===========================================================================
@bp.route("/<int:lot_id>/analyze")
@login_required
def analyze(lot_id):
    lot = PurchaseLot.query.filter_by(
        id=lot_id, user_id=current_user.id
    ).first_or_404()

    rows, global_score, badges, total = _analyze_lot(lot)
    return render_template(
        "purchases/analyze.html",
        lot=lot,
        rows=rows,
        global_score=global_score,
        badges=badges,
        total_qty=total,
    )
