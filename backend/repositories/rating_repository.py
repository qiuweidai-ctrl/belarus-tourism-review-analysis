from models import Rating
from app import db
from .base_repository import BaseRepository


class RatingRepository(BaseRepository):
    model = Rating

    def upsert(self, user_id, attraction_id, score):
        existing = Rating.query.filter_by(user_id=user_id, attraction_id=attraction_id).first()
        if existing:
            existing.score = score
            db.session.commit()
            return existing
        rating = Rating(user_id=user_id, attraction_id=attraction_id, score=score)
        db.session.add(rating)
        db.session.commit()
        return rating

    def get_user_ratings(self, user_id, limit=100):
        return Rating.query.filter_by(user_id=user_id).order_by(
            Rating.created_at.desc()
        ).limit(limit).all()

    def get_attraction_ratings(self, attraction_id, limit=100):
        return Rating.query.filter_by(attraction_id=attraction_id).order_by(
            Rating.created_at.desc()
        ).limit(limit).all()

    def get_avg_and_count(self, attraction_id):
        from sqlalchemy import func
        result = db.session.query(
            func.avg(Rating.score).label('avg'),
            func.count(Rating.id).label('cnt')
        ).filter_by(attraction_id=attraction_id).first()
        return {
            'avg_rating': round(float(result.avg or 0), 2),
            'count': result.cnt or 0
        }

    def user_has_rated(self, user_id, attraction_id):
        return Rating.query.filter_by(
            user_id=user_id, attraction_id=attraction_id
        ).first() is not None

    def delete_by_user_attraction(self, user_id, attraction_id):
        rating = Rating.query.filter_by(
            user_id=user_id, attraction_id=attraction_id
        ).first()
        if rating:
            db.session.delete(rating)
            db.session.commit()
            return True
        return False
