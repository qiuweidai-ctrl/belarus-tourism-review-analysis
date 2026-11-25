from collections import Counter
import re

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from sqlalchemy import func

from models import db, Attraction, ExternalRating, ExternalReview, Review, User, Article, Question
from services.attraction_presenter import serialize_attraction, serialize_card
from services.catalog_cache import cached_catalog
from services.catalog_queries import rated_query, global_mean, external_score

analytics_bp = Blueprint('analytics', __name__)

STOPWORDS = {
    'the', 'and', 'for', 'with', 'this', 'that', 'was', 'were', 'are', 'you',
    'your', 'our', 'their', 'they', 'have', 'has', 'had', 'not', 'but', 'from',
    'its', 'his', 'her', 'she', 'him', 'who', 'what', 'when', 'where', 'why',
    'how', 'all', 'any', 'can', 'would', 'could', 'should', 'will', 'just',
    'very', 'really', 'much', 'more', 'most', 'some', 'such', 'only', 'also',
    'there', 'here', 'then', 'than', 'too', 'get', 'got', 'go', 'went', 'one',
    'two', 'day', 'days', 'time', 'times', 'visit', 'visited', 'photo',
    'photos', 'place', 'places', 'really', 'thing', 'things', 'love', 'loved',
    'like', 'liked', 'nice', 'good', 'great', 'best', 'well', 'see', 'saw',
    'am', 'do', 'does', 'did', 'been', 'being', 'were', 'them', 'because',
    'about', 'into', 'out', 'over', 'under', 'after', 'before', 'between',
    'through', 'while', 'during', 'above', 'below', 'up', 'down', 'off',
    'again', 'further', 'once', 'each', 'few', 'nor', 'own', 'same', 'so',
    'century', 'th', 'st', 'ave', 'blvd',
}

WORD_RE = re.compile(r"[A-Za-z]{3,}")


# 统计页面的数据从数据库汇总。
def _active_catalog():
    def load():
        rows = rated_query(Attraction.category, Attraction.city, Attraction.region,
                           Attraction.ticket_price, external_score().label('score')).all()
        items = [{
            'category': row.category, 'city': row.city, 'region': row.region,
            'ticket_price': float(row.ticket_price) if row.ticket_price is not None else None,
            'primary_external_rating': {'normalized_score': round(float(row.score), 2)},
        } for row in rows]
        return [], items, global_mean()
    return cached_catalog('statistics', load)


def _norm(value):
    if value is None:
        return 0.0
    try:
        return round(float(value), 3)
    except (TypeError, ValueError):
        return 0.0


@analytics_bp.route('/overview', methods=['GET'])
def overview():
    total_attractions, avg_price, total_views = db.session.query(
        func.count(Attraction.id), func.avg(Attraction.ticket_price), func.sum(Attraction.view_count)
    ).filter(Attraction.catalog_status == 'active').one()
    external_mean = global_mean()
    total_reviews = Review.query.join(Attraction).filter(
        Review.status == 'published', Review.deleted_at.is_(None), Attraction.catalog_status == 'active'
    ).count()
    total_users = User.query.count()
    total_articles = Article.query.count()
    total_questions = Question.query.count()

    local_avg_rating = db.session.query(func.avg(Review.rating)).join(Attraction).filter(
        Review.status == 'published', Review.deleted_at.is_(None), Attraction.catalog_status == 'active'
    ).scalar()

    sentiment_rows = dict(
        db.session.query(Review.sentiment_label, func.count(Review.id))
        .join(Attraction).filter(
            Review.sentiment_label.isnot(None), Attraction.catalog_status == 'active',
            Review.status == 'published', Review.deleted_at.is_(None)
        )
        .group_by(Review.sentiment_label).all()
    )
    total_sentiment = sum(sentiment_rows.values()) or 0

    return jsonify({
        'attractions': total_attractions,
        'reviews': total_reviews,
        'users': total_users,
        'articles': total_articles,
        'questions': total_questions,
        'avg_rating': _norm(external_mean),
        'external_avg_rating': _norm(external_mean),
        'local_avg_rating': _norm(local_avg_rating) if local_avg_rating is not None else None,
        'avg_price': _norm(avg_price) if avg_price is not None else None,
        'total_views': int(total_views or 0),
        'sentiment': {
            'positive': sentiment_rows.get('positive', 0),
            'neutral': sentiment_rows.get('neutral', 0),
            'negative': sentiment_rows.get('negative', 0),
            'total': total_sentiment,
        },
    }), 200


@analytics_bp.route('/rating-distribution', methods=['GET'])
def rating_distribution():
    _, catalog, _ = _active_catalog()
    score_counts = Counter(
        item['primary_external_rating']['normalized_score']
        for item in catalog if item['primary_external_rating']
    )
    scores = [{'rating': score, 'count': count} for score, count in sorted(score_counts.items())]
    grouped = {}
    for item in catalog:
        bucket = grouped.setdefault(item['category'], {'ratings': [], 'prices': []})
        bucket['ratings'].append(item['primary_external_rating']['normalized_score'])
        if item['ticket_price'] is not None:
            bucket['prices'].append(item['ticket_price'])
    categories = sorted(({
        'category': category, 'count': len(values['ratings']),
        'avg_rating': _norm(sum(values['ratings']) / len(values['ratings'])),
        'avg_price': _norm(sum(values['prices']) / len(values['prices'])) if values['prices'] else None,
    } for category, values in grouped.items()), key=lambda x: -x['count'])

    return jsonify({'scores': scores, 'stars': scores, 'scale': 5, 'categories': categories}), 200


@analytics_bp.route('/region-distribution', methods=['GET'])
def region_distribution():
    _, catalog, _ = _active_catalog()
    def aggregate(field):
        grouped = {}
        for item in catalog:
            grouped.setdefault(item.get(field) or 'Unknown', []).append(
                item['primary_external_rating']['normalized_score']
            )
        return sorted(({
            field: name, 'count': len(scores),
            'avg_rating': _norm(sum(scores) / len(scores)),
        } for name, scores in grouped.items()), key=lambda x: -x['count'])
    regions = aggregate('region')
    cities = aggregate('city')[:20]

    return jsonify({'regions': regions, 'cities': cities}), 200


PRICE_BANDS = [
    (0, 0, 'Free'),
    (0.01, 5, 'Under 5 BYN'),
    (5, 10, '5 - 10 BYN'),
    (10, 20, '10 - 20 BYN'),
    (20, 50, '20 - 50 BYN'),
    (50, 1e9, 'Over 50 BYN'),
]


@analytics_bp.route('/price-analysis', methods=['GET'])
def price_analysis():
    prices = [
        float(p) for (p,) in db.session.query(Attraction.ticket_price)
        .filter(Attraction.ticket_price.isnot(None),
                Attraction.catalog_status == 'active').all()
    ]

    bands = []
    for lo, hi, label in PRICE_BANDS:
        if lo == 0 and hi == 0:
            count = sum(1 for p in prices if p <= 0)
        else:
            count = sum(1 for p in prices if lo < p <= hi)
        bands.append({'label': label, 'count': count})

    priced = [p for p in prices if p > 0]
    summary = {
        'total': len(prices),
        'free': sum(1 for p in prices if p <= 0),
        'min': _norm(min(prices)) if prices else 0,
        'max': _norm(max(prices)) if prices else 0,
        'avg': _norm(sum(prices) / len(prices)) if prices else 0,
        'median': _norm(sorted(prices)[len(prices) // 2]) if prices else 0,
        'avg_paid': _norm(sum(priced) / len(priced)) if priced else 0,
    }

    return jsonify({'bands': bands, 'summary': summary}), 200


@analytics_bp.route('/review-trend', methods=['GET'])
def review_trend():
    rows = db.session.query(
        func.date_format(Review.created_at, '%Y-%m').label('month'),
        func.count(Review.id),
        func.avg(Review.rating),
    ).join(Attraction).filter(
        Review.status == 'published', Attraction.catalog_status == 'active'
    ).group_by('month').order_by('month').all()

    points = [
        {'month': m, 'count': n, 'avg_rating': _norm(a)} for m, n, a in rows
    ]

    type_rows = dict(
        db.session.query(Review.travel_type, func.count(Review.id))
        .join(Attraction).filter(
            Review.travel_type.isnot(None), Attraction.catalog_status == 'active'
        )
        .group_by(Review.travel_type).all()
    )
    travel_types = [
        {'label': k or 'unknown', 'count': v}
        for k, v in sorted(type_rows.items(), key=lambda kv: -kv[1])
    ]

    return jsonify({'points': points, 'travel_types': travel_types}), 200


@analytics_bp.route('/sentiment-breakdown', methods=['GET'])
def sentiment_breakdown():
    overall = dict(
        db.session.query(Review.sentiment_label, func.count(Review.id))
        .join(Attraction).filter(
            Review.sentiment_label.isnot(None), Attraction.catalog_status == 'active'
        )
        .group_by(Review.sentiment_label).all()
    )

    rows = db.session.query(
        Attraction.category,
        Review.sentiment_label,
        func.count(Review.id),
    ).join(Attraction, Review.attraction_id == Attraction.id).filter(
        Attraction.catalog_status == 'active'
    ).group_by(
        Attraction.category, Review.sentiment_label
    ).all()

    per_category = {}
    for cat, label, count in rows:
        bucket = per_category.setdefault(cat or 'other', Counter())
        bucket[label or 'neutral'] += count

    breakdown = []
    for cat, bucket in per_category.items():
        pos = bucket.get('positive', 0)
        neu = bucket.get('neutral', 0)
        neg = bucket.get('negative', 0)
        total = pos + neu + neg
        breakdown.append({
            'category': cat,
            'positive': pos,
            'neutral': neu,
            'negative': neg,
            'total': total,
            'positive_ratio': _norm(pos / total * 100) if total else 0,
        })
    breakdown.sort(key=lambda x: -x['total'])

    return jsonify({
        'overall': [
            {'label': 'Positive', 'count': overall.get('positive', 0)},
            {'label': 'Neutral', 'count': overall.get('neutral', 0)},
            {'label': 'Negative', 'count': overall.get('negative', 0)},
        ],
        'by_category': breakdown,
    }), 200


@analytics_bp.route('/top-attractions', methods=['GET'])
def top_attractions():
    metric = request.args.get('metric', 'rating', type=str)
    limit = max(1, min(request.args.get('limit', 10, type=int), 50))
    excerpt_counts = db.session.query(
        ExternalReview.attraction_id, func.count(ExternalReview.id)
    ).group_by(ExternalReview.attraction_id).subquery()
    local_counts = db.session.query(
        Review.attraction_id, func.count(Review.id)
    ).filter(
        Review.status == 'published',
        Review.deleted_at.is_(None)
    ).group_by(Review.attraction_id).subquery()
    stored_count = func.coalesce(excerpt_counts.c[1], 0) + func.coalesce(local_counts.c[1], 0)
    mean = global_mean()
    rating_count = ExternalRating.review_count
    ranking_score = (rating_count * external_score() + 5.0 * mean) / (rating_count + 5.0)
    orders = {'rating': ranking_score, 'reviews': stored_count,
              'views': Attraction.view_count, 'wishlist': Attraction.wishlist_count}
    query = rated_query(Attraction, stored_count.label('stored_review_count')).outerjoin(
        excerpt_counts, excerpt_counts.c.attraction_id == Attraction.id
    ).outerjoin(local_counts, local_counts.c.attraction_id == Attraction.id)
    rows = query.order_by(orders.get(metric, ranking_score).desc(), Attraction.id.asc()).limit(limit).all()
    items = []
    for attraction, count in rows:
        item = serialize_card(attraction, mean) if request.args.get('view') == 'card' else serialize_attraction(attraction, mean)
        item['stored_review_count'] = int(count)
        item.setdefault('field_sources', {})
        item['field_sources']['stored_review_count'] = {
            'type': 'system_derived', 'provider': 'Site database',
            'method': 'Stored external excerpts plus published, non-deleted site reviews',
        }
        items.append(item)

    return jsonify({'metric': metric, 'items': items}), 200


@analytics_bp.route('/keywords', methods=['GET'])
def keywords():
    scope = request.args.get('scope', 'reviews', type=str)
    limit = min(request.args.get('limit', 80, type=int), 200)

    texts = []
    if scope in ('reviews', 'both'):
        for title, content in db.session.query(Review.title, Review.content).all():
            if title:
                texts.append(title)
            if content:
                texts.append(content)

    if scope in ('attractions', 'both'):
        for name, desc, loc in db.session.query(
            Attraction.name, Attraction.short_desc, Attraction.location
        ).filter(Attraction.catalog_status == 'active').all():
            texts.extend([name, desc, loc])

    counter = Counter()
    for text in texts:
        if not text:
            continue
        for word in WORD_RE.findall(str(text)):
            low = word.lower().strip("'-")
            if len(low) < 3 or low in STOPWORDS or low.isdigit():
                continue
            counter[low] += 1

    top = [
        {'word': w, 'count': c}
        for w, c in counter.most_common(limit)
    ]
    return jsonify({'scope': scope, 'total_words': sum(counter.values()), 'words': top}), 200

EXPORT_QUERIES = {
    'attractions': (
        'id, name, city, region, category, avg_rating, total_reviews, '
        'ticket_price, view_count, wishlist_count, sentiment_score',
        Attraction,
    ),
    'reviews': (
        'id, attraction_id, rating, sentiment_label, sentiment_score, '
        'travel_type, travel_month, helpful_count, status, created_at',
        Review,
    ),
    'users': (
        'id, username, email, role, status, created_at, last_login_at',
        User,
    ),
}


@analytics_bp.route('/export/<dataset>.csv', methods=['GET'])
def export_csv(dataset):
    import csv
    import io as _io
    from flask import Response

    if dataset not in EXPORT_QUERIES:
        return jsonify({'error': f"Unknown dataset '{dataset}'"}), 400

    if dataset == 'users':
        verify_jwt_in_request()
        user = db.session.get(User, int(get_jwt_identity()))
        if not user or user.role not in ('admin', 'moderator'):
            return jsonify({'error': 'Admin access required'}), 403

    columns, model = EXPORT_QUERIES[dataset]
    query = db.session.query(model)
    if model is Attraction:
        query = query.filter(Attraction.catalog_status == 'active')
    rows = query.all()

    buf = _io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(columns.split(', '))
    for row in rows:
        writer.writerow([getattr(row, c, None) for c in columns.split(', ')])
    buf.seek(0)

    return Response(
        buf.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={dataset}.csv'}
    ), 200
