import os
import re
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from repositories import AttractionRepository, UserRepository
from models import Attraction
from services.attraction_presenter import serialize_attraction
from services.catalog import catalog_errors
from services.catalog_queries import global_mean
from services.attraction_presenter import serialize_card

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


# 发布前检查来源、坐标和图片是否齐全。
def _publication_errors(attraction):
    record = {
        'name': attraction.name,
        'name_en': attraction.name_en,
        'description': attraction.description,
        'short_desc': attraction.short_desc,
        'location': attraction.location,
        'city': attraction.city,
        'region': attraction.region,
        'latitude': attraction.latitude,
        'longitude': attraction.longitude,
        'category': attraction.category,
        'image_url': attraction.image_url,
        'ticket_price': attraction.ticket_price,
        'price_source_url': attraction.price_source_url,
        'opening_hours': attraction.opening_hours,
        'opening_hours_source_url': attraction.opening_hours_source_url,
        'suitable_season': attraction.suitable_season,
        'field_sources': attraction.field_sources or {},
        'external_ratings': [{
            key: getattr(rating, key) for key in (
                'provider', 'provider_poi_id', 'score', 'scale', 'review_count',
                'source_url', 'retrieved_at', 'extractor_version',
            )
        } for rating in attraction.external_ratings],
    }
    return catalog_errors(record, require_local_image=True)


def _global_mean():
    return global_mean()


def _serialize_attraction(a, global_mean=None):
    return serialize_attraction(a, _global_mean() if global_mean is None else global_mean)


@attractions_bp.route('', methods=['GET'])
# 列表分页和前端筛选都在这里处理。
def list_attractions():
    page = request.args.get('page', 1, type=int)
    per_page = max(1, min(request.args.get('per_page', 10, type=int), 200))
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

    global_mean = _global_mean()
    return jsonify({
        'attractions': [
            serialize_card(a, global_mean) if request.args.get('view') == 'card'
            else _serialize_attraction(a, global_mean) for a in pagination.items
        ],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@attractions_bp.route('/catalog', methods=['GET'])
@attractions_bp.route('/map', methods=['GET'])
def compact_catalog():
    from sqlalchemy.orm import load_only
    columns = ('id', 'name', 'name_en', 'city', 'region', 'latitude', 'longitude',
               'category', 'image_url', 'short_desc', 'ticket_price', 'opening_hours',
               'suitable_season', 'wishlist_count', 'view_count', 'is_featured', 'is_verified',
               'avg_rating', 'total_reviews', 'sentiment_score')
    attractions = Attraction.query.options(load_only(*(
        getattr(Attraction, column) for column in columns
    ))).filter_by(catalog_status='active').order_by(Attraction.id).all()
    mean = _global_mean()
    return jsonify({'attractions': [serialize_card(a, mean, map_only=request.path.endswith('/map'))
                                    for a in attractions], 'total': len(attractions),
                    'categories': sorted({a.category for a in attractions if a.category})})


@attractions_bp.route('/<int:attraction_id>', methods=['GET'])
def get_attraction(attraction_id):
    attraction = attraction_repo.get_by_id(attraction_id)
    if not attraction or attraction.catalog_status != 'active':
        return jsonify({'error': 'Attraction not found'}), 404

    attraction_repo.increment_view_count(attraction_id)
    return jsonify(_serialize_attraction(attraction)), 200


@attractions_bp.route('', methods=['POST'])
@jwt_required()
def create_attraction():
    user_id = int(get_jwt_identity())
    user = user_repo.get_by_id(user_id)
    if not user or user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
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
        catalog_status='draft',
        field_sources=data.get('field_sources') or {},
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
        allowed.extend(['is_featured', 'is_verified', 'catalog_status', 'field_sources'])
    for key in allowed:
        if key in data:
            setattr(attraction, key, data[key])

    from app import db
    if attraction.catalog_status == 'active':
        errors = _publication_errors(attraction)
        if errors:
            db.session.rollback()
            return jsonify({
                'error': 'Attraction cannot be published until its source audit passes',
                'missing': errors,
            }), 400
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

    from services.catalog_images import local_image_metadata
    metadata = local_image_metadata(public_url)
    if not metadata:
        os.remove(absolute_path)
        return jsonify({'error': 'Image must decode correctly and be at least 160 x 120 pixels'}), 400
    attraction.image_url = public_url
    field_sources = dict(attraction.field_sources or {})
    field_sources['image_url'] = {
        'type': 'site_upload',
        'provider': 'Site upload',
        'url': public_url,
        'uploaded_by': user_id,
        'uploaded_at': datetime.utcnow().isoformat(),
        **metadata,
    }
    attraction.field_sources = field_sources
    attraction.image_source_url = public_url
    attraction.image_author = user.nickname or user.username
    attraction.image_license = None
    attraction.image_license_url = None
    attraction.images_json = [public_url]
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

    attraction = attraction_repo.get_by_id(attraction_id)
    if not attraction:
        return jsonify({'error': 'Attraction not found'}), 404
    attraction.catalog_status = 'archived'
    from app import db
    db.session.commit()
    return jsonify({'message': 'Attraction archived'}), 200


@attractions_bp.route('/categories', methods=['GET'])
def list_categories():
    cats = attraction_repo.get_categories()
    return jsonify({'categories': cats}), 200


@attractions_bp.route('/regions', methods=['GET'])
def list_regions():
    regions = attraction_repo.get_regions()
    return jsonify({'regions': regions}), 200
