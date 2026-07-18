# app/sales/models.py
# -----------------------------------------------------------------------------
# Le modele Sale est defini de maniere UNIQUE dans app/models.py (source de
# verite du schema ORM). On le re-exporte ici pour permettre l'import local :
#   from app.sales.models import Sale
# Redefinir la classe ici provoquerait un conflit de mapper SQLAlchemy
# (table "sales" declaree deux fois).
# -----------------------------------------------------------------------------

from app.models import Sale  # noqa: F401  ( re-export)

__all__ = ["Sale"]
