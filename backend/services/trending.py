import numpy as np
from datetime import datetime, timedelta
from models import db, Attraction, Review
from sqlalchemy import func
import math
from collections import defaultdict
from sqlalchemy.orm import load_only
from services.attraction_presenter import rating_payload
from services.thumbnails import thumbnail_url


DECAY_HALF_LIFE_DAYS = 30


# 较新的评价对热度影响更大。
def calculate_time_decay(created_at: datetime) -> float:
    if not created_at:
        return 1.0

    days_ago = (datetime.utcnow() - created_at).days

    if days_ago < 0:
        days_ago = 0

    decay_rate = math.log(2) / DECAY_HALF_LIFE_DAYS

    return math.exp(-decay_rate * days_ago)


def calculate_trending_score(attraction_id: int, days: int = 30) -> float:
    attraction = Attraction.query.get(attraction_id)

    if not attraction:
        return 0.0

    recent_time = datetime.utcnow() - timedelta(days=days)
    recent_review_count = Review.query.filter(
        Review.attraction_id == attraction_id,
        Review.created_at >= recent_time,
        Review.status == 'published', Review.deleted_at.is_(None)
    ).count()

    review_score = math.log(1 + recent_review_count) / math.log(1 + max(recent_review_count, 100))

    recent_reviews = Review.query.filter(
        Review.attraction_id == attraction_id,
        Review.created_at >= recent_time,
        Review.status == 'published', Review.deleted_at.is_(None)
    ).order_by(Review.created_at.desc()).limit(10).all()

    if recent_reviews:
        time_weights = []
        for review in recent_reviews:
            weight = calculate_time_decay(review.created_at)
            time_weights.append(weight)
        avg_time_decay = np.mean(time_weights)
    else:
        avg_time_decay = 0.0

    view_score = min(1.0, math.log1p(attraction.view_count or 0) / math.log1p(10000))
    wishlist_score = min(1.0, math.log1p(attraction.wishlist_count or 0) / math.log1p(1000))
    trending_score = (
        view_score * 0.35 + wishlist_score * 0.30 +
        review_score * 0.20 + avg_time_decay * 0.15
    ) * 100

    return round(trending_score, 2)


def _recent_activity(days, category=None):
    query = db.session.query(Review.attraction_id, Review.created_at).join(Attraction).filter(
        Attraction.catalog_status == 'active', Review.status == 'published',
        Review.deleted_at.is_(None), Review.created_at >= datetime.utcnow() - timedelta(days=days),
    )
    if category:
        query = query.filter(Attraction.category == category)
    counts, dates = defaultdict(int), defaultdict(list)
    for attraction_id, created_at in query.order_by(Review.created_at.desc(), Review.id.desc()):
        counts[attraction_id] += 1
        if len(dates[attraction_id]) < 10:
            dates[attraction_id].append(created_at)
    return counts, dates


def _activity_score(attraction, count, dates):
    review_score = math.log1p(count) / math.log1p(max(count, 100))
    decay = sum(calculate_time_decay(date) for date in dates) / len(dates) if dates else 0.0
    views = min(1.0, math.log1p(attraction.view_count or 0) / math.log1p(10000))
    saves = min(1.0, math.log1p(attraction.wishlist_count or 0) / math.log1p(1000))
    return round((views * .35 + saves * .30 + review_score * .20 + decay * .15) * 100, 2)


def get_trending_scores(limit: int = 20, days: int = 30, category=None) -> list:
    fields = ('id', 'name', 'location', 'category', 'image_url', 'view_count', 'wishlist_count',
              'total_reviews', 'avg_rating', 'sentiment_score')
    query = Attraction.query.options(load_only(*(getattr(Attraction, field) for field in fields))).filter_by(catalog_status='active')
    if category:
        query = query.filter(Attraction.category == category)
    attractions = query.order_by(Attraction.id).all()
    counts, dates = _recent_activity(days, category)
    ranked = [(attraction, _activity_score(attraction, counts[attraction.id], dates[attraction.id]))
              for attraction in attractions]
    ranked.sort(key=lambda item: item[1], reverse=True)
    trending_data = []
    for attraction, score in ranked[:max(0, limit)]:
        rating_data = rating_payload(attraction)
        trending_data.append({
            'attraction_id': attraction.id,
            'name': attraction.name,
            'score': score,
            'trending_score': score,
            'location': attraction.location,
            'category': attraction.category,
            'image_url': attraction.image_url,
            'thumbnail_url': thumbnail_url(attraction.image_url),
            'primary_external_rating': rating_data['primary_external_rating'],
            'local_rating': rating_data['local_rating'],
            'view_count': attraction.view_count or 0,
            'wishlist_count': attraction.wishlist_count or 0,
            'total_reviews': attraction.total_reviews or 0,
            'metric_source': 'first_party_engagement'
        })

    return trending_data


def categorize_trending(trending_data: list) -> dict:
    categories = {
        'stable_classics': [],
        'rising_stars': [],
        'hidden_gems': []
    }

    for item in trending_data:
        attraction_id = item['attraction_id']
        recent_time = datetime.utcnow() - timedelta(days=30)

        total_reviews = item['total_reviews']
        if total_reviews == 0:
            recent_ratio = 0
        else:
            recent_count = Review.query.filter(
                Review.attraction_id == attraction_id,
                Review.created_at >= recent_time,
                Review.status == 'published'
            ).count()
            recent_ratio = recent_count / total_reviews

        if item['view_count'] >= 100 and recent_ratio < 0.3:
            categories['stable_classics'].append(item)
        elif recent_ratio > 0.5 or item['score'] > 60:
            categories['rising_stars'].append(item)
        elif item['wishlist_count'] > 0 and item['score'] < 40:
            categories['hidden_gems'].append(item)

    return categories


def get_weekly_trend(attraction_id: int, weeks: int = 8) -> list:
    weekly_data = []

    for week in range(weeks):
        end_date = datetime.utcnow() - timedelta(weeks=week)
        start_date = end_date - timedelta(days=7)

        reviews = Review.query.filter(
            Review.attraction_id == attraction_id,
            Review.created_at >= start_date,
            Review.created_at < end_date,
            Review.status == 'published'
        ).all()

        if reviews:
            avg_rating = np.mean([r.rating for r in reviews])
            avg_sentiment = np.mean([float(r.sentiment_score) if r.sentiment_score else 0 for r in reviews])
            review_count = len(reviews)

            week_score = (
                (avg_rating / 5.0) * 0.4 +
                math.log(1 + review_count) / 5.0 * 0.3 +
                ((avg_sentiment + 1) / 2) * 0.3
            ) * 100
        else:
            week_score = 0

        weekly_data.append({
            'week': week + 1,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'review_count': len(reviews) if reviews else 0,
            'score': round(week_score, 2)
        })

    weekly_data.reverse()

    return weekly_data


def get_trending_by_category(category: str, limit: int = 10) -> list:
    return get_trending_scores(limit, category=category)


def compare_attractions(attraction_ids: list) -> dict:
    comparison = {}

    for aid in attraction_ids:
        attraction = Attraction.query.get(aid)
        if attraction:
            score = calculate_trending_score(aid)

            weekly = get_weekly_trend(aid, weeks=4)

            comparison[aid] = {
                'name': attraction.name,
                'current_score': score,
                'primary_external_rating': rating_payload(attraction)['primary_external_rating'],
                'local_rating': rating_payload(attraction)['local_rating'],
                'total_reviews': attraction.total_reviews or 0,
                'weekly_trend': weekly
            }

    return comparison
