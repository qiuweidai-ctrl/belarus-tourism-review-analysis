from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from werkzeug.security import check_password_hash
from repositories import UserRepository
from services import record_event

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

    record_event('register', user=user, detail=f'New user registered: {user.username}')

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

    if not user:
        record_event(
            'login_failed', username=data['username'],
            status='failure', detail='Username does not exist'
        )
        return jsonify({'error': 'Invalid username or password'}), 401

    if not check_password_hash(user.password_hash, data['password']):
        record_event(
            'login_failed', username=data['username'],
            status='failure', detail='Wrong password'
        )
        return jsonify({'error': 'Invalid username or password'}), 401

    if user.status != 'active':
        record_event(
            'login_failed', user=user, status='blocked',
            detail=f'Account status: {user.status}'
        )
        return jsonify({'error': 'Account is not active'}), 403

    user_repo.update_login_info(user.id, ip_address=request.remote_addr)

    token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    record_event('login', user=user, detail='Login success')

    return jsonify({
        'access_token': token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'nickname': user.nickname,
            'avatar_url': user.avatar_url
        }
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh():
    identity = get_jwt_identity()
    token = create_access_token(identity=identity)

    user = user_repo.get_by_id(int(identity))
    record_event('token_refresh', user=user, detail='Access token refreshed')

    return jsonify({'access_token': token}), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    user_id = int(get_jwt_identity())
    user = user_repo.get_by_id(user_id)
    record_event('logout', user=user, detail='User logged out')
    return jsonify({'message': 'Logged out'}), 200


@auth_bp.route('/events', methods=['GET'])
@jwt_required()
def my_events():
    from models import LoginEvent
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = LoginEvent.query.filter_by(user_id=user_id).order_by(LoginEvent.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    from services import serialize_event
    return jsonify({
        'events': [serialize_event(e) for e in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200
