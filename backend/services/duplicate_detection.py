
from datasketch import MinHash, MinHashLSH
from models import db, Review
import re
from datetime import datetime
import hashlib

SIMILARITY_THRESHOLD = 0.7

_lsh_index = None
_review_minhashes = {}
_last_index_time = None


def preprocess_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower()

    text = re.sub(r'[^\w\s]', ' ', text)

    text = re.sub(r'\s+', ' ', text).strip()

    return text


def create_minhash(text: str, num_perm: int = 128) -> MinHash:
    minhash = MinHash(num_perm=num_perm)

    words = preprocess_text(text).split()

    for word in words:
        if len(word) > 2:
            minhash.update(word.encode('utf8'))

    return minhash


def similarity(minhash1: MinHash, minhash2: MinHash) -> float:
    return minhash1.jaccard(minhash2)


def build_lsh_index():
    global _lsh_index, _review_minhashes, _last_index_time

    _lsh_index = MinHashLSH(threshold=SIMILARITY_THRESHOLD, num_perm=128)

    reviews = Review.query.filter_by(status='published').all()

    _review_minhashes = {}

    for review in reviews:
        if review.content:
            minhash = create_minhash(review.content)

            _lsh_index.insert(f"review_{review.id}", minhash)

            _review_minhashes[review.id] = minhash

    _last_index_time = datetime.utcnow()

    return len(_review_minhashes)


def check_duplicate(content: str, exclude_review_id: int = None) -> dict:
    global _lsh_index, _review_minhashes

    if _lsh_index is None or len(_review_minhashes) == 0:
        build_lsh_index()

    if not content:
        return {
            'is_duplicate': False,
            'similar_reviews': [],
            'max_similarity': 0.0
        }

    new_minhash = create_minhash(content)

    candidates = _lsh_index.query(new_minhash)

    similar_reviews = []

    for candidate_key in candidates:
        if exclude_review_id and int(candidate_key.split('_')[1]) == exclude_review_id:
            continue

        review_id = int(candidate_key.split('_')[1])

        if review_id in _review_minhashes:
            sim = similarity(new_minhash, _review_minhashes[review_id])

            if sim >= SIMILARITY_THRESHOLD:
                review = Review.query.get(review_id)
                if review:
                    similar_reviews.append({
                        'review_id': review_id,
                        'similarity': round(sim * 100, 2),
                        'author': review.author.username if review.author else 'Anonymous',
                        'preview': review.content[:100] if review.content else ''
                    })

    similar_reviews.sort(key=lambda x: x['similarity'], reverse=True)

    max_similarity = similar_reviews[0]['similarity'] if similar_reviews else 0.0

    return {
        'is_duplicate': len(similar_reviews) > 0,
        'similar_reviews': similar_reviews,
        'max_similarity': max_similarity,
        'warning_level': get_warning_level(max_similarity)
    }


def get_warning_level(similarity: float) -> str:
    if similarity >= 90:
        return 'high'
    elif similarity >= 70:
        return 'medium'
    else:
        return 'low'


def add_to_index(review_id: int, content: str):
    global _lsh_index, _review_minhashes

    if _lsh_index is None:
        build_lsh_index()

    if content:
        minhash = create_minhash(content)
        _lsh_index.insert(f"review_{review_id}", minhash)
        _review_minhashes[review_id] = minhash


def remove_from_index(review_id: int):
    global _lsh_index, _review_minhashes

    if review_id in _review_minhashes:
        key = f"review_{review_id}"
        try:
            _lsh_index.remove(key)
        except:
            pass
        del _review_minhashes[review_id]


def find_similar_pairs(min_similarity: float = 0.8, limit: int = 100) -> list:
    global _review_minhashes

    if _review_minhashes is None or len(_review_minhashes) == 0:
        build_lsh_index()

    similar_pairs = []
    review_ids = list(_review_minhashes.keys())

    review_ids = review_ids[-1000:]

    for i, rid1 in enumerate(review_ids):
        for rid2 in review_ids[i+1:]:
            sim = similarity(_review_minhashes[rid1], _review_minhashes[rid2])

            if sim >= min_similarity:
                review1 = Review.query.get(rid1)
                review2 = Review.query.get(rid2)

                if review1 and review2:
                    similar_pairs.append({
                        'review_1': {
                            'id': rid1,
                            'user_id': review1.user_id,
                            'author': review1.author.username if review1.author else 'Anonymous',
                            'content_preview': review1.content[:100] if review1.content else '',
                            'created_at': review1.created_at.isoformat()
                        },
                        'review_2': {
                            'id': rid2,
                            'user_id': review2.user_id,
                            'author': review2.author.username if review2.author else 'Anonymous',
                            'content_preview': review2.content[:100] if review2.content else '',
                            'created_at': review2.created_at.isoformat()
                        },
                        'similarity': round(sim * 100, 2)
                    })

                    if len(similar_pairs) >= limit:
                        return similar_pairs

    similar_pairs.sort(key=lambda x: x['similarity'], reverse=True)

    return similar_pairs


def batch_check_similarity(review_ids: list) -> dict:
    global _review_minhashes

    results = {}

    for rid in review_ids:
        if rid in _review_minhashes:
            similar = []

            for other_rid, other_minhash in _review_minhashes.items():
                if other_rid != rid:
                    sim = similarity(_review_minhashes[rid], other_minhash)

                    if sim >= SIMILARITY_THRESHOLD:
                        similar.append({
                            'review_id': other_rid,
                            'similarity': round(sim * 100, 2)
                        })

            results[rid] = {
                'similar_count': len(similar),
                'similar_reviews': similar[:5]
            }

    return results


def get_user_review_pattern(user_id: int) -> dict:
    from models import Review

    reviews = Review.query.filter_by(
        user_id=user_id,
        status='published'
    ).order_by(Review.created_at.desc()).limit(20).all()

    if len(reviews) < 2:
        return {'pattern': 'normal', 'suspicion_level': 'low'}

    intervals = []
    for i in range(len(reviews) - 1):
        delta = (reviews[i].created_at - reviews[i+1].created_at).total_seconds() / 3600
        intervals.append(delta)

    avg_interval = sum(intervals) / len(intervals) if intervals else 24

    total_similarity = 0
    pairs_checked = 0

    for i in range(len(reviews)):
        for j in range(i + 1, len(reviews)):
            if reviews[i].id in _review_minhashes and reviews[j].id in _review_minhashes:
                sim = similarity(
                    _review_minhashes[reviews[i].id],
                    _review_minhashes[reviews[j].id]
                )
                total_similarity += sim
                pairs_checked += 1

    avg_similarity = total_similarity / pairs_checked if pairs_checked > 0 else 0

    suspicion_level = 'low'
    pattern = 'normal'

    if avg_interval < 1:
        suspicion_level = 'high'
        pattern = 'rapid_firing'
    elif avg_interval < 6:
        if avg_similarity > 0.6:
            suspicion_level = 'high'
            pattern = 'rapid_copy_paste'
        else:
            suspicion_level = 'medium'
            pattern = 'rapid_normal'
    elif avg_similarity > 0.7:
        suspicion_level = 'medium'
        pattern = 'copy_paste'

    return {
        'pattern': pattern,
        'suspicion_level': suspicion_level,
        'review_count': len(reviews),
        'avg_interval_hours': round(avg_interval, 2),
        'avg_content_similarity': round(avg_similarity * 100, 2)
    }


def rebuild_index():
    build_lsh_index()
    return len(_review_minhashes)
