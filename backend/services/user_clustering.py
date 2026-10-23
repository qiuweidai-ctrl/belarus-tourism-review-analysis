
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from models import db, User, Review, Wishlist, RatingDimension
from datetime import datetime, timedelta
import pickle

FEATURE_DIM = 8

N_CLUSTERS = 4

CLUSTER_NAMES = {
    0: 'General Tourist',
    1: 'Museum Lover',
    2: 'Nature Explorer',
    3: 'History Enthusiast'
}

_cluster_model = None
_scaler = None
_last_clustering_time = None


def extract_user_features(user_id: int) -> np.ndarray:
    from models import Review, Attraction

    features = np.zeros(FEATURE_DIM)

    reviews = Review.query.filter_by(
        user_id=user_id,
        status='published'
    ).all()

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    recent_reviews = [r for r in reviews if r.created_at >= thirty_days_ago]
    features[0] = len(recent_reviews) / 10.0

    if reviews:
        features[1] = np.mean([r.rating for r in reviews]) / 5.0

    if reviews:
        avg_length = np.mean([len(r.content) for r in reviews]) / 500.0
        features[2] = min(avg_length, 1.0)

    total_helpful = sum(r.helpful_count for r in reviews)
    features[3] = min(total_helpful / 50.0, 1.0)

    wishlist_count = Wishlist.query.filter_by(user_id=user_id).count()
    features[4] = min(wishlist_count / 20.0, 1.0)

    if reviews:
        category_counts = {}
        for review in reviews:
            attraction = Attraction.query.get(review.attraction_id)
            if attraction:
                cat = attraction.category
                category_counts[cat] = category_counts.get(cat, 0) + 1

        total = len(reviews)

        features[5] = category_counts.get('museum', 0) / total

        features[6] = (category_counts.get('nature', 0) +
                       category_counts.get('park', 0)) / total

        features[7] = (category_counts.get('castle', 0) +
                       category_counts.get('memorial', 0) +
                       category_counts.get('church', 0)) / total

    return features


def build_user_feature_matrix(user_ids: list = None) -> tuple:
    if user_ids is None:
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        active_users = db.session.query(User.id).join(Review).filter(
            Review.created_at >= six_months_ago
        ).distinct().all()
        user_ids = [u[0] for u in active_users]

    if not user_ids:
        return np.array([]), []

    features_list = []
    valid_user_ids = []

    for user_id in user_ids:
        features = extract_user_features(user_id)
        features_list.append(features)
        valid_user_ids.append(user_id)

    return np.array(features_list), valid_user_ids


def train_clustering():
    global _cluster_model, _scaler, _last_clustering_time

    feature_matrix, user_ids = build_user_feature_matrix()

    if len(user_ids) < N_CLUSTERS:
        return False, "Not enough users"

    _scaler = StandardScaler()
    scaled_features = _scaler.fit_transform(feature_matrix)

    _cluster_model = KMeans(
        n_clusters=N_CLUSTERS,
        random_state=42,
        n_init=10
    )
    _cluster_model.fit(scaled_features)

    _last_clustering_time = datetime.utcnow()

    return True, user_ids


def get_user_cluster(user_id: int) -> dict:
    global _cluster_model, _scaler

    if _cluster_model is None or _scaler is None:
        success, _ = train_clustering()
        if not success:
            return {'cluster_id': -1, 'cluster_name': 'Unknown', 'features': {}}

    features = extract_user_features(user_id)
    scaled_features = _scaler.transform([features])

    cluster_id = int(_cluster_model.predict(scaled_features)[0])

    center = _cluster_model.cluster_centers_[cluster_id]

    return {
        'cluster_id': cluster_id,
        'cluster_name': CLUSTER_NAMES.get(cluster_id, f'Cluster {cluster_id}'),
        'features': {
            'activity': float(features[0]),
            'rating_tendency': float(features[1]),
            'review_length': float(features[2]),
            'helpfulness': float(features[3]),
            'wishlist_usage': float(features[4]),
            'museum_preference': float(features[5]),
            'nature_preference': float(features[6]),
            'history_preference': float(features[7])
        },
        'centroid': center.tolist()
    }


def get_cluster_distribution() -> dict:
    global _cluster_model, _scaler

    if _cluster_model is None or _scaler is None:
        success, user_ids = train_clustering()
        if not success:
            return {}

    feature_matrix, user_ids = build_user_feature_matrix()

    if len(user_ids) == 0:
        return {}

    scaled_features = _scaler.transform(feature_matrix)
    labels = _cluster_model.predict(scaled_features)

    distribution = {}
    for i in range(N_CLUSTERS):
        count = int(np.sum(labels == i))
        distribution[CLUSTER_NAMES.get(i, f'Cluster {i}')] = {
            'count': count,
            'percentage': round(count / len(user_ids) * 100, 2)
        }

    return distribution


def get_cluster_users(cluster_id: int, limit: int = 20, offset: int = 0) -> list:
    global _cluster_model, _scaler

    if _cluster_model is None or _scaler is None:
        success, user_ids = train_clustering()
        if not success:
            return []

    feature_matrix, user_ids = build_user_feature_matrix()

    if len(user_ids) == 0:
        return []

    scaled_features = _scaler.transform(feature_matrix)
    labels = _cluster_model.predict(scaled_features)

    cluster_user_ids = [uid for uid, label in zip(user_ids, labels) if label == cluster_id]

    total = len(cluster_user_ids)
    paginated_ids = cluster_user_ids[offset:offset + limit]

    users = User.query.filter(User.id.in_(paginated_ids)).all()

    return {
        'total': total,
        'users': [
            {
                'id': u.id,
                'username': u.username,
                'nickname': u.nickname,
                'avatar_url': u.avatar_url,
                'review_count': Review.query.filter_by(user_id=u.id, status='published').count()
            }
            for u in users
        ]
    }


def explain_cluster(cluster_id: int) -> dict:
    global _cluster_model

    if _cluster_model is None:
        return {}

    center = _cluster_model.cluster_centers_[cluster_id]

    feature_names = [
        'Activity', 'Rating tendency', 'Review detail', 'Helpfulness',
        'Wishlist usage', 'Museum preference', 'Nature preference', 'History preference'
    ]

    explanations = []
    for i, (name, value) in enumerate(zip(feature_names, center)):
        if abs(value) > 0.5:
            if value > 0:
                explanations.append(f"High {name.lower()}")
            else:
                explanations.append(f"Low {name.lower()}")

    return {
        'cluster_id': cluster_id,
        'cluster_name': CLUSTER_NAMES.get(cluster_id, f'Cluster {cluster_id}'),
        'centroid': center.tolist(),
        'feature_names': feature_names,
        'explanations': explanations
    }
