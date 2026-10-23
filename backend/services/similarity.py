import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from models import db, Attraction, Review, AttractionTag, Tag
import pickle
import os

_tfidf_vectorizer = None
_attraction_vectors = None
_attraction_ids = None
_last_update = None


def build_attraction_text(attraction: Attraction) -> str:
    texts = []

    if attraction.name:
        texts.append(attraction.name)
    if attraction.name_en:
        texts.append(attraction.name_en)

    if attraction.description:
        texts.append(attraction.description)
    if attraction.short_desc:
        texts.append(attraction.short_desc)

    if attraction.category:
        texts.append(attraction.category)

    if attraction.city:
        texts.append(attraction.city)
    if attraction.region:
        texts.append(attraction.region)

    tags = [row[0] for row in (
        db.session.query(Tag.name)
        .join(AttractionTag, AttractionTag.tag_id == Tag.id)
        .filter(AttractionTag.attraction_id == attraction.id)
        .all()
    )]
    if tags:
        texts.extend(tags)

    reviews = Review.query.filter_by(
        attraction_id=attraction.id,
        status='published'
    ).order_by(Review.rating.desc()).limit(5).all()

    review_texts = []
    for review in reviews:
        if review.content:
            review_texts.append(review.content[:200])

    if review_texts:
        texts.append(' '.join(review_texts))

    return ' '.join(texts).strip() or f'attraction {attraction.id}'


def rebuild_tfidf_index():
    global _tfidf_vectorizer, _attraction_vectors, _attraction_ids, _last_update

    attractions = Attraction.query.filter_by(is_verified=True).all()

    if not attractions:
        _tfidf_vectorizer = None
        _attraction_vectors = None
        _attraction_ids = []
        _last_update = 0
        return False

    texts = []
    _attraction_ids = []

    for attraction in attractions:
        text = build_attraction_text(attraction)
        texts.append(text)
        _attraction_ids.append(attraction.id)

    _tfidf_vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        stop_words='english',
        min_df=1,
        max_df=0.95
    )

    _attraction_vectors = _tfidf_vectorizer.fit_transform(texts)
    _last_update = len(attractions)

    return True


def get_similar_attractions(attraction_id: int, top_k: int = 5) -> list:
    global _tfidf_vectorizer, _attraction_vectors, _attraction_ids

    current_count = Attraction.query.filter_by(is_verified=True).count()
    if (_attraction_vectors is None or
        _last_update != current_count or
        attraction_id not in _attraction_ids):
        if not rebuild_tfidf_index():
            return []

    if _attraction_vectors is None or _attraction_ids is None:
        return []

    try:
        idx = _attraction_ids.index(attraction_id)
    except ValueError:
        if not rebuild_tfidf_index():
            return []
        try:
            idx = _attraction_ids.index(attraction_id)
        except ValueError:
            return []

    target_vector = _attraction_vectors[idx]
    similarities = cosine_similarity(target_vector, _attraction_vectors)[0]

    top_indices = similarities.argsort()[::-1]

    results = []
    for i in top_indices:
        if _attraction_ids[i] != attraction_id:
            results.append({
                'attraction_id': _attraction_ids[i],
                'similarity': float(similarities[i])
            })
            if len(results) >= top_k:
                break

    return results


def get_personalized_recommendations(user_id: int, top_k: int = 10) -> list:
    global _tfidf_vectorizer, _attraction_vectors, _attraction_ids

    from models import Review, Wishlist

    rated_ids = set(
        r.attraction_id for r in Review.query.filter_by(user_id=user_id, status='published').all()
    )
    wishlist_ids = set(
        w.attraction_id for w in Wishlist.query.filter_by(user_id=user_id).all()
    )
    interacted_ids = rated_ids | wishlist_ids

    if not interacted_ids:
        return get_trending_attractions(top_k)

    current_count = Attraction.query.filter_by(is_verified=True).count()
    if _attraction_vectors is None or _attraction_ids is None or _last_update != current_count:
        if not rebuild_tfidf_index():
            return get_trending_attractions(top_k)

    indices = [_attraction_ids.index(aid) for aid in interacted_ids if aid in _attraction_ids]

    if not indices:
        return get_trending_attractions(top_k)

    user_interest_vector = np.asarray(_attraction_vectors[indices].mean(axis=0))

    similarities = cosine_similarity(user_interest_vector, _attraction_vectors)[0]

    results = []
    for i in similarities.argsort()[::-1]:
        if _attraction_ids[i] not in interacted_ids:
            results.append({
                'attraction_id': _attraction_ids[i],
                'similarity': float(similarities[i])
            })
            if len(results) >= top_k:
                break

    return results


def get_trending_attractions(top_k: int = 10) -> list:
    from services.trending import get_trending_scores

    trending = get_trending_scores(top_k)
    return [{'attraction_id': t['attraction_id'], 'similarity': 0.0} for t in trending]
