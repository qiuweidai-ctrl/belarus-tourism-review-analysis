from flask import Blueprint, jsonify, request

from models import Attraction, ExternalReview
from services.external_reviews import serialize_external_review

external_reviews_bp = Blueprint('external_reviews', __name__)


@external_reviews_bp.route('/<int:attraction_id>/external-reviews', methods=['GET'])
# 外部摘录单独返回，不混进本站评价列表。
def list_external_reviews(attraction_id):
    attraction = Attraction.query.filter_by(id=attraction_id, catalog_status='active').first()
    if not attraction:
        return jsonify({'error': 'Attraction not found'}), 404
    page = max(1, request.args.get('page', 1, type=int))
    per_page = max(1, min(request.args.get('per_page', 10, type=int), 50))
    result = ExternalReview.query.filter_by(attraction_id=attraction_id).order_by(
        ExternalReview.published_at.desc(), ExternalReview.id.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'items': [serialize_external_review(row) for row in result.items],
        'total': result.total, 'pages': result.pages, 'current_page': page,
        'content_kind': 'external_review_excerpt',
        'notice': 'Short attributed excerpts, not full reviews or site-user reviews.',
    })
