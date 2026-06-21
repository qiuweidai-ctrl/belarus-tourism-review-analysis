"""
Wishlist routes (presentation layer).
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from repositories import WishlistRepository, AttractionRepository

wishlist_bp = Blueprint('wishlist', __name__)

wishlist_repo = WishlistRepository()
attraction_repo = AttractionRepository()


def _serialize_wishlist_item(item):
    a = item.attraction
    return {
        'id': item.id,
        'attraction_id': a.id,
        'name': a.name,
        'location': a.location,
        'category': a.category,
        'image_url': a.image_url,
        'avg_rating': round(float(a.avg_rating or 0), 2),
        'note': item.note,
        'priority': item.priority,
        'visited': bool(item.visited),
        'created_at': item.created_at.isoformat() if item.created_at else None
    }


@wishlist_bp.route('', methods=['GET'])
@jwt_required()
def get_wishlist():
    user_id = int(get_jwt_identity())
    visited = request.args.get('visited', None, type=lambda x: x.lower() == 'true')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = wishlist_repo.get_user_wishlist(user_id, visited=visited, page=page, per_page=per_page)

    return jsonify({
        'items': [_serialize_wishlist_item(item) for item in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@wishlist_bp.route('/toggle', methods=['POST'])
@jwt_required()
def toggle_wishlist():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    attraction_id = data.get('attraction_id')
    if not attraction_id:
        return jsonify({'error': 'attraction_id is required'}), 400

    attraction = attraction_repo.get_by_id(attraction_id)
    if not attraction:
        return jsonify({'error': 'Attraction not found'}), 404

    item, is_new = wishlist_repo.toggle(
        user_id, attraction_id,
        note=data.get('note'),
        priority=data.get('priority', 3)
    )

    if is_new:
        attraction_repo.increment_wishlist_count(attraction_id, 1)
    else:
        # toggling visited - update wishlist count accordingly
        attraction_repo.increment_wishlist_count(attraction_id, 0)

    return jsonify({
        'message': 'Removed from wishlist' if not is_new else 'Added to wishlist',
        'wishlisted': is_new,
        'visited': bool(item.visited)
    }), 200


@wishlist_bp.route('/check/<int:attraction_id>', methods=['GET'])
@jwt_required()
def check_wishlist(attraction_id):
    user_id = int(get_jwt_identity())
    is_wishlisted = wishlist_repo.is_wishlisted(user_id, attraction_id)
    return jsonify({'wishlisted': is_wishlisted}), 200


@wishlist_bp.route('/<int:attraction_id>', methods=['DELETE'])
@jwt_required()
def remove_wishlist(attraction_id):
    user_id = int(get_jwt_identity())
    success = wishlist_repo.remove(user_id, attraction_id)
    if success:
        attraction_repo.increment_wishlist_count(attraction_id, -1)
    return jsonify({'message': 'Removed' if success else 'Not found'}), 200
