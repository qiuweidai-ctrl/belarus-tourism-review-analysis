import os
import re
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from repositories import AttractionRepository, UserRepository

attractions_bp = Blueprint('attractions', __name__)

attraction_repo = AttractionRepository()
user_repo = UserRepository()

ALLOWED_IMG_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
IMG_MAX_BYTES = 8 * 1024 * 1024
_FILENAME_SAFE_RE = re.compile(r'[^A-Za-z0-9_.-]+')


def _safe_filename(name: str) -> str:
    name = name.strip().replace(' ', '_')
    name = _FILENAME_SAFE_RE.sub('', name)
    return name[:80] or 'image'


def _can_edit_attraction(user, attraction) -> bool:
    if not user or not attraction:
        return False
    if user.role == 'admin':
        return True
    return attraction.created_by == user.id


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
        'created_by': a.created_by,
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
    data = request.get_json() or {}

    if not data.get('name') or not data.get('location'):
        return jsonify({'error': 'name and location are required'}), 400

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

    user_id = int(get_jwt_identity())
    user = user_repo.get_by_id(user_id)
    if not _can_edit_attraction(user, attraction):
        return jsonify({'error': 'Only the creator or an admin can edit this attraction'}), 403

    data = request.get_json() or {}
    allowed = [
        'name', 'name_en', 'description', 'short_desc', 'location',
        'city', 'region', 'latitude', 'longitude', 'category',
        'suitable_season', 'opening_hours', 'ticket_price',
        'image_url', 'images_json'
    ]
    if user.role == 'admin':
        allowed.extend(['is_featured', 'is_verified'])
    for key in allowed:
        if key in data:
            setattr(attraction, key, data[key])

    from app import db
    db.session.commit()
    return jsonify({'message': 'Attraction updated'}), 200


@attractions_bp.route('/<int:attraction_id>/image', methods=['POST'])
@jwt_required()
def upload_attraction_image(attraction_id):
    attraction = attraction_repo.get_by_id(attraction_id)
    if not attraction:
        return jsonify({'error': 'Attraction not found'}), 404

    user_id = int(get_jwt_identity())
    user = user_repo.get_by_id(user_id)
    if not _can_edit_attraction(user, attraction):
        return jsonify({'error': 'Only the creator or an admin can change this image'}), 403

    if 'image' not in request.files and 'file' not in request.files:
        return jsonify({'error': "No file part 'image' in request"}), 400

    f = request.files.get('image') or request.files.get('file')
    if not f or not f.filename:
        return jsonify({'error': 'No file selected'}), 400

    orig = f.filename
    ext = orig.rsplit('.', 1)[-1].lower() if '.' in orig else ''
    if ext not in ALLOWED_IMG_EXT:
        return jsonify({
            'error': f'Unsupported file type .{ext}. Allowed: {sorted(ALLOWED_IMG_EXT)}'
        }), 400

    head = f.read(12)
    f.seek(0)
    is_png  = head.startswith(b'\x89PNG\r\n\x1a\n')
    is_jpg  = head.startswith(b'\xff\xd8\xff')
    is_gif  = head.startswith(b'GIF8')
    is_webp = head[:4] == b'RIFF' and head[8:12] == b'WEBP'
    if not (is_png or is_jpg or is_gif or is_webp):
        return jsonify({'error': 'File content does not look like a valid image'}), 400

    upload_dir = os.path.join('static', 'images', 'attractions')
    os.makedirs(upload_dir, exist_ok=True)

    safe_base = _safe_filename(f'{attraction_id}_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:6]}')
    filename = f'{safe_base}.{ext}'
    absolute_path = os.path.join(upload_dir, filename)
    f.save(absolute_path)

    try:
        size = os.path.getsize(absolute_path)
        if size > IMG_MAX_BYTES:
            try: os.remove(absolute_path)
            except OSError: pass
            return jsonify({'error': f'Image too large ({size} bytes; max {IMG_MAX_BYTES})'}), 413
    except OSError:
        pass

    public_url = url_for('static', filename=f'images/attractions/{filename}', _external=False)

    if attraction.image_url and '/static/images/attractions/' in attraction.image_url:
        old_rel = attraction.image_url.split('/static/', 1)[-1]
        old_abs = os.path.join('static', old_rel.replace('/', os.sep))
        try:
            if os.path.isfile(old_abs) and old_abs != absolute_path:
                os.remove(old_abs)
        except OSError:
            pass

    attraction.image_url = public_url
    from app import db
    db.session.commit()

    return jsonify({
        'image_url': public_url,
        'attraction': _serialize_attraction(attraction)
    }), 200


@attractions_bp.route('/<int:attraction_id>', methods=['DELETE'])
@jwt_required()
def delete_attraction(attraction_id):
    user_id = int(get_jwt_identity())
    user = user_repo.get_by_id(user_id)
    if not user or user.role != 'admin':
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
