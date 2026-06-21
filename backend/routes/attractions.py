"""
Attraction routes (presentation layer).
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from repositories import AttractionRepository, UserRepository

attractions_bp = Blueprint('attractions', __name__)

attraction_repo = AttractionRepository()
user_repo = UserRepository()


def _serialize_attraction(a):
    return {
        'id': a.id,
        'name': a.name,
        'name_en': a.name_en,
        'description': a.description,
        'short_desc': a.short_desc,
        'location': a.location,
        'city': a.city,
        'region': a.region,
        'latitude': float(a.latitude) if a.latitude else None,
        'longitude': float(a.longitude) if a.longitude else None,
        'category': a.category,
        'suitable_season': a.suitable_season,
        'opening_hours': a.opening_hours,
        'ticket_price': float(a.ticket_price) if a.ticket_price else None,
        'image_url': a.image_url,
        'images': a.images_json,
        'avg_rating': round(float(a.avg_rating or 0), 2),
        'total_reviews': a.total_reviews or 0,
        'sentiment_score': round(float(a.sentiment_score or 0), 3),
        'sentiment_pos_count': a.sentiment_pos_count or 0,
        'sentiment_neg_count': a.sentiment_neg_count or 0,
        'wishlist_count': a.wishlist_count or 0,
        'view_count': a.view_count or 0,
        'is_featured': bool(a.is_featured),
        'is_verified': bool(a.is_verified),
        'created_at': a.created_at.isoformat() if a.created_at else None
    }


@attractions_bp.route('', methods=['GET'])
def list_attractions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)
    category = request.args.get('category', None, type=str)
    region = request.args.get('region', None, type=str)
    sort = request.args.get('sort', 'created_at', type=str)
    featured = request.args.get('featured', None, type=lambda x: x.lower() == 'true')

    pagination = attraction_repo.paginate(
        page=page, per_page=per_page,
        category=category, region=region,
        search=search or None, sort_by=sort,
        is_featured=featured
    )

    return jsonify({
        'attractions': [_serialize_attraction(a) for a in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@attractions_bp.route('/<int:attraction_id>', methods=['GET'])
def get_attraction(attraction_id):
    attraction = attraction_repo.get_by_id(attraction_id)
    if not attraction:
        return jsonify({'error': 'Attraction not found'}), 404

    attraction_repo.increment_view_count(attraction_id)
    return jsonify(_serialize_attraction(attraction)), 200


@attractions_bp.route('', methods=['POST'])
@jwt_required()
def create_attraction():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    attraction = attraction_repo.create(
        name=data.get('name', ''),
        name_en=data.get('name_en'),
        description=data.get('description', ''),
        short_desc=data.get('short_desc'),
        location=data.get('location', ''),
        city=data.get('city'),
        region=data.get('region'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        category=data.get('category', 'other'),
        suitable_season=data.get('suitable_season'),
        opening_hours=data.get('opening_hours'),
        ticket_price=data.get('ticket_price'),
        image_url=data.get('image_url'),
        images_json=data.get('images'),
        created_by=user_id
    )

    return jsonify({'message': 'Attraction created', 'id': attraction.id}), 201


@attractions_bp.route('/<int:attraction_id>', methods=['PUT'])
@jwt_required()
def update_attraction(attraction_id):
    attraction = attraction_repo.get_by_id(attraction_id)
    if not attraction:
        return jsonify({'error': 'Attraction not found'}), 404

    data = request.get_json()
    allowed = [
        'name', 'name_en', 'description', 'short_desc', 'location',
        'city', 'region', 'latitude', 'longitude', 'category',
        'suitable_season', 'opening_hours', 'ticket_price',
        'image_url', 'images_json', 'is_featured', 'is_verified'
    ]
    for key in allowed:
        if key in data:
            setattr(attraction, key, data[key])

    from app import db
    db.session.commit()
    return jsonify({'message': 'Attraction updated'}), 200


@attractions_bp.route('/<int:attraction_id>', methods=['DELETE'])
@jwt_required()
def delete_attraction(attraction_id):
    user_id = int(get_jwt_identity())
    user = user_repo.get_by_id(user_id)
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    success = attraction_repo.delete(attraction_id)
    if not success:
        return jsonify({'error': 'Attraction not found'}), 404
    return jsonify({'message': 'Attraction deleted'}), 200


@attractions_bp.route('/categories', methods=['GET'])
def list_categories():
    cats = attraction_repo.get_categories()
    return jsonify({'categories': cats}), 200


@attractions_bp.route('/regions', methods=['GET'])
def list_regions():
    regions = attraction_repo.get_regions()
    return jsonify({'regions': regions}), 200
