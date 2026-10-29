
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import similarity, user_clustering, text_analysis, trending, duplicate_detection
from models import db, Attraction
from routes.admin import require_admin

algo_bp = Blueprint('algo', __name__, url_prefix='/api/algo')


@algo_bp.route('/similar/<int:attraction_id>', methods=['GET'])
def get_similar_attractions(attraction_id):
    top_k = request.args.get('top_k', 5, type=int)

    similar = similarity.get_similar_attractions(attraction_id, top_k)

    results = []
    for item in similar:
        attraction = Attraction.query.get(item['attraction_id'])
        if attraction:
            results.append({
                'attraction_id': attraction.id,
                'name': attraction.name,
                'location': attraction.location,
                'category': attraction.category,
                'avg_rating': float(attraction.avg_rating),
                'image_url': attraction.image_url,
                'similarity': round(item['similarity'] * 100, 2)
            })

    return jsonify({
        'success': True,
        'data': results
    })


@algo_bp.route('/recommendations/personal', methods=['GET'])
@jwt_required()
def get_personal_recommendations():
    user_id = get_jwt_identity()
    top_k = request.args.get('top_k', 10, type=int)

    recommendations = similarity.get_personalized_recommendations(user_id, top_k)

    results = []
    for item in recommendations:
        attraction = Attraction.query.get(item['attraction_id'])
        if attraction:
            results.append({
                'attraction_id': attraction.id,
                'name': attraction.name,
                'location': attraction.location,
                'category': attraction.category,
                'avg_rating': float(attraction.avg_rating),
                'image_url': attraction.image_url,
                'similarity_score': round(item['similarity'] * 100, 2)
            })

    return jsonify({
        'success': True,
        'data': results
    })


@algo_bp.route('/clustering/my', methods=['GET'])
@jwt_required()
def get_my_cluster():
    user_id = get_jwt_identity()

    cluster_info = user_clustering.get_user_cluster(user_id)

    return jsonify({
        'success': True,
        'data': cluster_info
    })


@algo_bp.route('/clustering/distribution', methods=['GET'])
@require_admin
def get_cluster_distribution():
    distribution = user_clustering.get_cluster_distribution()

    return jsonify({
        'success': True,
        'data': distribution
    })


@algo_bp.route('/clustering/<int:cluster_id>/users', methods=['GET'])
@require_admin
def get_cluster_users(cluster_id):
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)

    result = user_clustering.get_cluster_users(cluster_id, limit, offset)

    return jsonify({
        'success': True,
        'data': result
    })


@algo_bp.route('/clustering/<int:cluster_id>/explain', methods=['GET'])
@require_admin
def explain_cluster(cluster_id):
    explanation = user_clustering.explain_cluster(cluster_id)

    return jsonify({
        'success': True,
        'data': explanation
    })


@algo_bp.route('/clustering/retrain', methods=['POST'])
@require_admin
def retrain_clustering():
    success, message = user_clustering.train_clustering()

    if success:
        return jsonify({
            'success': True,
            'message': f'Clustering retrained successfully. {message} users processed.'
        })
    else:
        return jsonify({
            'success': False,
            'message': message
        })


@algo_bp.route('/quality/<int:review_id>', methods=['GET'])
def get_review_quality(review_id):
    from models import Review

    review = Review.query.get(review_id)
    if not review:
        return jsonify({'success': False, 'message': 'Review not found'}), 404

    quality = text_analysis.calculate_review_quality(review)

    return jsonify({
        'success': True,
        'data': {
            'review_id': review_id,
            **quality
        }
    })


@algo_bp.route('/quality/batch', methods=['POST'])
@require_admin
def batch_calculate_quality():
    data = request.get_json() or {}
    review_ids = data.get('review_ids')

    results = text_analysis.batch_calculate_quality(review_ids)

    return jsonify({
        'success': True,
        'data': results
    })


@algo_bp.route('/quality/attraction/<int:attraction_id>/top', methods=['GET'])
def get_top_quality_reviews(attraction_id):
    limit = request.args.get('limit', 5, type=int)

    top_reviews = text_analysis.get_top_quality_reviews(attraction_id, limit)

    return jsonify({
        'success': True,
        'data': top_reviews
    })


@algo_bp.route('/trending', methods=['GET'])
def get_trending():
    limit = request.args.get('limit', 20, type=int)
    days = request.args.get('days', 30, type=int)

    trending_data = trending.get_trending_scores(limit, days)

    results = []
    for item in trending_data:
        attraction = Attraction.query.get(item['attraction_id'])
        if attraction:
            results.append({
                'attraction_id': attraction.id,
                'name': attraction.name,
                'location': attraction.location,
                'category': attraction.category,
                'avg_rating': float(attraction.avg_rating),
                'total_reviews': attraction.total_reviews,
                'image_url': attraction.image_url,
                'trending_score': item['score']
            })

    return jsonify({
        'success': True,
        'data': results
    })


@algo_bp.route('/trending/categories', methods=['GET'])
def get_trending_by_category():
    category = request.args.get('category', 'museum')
    limit = request.args.get('limit', 10, type=int)

    trending_data = trending.get_trending_by_category(category, limit)

    return jsonify({
        'success': True,
        'data': trending_data
    })


@algo_bp.route('/trending/<int:attraction_id>/weekly', methods=['GET'])
def get_weekly_trend(attraction_id):
    weeks = request.args.get('weeks', 8, type=int)

    weekly_data = trending.get_weekly_trend(attraction_id, weeks)

    return jsonify({
        'success': True,
        'data': weekly_data
    })


@algo_bp.route('/trending/categorize', methods=['GET'])
def get_categorized_trending():
    limit = request.args.get('limit', 20, type=int)

    all_trending = trending.get_trending_scores(limit)
    categorized = trending.categorize_trending(all_trending)

    return jsonify({
        'success': True,
        'data': {
            'stable_classics': categorized['stable_classics'][:10],
            'rising_stars': categorized['rising_stars'][:10],
            'hidden_gems': categorized['hidden_gems'][:10]
        }
    })


@algo_bp.route('/duplicate/check', methods=['POST'])
def check_duplicate():
    data = request.get_json() or {}
    content = data.get('content', '')
    exclude_id = data.get('exclude_review_id')

    result = duplicate_detection.check_duplicate(content, exclude_id)

    return jsonify({
        'success': True,
        'data': result
    })


@algo_bp.route('/duplicate/pairs', methods=['GET'])
@require_admin
def find_duplicate_pairs():
    min_sim = request.args.get('min_similarity', 0.8, type=float)
    limit = request.args.get('limit', 100, type=int)

    pairs = duplicate_detection.find_similar_pairs(min_sim, limit)

    return jsonify({
        'success': True,
        'data': pairs
    })


@algo_bp.route('/duplicate/user-pattern/<int:user_id>', methods=['GET'])
@require_admin
def get_user_review_pattern(user_id):
    pattern = duplicate_detection.get_user_review_pattern(user_id)

    return jsonify({
        'success': True,
        'data': pattern
    })


@algo_bp.route('/duplicate/rebuild-index', methods=['POST'])
@require_admin
def rebuild_duplicate_index():
    count = duplicate_detection.rebuild_index()

    return jsonify({
        'success': True,
        'message': f'Index rebuilt with {count} reviews'
    })


@algo_bp.route('/summary/<int:attraction_id>', methods=['GET'])
def get_attraction_summary(attraction_id):
    summary = text_analysis.generate_attraction_summary(attraction_id)

    return jsonify({
        'success': True,
        'data': {
            'attraction_id': attraction_id,
            'summary': summary
        }
    })


@algo_bp.route('/trending/recalculate', methods=['POST'])
@require_admin
def recalculate_trending():
    attractions = Attraction.query.filter_by(is_verified=True).all()

    updated_count = 0
    for attraction in attractions:
        score = trending.calculate_trending_score(attraction.id)
        updated_count += 1

    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Updated trending scores for {updated_count} attractions'
    })
