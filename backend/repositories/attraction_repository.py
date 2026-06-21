from models import Attraction
from app import db
from .base_repository import BaseRepository


class AttractionRepository(BaseRepository):
    model = Attraction

    def paginate(self, page=1, per_page=10, category=None, region=None,
                 search=None, sort_by='created_at', is_featured=None):
        query = Attraction.query

        if category:
            query = query.filter(Attraction.category == category)
        if region:
            query = query.filter(Attraction.region == region)
        if is_featured is not None:
            query = query.filter(Attraction.is_featured == is_featured)
        if search:
            query = query.filter(
                (Attraction.name.ilike(f'%{search}%')) |
                (Attraction.name_en.ilike(f'%{search}%')) |
                (Attraction.description.ilike(f'%{search}%'))
            )

        sort_map = {
            'created_at': Attraction.created_at.desc(),
            'rating': Attraction.avg_rating.desc(),
            'name': Attraction.name.asc(),
            'reviews': Attraction.total_reviews.desc(),
        }
        order = sort_map.get(sort_by, Attraction.created_at.desc())
        return query.order_by(order).paginate(page=page, per_page=per_page, error_out=False)

    def increment_view_count(self, attraction_id):
        attraction = self.get_by_id(attraction_id)
        if attraction:
            attraction.view_count = (attraction.view_count or 0) + 1
            db.session.commit()
        return attraction

    def increment_wishlist_count(self, attraction_id, delta=1):
        attraction = self.get_by_id(attraction_id)
        if attraction:
            attraction.wishlist_count = max(0, (attraction.wishlist_count or 0) + delta)
            db.session.commit()
        return attraction

    def update_rating_stats(self, attraction_id, avg_rating, total_reviews,
                          sentiment_score=None, pos_count=None, neg_count=None):
        attraction = self.get_by_id(attraction_id)
        if attraction:
            attraction.avg_rating = avg_rating
            attraction.total_reviews = total_reviews
            if sentiment_score is not None:
                attraction.sentiment_score = sentiment_score
            if pos_count is not None:
                attraction.sentiment_pos_count = pos_count
            if neg_count is not None:
                attraction.sentiment_neg_count = neg_count
            db.session.commit()
        return attraction

    def get_categories(self):
        result = db.session.query(Attraction.category).distinct().all()
        return [r[0] for r in result if r[0]]

    def get_regions(self):
        result = db.session.query(Attraction.region).distinct().all()
        return [r[0] for r in result if r[0]]
