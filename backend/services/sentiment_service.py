import requests
import time
from config import Config


class SentimentService:
    """
    Business logic layer for AI sentiment analysis.
    Handles DeepSeek API calls and fallback mechanism.
    """
    MODEL = 'deepseek-chat'
    TIMEOUT = 15

    def analyze(self, text: str) -> dict:
        """
        Analyze sentiment of the given text.
        Returns dict with label, score, reason, and method.
        """
        start_time = time.time()

        try:
            result = self._call_deepseek(text)
            elapsed_ms = int((time.time() - start_time) * 1000)
            result['processing_time_ms'] = elapsed_ms
            result['method'] = 'deepseek_api'
            return result
        except Exception as e:
            result = self._fallback_analysis(text)
            elapsed_ms = int((time.time() - start_time) * 1000)
            result['processing_time_ms'] = elapsed_ms
            result['method'] = 'fallback_keyword'
            return result

    def _call_deepseek(self, text: str) -> dict:
        prompt = (
            "You are a travel review sentiment analyzer. "
            "Analyze the following review and respond ONLY with a valid JSON object with exactly these fields:\n"
            "  - \"label\": one of \"positive\", \"neutral\", \"negative\" (string)\n"
            "  - \"score\": a float from -1.0 (very negative) to 1.0 (very positive) (number)\n"
            "  - \"reason\": a short English phrase explaining your classification (string)\n\n"
            f"Review text:\n{text}\n\n"
            "Respond with JSON only, no markdown, no explanation."
        )

        headers = {
            'Authorization': f'Bearer {Config.DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': self.MODEL,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.3,
            'max_tokens': 120
        }

        response = requests.post(
            Config.DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=self.TIMEOUT
        )
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content'].strip()

        import json
        parsed = json.loads(content)

        return {
            'label': parsed.get('label', 'neutral'),
            'score': float(parsed.get('score', 0.0)),
            'reason': parsed.get('reason', ''),
            'raw_response': parsed,
            'status': 'success',
            'model': self.MODEL
        }

    def _fallback_analysis(self, text: str) -> dict:
        """Keyword-based fallback when DeepSeek API is unavailable."""
        text_lower = text.lower()
        positive_words = {
            'amazing': 0.8, 'beautiful': 0.7, 'great': 0.6, 'excellent': 0.9,
            'wonderful': 0.8, 'fantastic': 0.9, 'love': 0.7, 'best': 0.8,
            'perfect': 0.9, 'incredible': 0.9, 'awesome': 0.8, 'nice': 0.5,
            'good': 0.4, 'pleasant': 0.5, 'stunning': 0.8, 'breathtaking': 0.8,
            'recommend': 0.6, 'lovely': 0.6, 'impressive': 0.7, 'memorable': 0.7
        }
        negative_words = {
            'bad': -0.5, 'terrible': -0.9, 'awful': -0.9, 'horrible': -0.9,
            'worst': -0.8, 'boring': -0.5, 'dirty': -0.6, 'poor': -0.5,
            'disappointing': -0.7, 'hate': -0.8, 'disgusting': -0.9,
            'overpriced': -0.6, 'crowded': -0.3, 'rude': -0.7, 'dangerous': -0.7,
            'expensive': -0.4, 'bland': -0.4, 'mediocre': -0.3, 'avoid': -0.6
        }

        pos_score = sum(
            score for word, score in positive_words.items() if word in text_lower
        )
        neg_score = sum(
            abs(score) for word, score in negative_words.items() if word in text_lower
        )

        raw = pos_score - neg_score
        norm = max(-1.0, min(1.0, raw)) if (pos_score + neg_score) > 0 else 0.0

        if norm > 0.2:
            label = 'positive'
        elif norm < -0.2:
            label = 'negative'
        else:
            label = 'neutral'

        return {
            'label': label,
            'score': round(norm, 3),
            'reason': 'Fallback: keyword-based sentiment analysis',
            'raw_response': None,
            'status': 'fallback',
            'model': 'fallback_keyword'
        }
