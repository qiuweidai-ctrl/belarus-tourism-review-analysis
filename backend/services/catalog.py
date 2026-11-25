import math
import re
import unicodedata
from datetime import datetime
from urllib.parse import urlparse


CORE_SOURCE_FIELDS = (
    'name', 'name_en', 'description', 'short_desc', 'location', 'city', 'region',
    'coordinates', 'category', 'image_url',
)


def normalize_name(value):
    value = unicodedata.normalize('NFKD', value or '').casefold()
    value = ''.join(c for c in value if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', value).strip()


def distance_meters(a_lat, a_lon, b_lat, b_lon):
    if None in (a_lat, a_lon, b_lat, b_lon):
        return None
    radius = 6371000.0
    p1, p2 = math.radians(float(a_lat)), math.radians(float(b_lat))
    dp = math.radians(float(b_lat) - float(a_lat))
    dl = math.radians(float(b_lon) - float(a_lon))
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * radius * math.atan2(math.sqrt(h), math.sqrt(1 - h))


def normalized_score(rating, target_scale=5.0):
    score = float(rating.get('score') or 0)
    scale = float(rating.get('scale') or 0)
    return score / scale * target_scale if scale > 0 else 0.0


# 有多个平台时，优先用评价数量多的那个。
def select_primary_rating(ratings):
    valid = [
        r for r in ratings
        if float(r.get('score') or 0) > 0
        and float(r.get('scale') or 0) > 0
        and int(r.get('review_count') or 0) > 0
    ]
    if not valid:
        return None
    return max(
        valid,
        key=lambda r: (
            int(r.get('review_count') or 0),
            str(r.get('retrieved_at') or ''),
        ),
    )


# 评价少的景点适当向整体均值靠拢。
def bayesian_score(rating, global_mean, minimum_reviews=5):
    if not rating:
        return None
    review_count = int(rating.get('review_count') or 0)
    score = normalized_score(rating)
    weight = review_count / (review_count + minimum_reviews)
    return weight * score + (1 - weight) * float(global_mean)


def _source_present(source):
    if not isinstance(source, dict):
        return False
    if source.get('type') == 'site_upload':
        return bool(source.get('uploaded_by') and source.get('uploaded_at'))
    url = source.get('url') or source.get('source_url')
    return isinstance(url, str) and urlparse(url).scheme in ('http', 'https') and bool(urlparse(url).netloc)


def catalog_errors(record, require_local_image=False):
    ratings = record.get('external_ratings') or []
    sources = record.get('field_sources') or {}
    if not isinstance(sources, dict):
        sources = {}
    values = {field: record.get(field) for field in CORE_SOURCE_FIELDS}
    try:
        latitude, longitude = float(record['latitude']), float(record['longitude'])
        values['coordinates'] = (math.isfinite(latitude) and math.isfinite(longitude)
                                 and -90 <= latitude <= 90 and -180 <= longitude <= 180)
    except (KeyError, TypeError, ValueError):
        values['coordinates'] = False
    errors = []
    for field in CORE_SOURCE_FIELDS:
        value = values[field]
        if not value or (isinstance(value, str) and not value.strip()):
            errors.append(field)
        if not _source_present(sources.get(field)):
            errors.append(f'{field}.source')
    for field, maximum in (('name', 200), ('name_en', 200), ('location', 300),
                           ('city', 100), ('region', 100), ('short_desc', 500)):
        if len(str(record.get(field) or '')) > maximum:
            errors.append(f'{field}.too_long')
    valid_ratings = []
    for rating in ratings:
        try:
            score, scale = float(rating.get('score') or 0), float(rating.get('scale') or 0)
            valid = (math.isfinite(score) and math.isfinite(scale)
                     and 0 < score <= scale and int(rating.get('review_count') or 0) > 0)
        except (TypeError, ValueError, OverflowError):
            valid = False
        if valid and all(rating.get(key) for key in (
            'provider', 'provider_poi_id', 'source_url', 'retrieved_at',
            'extractor_version',
        )) and _source_present({'url': rating.get('source_url')}):
            valid_ratings.append(rating)
    if not valid_ratings:
        errors.append('external_rating')
    photo_source = sources.get('image_url') or {}
    if isinstance(photo_source, dict) and photo_source.get('provider_poi_id'):
        if not any(rating.get('provider') == photo_source.get('provider')
                   and str(rating.get('provider_poi_id')) == str(photo_source['provider_poi_id'])
                   for rating in ratings):
            errors.append('image_url.rating_identity_conflict')
    for field, source_field in (
        ('ticket_price', 'price_source_url'), ('opening_hours', 'opening_hours_source_url'),
    ):
        if record.get(field) not in (None, '') and not (
            record.get(source_field) and _source_present(sources.get(field))
        ):
            errors.append(f'{field}.source')
    if record.get('suitable_season') and not _source_present(sources.get('suitable_season')):
        errors.append('suitable_season.source')
    if require_local_image:
        from services.catalog_images import local_image_metadata
        if not local_image_metadata(record.get('image_url')):
            errors.append('image_url.unavailable')
    return errors


def has_required_sources(record, require_local_image=False):
    return not catalog_errors(record, require_local_image=require_local_image)


def compatible_category(left, right):
    left, right = (left or 'other').casefold(), (right or 'other').casefold()
    return left == right or 'other' in (left, right)


def find_duplicate(candidate, existing):
    provider_ids = {
        (r.get('provider'), str(r.get('provider_poi_id')))
        for r in candidate.get('external_ratings') or []
    }
    for item in existing:
        other_ids = {
            (r.get('provider'), str(r.get('provider_poi_id')))
            for r in item.get('external_ratings') or []
        }
        if provider_ids & other_ids:
            return item, 'provider_poi_id'

    name = normalize_name(candidate.get('name_en'))
    city = normalize_name(candidate.get('city') or candidate.get('region'))
    name_matches = [
        item for item in existing
        if normalize_name(item.get('name_en')) == name
        and normalize_name(item.get('city') or item.get('region')) == city
    ]
    if len(name_matches) == 1:
        return name_matches[0], 'name_city'
    if len(name_matches) > 1:
        return None, 'ambiguous_name_city'

    nearby = []
    for item in existing:
        distance = distance_meters(
            candidate.get('latitude'), candidate.get('longitude'),
            item.get('latitude'), item.get('longitude'),
        )
        if distance is not None and distance <= 100 and compatible_category(
            candidate.get('category'), item.get('category')
        ):
            nearby.append(item)
    if len(nearby) == 1:
        return nearby[0], 'coordinates'
    if len(nearby) > 1:
        return None, 'ambiguous_coordinates'
    return None, None


def iso_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace('Z', '+00:00')).replace(tzinfo=None)
