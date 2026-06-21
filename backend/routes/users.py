"""
User profile routes.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from models import db, User
from repositories import UserRepository

users_bp = Blueprint('users', __name__)
user_repo = UserRepository()


@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = int(get_jwt_identity())
    user = user_repo.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'nickname': user.nickname,
        'avatar_url': user.avatar_url,
        'bio': user.bio,
        'role': user.role,
        'status': user.status,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None
    }), 200


@users_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_me():
    user_id = int(get_jwt_identity())
    user = user_repo.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()

    # Password change
    if data.get('new_password'):
        if not data.get('current_password'):
            return jsonify({'error': 'current_password is required'}), 400
        from werkzeug.security import check_password_hash
        if not check_password_hash(user.password_hash, data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400
        user.password_hash = generate_password_hash(data['new_password'])

    # Profile update
    for field in ['nickname', 'avatar_url', 'bio']:
        if field in data:
            setattr(user, field, data[field])

    db.session.commit()
    return jsonify({'message': 'Profile updated'}), 200


@users_bp.route('/<int:target_user_id>', methods=['GET'])
def get_user_profile(target_user_id):
    user = user_repo.get_by_id(target_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'username': user.username,
        'nickname': user.nickname,
        'avatar_url': user.avatar_url,
        'bio': user.bio,
        'created_at': user.created_at.isoformat() if user.created_at else None
    }), 200
