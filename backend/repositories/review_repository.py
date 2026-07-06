from models import Review
from app import db
from .base_repository import BaseRepository
from datetime import datetime


class ReviewRepository(BaseRepository):
    model = Review

    def find_by_user_and_attraction(self, user_id, attraction_id):
        return Review.query.filter_by(
            user_id=user_id,
            attraction_id=attraction_id
        ).first()

    def paginate_by_attraction(self, attraction_id, page=1, per_page=10, status='published'):
        query = Review.query.filter_by(attraction_id=attraction_id, status=status)
        return query.order_by(Review.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    def paginate_by_user(self, user_id, page=1, per_page=20, status='published'):
        query = Review.query.filter_by(user_id=user_id, status=status)
        return query.order_by(Review.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    def get_attraction_stats(self, attraction_id):
        from sqlalchemy import func
        result = db.session.query(
            func.avg(Review.rating).label('avg_rating'),
            func.count(Review.id).label('total')
        ).filter_by(attraction_id=attraction_id, status='published').first()
        return {
            'avg_rating': round(float(result.avg_rating or 0), 2),
            'total_reviews': result.total or 0
        }

    def get_sentiment_stats(self, attraction_id):
        from sqlalchemy import func
        from sqlalchemy import case
        result = db.session.query(
            func.avg(Review.sentiment_score).label('avg_score'),
            func.sum(case((Review.sentiment_label == 'positive', 1), else_=0)).label('pos_count'),
            func.sum(case((Review.sentiment_label == 'negative', 1), else_=0)).label('neg_count'),
        ).filter_by(attraction_id=attraction_id, status='published').first()
        return {
            'avg_sentiment': round(float(result.avg_score or 0), 3),
            'pos_count': int(result.pos_count or 0),
            'neg_count': int(result.neg_count or 0)
        }

    def soft_delete(self, review_id):
        review = self.get_by_id(review_id)
        if review:
            review.status = 'deleted'
            review.deleted_at = datetime.utcnow()
            db.session.commit()
        return review

    def paginate_all(self, page=1, per_page=20, sentiment=None, status='published'):
        query = Review.query.filter_by(status=status)
        if sentiment:
            query = query.filter_by(sentiment_label=sentiment)
        return query.order_by(Review.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
