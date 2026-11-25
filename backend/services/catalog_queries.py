from sqlalchemy import select, func

from models import Attraction, ExternalRating, db


# 查询时和详情页使用同一套评分来源规则。
def primary_rating_id():
    return select(ExternalRating.id).where(
        ExternalRating.attraction_id == Attraction.id,
        ExternalRating.score > 0, ExternalRating.scale > 0,
        ExternalRating.review_count > 0,
    ).order_by(
        ExternalRating.review_count.desc(), ExternalRating.retrieved_at.desc(),
        ExternalRating.id.desc(),
    ).limit(1).correlate(Attraction).scalar_subquery()


def rated_query(*columns):
    return db.session.query(*columns).select_from(Attraction).join(
        ExternalRating, ExternalRating.id == primary_rating_id()
    ).filter(Attraction.catalog_status == 'active')


def external_score():
    return ExternalRating.score * 5.0 / ExternalRating.scale


def global_mean():
    from services.catalog_cache import cached_catalog
    return cached_catalog('mean', lambda: float(rated_query(func.avg(external_score())).scalar() or 0))
