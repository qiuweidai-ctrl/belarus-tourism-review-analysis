"""
Q&A (Questions & Answers) routes for attractions.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Question, Answer, QuestionUpvote, AnswerUpvote, db
from datetime import datetime

qa_bp = Blueprint('qa', __name__)


@qa_bp.route('/questions', methods=['GET'])
def list_questions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    attraction_id = request.args.get('attraction_id', None, type=int)

    query = Question.query.filter_by(status='published')
    if attraction_id:
        query = query.filter_by(attraction_id=attraction_id)

    pagination = query.order_by(Question.has_accepted_answer.desc(), Question.upvote_count.desc(), Question.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'questions': [{
            'id': q.id,
            'user_id': q.user_id,
            'username': q.author.username if q.author else 'Unknown',
            'nickname': q.author.nickname if q.author else None,
            'attraction_id': q.attraction_id,
            'attraction_name': q.attraction.name if q.attraction else None,
            'title': q.title,
            'content': q.content,
            'view_count': q.view_count or 0,
            'answer_count': q.answer_count or 0,
            'upvote_count': q.upvote_count or 0,
            'has_accepted_answer': bool(q.has_accepted_answer),
            'created_at': q.created_at.isoformat() if q.created_at else None
        } for q in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@qa_bp.route('/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    question = Question.query.get(question_id)
    if not question or question.status != 'published':
        return jsonify({'error': 'Question not found'}), 404

    question.view_count = (question.view_count or 0) + 1
    db.session.commit()

    return jsonify({
        'id': question.id,
        'user_id': question.user_id,
        'username': question.author.username if question.author else 'Unknown',
        'attraction_id': question.attraction_id,
        'title': question.title,
        'content': question.content,
        'view_count': question.view_count,
        'answer_count': question.answer_count or 0,
        'upvote_count': question.upvote_count or 0,
        'has_accepted_answer': bool(question.has_accepted_answer),
        'created_at': question.created_at.isoformat() if question.created_at else None
    }), 200


@qa_bp.route('/questions', methods=['POST'])
@jwt_required()
def create_question():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data.get('title') or not data.get('attraction_id'):
        return jsonify({'error': 'title and attraction_id are required'}), 400

    question = Question(
        user_id=user_id,
        attraction_id=data['attraction_id'],
        title=data['title'],
        content=data.get('content', ''),
        ip_address=request.remote_addr
    )
    db.session.add(question)
    db.session.commit()
    return jsonify({'message': 'Question created', 'id': question.id}), 201


@qa_bp.route('/questions/<int:question_id>/upvote', methods=['POST'])
@jwt_required()
def upvote_question(question_id):
    user_id = int(get_jwt_identity())
    question = Question.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404

    existing = QuestionUpvote.query.filter_by(question_id=question_id, user_id=user_id).first()
    if existing:
        db.session.delete(existing)
        question.upvote_count = max(0, (question.upvote_count or 0) - 1)
        upvoted = False
    else:
        upvote = QuestionUpvote(question_id=question_id, user_id=user_id)
        db.session.add(upvote)
        question.upvote_count = (question.upvote_count or 0) + 1
        upvoted = True
    db.session.commit()
    return jsonify({'upvoted': upvoted, 'upvote_count': question.upvote_count}), 200


@qa_bp.route('/questions/<int:question_id>/answers', methods=['GET'])
def list_answers(question_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = Answer.query.filter_by(question_id=question_id, status='published').order_by(
        Answer.is_accepted.desc(), Answer.upvote_count.desc(), Answer.created_at.asc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'answers': [{
            'id': a.id,
            'user_id': a.user_id,
            'username': a.author.username if a.author else 'Unknown',
            'content': a.content,
            'upvote_count': a.upvote_count or 0,
            'is_accepted': bool(a.is_accepted),
            'created_at': a.created_at.isoformat() if a.created_at else None
        } for a in pagination.items],
        'total': pagination.total
    }), 200


@qa_bp.route('/questions/<int:question_id>/answers', methods=['POST'])
@jwt_required()
def create_answer(question_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data.get('content'):
        return jsonify({'error': 'content is required'}), 400

    question = Question.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404

    answer = Answer(
        question_id=question_id,
        user_id=user_id,
        content=data['content']
    )
    db.session.add(answer)
    question.answer_count = (question.answer_count or 0) + 1
    db.session.commit()
    return jsonify({'message': 'Answer created', 'id': answer.id}), 201


@qa_bp.route('/answers/<int:answer_id>/upvote', methods=['POST'])
@jwt_required()
def upvote_answer(answer_id):
    user_id = int(get_jwt_identity())
    answer = Answer.query.get(answer_id)
    if not answer:
        return jsonify({'error': 'Answer not found'}), 404

    existing = AnswerUpvote.query.filter_by(answer_id=answer_id, user_id=user_id).first()
    if existing:
        db.session.delete(existing)
        answer.upvote_count = max(0, (answer.upvote_count or 0) - 1)
        upvoted = False
    else:
        upvote = AnswerUpvote(answer_id=answer_id, user_id=user_id)
        db.session.add(upvote)
        answer.upvote_count = (answer.upvote_count or 0) + 1
        upvoted = True
    db.session.commit()
    return jsonify({'upvoted': upvoted, 'upvote_count': answer.upvote_count}), 200


@qa_bp.route('/answers/<int:answer_id>/accept', methods=['POST'])
@jwt_required()
def accept_answer(answer_id):
    user_id = int(get_jwt_identity())
    answer = Answer.query.get(answer_id)
    if not answer:
        return jsonify({'error': 'Answer not found'}), 404

    question = Question.query.get(answer.question_id)
    if question.user_id != user_id:
        return jsonify({'error': 'Only the question author can accept an answer'}), 403

    # Unaccept all other answers
    Answer.query.filter_by(question_id=question.id, is_accepted=True).update({'is_accepted': False})
    answer.is_accepted = True
    question.has_accepted_answer = True
    db.session.commit()
    return jsonify({'message': 'Answer accepted'}), 200
