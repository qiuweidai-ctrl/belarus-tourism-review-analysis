"""
Recommendation routes (presentation layer).
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from repositories import RatingRepository, AttractionRepository
from services import RecommendationService

recommendation_bp = Blueprint('recommendation', __name__)

rating_repo = RatingRepository()
attraction_repo = AttractionRepository()
rec_service = RecommendationService()


@recommendation_bp.route('', methods=['GET'])
@jwt_required()
def get_recommendations():
    user_id = int(get_jwt_identity())
    limit = request.args.get('limit', 5, type=int)

    user_ratings = rating_repo.get_user_ratings(user_id)
    rated_ids = [r.attraction_id for r in user_ratings]

    all_attractions = attraction_repo.get_all(limit=1000)
    recommendations = rec_service.get_recommendations(
        user_id=user_id,
        rated_attraction_ids=rated_ids,
        all_attractions=all_attractions,
        limit=limit
    )

    return jsonify({'recommendations': recommendations}), 200


@recommendation_bp.route('/predict-rating', methods=['POST'])
@jwt_required()
def predict_rating():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    attraction_id = data.get('attraction_id')
    if not attraction_id:
        return jsonify({'error': 'attraction_id is required'}), 400

    attraction = attraction_repo.get_by_id(attraction_id)
    if not attraction:
        return jsonify({'error': 'Attraction not found'}), 404

    user_ratings = rating_repo.get_user_ratings(user_id)
    user_history = [
        {'name': attraction_repo.get_by_id(r.attraction_id).name, 'score': r.score}
        for r in user_ratings
        if attraction_repo.get_by_id(r.attraction_id)
    ]

    prediction = rec_service.predict_rating(
        user_id=user_id,
        attraction_id=attraction_id,
        attraction_name=attraction.name,
        attraction_avg=float(attraction.avg_rating or 0),
        user_history=user_history
    )

    return jsonify(prediction), 200
