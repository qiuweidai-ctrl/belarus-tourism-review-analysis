"""
Authentication routes (presentation layer).
Receives HTTP requests, calls services, returns JSON responses.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash
from repositories import UserRepository
from services import SentimentService

auth_bp = Blueprint('auth', __name__)

user_repo = UserRepository()


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required = ['username', 'email', 'password']
    if not data or not all(k in data for k in required):
        return jsonify({'error': 'username, email and password are required'}), 400

    if user_repo.find_by_username(data['username']):
        return jsonify({'error': 'Username already exists'}), 409
    if user_repo.find_by_email(data['email']):
        return jsonify({'error': 'Email already exists'}), 409

    user = user_repo.create_user(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        role=data.get('role', 'user'),
        nickname=data.get('nickname')
    )

    return jsonify({
        'message': 'User registered successfully',
        'user_id': user.id
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400

    user = user_repo.find_by_username(data['username'])
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401

    if user.status != 'active':
        return jsonify({'error': 'Account is not active'}), 403

    user_repo.update_login_info(user.id, ip_address=request.remote_addr)

    token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'access_token': token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'nickname': user.nickname
        }
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    from flask_jwt_extended import jwt_required, get_jwt_identity
    identity = get_jwt_identity()
    token = create_access_token(identity=identity)
    return jsonify({'access_token': token}), 200
