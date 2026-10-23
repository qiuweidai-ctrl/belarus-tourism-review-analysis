
import numpy as np
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import re
from models import db, Review, Attraction
from datetime import datetime

SENTENCES_COUNT = 3


def calculate_review_quality(review: Review) -> dict:
    content = review.content or ""

    length_score = calculate_length_score(content)

    info_score = calculate_information_score(content)

    sentiment_score = calculate_sentiment_intensity(review.sentiment_score)

    helpful_score = min(review.helpful_count / 20.0, 1.0)

    weights = {
        'length': 0.15,
        'information': 0.30,
        'sentiment': 0.20,
        'helpfulness': 0.35
    }

    final_score = (
        length_score * weights['length'] +
        info_score * weights['information'] +
        sentiment_score * weights['sentiment'] +
        helpful_score * weights['helpfulness']
    )

    quality_score = round(final_score * 100, 2)

    if quality_score >= 80:
        grade = 'A'
        label = 'Excellent'
    elif quality_score >= 60:
        grade = 'B'
        label = 'Good'
    elif quality_score >= 40:
        grade = 'C'
        label = 'Fair'
    else:
        grade = 'D'
        label = 'Needs improvement'

    return {
        'quality_score': quality_score,
        'grade': grade,
        'label': label,
        'breakdown': {
            'length_score': round(length_score * 100, 2),
            'information_score': round(info_score * 100, 2),
            'sentiment_score': round(sentiment_score * 100, 2),
            'helpfulness_score': round(helpful_score * 100, 2)
        }
    }


def calculate_length_score(content: str) -> float:
    length = len(content)

    if length < 50:
        return length / 50.0 * 0.3
    elif length < 200:
        return 0.3 + (length - 50) / 150.0 * 0.4
    elif length <= 500:
        return 0.7 + (length - 200) / 300.0 * 0.3
    else:
        return min(1.0, 0.9 + (500 - length) / 500.0 * 0.1)


def calculate_information_score(content: str) -> float:
    if not content:
        return 0.0

    score = 0.0

    adjectives = len(re.findall(r'\b(beautiful|stunning|amazing|wonderful|great|good|bad|awful|terrible|excellent|lovely|nice|fantastic|awesome)\b', content.lower()))
    score += min(adjectives / 5.0, 0.3)

    numbers = len(re.findall(r'\b\d+\b', content))
    score += min(numbers / 3.0, 0.2)

    proper_nouns = len(re.findall(r'\b[A-Z][a-z]+\b', content))
    score += min(proper_nouns / 5.0, 0.2)

    sentences = len(re.split(r'[.!?]+', content))
    if 3 <= sentences <= 10:
        score += 0.2
    elif sentences < 3:
        score += sentences / 3.0 * 0.2
    else:
        score += max(0, 0.2 - (sentences - 10) / 20.0 * 0.2)

    exclamations = content.count('!') + content.count('?')
    score += min(exclamations / 3.0, 0.1)

    return min(score, 1.0)


def calculate_sentiment_intensity(sentiment_score: float) -> float:
    if sentiment_score is None:
        return 0.5

    intensity = abs(float(sentiment_score))

    return min(intensity, 1.0)


def generate_attraction_summary(attraction_id: int) -> str:
    reviews = Review.query.filter_by(
        attraction_id=attraction_id,
        status='published'
    ).order_by(Review.rating.desc()).limit(20).all()

    if not reviews:
        return ""

    combined_text = "\n".join([r.content for r in reviews if r.content])

    if len(combined_text) < 100:
        return reviews[0].content[:200] if reviews[0].content else ""

    try:
        language = 'english'
        stemmer = Stemmer(language)
        summarizer = TextRankSummarizer(stemmer)
        summarizer.stop_words = get_stop_words(language)

        parser = PlaintextParser.from_string(combined_text, Tokenizer(language))

        summary_sentences = summarizer(parser.document, SENTENCES_COUNT)

        if summary_sentences:
            return " ".join([str(sentence) for sentence in summary_sentences])
        else:
            return reviews[0].content[:200]

    except Exception as e:
        return reviews[0].content[:200] if reviews[0].content else ""


def extract_key_sentences(reviews: list, top_n: int = 5) -> list:
    if not reviews:
        return []

    all_sentences = []
    for review in reviews:
        if review.content:
            sentences = re.split(r'[.!?]+', review.content)
            for sent in sentences:
                sent = sent.strip()
                if len(sent) > 30:
                    all_sentences.append({
                        'text': sent,
                        'rating': review.rating,
                        'helpful': review.helpful_count
                    })

    if not all_sentences:
        return []

    scored_sentences = []
    for s in all_sentences:
        score = s['rating'] / 5.0 * 0.6 + min(s['helpful'] / 10.0, 0.4)
        scored_sentences.append((s['text'], score))

    scored_sentences.sort(key=lambda x: x[1], reverse=True)

    selected = []
    seen_texts = set()

    for text, score in scored_sentences:
        is_duplicate = False
        for existing in selected:
            common_words = set(text.lower().split()) & set(existing.lower().split())
            if len(common_words) / len(set(text.lower().split())) > 0.5:
                is_duplicate = True
                break

        if not is_duplicate:
            selected.append(text)
            if len(selected) >= top_n:
                break

    return selected


def batch_calculate_quality(review_ids: list = None) -> dict:
    if review_ids:
        reviews = Review.query.filter(Review.id.in_(review_ids)).all()
    else:
        reviews = Review.query.filter_by(
            ai_processed=False,
            status='published'
        ).limit(100).all()

    results = {}
    for review in reviews:
        quality = calculate_review_quality(review)
        results[review.id] = quality

        review.ai_processed = True

    db.session.commit()

    return results


def get_top_quality_reviews(attraction_id: int, limit: int = 5) -> list:
    reviews = Review.query.filter_by(
        attraction_id=attraction_id,
        status='published',
        ai_processed=True
    ).order_by(Review.helpful_count.desc()).limit(limit * 2).all()

    scored_reviews = []
    for review in reviews:
        quality = calculate_review_quality(review)
        scored_reviews.append({
            'review_id': review.id,
            'quality': quality,
            'review': {
                'id': review.id,
                'user_id': review.user_id,
                'author': review.author.username if review.author else 'Anonymous',
                'content': review.content[:300],
                'rating': review.rating,
                'helpful_count': review.helpful_count,
                'created_at': review.created_at.isoformat()
            }
        })

    scored_reviews.sort(key=lambda x: x['quality']['quality_score'], reverse=True)

    return scored_reviews[:limit]
