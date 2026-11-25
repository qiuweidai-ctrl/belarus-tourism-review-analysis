# 保留平台作者、日期和链接，前端用这些字段展示出处。
def serialize_external_review(row):
    source_date = row.published_at.isoformat() if row.published_at else None
    date_kind = 'updated' if row.provider == 'Yandex Maps' else 'published'
    return {
        'id': row.id, 'attraction_id': row.attraction_id,
        'provider': row.provider, 'provider_poi_id': row.provider_poi_id,
        'provider_review_id': row.provider_review_id, 'author_name': row.author_name,
        'source_date': source_date, 'source_date_kind': date_kind,
        'published_at': source_date if date_kind == 'published' else None,
        'date_source': row.date_source, 'original_language': row.original_language,
        'excerpt': row.excerpt, 'is_truncated': row.is_truncated,
        'score': float(row.score) if row.score is not None else None,
        'scale': float(row.scale) if row.scale is not None else None,
        'source_url': row.source_url, 'retrieved_at': row.retrieved_at.isoformat(),
        'content_kind': 'external_review_excerpt',
    }
