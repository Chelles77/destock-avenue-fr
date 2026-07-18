# app/purchases/rex_engine.py
# -----------------------------------------------------------------------------
# Moteur REX (Retour d'EXperience) : compare la theorie (donnees d'achat) a la
# realite (tri physique) et genere des insights persistes (RexInsight).
#
# NOTE : la mise a jour de UserBrandPreference est volontairement omise tant
# qu'aucune notion de "marque" n'existe dans le schema. Les insights se basent
# sur source_country + historique des inspections de l'utilisateur.
# -----------------------------------------------------------------------------

from app.extensions import db
from app.models import PurchaseLot, LotInspection, RexInsight


def _historical_damage_avg(user_id, source_country, exclude_lot_id):
    """Taux de casse moyen historique pour une provenance donnee (%).

    Moyenne des rate_damaged des lots deja inspectes du meme utilisateur et de
    la meme provenance, en excluant le lot courant. Retourne None si aucun.
    """
    if not source_country:
        return None
    q = (
        db.session.query(LotInspection)
        .join(PurchaseLot, LotInspection.lot_id == PurchaseLot.id)
        .filter(
            PurchaseLot.user_id == user_id,
            PurchaseLot.source_country == source_country,
            LotInspection.lot_id != exclude_lot_id,
            LotInspection.qty_total_received > 0,
        )
    )
    rates = [insp.rate_damaged for insp in q.all()]
    if not rates:
        return None
    return round(sum(rates) / len(rates), 1)


def analyze_rex(lot_id):
    """Analyse un lot inspecte et (re)genere ses RexInsight. Retourne la liste."""
    lot = db.session.get(PurchaseLot, lot_id)
    if lot is None or lot.inspection is None:
        return []

    insp = lot.inspection

    # Purge des insights precedents de ce lot (idempotent en cas de re-tri).
    RexInsight.query.filter_by(lot_id=lot.id).delete()

    insights = []

    def add(message, severity="info"):
        ri = RexInsight(user_id=lot.user_id, lot_id=lot.id,
                        message=message, severity=severity)
        db.session.add(ri)
        insights.append(ri)

    country = lot.source_country or "?"

    # 1. Ecart de livraison : recu vs quantite annoncee (theorique).
    theo = lot.quantity or 0
    received = insp.qty_total_received or 0
    if theo and received != theo:
        gap = received - theo
        signe = f"+{gap}" if gap > 0 else str(gap)
        add(f"📦 Ecart de livraison : {received} recu(s) vs {theo} annonce(s) ({signe}).",
            "warning" if gap < 0 else "info")

    # 2. Taux de casse vs historique de la provenance.
    if insp.rate_damaged > 20:
        avg = _historical_damage_avg(lot.user_id, lot.source_country, lot.id)
        if avg is not None:
            comp = "superieur" if insp.rate_damaged > avg else "inferieur ou egal"
            add(f"⚠️ Taux de casse eleve ({insp.rate_damaged}%) pour {country}. "
                f"Moyenne historique {country} : {avg}% ({comp} a la moyenne).",
                "warning")
        else:
            add(f"⚠️ Taux de casse eleve ({insp.rate_damaged}%) pour {country}. "
                f"Pas encore d'historique de comparaison.", "warning")

    # 3. Faible proportion de neuf.
    if insp.rate_new < 30:
        add(f"🔴 Peu de neuf ({insp.rate_new}%). Lot plutot 'occasion' "
            f"que 'retour client'.", "warning")

    # 4. Lot sain (signal positif).
    if insp.rate_damaged < 10 and insp.rate_new >= 50:
        add(f"✅ Lot sain : {insp.rate_new}% neuf, seulement {insp.rate_damaged}% "
            f"de casse. Bonne source ({country}).", "positive")

    db.session.commit()
    return insights
