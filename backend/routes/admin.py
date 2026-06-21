"""
Admin management routes.
All endpoints require admin role.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Review, Attraction, db
from repositories import UserRepository, ReviewRepository, AttractionRepository
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

user_repo = UserRepository()
review_repo = ReviewRepository()
attraction_repo = AttractionRepository()


def require_admin(f):
    from functools import wraps
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user = user_repo.get_by_id(user_id)
        if not user or user.role not in ('admin', 'moderator'):
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated


def serialize_user(u):
    return {
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'role': u.role,
        'status': u.status,
        'nickname': u.nickname,
        'avatar_url': u.avatar_url,
        'created_at': u.created_at.isoformat() if u.created_at else None,
        'last_login_at': u.last_login_at.isoformat() if u.last_login_at else None
    }


@admin_bp.route('/stats', methods=['GET'])
@require_admin
def dashboard_stats():
    user_count = User.query.count()
    attraction_count = Attraction.query.count()
    review_count = Review.query.filter_by(status='published').count()
    pending_reviews = Review.query.filter_by(status='pending').count()
    banned_users = User.query.filter_by(status='banned').count()

    # Monthly registration trend (last 6 months)
    from datetime import datetime, timedelta
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    monthly_users = db.session.query(
        func.date_format(User.created_at, '%Y-%m').label('month'),
        func.count(User.id).label('count')
    ).filter(User.created_at >= six_months_ago).group_by('month').order_by('month').all()

    return jsonify({
        'user_count': user_count,
        'attraction_count': attraction_count,
        'review_count': review_count,
        'pending_reviews': pending_reviews,
        'banned_users': banned_users,
        'monthly_registrations': [{'month': m, 'count': c} for m, c in monthly_users]
    }), 200


@admin_bp.route('/users', methods=['GET'])
@require_admin
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role = request.args.get('role', None, type=str)
    status = request.args.get('status', None, type=str)

    pagination = user_repo.paginate(page=page, per_page=per_page, role=role, status=status)
    return jsonify({
        'users': [serialize_user(u) for u in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@require_admin
def update_user(user_id):
    user = user_repo.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    for field in ['role', 'status', 'nickname', 'avatar_url', 'bio']:
        if field in data:
            setattr(user, field, data[field])
    db.session.commit()
    return jsonify({'message': 'User updated', 'user': serialize_user(user)}), 200


@admin_bp.route('/users/<int:user_id>/ban', methods=['POST'])
@require_admin
def ban_user(user_id):
    user = user_repo.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    user.status = 'banned'
    db.session.commit()
    return jsonify({'message': 'User banned'}), 200


@admin_bp.route('/users/<int:user_id>/unban', methods=['POST'])
@require_admin
def unban_user(user_id):
    user = user_repo.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    user.status = 'active'
    db.session.commit()
    return jsonify({'message': 'User unbanned'}), 200


@admin_bp.route('/reviews', methods=['GET'])
@require_admin
def list_reviews():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', None, type=str)
    sentiment = request.args.get('sentiment', None, type=str)

    pagination = review_repo.paginate_all(page=page, per_page=per_page, status=status or 'published', sentiment=sentiment)
    return jsonify({
        'reviews': [{
            'id': r.id,
            'user_id': r.user_id,
            'username': r.author.username if r.author else 'Unknown',
            'attraction_id': r.attraction_id,
            'attraction_name': r.attraction.name if r.attraction else None,
            'title': r.title,
            'content': r.content[:200],
            'rating': r.rating,
            'sentiment_label': r.sentiment_label,
            'status': r.status,
            'created_at': r.created_at.isoformat() if r.created_at else None
        } for r in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@admin_bp.route('/reviews/<int:review_id>/hide', methods=['POST'])
@require_admin
def hide_review(review_id):
    review = review_repo.get_by_id(review_id)
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    review.status = 'hidden'
    db.session.commit()
    return jsonify({'message': 'Review hidden'}), 200


@admin_bp.route('/reviews/<int:review_id>/approve', methods=['POST'])
@require_admin
def approve_review(review_id):
    review = review_repo.get_by_id(review_id)
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    review.status = 'published'
    db.session.commit()
    return jsonify({'message': 'Review approved'}), 200


@admin_bp.route('/attractions', methods=['GET'])
@require_admin
def list_all_attractions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    featured = request.args.get('featured', None, type=lambda x: x.lower() == 'true')

    pagination = attraction_repo.paginate(page=page, per_page=per_page, is_featured=featured)
    return jsonify({
        'attractions': [{
            'id': a.id,
            'name': a.name,
            'category': a.category,
            'region': a.region,
            'avg_rating': round(float(a.avg_rating or 0), 2),
            'total_reviews': a.total_reviews or 0,
            'view_count': a.view_count or 0,
            'is_featured': bool(a.is_featured),
            'is_verified': bool(a.is_verified),
            'created_at': a.created_at.isoformat() if a.created_at else None
        } for a in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages
    }), 200


@admin_bp.route('/attractions/<int:attraction_id>/feature', methods=['POST'])
@require_admin
def toggle_feature(attraction_id):
    attraction = attraction_repo.get_by_id(attraction_id)
    if not attraction:
        return jsonify({'error': 'Attraction not found'}), 404
    attraction.is_featured = not attraction.is_featured
    db.session.commit()
    return jsonify({'is_featured': bool(attraction.is_featured)}), 200


@admin_bp.route('/attractions/<int:attraction_id>/verify', methods=['POST'])
@require_admin
def verify_attraction(attraction_id):
    attraction = attraction_repo.get_by_id(attraction_id)
    if not attraction:
        return jsonify({'error': 'Attraction not found'}), 404
    attraction.is_verified = True
    db.session.commit()
    return jsonify({'message': 'Attraction verified'}), 200
