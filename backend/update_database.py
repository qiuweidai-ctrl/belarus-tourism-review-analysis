import argparse
import json
from pathlib import Path
from sqlalchemy import func
from werkzeug.security import generate_password_hash
from app import create_app
from init_db import ensure_database_exists
from models import Attraction, AttractionTag, ExternalRating, ExternalReview, Review, Tag, User, db
from services.catalog import compatible_category, distance_meters, has_required_sources, iso_datetime, normalize_name

DATA_FILE = Path(__file__).with_name('rated_attractions.json')
REVIEW_FILE = Path(__file__).with_name('external_review_excerpts.json')

TAG_DEFINITIONS = {
    'history': ('History', '#8b4513'), 'nature': ('Nature', '#2a9d5c'),
    'architecture': ('Architecture', '#1a5e63'), 'memorial': ('Memorial', '#607d8b'),
    'museums': ('Museums', '#ff5722'), 'religious': ('Religious Sites', '#673ab7'),
    'urban': ('Urban', '#9e9e9e'),
}


CATEGORY_TAGS = {
    'castle': ['history', 'architecture'], 'palace': ['history', 'architecture'],
    'church': ['history', 'religious'], 'museum': ['history', 'museums'],
    'memorial': ['history', 'memorial'], 'nature': ['nature'], 'park': ['nature'],
    'architecture': ['architecture', 'urban'],
}


PRESERVED_FIELDS = {
    'avg_rating', 'total_reviews', 'sentiment_score', 'sentiment_pos_count',
    'sentiment_neg_count', 'wishlist_count', 'view_count',
}


PRESERVE_IF_EMPTY_FIELDS = {
    'wikidata_qid',
}


def load_records():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f'{DATA_FILE.name} is missing; restore it from the repository')
    records = json.loads(DATA_FILE.read_text(encoding='utf-8'))
    invalid = [r.get('name_en') for r in records
               if not has_required_sources(r, require_local_image=True)]
    if invalid:
        raise ValueError(f'{len(invalid)} catalog records failed source audit: {invalid[:5]}')
    return records


def ensure_default_users():
    defaults = [
        ('admin', 'admin@belarus-tourism.com', 'admin123', 'admin', 'Administrator'),
        ('demo', 'demo@example.com', 'demo123', 'user', 'Demo User'),
    ]
    for username, email, password, role, nickname in defaults:
        existing = User.query.filter(func.lower(User.username) == username).first()
        # 已有账号保持原来的密码和资料。
        if existing:
            continue
        else:
            db.session.add(User(
                username=username, email=email, password_hash=generate_password_hash(password),
                role=role, nickname=nickname, status='active', email_verified=True,
            ))
    db.session.commit()


# 优先按平台景点编号匹配，重复导入不会新增同一个景点。
def _match_existing(record, attractions):
    provider_matches = set()
    for rating in record.get('external_ratings') or []:
        existing_rating = ExternalRating.query.filter_by(
            provider=rating['provider'],
            provider_poi_id=str(rating['provider_poi_id']),
        ).first()
        if existing_rating:
            provider_matches.add(existing_rating.attraction_id)
    if len(provider_matches) == 1:
        attraction_id = next(iter(provider_matches))
        return next(a for a in attractions if a.id == attraction_id), 'provider_poi_id'
    if len(provider_matches) > 1:
        return None, 'ambiguous'
    exact = [a for a in attractions
             if normalize_name(a.name_en or a.name) == normalize_name(record['name_en'])
             and normalize_name(a.city or a.region)
             == normalize_name(record.get('city') or record.get('region'))]
    if len(exact) == 1:
        return exact[0], 'name_city'
    nearby = []
    for attraction in attractions:
        distance = distance_meters(
            attraction.latitude, attraction.longitude,
            record.get('latitude'), record.get('longitude'),
        )
        if (
            distance is not None and distance <= 100
            and compatible_category(attraction.category, record.get('category'))
        ):
            nearby.append(attraction)
    if len(nearby) == 1:
        return nearby[0], 'coordinates'
    return (None, 'ambiguous') if len(exact) > 1 or len(nearby) > 1 else (None, 'new')


def upsert_catalog(records):
    existing = Attraction.query.all()
    active_ids, conflicts = [], []
    added = updated = 0
    for record in records:
        if not has_required_sources(record, require_local_image=True):
            raise ValueError(f'Incomplete record cannot be imported: {record.get("name_en")}')
        attraction, reason = _match_existing(record, existing)
        if reason == 'ambiguous':
            conflicts.append({'name': record['name_en'], 'reason': reason})
            continue
        values = {k: v for k, v in record.items() if k not in {'source_id', 'external_ratings'}}
        for field in ('source_retrieved_at', 'price_checked_at'):
            values[field] = iso_datetime(values.get(field))
        if attraction is None:
            attraction = Attraction(**values)
            db.session.add(attraction)
            db.session.flush()
            existing.append(attraction)
            added += 1
        else:
            for field, value in values.items():
                if field not in PRESERVED_FIELDS:
                    if field in PRESERVE_IF_EMPTY_FIELDS and value in (None, ''):
                        continue
                    setattr(attraction, field, value)
            updated += 1
        active_ids.append(attraction.id)
        desired_rating_keys = {
            (item['provider'], str(item['provider_poi_id']))
            for item in record['external_ratings']
        }
        for stale_rating in list(attraction.external_ratings):
            key = (stale_rating.provider, str(stale_rating.provider_poi_id))
            if key not in desired_rating_keys:
                db.session.delete(stale_rating)
        for item in record['external_ratings']:
            external = ExternalRating.query.filter_by(
                provider=item['provider'], provider_poi_id=str(item['provider_poi_id'])
            ).first()
            if external is None:
                external = ExternalRating(
                    provider=item['provider'], provider_poi_id=str(item['provider_poi_id'])
                )
                db.session.add(external)
            external.attraction_id, external.score = attraction.id, item['score']
            external.scale, external.review_count = item['scale'], item['review_count']
            external.source_url = item['source_url']
            external.retrieved_from = item.get('retrieved_from') or item['source_url']
            external.retrieved_at = iso_datetime(item['retrieved_at'])
            external.extractor_version = item['extractor_version']
    db.session.commit()
    return added, updated, active_ids, conflicts


# 旧景点只归档，关联的用户内容仍然保留。
def archive_unlisted(active_ids):
    query = Attraction.query
    if active_ids:
        query = query.filter(Attraction.id.notin_(active_ids))
    count = query.update({'catalog_status': 'archived'}, synchronize_session=False)
    db.session.commit()
    return count


def ensure_tags(attractions):
    tags = {}
    for slug, (name, color) in TAG_DEFINITIONS.items():
        tag = Tag.query.filter_by(slug=slug).first()
        if not tag:
            tag = Tag(name=name, slug=slug, color=color, description=name, use_count=0)
            db.session.add(tag)
        tags[slug] = tag
    db.session.commit()
    added = 0
    for attraction in attractions:
        for slug in CATEGORY_TAGS.get((attraction.category or '').lower(), []):
            tag = tags[slug]
            if not AttractionTag.query.filter_by(
                attraction_id=attraction.id, tag_id=tag.id
            ).first():
                db.session.add(AttractionTag(attraction_id=attraction.id, tag_id=tag.id))
                added += 1
    db.session.commit()
    return added


def refresh_local_metrics(attractions):
    for attraction in attractions:
        average, count = db.session.query(func.avg(Review.rating), func.count(Review.id)).filter(
            Review.attraction_id == attraction.id, Review.status == 'published',
            Review.deleted_at.is_(None),
        ).first()
        attraction.avg_rating = round(float(average), 2) if count else 0
        attraction.total_reviews = int(count or 0)
        if not count:
            attraction.sentiment_score = None
            attraction.sentiment_pos_count = attraction.sentiment_neg_count = 0
    db.session.commit()


def import_external_reviews():
    rows = json.loads(REVIEW_FILE.read_text(encoding='utf-8'))
    ratings = {(r.provider, str(r.provider_poi_id)): r.attraction_id for r in ExternalRating.query.all()}
    existing = {(r.provider, r.provider_poi_id, r.provider_review_id) for r in ExternalReview.query.all()}
    fields = {column.name for column in ExternalReview.__table__.columns}
    added = 0
    # 外部评论按平台编号去重，不生成本站用户账号。
    for row in rows:
        key = (row['provider'], str(row['provider_poi_id']), str(row['provider_review_id']))
        if key in existing:
            continue
        attraction_id = ratings.get(key[:2])
        if attraction_id is None:
            raise ValueError('External review has no matching attraction')
        values = {key: value for key, value in row.items() if key in fields}
        values['attraction_id'] = attraction_id
        for field in ('published_at', 'retrieved_at'):
            values[field] = iso_datetime(values[field])
        db.session.add(ExternalReview(**values))
        existing.add(key)
        added += 1
    db.session.commit()
    return added


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()
    records = load_records()
    if not records:
        raise ValueError('The catalog is empty')
    ensure_database_exists(reset=args.reset)
    app = create_app()
    with app.app_context():
        # 表结构直接来自models.py，首次运行会创建22张表。
        db.create_all()
        ensure_default_users()
        added, updated, active_ids, conflicts = upsert_catalog(records)
        if conflicts:
            raise ValueError(f'Catalog matching conflicts: {len(conflicts)}')
        archived = archive_unlisted(active_ids)
        ensure_tags(Attraction.query.filter_by(catalog_status='active').all())
        excerpts = import_external_reviews()
        refresh_local_metrics(Attraction.query.all())
        print(f'Catalog: {len(active_ids)} active, {added} added, {updated} updated, {archived} archived')
        print(f'External review excerpts added: {excerpts}')


if __name__ == '__main__':
    main()
