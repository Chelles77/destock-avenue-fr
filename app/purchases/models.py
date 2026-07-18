# app/purchases/models.py
# -----------------------------------------------------------------------------
# PurchaseLot et PurchaseTag sont definis de maniere UNIQUE dans app/models.py
# (source de verite du schema). Re-export ici pour l'import local :
#   from app.purchases.models import PurchaseLot, PurchaseTag
# Redefinir provoquerait un conflit de mapper SQLAlchemy.
# -----------------------------------------------------------------------------

from app.models import (  # noqa: F401  (re-export)
    PurchaseLot, PurchaseTag, LotInspection, RexInsight,
)

__all__ = ["PurchaseLot", "PurchaseTag", "LotInspection", "RexInsight"]
