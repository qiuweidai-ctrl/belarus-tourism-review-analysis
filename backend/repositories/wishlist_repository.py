from models import Wishlist
from app import db
from .base_repository import BaseRepository


class WishlistRepository(BaseRepository):
    model = Wishlist

    def toggle(self, user_id, attraction_id, note=None, priority=3):
        existing = Wishlist.query.filter_by(
            user_id=user_id, attraction_id=attraction_id
        ).first()
        if existing:
            existing.visited = not existing.visited if existing.visited else True
            db.session.commit()
            return existing, False
        item = Wishlist(
            user_id=user_id,
            attraction_id=attraction_id,
            note=note,
            priority=priority,
            visited=False
        )
        db.session.add(item)
        db.session.commit()
        return item, True

    def get_user_wishlist(self, user_id, visited=None, page=1, per_page=20):
        query = Wishlist.query.filter_by(user_id=user_id)
        if visited is not None:
            query = query.filter_by(visited=visited)
        return query.order_by(
            Wishlist.priority.asc(), Wishlist.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

    def is_wishlisted(self, user_id, attraction_id):
        return Wishlist.query.filter_by(
            user_id=user_id, attraction_id=attraction_id
        ).first() is not None

    def remove(self, user_id, attraction_id):
        item = Wishlist.query.filter_by(
            user_id=user_id, attraction_id=attraction_id
        ).first()
        if item:
            db.session.delete(item)
            db.session.commit()
            return True
        return False

    def update_note(self, user_id, attraction_id, note):
        item = Wishlist.query.filter_by(
            user_id=user_id, attraction_id=attraction_id
        ).first()
        if item:
            item.note = note
            db.session.commit()
        return item
