from services.catalog import bayesian_score, normalized_score, select_primary_rating
from services.thumbnails import thumbnail_url


def serialize_external_rating(rating):
    if isinstance(rating, dict):
        data = rating
    else:
        data = {
            'provider': rating.provider,
            'provider_poi_id': rating.provider_poi_id,
            'score': float(rating.score),
            'scale': float(rating.scale),
            'review_count': rating.review_count,
            'source_url': rating.source_url,
            'retrieved_from': rating.retrieved_from,
            'retrieved_at': rating.retrieved_at,
            'extractor_version': rating.extractor_version,
        }
    return {
        'provider': data.get('provider'),
        'provider_poi_id': str(data.get('provider_poi_id')),
        'score': round(float(data.get('score') or 0), 2),
        'scale': round(float(data.get('scale') or 5), 2),
        'normalized_score': round(normalized_score(data), 2),
        'review_count': int(data.get('review_count') or 0),
        'count_kind': data.get('count_kind') or (
            'rating_votes' if data.get('provider') == 'Yandex Maps' else 'reviews'
        ),
        'source_url': data.get('source_url'),
        'retrieved_from': data.get('retrieved_from') or data.get('source_url'),
        'retrieved_at': (
            data.get('retrieved_at').isoformat()
            if hasattr(data.get('retrieved_at'), 'isoformat')
            else data.get('retrieved_at')
        ),
    }


def rating_payload(attraction, global_mean=0):
    external = [serialize_external_rating(r) for r in attraction.external_ratings]
    external.sort(key=lambda r: (r['review_count'], r['retrieved_at'] or ''), reverse=True)
    primary = select_primary_rating(external)
    local_count = int(attraction.total_reviews or 0)
    sentiment = None if local_count == 0 else round(float(attraction.sentiment_score or 0), 3)
    return {
        'local_rating': {
            'score': round(float(attraction.avg_rating), 2) if local_count else None,
            'review_count': local_count,
        },
        'primary_external_rating': primary,
        'external_ratings': external,
        'bayesian_score': (
            round(bayesian_score(primary, global_mean), 4) if primary else None
        ),
        'sentiment_score': sentiment,
    }


def calculate_global_mean(attractions):
    scores = []
    for attraction in attractions:
        ratings = [serialize_external_rating(r) for r in attraction.external_ratings]
        primary = select_primary_rating(ratings)
        if primary:
            scores.append(normalized_score(primary))
    return sum(scores) / len(scores) if scores else 0.0


def serialize_attraction(attraction, global_mean=0):
    sources = dict(attraction.field_sources or {})
    for field in ('view_count', 'wishlist_count', 'local_rating', 'avg_rating', 'total_reviews'):
        sources[field] = {'type': 'first_party', 'provider': 'Site activity'}
    for field in ('bayesian_score', 'sentiment_score'):
        sources[field] = {'type': 'system_derived', 'provider': 'Site calculation'}
    payload = {
        'id': attraction.id,
        'name': attraction.name,
        'name_en': attraction.name_en,
        'name_original': (attraction.field_sources or {}).get('name_en', {}).get('original_name'),
        'name_transliteration_method': (attraction.field_sources or {}).get('name_en', {}).get('method'),
        'description': attraction.description,
        'short_desc': attraction.short_desc,
        'location': attraction.location,
        'city': attraction.city,
        'region': attraction.region,
        'latitude': float(attraction.latitude) if attraction.latitude is not None else None,
        'longitude': float(attraction.longitude) if attraction.longitude is not None else None,
        'category': attraction.category,
        'suitable_season': attraction.suitable_season,
        'opening_hours': attraction.opening_hours,
        'ticket_price': float(attraction.ticket_price) if attraction.ticket_price is not None else None,
        'image_url': attraction.image_url,
        'thumbnail_url': thumbnail_url(attraction.image_url),
        'images': attraction.images_json,
        'avg_rating': round(float(attraction.avg_rating or 0), 2),
        'total_reviews': int(attraction.total_reviews or 0),
        'sentiment_pos_count': int(attraction.sentiment_pos_count or 0),
        'sentiment_neg_count': int(attraction.sentiment_neg_count or 0),
        'wishlist_count': int(attraction.wishlist_count or 0),
        'view_count': int(attraction.view_count or 0),
        'is_featured': bool(attraction.is_featured),
        'is_verified': bool(attraction.is_verified),
        'catalog_status': attraction.catalog_status,
        'field_sources': sources,
        'wikidata_qid': attraction.wikidata_qid,
        'source_name': attraction.source_name,
        'source_url': attraction.source_url,
        'source_license': attraction.source_license,
        'source_retrieved_at': attraction.source_retrieved_at.isoformat() if attraction.source_retrieved_at else None,
        'description_source_url': attraction.description_source_url,
        'description_license': attraction.description_license,
        'image_source_url': attraction.image_source_url,
        'image_author': attraction.image_author,
        'image_license': attraction.image_license,
        'image_license_url': attraction.image_license_url,
        'price_source_url': attraction.price_source_url,
        'price_checked_at': attraction.price_checked_at.isoformat() if attraction.price_checked_at else None,
        'opening_hours_source_url': attraction.opening_hours_source_url,
        'created_by': attraction.created_by,
        'created_at': attraction.created_at.isoformat() if attraction.created_at else None,
    }
    payload.update(rating_payload(attraction, global_mean))
    return payload


# 列表只返回卡片需要的字段，详情再加载完整数据。
def serialize_card(attraction, global_mean=0, map_only=False):
    fields = ('id', 'name', 'name_en', 'city', 'region', 'category', 'latitude', 'longitude')
    result = {field: getattr(attraction, field) for field in fields}
    for field in ('latitude', 'longitude'):
        result[field] = float(result[field]) if result[field] is not None else None
    result['image_url'] = attraction.image_url
    result['thumbnail_url'] = thumbnail_url(attraction.image_url, 160 if map_only else 480)
    payload = rating_payload(attraction, global_mean)
    result['primary_external_rating'] = payload['primary_external_rating']
    if not map_only:
        result.update({key: value for key, value in payload.items() if key != 'external_ratings'})
        for field in ('short_desc', 'opening_hours', 'suitable_season', 'wishlist_count',
                      'view_count', 'is_featured', 'is_verified', 'total_reviews'):
            result[field] = getattr(attraction, field)
        result['ticket_price'] = float(attraction.ticket_price) if attraction.ticket_price is not None else None
    return result
