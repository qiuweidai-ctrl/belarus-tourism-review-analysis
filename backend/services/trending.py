
import numpy as np
from datetime import datetime, timedelta
from models import db, Attraction, Review
from sqlalchemy import func
import math


DECAY_HALF_LIFE_DAYS = 30


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

    rating_score = float(attraction.avg_rating) / 5.0

    recent_time = datetime.utcnow() - timedelta(days=days)
    recent_review_count = Review.query.filter(
        Review.attraction_id == attraction_id,
        Review.created_at >= recent_time,
        Review.status == 'published'
    ).count()

    review_score = math.log(1 + recent_review_count) / math.log(1 + max(recent_review_count, 100))

    sentiment_score = float(attraction.sentiment_score) if attraction.sentiment_score else 0.5
    sentiment_score = (sentiment_score + 1) / 2

    recent_reviews = Review.query.filter(
        Review.attraction_id == attraction_id,
        Review.created_at >= recent_time,
        Review.status == 'published'
    ).order_by(Review.created_at.desc()).limit(10).all()

    if recent_reviews:
        time_weights = []
        for review in recent_reviews:
            weight = calculate_time_decay(review.created_at)
            time_weights.append(weight)
        avg_time_decay = np.mean(time_weights)
    else:
        avg_time_decay = 0.1

    trending_score = (
        rating_score * 0.25 +
        review_score * 0.35 +
        sentiment_score * 0.15 +
        avg_time_decay * 0.25
    ) * 100

    return round(trending_score, 2)


def get_trending_scores(limit: int = 20, days: int = 30) -> list:
    attractions = Attraction.query.filter_by(is_verified=True).all()

    trending_data = []
    for attraction in attractions:
        score = calculate_trending_score(attraction.id, days)
        trending_data.append({
            'attraction_id': attraction.id,
            'name': attraction.name,
            'score': score,
            'avg_rating': float(attraction.avg_rating),
            'total_reviews': attraction.total_reviews
        })

    trending_data.sort(key=lambda x: x['score'], reverse=True)

    return trending_data[:limit]


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

        if item['avg_rating'] >= 4.0 and recent_ratio < 0.3:
            categories['stable_classics'].append(item)
        elif recent_ratio > 0.5 or item['score'] > 60:
            categories['rising_stars'].append(item)
        elif item['avg_rating'] >= 3.5 and item['score'] < 40:
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
    attractions = Attraction.query.filter_by(
        category=category,
        is_verified=True
    ).all()

    trending = []
    for attraction in attractions:
        score = calculate_trending_score(attraction.id)
        trending.append({
            'attraction_id': attraction.id,
            'name': attraction.name,
            'score': score,
            'avg_rating': float(attraction.avg_rating),
            'total_reviews': attraction.total_reviews
        })

    trending.sort(key=lambda x: x['score'], reverse=True)

    return trending[:limit]


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
                'avg_rating': float(attraction.avg_rating),
                'total_reviews': attraction.total_reviews,
                'weekly_trend': weekly
            }

    return comparison
