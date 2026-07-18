# app/models.py
# -----------------------------------------------------------------------------
# Schema ORM de ReventePro V4.
#
# Chaine metier :
#   PurchaseLot (lot achete) --> RawProduct (produit brut du lot)
#       --> StockItem (article prepare, mis en vente) --> Sale (vente realisee)
#
# Chaque table possede une colonne user_id : isolation stricte des donnees
# par utilisateur (multi-tenant simple). Toujours filtrer les requetes par
# current_user.id dans les routes.
# -----------------------------------------------------------------------------

from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


def _utcnow():
    """Horodatage UTC "timezone-aware".

    On evite datetime.utcnow() (deprecie et naif) au profit d'un helper
    reutilise par toutes les colonnes de dates.
    """
    return datetime.now(timezone.utc)


# Ratio de revente FIXE : on estime le CA a 30% du prix neuf affiche.
RESALE_RATIO = 0.30


# =============================================================================
# 1. UTILISATEURS
# =============================================================================
class User(UserMixin, db.Model):
    """Compte utilisateur de l'application.

    Herite de UserMixin (Flask-Login) qui fournit is_authenticated,
    is_active, is_anonymous et get_id() sans code supplementaire.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=_utcnow, nullable=False)

    # ---- Relations (backref cree l'attribut ".owner" sur chaque enfant) ----
    # lazy="dynamic" : la relation renvoie une Query, pas une liste. Ideal pour
    # de gros volumes (permet .filter(), .count(), pagination sans tout charger).
    # cascade : supprimer un User efface toutes ses donnees liees.
    raw_products = db.relationship(
        "RawProduct", backref="owner", lazy="dynamic",
        cascade="all, delete-orphan",
    )
    stock_items = db.relationship(
        "StockItem", backref="owner", lazy="dynamic",
        cascade="all, delete-orphan",
    )
    sales = db.relationship(
        "Sale", backref="owner", lazy="dynamic",
        cascade="all, delete-orphan",
    )
    purchase_lots = db.relationship(
        "PurchaseLot", backref="owner", lazy="dynamic",
        cascade="all, delete-orphan",
    )
    expenses = db.relationship(
        "Expense", backref="owner", lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # ---- Gestion du mot de passe (werkzeug.security) -----------------------
    def set_password(self, password):
        """Hache et stocke le mot de passe. Le clair n'est jamais persiste."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Compare un mot de passe en clair au hash stocke."""
        return check_password_hash(self.password_hash, password)

    # Empeche la lecture du mot de passe en clair au niveau attribut.
    @property
    def password(self):
        raise AttributeError("Le mot de passe n'est pas lisible en clair.")

    @password.setter
    def password(self, value):
        self.set_password(value)

    def __repr__(self):
        return f"<User {self.id} {self.email}>"


# =============================================================================
# 2. PRODUITS BRUTS  (matiere premiere issue d'un lot, avant preparation)
# =============================================================================
class RawProduct(db.Model):
    __tablename__ = "raw_products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    supplier = db.Column(db.String(150))
    cost_price = db.Column(db.Float, default=0.0, nullable=False)  # cout unitaire
    quantity = db.Column(db.Integer, default=1, nullable=False)
    date_added = db.Column(db.DateTime(timezone=True), default=_utcnow, nullable=False)

    # Lot d'achat d'origine (tracabilite : de quel lot vient ce produit brut).
    # Nullable : un produit peut aussi etre achete a l'unite, hors lot.
    purchase_lot_id = db.Column(db.Integer, db.ForeignKey("purchase_lots.id"), index=True)

    # Cle etrangere vers le proprietaire (isolation des donnees).
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    # Un produit brut, une fois prepare, peut donner naissance a des StockItem.
    stock_items = db.relationship(
        "StockItem", backref="raw_product", lazy="dynamic",
    )

    def __repr__(self):
        return f"<RawProduct {self.id} {self.name} x{self.quantity}>"


# =============================================================================
# 3. STOCK  (article prepare, decrit, photographie et mis en vente)
# =============================================================================
class StockItem(db.Model):
    __tablename__ = "stock_items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    buy_price = db.Column(db.Float, default=0.0, nullable=False)   # prix d'achat impute
    sell_price = db.Column(db.Float, default=0.0, nullable=False)  # prix de vente vise
    description = db.Column(db.Text)
    condition = db.Column(db.String(50))   # ex : "Neuf", "Tres bon etat", "Occasion"
    status = db.Column(db.String(30), default="draft", nullable=False, index=True)
    # status : draft (preparation) | available (pret) | sold (vendu) | archived

    # ---- Fiche marketplace (type Amazon), prete des la creation ----
    marketplace_title = db.Column(db.String(255))       # titre optimise pour la vente
    marketplace_description = db.Column(db.Text)         # description finale (HTML/texte)
    main_image_path = db.Column(db.String(255))          # chemin de la photo principale

    date_entry = db.Column(db.DateTime(timezone=True), default=_utcnow, nullable=False)

    # Origine facultative : d'ou vient cet article (produit brut source).
    raw_product_id = db.Column(db.Integer, db.ForeignKey("raw_products.id"), index=True)

    # Proprietaire.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    # Un article de stock donne lieu a une vente (uselist=False -> relation 1-1).
    sale = db.relationship(
        "Sale", backref="stock_item", uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<StockItem {self.id} {self.name} [{self.status}]>"


# =============================================================================
# 4. VENTES  (transaction realisee sur un article de stock)
# =============================================================================
class Sale(db.Model):
    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)
    sale_price = db.Column(db.Float, nullable=False)          # prix de vente encaisse
    platform = db.Column(db.String(80))                       # Vinted, Leboncoin, eBay...
    sale_date = db.Column(db.DateTime(timezone=True), default=_utcnow, nullable=False)
    fees = db.Column(db.Float, default=0.0, nullable=False)          # commissions plateforme
    shipping_cost = db.Column(db.Float, default=0.0, nullable=False)  # frais de port
    buyer_info = db.Column(db.Text)                                   # infos acheteur (pseudo, note)

    # Article vendu (unique cote StockItem : relation 1-1).
    stock_item_id = db.Column(
        db.Integer, db.ForeignKey("stock_items.id"), nullable=False, unique=True, index=True,
    )

    # Proprietaire.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    @property
    def net_profit(self):
        """Marge nette = prix vente - achat article - frais - port.

        Retourne None si l'article source n'est plus rattache.
        """
        if self.stock_item is None:
            return None
        return round(
            self.sale_price - self.stock_item.buy_price - self.fees - self.shipping_cost,
            2,
        )

    def __repr__(self):
        return f"<Sale {self.id} {self.sale_price} on {self.platform}>"


# =============================================================================
# 5. LOTS D'ACHAT  (achat groupe : palette, destockage, lot de plusieurs pieces)
# =============================================================================
class PurchaseLot(db.Model):
    __tablename__ = "purchase_lots"

    id = db.Column(db.Integer, primary_key=True)
    lot_number = db.Column(db.String(80), unique=True, nullable=False, index=True)  # ex : A2Z50763
    name = db.Column(db.String(150))  # libelle libre (compat affichage) ; defaut = lot_number

    # ---- Donnees du simulateur B-Stock ----
    estimated_retail_total = db.Column(db.Float, default=0.0, nullable=False)   # prix neuf affiche
    quantity = db.Column(db.Integer, default=1, nullable=False)                 # nb de pieces
    bid_price = db.Column(db.Float, default=0.0, nullable=False)                # prix d'enchere
    auction_fee_percent = db.Column(db.Float, default=5.0, nullable=False)      # % frais d'encheres
    shipping_cost = db.Column(db.Float, default=0.0, nullable=False)            # port total

    # Le lot est sauvegarde meme s'il n'est PAS achete (simulation comparative).
    is_purchased = db.Column(db.Boolean, default=False, nullable=False, index=True)

    date = db.Column(db.DateTime(timezone=True), default=_utcnow, nullable=False)

    # ---- Renseignes APRES reception (analyse) ----
    source_platform = db.Column(db.String(120), index=True)
    source_country = db.Column(db.String(10), index=True)  # IT | ES | DE | FR | Autre
    category = db.Column(db.String(120), index=True)
    lot_condition = db.Column(db.String(80))

    # Proprietaire.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    # Produits bruts issus de ce lot (backref ".purchase_lot" sur RawProduct).
    raw_products = db.relationship(
        "RawProduct", backref="purchase_lot", lazy="dynamic",
    )

    # Tri physique du lot (1-1 ; backref ".lot" sur LotInspection).
    inspection = db.relationship(
        "LotInspection", backref="lot", uselist=False,
        cascade="all, delete-orphan",
    )

    # Insights REX generes pour ce lot (plus recents en premier).
    rex_insights = db.relationship(
        "RexInsight", backref="lot", lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="RexInsight.date_created.desc()",
    )

    # ---- Metriques calculees (simulateur decisionnel) ----
    @property
    def real_sales_total(self):
        """CA de revente estime = 30% du prix neuf affiche (ratio fixe)."""
        return round(self.estimated_retail_total * RESALE_RATIO, 2)

    @property
    def coefficient(self):
        """Coefficient multiplicateur = CA revente estime / cout total."""
        c = self.total_cost
        return round(self.real_sales_total / c, 2) if c else 0.0

    @property
    def total_cost(self):
        """Cout total = enchere + frais d'encheres + port."""
        return round(
            (self.bid_price or 0.0)
            + (self.bid_price or 0.0) * (self.auction_fee_percent or 0.0) / 100.0
            + (self.shipping_cost or 0.0),
            2,
        )

    @property
    def unit_cost(self):
        """Prix de revient par piece."""
        return round(self.total_cost / self.quantity, 2) if self.quantity else 0.0

    @property
    def unit_real_sales(self):
        """CA de revente realiste par piece."""
        return round(self.real_sales_total / self.quantity, 2) if self.quantity else 0.0

    @property
    def net_margin_percent(self):
        """Marge nette % (base : CA de revente realiste)."""
        urs = self.unit_real_sales
        if not urs:
            return 0.0
        return round((urs - self.unit_cost) / urs * 100, 1)

    @property
    def verdict(self):
        """Verdict base sur le coefficient multiplicateur (x CA / cout)."""
        c = self.coefficient
        if c >= 3.0:
            return "OPPORTUNITE"   # x3 ou plus
        if c >= 2.0:
            return "CORRECT"       # bon lot
        return "RISQUE"            # marge insuffisante

    # ---- Suivi reel (post-vente) ----
    @property
    def total_investment(self):
        """Investissement reel engage = cout total du lot."""
        return self.total_cost

    @property
    def generated_revenue(self):
        """CA genere : somme des ventes des articles issus de ce lot."""
        total = 0.0
        for rp in self.raw_products:
            for item in rp.stock_items:
                if item.sale is not None:
                    total += item.sale.sale_price
        return round(total, 2)

    @property
    def roi_percent(self):
        """Retour sur investissement reel en %."""
        inv = self.total_investment
        if not inv:
            return 0.0
        return round((self.generated_revenue - inv) / inv * 100, 1)

    @property
    def is_profitable(self):
        """Verdict : le lot a-t-il rembourse son investissement ?"""
        return self.generated_revenue >= self.total_investment

    def __repr__(self):
        return f"<PurchaseLot {self.id} {self.lot_number}>"


# =============================================================================
# 6. CHARGES  (depenses generales : abonnements, materiel, carburant...)
# =============================================================================
class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(80), nullable=False, index=True)  # ex : "Emballage"
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime(timezone=True), default=_utcnow, nullable=False)

    # Proprietaire.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    def __repr__(self):
        return f"<Expense {self.id} {self.category} {self.amount} EUR>"


# =============================================================================
# 7. TAGS D'ACHAT  (memoire intuitive : historique des valeurs saisies)
# =============================================================================
class PurchaseTag(db.Model):
    """Valeurs uniques deja utilisees par l'utilisateur (auto-completion).

    tag_type : 'source' | 'category' | 'condition'.
    Une contrainte d'unicite evite les doublons par utilisateur/type/valeur.
    """

    __tablename__ = "purchase_tags"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(120), nullable=False)
    tag_type = db.Column(db.String(20), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    __table_args__ = (
        db.UniqueConstraint("user_id", "tag_type", "label", name="uq_tag_user_type_label"),
    )

    def __repr__(self):
        return f"<PurchaseTag {self.tag_type}:{self.label}>"


# =============================================================================
# 8. INSPECTION DE LOT  (tri physique apres reception)
# =============================================================================
class LotInspection(db.Model):
    __tablename__ = "lot_inspections"

    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey("purchase_lots.id"),
                       nullable=False, unique=True, index=True)
    inspection_date = db.Column(db.DateTime(timezone=True), default=_utcnow, nullable=False)

    qty_total_received = db.Column(db.Integer, default=0, nullable=False)
    qty_new = db.Column(db.Integer, default=0, nullable=False)      # neuf scelle
    qty_good = db.Column(db.Integer, default=0, nullable=False)     # bon etat, fonctionnel
    qty_damaged = db.Column(db.Integer, default=0, nullable=False)  # casse / HS
    qty_parts = db.Column(db.Integer, default=0, nullable=False)    # pieces detachees
    notes = db.Column(db.Text)

    @property
    def rate_new(self):
        """% de pieces neuves."""
        t = self.qty_total_received
        return round(self.qty_new / t * 100, 1) if t else 0.0

    @property
    def rate_damaged(self):
        """% de pieces cassees."""
        t = self.qty_total_received
        return round(self.qty_damaged / t * 100, 1) if t else 0.0

    @property
    def quality_score(self):
        """Score qualite /10 : neuf > bon > pieces > casse."""
        t = self.qty_total_received
        if not t:
            return 0.0
        pts = self.qty_new * 1.0 + self.qty_good * 0.7 + self.qty_parts * 0.3
        return round(max(0.0, min(pts / t * 10, 10.0)), 1)

    def __repr__(self):
        return f"<LotInspection lot={self.lot_id} recu={self.qty_total_received}>"


# =============================================================================
# 9. INSIGHT REX  (lecons apprises generees automatiquement)
# =============================================================================
class RexInsight(db.Model):
    __tablename__ = "rex_insights"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    lot_id = db.Column(db.Integer, db.ForeignKey("purchase_lots.id"), index=True)
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), default="info")  # info | warning | positive
    date_created = db.Column(db.DateTime(timezone=True), default=_utcnow, nullable=False)

    def __repr__(self):
        return f"<RexInsight {self.id} {self.severity}>"
