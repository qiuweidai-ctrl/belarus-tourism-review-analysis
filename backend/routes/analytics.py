from collections import Counter
import re

from flask import Blueprint, request, jsonify
from sqlalchemy import func

from models import db, Attraction, Review, User, Article, Question

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


def _norm(value):
    if value is None:
        return 0.0
    try:
        return round(float(value), 3)
    except (TypeError, ValueError):
        return 0.0


@analytics_bp.route('/overview', methods=['GET'])
def overview():
    total_attractions = Attraction.query.count()
    total_reviews = Review.query.filter_by(status='published').count()
    total_users = User.query.count()
    total_articles = Article.query.count()
    total_questions = Question.query.count()

    avg_rating = db.session.query(func.avg(Review.rating)).scalar() or 0
    avg_price = db.session.query(func.avg(Attraction.ticket_price)).scalar() or 0
    total_views = db.session.query(func.sum(Attraction.view_count)).scalar() or 0

    sentiment_rows = dict(
        db.session.query(Review.sentiment_label, func.count(Review.id))
        .filter(Review.sentiment_label.isnot(None))
        .group_by(Review.sentiment_label).all()
    )
    total_sentiment = sum(sentiment_rows.values()) or 0

    return jsonify({
        'attractions': total_attractions,
        'reviews': total_reviews,
        'users': total_users,
        'articles': total_articles,
        'questions': total_questions,
        'avg_rating': _norm(avg_rating),
        'avg_price': _norm(avg_price),
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
    rows = dict(
        db.session.query(Review.rating, func.count(Review.id))
        .filter(Review.status == 'published')
        .group_by(Review.rating).all()
    )
    stars = [{'rating': s, 'count': rows.get(s, 0)} for s in (1, 2, 3, 4, 5)]

    cat_rows = db.session.query(
        Attraction.category,
        func.count(Attraction.id),
        func.avg(Attraction.avg_rating),
        func.avg(Attraction.ticket_price)
    ).group_by(Attraction.category).all()

    categories = sorted(
        (
            {
                'category': c,
                'count': n,
                'avg_rating': _norm(r),
                'avg_price': _norm(p),
            }
            for c, n, r, p in cat_rows
        ),
        key=lambda x: -x['count'],
    )

    return jsonify({'stars': stars, 'categories': categories}), 200


@analytics_bp.route('/region-distribution', methods=['GET'])
def region_distribution():
    rows = db.session.query(
        Attraction.region,
        func.count(Attraction.id),
        func.avg(Attraction.avg_rating)
    ).group_by(Attraction.region).all()

    regions = sorted(
        (
            {'region': r or 'Unknown', 'count': n, 'avg_rating': _norm(a)}
            for r, n, a in rows
        ),
        key=lambda x: -x['count'],
    )

    city_rows = db.session.query(
        Attraction.city,
        func.count(Attraction.id),
        func.avg(Attraction.avg_rating)
    ).group_by(Attraction.city).all()

    cities = sorted(
        (
            {'city': c or 'Unknown', 'count': n, 'avg_rating': _norm(a)}
            for c, n, a in city_rows
        ),
        key=lambda x: -x['count'],
    )[:20]

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
        .filter(Attraction.ticket_price.isnot(None)).all()
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
    ).filter(Review.status == 'published').group_by('month').order_by('month').all()

    points = [
        {'month': m, 'count': n, 'avg_rating': _norm(a)} for m, n, a in rows
    ]

    type_rows = dict(
        db.session.query(Review.travel_type, func.count(Review.id))
        .filter(Review.travel_type.isnot(None))
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
        .filter(Review.sentiment_label.isnot(None))
        .group_by(Review.sentiment_label).all()
    )

    rows = db.session.query(
        Attraction.category,
        Review.sentiment_label,
        func.count(Review.id),
    ).join(Attraction, Review.attraction_id == Attraction.id).group_by(
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


TOP_METRICS = {
    'rating': 'avg_rating',
    'reviews': 'total_reviews',
    'views': 'view_count',
    'wishlist': 'wishlist_count',
}


@analytics_bp.route('/top-attractions', methods=['GET'])
def top_attractions():
    metric = request.args.get('metric', 'rating', type=str)
    limit = min(request.args.get('limit', 10, type=int), 50)
    column = TOP_METRICS.get(metric, 'avg_rating')

    rows = db.session.query(Attraction).order_by(
        getattr(Attraction, column).desc()
    ).limit(limit).all()

    items = [{
        'id': a.id,
        'name': a.name,
        'city': a.city,
        'region': a.region,
        'category': a.category,
        'image_url': a.image_url,
        'avg_rating': _norm(a.avg_rating),
        'total_reviews': a.total_reviews or 0,
        'view_count': a.view_count or 0,
        'wishlist_count': a.wishlist_count or 0,
        'ticket_price': _norm(a.ticket_price),
    } for a in rows]

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
        ).all():
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

    columns, model = EXPORT_QUERIES[dataset]
    rows = db.session.query(model).all()

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
