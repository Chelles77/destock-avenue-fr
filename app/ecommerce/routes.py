from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import StockItem

bp = Blueprint('ecommerce', __name__, url_prefix='/api/ecommerce')

@bp.route('/sync-sale', methods=['POST'])
def sync_sale():
    """
    Reçoit une notification de vente depuis le site ecommerce.
    Met à jour le statut du produit en ReventePro.

    Payload attendu:
    {
        "sourceId": 1,  # ID du produit dans ReventePro
        "siteProductId": 2,  # ID du produit sur le site
        "title": "Montre",
        "price": 49.99
    }
    """
    try:
        data = request.json
        source_id = data.get('sourceId')

        if not source_id:
            return jsonify({'error': 'sourceId manquant'}), 400

        # Trouve le produit dans ReventePro
        product = StockItem.query.filter_by(id=source_id).first()

        if not product:
            return jsonify({'error': f'Produit {source_id} non trouvé'}), 404

        # Marque comme vendu
        product.status = 'sold'
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Produit {source_id} marqué comme vendu dans ReventePro',
            'product': {
                'id': product.id,
                'name': product.name,
                'status': product.status
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/products/available', methods=['GET'])
def get_available_products():
    """
    Retourne tous les produits disponibles pour publication.
    """
    try:
        products = StockItem.query.filter(
            StockItem.status.in_(['available', 'in_stock'])
        ).all()

        return jsonify([{
            'id': p.id,
            'name': p.name,
            'buyPrice': p.buy_price,
            'sellPrice': p.sell_price,
            'description': p.description,
            'condition': p.condition,
            'status': p.status
        } for p in products]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
