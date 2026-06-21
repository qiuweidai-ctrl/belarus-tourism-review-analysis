"""
Article (travel guide / blog) routes.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Article, ArticleLike, ArticleComment, db
from app import db as _db
from datetime import datetime

articles_bp = Blueprint('articles', __name__)


def _serialize_article(a, user_id=None):
    liked = False
    if user_id:
        liked = ArticleLike.query.filter_by(article_id=a.id, user_id=user_id).first() is not None
    return {
        'id': a.id,
        'user_id': a.user_id,
        'username': a.author.username if a.author else 'Unknown',
        'nickname': a.author.nickname if a.author else None,
        'attraction_id': a.attraction_id,
        'attraction_name': a.attraction.name if a.attraction else None,
        'title': a.title,
        'summary': a.summary,
        'content': a.content,
        'cover_image_url': a.cover_image_url,
        'tags': a.tags_json,
        'view_count': a.view_count or 0,
        'like_count': a.like_count or 0,
        'comment_count': a.comment_count or 0,
        'is_featured': bool(a.is_featured),
        'is_published': bool(a.is_published),
        'created_at': a.created_at.isoformat() if a.created_at else None,
        'published_at': a.published_at.isoformat() if a.published_at else None,
        'liked': liked
    }


@articles_bp.route('', methods=['GET'])
def list_articles():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    attraction_id = request.args.get('attraction_id', None, type=int)
    user_id = request.args.get('user_id', None, type=int)
    featured = request.args.get('featured', None, type=lambda x: x.lower() == 'true')

    query = Article.query.filter_by(status='published', is_published=True)
    if attraction_id:
        query = query.filter_by(attraction_id=attraction_id)
    if user_id:
        query = query.filter_by(user_id=user_id)
    if featured is not None:
        query = query.filter_by(is_featured=featured)

    pagination = query.order_by(Article.is_featured.desc(), Article.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    current_user = request.args.get('current_user_id', None, type=int)
    return jsonify({
        'articles': [_serialize_article(a, current_user) for a in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@articles_bp.route('/<int:article_id>', methods=['GET'])
def get_article(article_id):
    article = Article.query.get(article_id)
    if not article or article.status != 'published':
        return jsonify({'error': 'Article not found'}), 404

    article.view_count = (article.view_count or 0) + 1
    db.session.commit()

    user_id = None
    try:
        from flask_jwt_extended import get_jwt_identity
        user_id = int(get_jwt_identity())
    except Exception:
        pass

    return jsonify(_serialize_article(article, user_id)), 200


@articles_bp.route('', methods=['POST'])
@jwt_required()
def create_article():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data.get('title') or not data.get('content'):
        return jsonify({'error': 'title and content are required'}), 400

    article = Article(
        user_id=user_id,
        attraction_id=data.get('attraction_id'),
        title=data['title'],
        summary=data.get('summary', ''),
        content=data['content'],
        cover_image_url=data.get('cover_image_url'),
        tags_json=data.get('tags'),
        is_published=data.get('is_published', True),
        ip_address=request.remote_addr,
        published_at=datetime.utcnow() if data.get('is_published', True) else None
    )
    db.session.add(article)
    db.session.commit()

    return jsonify({'message': 'Article created', 'id': article.id}), 201


@articles_bp.route('/<int:article_id>', methods=['PUT'])
@jwt_required()
def update_article(article_id):
    user_id = int(get_jwt_identity())
    article = Article.query.get(article_id)
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    if article.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    for field in ['title', 'summary', 'content', 'cover_image_url', 'tags_json', 'is_published', 'is_featured']:
        if field in data:
            setattr(article, field, data[field])
    if data.get('is_published') and not article.published_at:
        article.published_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Article updated'}), 200


@articles_bp.route('/<int:article_id>', methods=['DELETE'])
@jwt_required()
def delete_article(article_id):
    user_id = int(get_jwt_identity())
    article = Article.query.get(article_id)
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    if article.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    article.status = 'deleted'
    article.deleted_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Article deleted'}), 200


@articles_bp.route('/<int:article_id>/like', methods=['POST'])
@jwt_required()
def like_article(article_id):
    user_id = int(get_jwt_identity())
    article = Article.query.get(article_id)
    if not article:
        return jsonify({'error': 'Article not found'}), 404

    existing = ArticleLike.query.filter_by(article_id=article_id, user_id=user_id).first()
    if existing:
        db.session.delete(existing)
        article.like_count = max(0, (article.like_count or 0) - 1)
        liked = False
    else:
        like = ArticleLike(article_id=article_id, user_id=user_id)
        db.session.add(like)
        article.like_count = (article.like_count or 0) + 1
        liked = True
    db.session.commit()
    return jsonify({'liked': liked, 'like_count': article.like_count}), 200


@articles_bp.route('/<int:article_id>/comments', methods=['GET'])
def list_comments(article_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = ArticleComment.query.filter_by(article_id=article_id).order_by(
        ArticleComment.created_at.asc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'comments': [{
            'id': c.id,
            'user_id': c.user_id,
            'username': c.user.username if c.user else 'Unknown',
            'content': c.content,
            'like_count': c.like_count or 0,
            'created_at': c.created_at.isoformat() if c.created_at else None
        } for c in pagination.items],
        'total': pagination.total
    }), 200


@articles_bp.route('/<int:article_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(article_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data.get('content'):
        return jsonify({'error': 'content is required'}), 400

    article = Article.query.get(article_id)
    if not article:
        return jsonify({'error': 'Article not found'}), 404

    comment = ArticleComment(
        article_id=article_id,
        user_id=user_id,
        parent_id=data.get('parent_id'),
        content=data['content']
    )
    db.session.add(comment)
    article.comment_count = (article.comment_count or 0) + 1
    db.session.commit()
    return jsonify({'id': comment.id, 'created_at': comment.created_at.isoformat()}), 201
