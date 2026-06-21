from models import User
from app import db
from .base_repository import BaseRepository
from werkzeug.security import generate_password_hash


class UserRepository(BaseRepository):
    model = User

    def find_by_username(self, username):
        return User.query.filter_by(username=username).first()

    def find_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def create_user(self, username, email, password, role='user', nickname=None):
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            nickname=nickname or username,
            status='active',
            email_verified=False
        )
        db.session.add(user)
        db.session.commit()
        return user

    def update_login_info(self, user_id, ip_address=None):
        from datetime import datetime
        user = self.get_by_id(user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            user.last_login_ip = ip_address
            db.session.commit()
        return user

    def paginate(self, page=1, per_page=20, role=None, status=None):
        query = User.query
        if role:
            query = query.filter(User.role == role)
        if status:
            query = query.filter(User.status == status)
        query = query.order_by(User.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)
