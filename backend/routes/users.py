import os
import re
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from models import db, User
from repositories import UserRepository

users_bp = Blueprint('users', __name__)
user_repo = UserRepository()

ALLOWED_AVATAR_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
AVATAR_MAX_BYTES = 4 * 1024 * 1024

_FILENAME_SAFE_RE = re.compile(r'[^A-Za-z0-9_.-]+')


def _safe_filename(name: str) -> str:
    name = name.strip().replace(' ', '_')
    name = _FILENAME_SAFE_RE.sub('', name)
    return name[:80] or 'avatar'


def _delete_old_avatar(absolute_path: str) -> None:
    if not absolute_path:
        return
    try:
        if os.path.isfile(absolute_path):
            os.remove(absolute_path)
    except Exception:
        pass


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

    if data.get('new_password'):
        if not data.get('current_password'):
            return jsonify({'error': 'current_password is required'}), 400
        from werkzeug.security import check_password_hash
        if not check_password_hash(user.password_hash, data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400
        user.password_hash = generate_password_hash(data['new_password'])

    for field in ['nickname', 'avatar_url', 'bio']:
        if field in data:
            setattr(user, field, data[field])

    db.session.commit()
    return jsonify({'message': 'Profile updated'}), 200


@users_bp.route('/me/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    user_id = int(get_jwt_identity())
    user = user_repo.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if 'avatar' not in request.files:
        return jsonify({'error': "No file part 'avatar' in request"}), 400

    f = request.files['avatar']
    if not f or not f.filename:
        return jsonify({'error': 'No file selected'}), 400

    orig = f.filename
    ext = orig.rsplit('.', 1)[-1].lower() if '.' in orig else ''
    if ext not in ALLOWED_AVATAR_EXT:
        return jsonify({
            'error': f'Unsupported file type .{ext}. Allowed: {sorted(ALLOWED_AVATAR_EXT)}'
        }), 400

    head = f.read(8)
    f.seek(0)
    head_bytes = head[:8]
    def _looks_like(b: bytes, sig: bytes) -> bool:
        return head_bytes.startswith(sig)
    is_png  = _looks_like(head_bytes, b'\x89PNG\r\n\x1a\n')
    is_jpg  = head_bytes.startswith(b'\xff\xd8\xff')
    is_gif  = head_bytes.startswith(b'GIF8')
    is_webp = head_bytes[:4] == b'RIFF' and head_bytes[8:12] == b'WEBP'
    if not (is_png or is_jpg or is_gif or is_webp):
        return jsonify({'error': 'File content does not look like a valid image'}), 400

    upload_root = current_app.config.get('UPLOAD_FOLDER') or 'static/uploads'
    avatar_dir = os.path.join(upload_root, 'avatars')
    os.makedirs(avatar_dir, exist_ok=True)

    safe_base = _safe_filename(f'{user_id}_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:6]}')
    filename = f'{safe_base}.{ext}'
    absolute_path = os.path.join(avatar_dir, filename)

    f.save(absolute_path)

    try:
        size = os.path.getsize(absolute_path)
        if size > AVATAR_MAX_BYTES:
            _delete_old_avatar(absolute_path)
            return jsonify({'error': f'Image too large ({size} bytes; max {AVATAR_MAX_BYTES})'}), 413
    except OSError:
        pass

    public_path = f'/static/uploads/avatars/{filename}'
    avatar_url = url_for('static', filename=f'uploads/avatars/{filename}', _external=False)

    if user.avatar_url and user.avatar_url.startswith('/static/uploads/avatars/'):
        rel = user.avatar_url.lstrip('/').replace('/', os.sep)
        if rel.startswith('static' + os.sep) or rel.startswith('static/'):
            old_abs = os.path.join(current_app.root_path, rel) if hasattr(current_app, 'root_path') else os.path.join(os.getcwd(), rel)
        else:
            old_abs = os.path.join('static', rel)
        _delete_old_avatar(old_abs)

    user.avatar_url = avatar_url
    db.session.commit()

    return jsonify({
        'avatar_url': avatar_url,
        'size': os.path.getsize(absolute_path) if os.path.isfile(absolute_path) else None,
        'url': avatar_url,
        'path': public_path,
    }), 200


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
