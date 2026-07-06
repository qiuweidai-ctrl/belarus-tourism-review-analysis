"""
Review routes (presentation layer).
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from repositories import (
    ReviewRepository, RatingRepository, AttractionRepository,
    WishlistRepository, UserRepository, SentimentLogRepository
)
from services import SentimentService
from app import db
from datetime import datetime

reviews_bp = Blueprint('reviews', __name__)

review_repo = ReviewRepository()
rating_repo = RatingRepository()
attraction_repo = AttractionRepository()
wishlist_repo = WishlistRepository()
user_repo = UserRepository()
sentiment_log_repo = SentimentLogRepository()
sentiment_service = SentimentService()


def _serialize_review(r):
    return {
        'id': r.id,
        'user_id': r.user_id,
        'username': r.author.username if r.author else 'Unknown',
        'nickname': r.author.nickname if r.author else None,
        'attraction_id': r.attraction_id,
        'title': r.title,
        'content': r.content,
        'rating': r.rating,
        'travel_type': r.travel_type,
        'travel_date': r.travel_date.isoformat() if r.travel_date else None,
        'travel_month': r.travel_month,
        'helpful_count': r.helpful_count or 0,
        'reply_count': r.reply_count or 0,
        'sentiment_label': r.sentiment_label,
        'sentiment_score': round(float(r.sentiment_score or 0), 3),
        'status': r.status,
        'created_at': r.created_at.isoformat() if r.created_at else None
    }


@reviews_bp.route('', methods=['GET'])
def list_reviews():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    attraction_id = request.args.get('attraction_id', None, type=int)
    sentiment = request.args.get('sentiment', None, type=str)
    user_id = request.args.get('user_id', None, type=int)

    if attraction_id:
        pagination = review_repo.paginate_by_attraction(attraction_id, page, per_page)
    elif user_id:
        pagination = review_repo.paginate_by_user(user_id, page, per_page)
    else:
        pagination = review_repo.paginate_all(page, per_page, sentiment=sentiment)

    return jsonify({
        'reviews': [_serialize_review(r) for r in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@reviews_bp.route('', methods=['POST'])
@jwt_required()
def create_review():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data.get('content') or not data.get('attraction_id'):
        return jsonify({'error': 'content and attraction_id are required'}), 400

    attraction = attraction_repo.get_by_id(data['attraction_id'])
    if not attraction:
        return jsonify({'error': 'Attraction not found'}), 404

    rating_score = data.get('rating', 3)

    # Analyze sentiment via service layer
    sentiment_result = sentiment_service.analyze(data['content'])

    # Save review
    review = review_repo.create(
        user_id=user_id,
        attraction_id=data['attraction_id'],
        title=data.get('title'),
        content=data['content'],
        rating=rating_score,
        travel_type=data.get('travel_type'),
        travel_date=data.get('travel_date'),
        travel_month=data.get('travel_month'),
        sentiment_label=sentiment_result['label'],
        sentiment_score=sentiment_result['score'],
        ai_processed=True,
        ip_address=request.remote_addr,
        status='published'
    )

    # Save/update rating
    rating_repo.upsert(user_id, data['attraction_id'], rating_score)

    # Update sentiment analysis log
    sentiment_log_repo.upsert(
        review_id=review.id,
        label=sentiment_result['label'],
        score=sentiment_result['score'],
        raw_response=sentiment_result.get('raw_response'),
        model=sentiment_result.get('model', 'deepseek-chat'),
        processing_time_ms=sentiment_result.get('processing_time_ms'),
        status=sentiment_result.get('status', 'success'),
        confidence=sentiment_result.get('confidence')
    )

    # Recalculate attraction stats
    _update_attraction_stats(data['attraction_id'])

    return jsonify({
        'message': 'Review created',
        'review_id': review.id,
        'sentiment': {
            'label': sentiment_result['label'],
            'score': sentiment_result['score'],
            'method': sentiment_result.get('method', 'deepseek_api')
        }
    }), 201


@reviews_bp.route('/<int:review_id>', methods=['GET'])
def get_review(review_id):
    review = review_repo.get_by_id(review_id)
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    return jsonify(_serialize_review(review)), 200


@reviews_bp.route('/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    review = review_repo.get_by_id(review_id)
    if not review:
        return jsonify({'error': 'Review not found'}), 404

    user_id = int(get_jwt_identity())
    user = user_repo.get_by_id(user_id)
    if review.user_id != user_id and user.role not in ('admin', 'moderator'):
        return jsonify({'error': 'Unauthorized'}), 403

    attraction_id = review.attraction_id
    review_repo.soft_delete(review_id)
    _update_attraction_stats(attraction_id)

    return jsonify({'message': 'Review deleted'}), 200


@reviews_bp.route('/<int:review_id>/helpful', methods=['POST'])
@jwt_required()
def vote_helpful(review_id):
    from models import ReviewHelpfulVote
    user_id = int(get_jwt_identity())
    review = review_repo.get_by_id(review_id)
    if not review:
        return jsonify({'error': 'Review not found'}), 404

    existing = ReviewHelpfulVote.query.filter_by(
        review_id=review_id, user_id=user_id
    ).first()

    if existing:
        return jsonify({'error': 'Already voted'}), 409

    vote = ReviewHelpfulVote(review_id=review_id, user_id=user_id, is_helpful=True)
    db.session.add(vote)
    review.helpful_count = (review.helpful_count or 0) + 1
    db.session.commit()

    return jsonify({'helpful_count': review.helpful_count}), 200


@reviews_bp.route('/attraction/<int:attraction_id>/stats', methods=['GET'])
def attraction_review_stats(attraction_id):
    stats = review_repo.get_attraction_stats(attraction_id)
    sentiment = review_repo.get_sentiment_stats(attraction_id)
    return jsonify({**stats, **sentiment}), 200


def _update_attraction_stats(attraction_id):
    stats = review_repo.get_attraction_stats(attraction_id)
    sentiment = review_repo.get_sentiment_stats(attraction_id)
    attraction_repo.update_rating_stats(
        attraction_id,
        avg_rating=stats['avg_rating'],
        total_reviews=stats['total_reviews'],
        sentiment_score=sentiment['avg_sentiment'],
        pos_count=sentiment['pos_count'],
        neg_count=sentiment['neg_count']
    )
