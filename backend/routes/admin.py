from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Review, Attraction, LoginEvent, db
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
    actor_id = int(get_jwt_identity())
    actor = user_repo.get_by_id(actor_id)
    user = user_repo.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json() or {}
    if actor.role != 'admin' and user.role == 'admin':
        return jsonify({'error': 'Only an admin can edit an admin account'}), 403
    if 'role' in data:
        if actor.role != 'admin':
            return jsonify({'error': 'Only an admin can change user roles'}), 403
        if user_id == actor_id:
            return jsonify({'error': 'You cannot change your own role'}), 400
        if data['role'] not in ('user', 'moderator', 'admin'):
            return jsonify({'error': 'Invalid role'}), 400
    if 'status' in data:
        if user_id == actor_id:
            return jsonify({'error': 'You cannot change your own status'}), 400
        if data['status'] not in ('active', 'inactive', 'banned'):
            return jsonify({'error': 'Invalid status'}), 400
    for field in ['role', 'status', 'nickname', 'avatar_url', 'bio']:
        if field in data:
            setattr(user, field, data[field])
    db.session.commit()
    return jsonify({'message': 'User updated', 'user': serialize_user(user)}), 200


@admin_bp.route('/users/<int:user_id>/ban', methods=['POST'])
@require_admin
def ban_user(user_id):
    actor_id = int(get_jwt_identity())
    actor = user_repo.get_by_id(actor_id)
    user = user_repo.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if user_id == actor_id:
        return jsonify({'error': 'You cannot ban your own account'}), 400
    if user.role == 'admin' and actor.role != 'admin':
        return jsonify({'error': 'Only an admin can ban an admin account'}), 403
    user.status = 'banned'
    db.session.commit()
    return jsonify({'message': 'User banned'}), 200


@admin_bp.route('/users/<int:user_id>/unban', methods=['POST'])
@require_admin
def unban_user(user_id):
    actor = user_repo.get_by_id(int(get_jwt_identity()))
    user = user_repo.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if user.role == 'admin' and actor.role != 'admin':
        return jsonify({'error': 'Only an admin can unban an admin account'}), 403
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


@admin_bp.route('/login-events', methods=['GET'])
@require_admin
def list_login_events():
    from services import serialize_event

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)
    event_type = request.args.get('event_type', None, type=str)
    user_id = request.args.get('user_id', None, type=int)
    ip = request.args.get('ip', None, type=str)

    query = LoginEvent.query.order_by(LoginEvent.created_at.desc())
    if event_type:
        query = query.filter(LoginEvent.event_type == event_type)
    if user_id:
        query = query.filter(LoginEvent.user_id == user_id)
    if ip:
        query = query.filter(LoginEvent.ip_address == ip)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    type_stats = dict(
        db.session.query(LoginEvent.event_type, func.count(LoginEvent.id))
        .group_by(LoginEvent.event_type).all()
    )

    return jsonify({
        'events': [serialize_event(e) for e in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'type_stats': type_stats,
    }), 200
