"""
Tag and multi-dimensional rating routes.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Tag, AttractionTag, RatingDimension, db
from sqlalchemy import func

tags_bp = Blueprint('tags', __name__)


@tags_bp.route('', methods=['GET'])
def list_tags():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    search = request.args.get('search', '', type=str)

    query = Tag.query
    if search:
        query = query.filter(Tag.name.ilike(f'%{search}%'))

    pagination = query.order_by(Tag.use_count.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'tags': [{
            'id': t.id,
            'name': t.name,
            'slug': t.slug,
            'description': t.description,
            'color': t.color,
            'use_count': t.use_count or 0
        } for t in pagination.items],
        'total': pagination.total
    }), 200


@tags_bp.route('', methods=['POST'])
@jwt_required()
def create_tag():
    data = request.get_json()
    if not data.get('name') or not data.get('slug'):
        return jsonify({'error': 'name and slug are required'}), 400

    existing = Tag.query.filter((Tag.name == data['name']) | (Tag.slug == data['slug'])).first()
    if existing:
        return jsonify({'error': 'Tag name or slug already exists'}), 409

    tag = Tag(
        name=data['name'],
        slug=data['slug'],
        description=data.get('description'),
        color=data.get('color', '#1a5e63')
    )
    db.session.add(tag)
    db.session.commit()
    return jsonify({'message': 'Tag created', 'id': tag.id}), 201


@tags_bp.route('/attraction/<int:attraction_id>', methods=['GET'])
def get_attraction_tags(attraction_id):
    tags = db.session.query(Tag).join(AttractionTag, AttractionTag.tag_id == Tag.id).filter(
        AttractionTag.attraction_id == attraction_id
    ).all()
    return jsonify({
        'tags': [{'id': t.id, 'name': t.name, 'slug': t.slug, 'color': t.color} for t in tags]
    }), 200


@tags_bp.route('/attraction/<int:attraction_id>', methods=['POST'])
@jwt_required()
def set_attraction_tags(attraction_id):
    data = request.get_json()
    tag_ids = data.get('tag_ids', [])

    # Remove existing
    AttractionTag.query.filter_by(attraction_id=attraction_id).delete()
    db.session.flush()

    # Add new
    for tag_id in tag_ids:
        at = AttractionTag(attraction_id=attraction_id, tag_id=tag_id)
        db.session.add(at)
        Tag.query.filter_by(id=tag_id).update({'use_count': Tag.use_count + 1})

    db.session.commit()
    return jsonify({'message': 'Tags updated'}), 200


# ============================================================
# Multi-dimensional ratings
# ============================================================

@tags_bp.route('/dimensions/<int:attraction_id>', methods=['GET'])
def get_rating_dimensions(attraction_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    pagination = RatingDimension.query.filter_by(attraction_id=attraction_id).order_by(
        RatingDimension.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    # Compute averages
    dims = pagination.items
    if dims:
        avg = db.session.query(
            func.avg(RatingDimension.scenery).label('scenery'),
            func.avg(RatingDimension.service).label('service'),
            func.avg(RatingDimension.value).label('value'),
            func.avg(RatingDimension.facilities).label('facilities'),
            func.count(RatingDimension.id).label('count')
        ).filter_by(attraction_id=attraction_id).first()
        avgs = {
            'scenery': round(float(avg.scenery or 0), 2),
            'service': round(float(avg.service or 0), 2),
            'value': round(float(avg.value or 0), 2),
            'facilities': round(float(avg.facilities or 0), 2),
            'count': avg.count or 0
        }
    else:
        avgs = {'scenery': 0, 'service': 0, 'value': 0, 'facilities': 0, 'count': 0}

    return jsonify({
        'averages': avgs,
        'total': pagination.total
    }), 200


@tags_bp.route('/dimensions', methods=['POST'])
@jwt_required()
def set_rating_dimensions():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data.get('attraction_id'):
        return jsonify({'error': 'attraction_id is required'}), 400

    # Update or create
    existing = RatingDimension.query.filter_by(
        user_id=user_id, attraction_id=data['attraction_id']
    ).first()

    kwargs = {k: data.get(k) for k in ['scenery', 'service', 'value', 'facilities'] if data.get(k) is not None}

    if existing:
        for k, v in kwargs.items():
            setattr(existing, k, v)
    else:
        existing = RatingDimension(
            user_id=user_id,
            attraction_id=data['attraction_id'],
            **kwargs
        )
        db.session.add(existing)

    db.session.commit()
    return jsonify({'message': 'Rating dimensions saved'}), 200


@tags_bp.route('/dimensions/my', methods=['GET'])
@jwt_required()
def get_my_rating_dimensions():
    user_id = int(get_jwt_identity())
    attraction_id = request.args.get('attraction_id', None, type=int)

    query = RatingDimension.query.filter_by(user_id=user_id)
    if attraction_id:
        query = query.filter_by(attraction_id=attraction_id)

    dims = query.order_by(RatingDimension.created_at.desc()).limit(50).all()
    return jsonify({
        'dimensions': [{
            'attraction_id': d.attraction_id,
            'scenery': d.scenery,
            'service': d.service,
            'value': d.value,
            'facilities': d.facilities,
            'created_at': d.created_at.isoformat() if d.created_at else None
        } for d in dims]
    }), 200
