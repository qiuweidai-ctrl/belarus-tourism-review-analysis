import requests
from config import Config


def analyze_sentiment(text: str) -> dict:
    prompt = (
        f"Analyze the sentiment of the following travel review and respond ONLY with a JSON object "
        f"with three fields: 'label' (one of: positive, neutral, negative), "
        f"'score' (a float from -1.0 to 1.0), and 'reason' (a short English phrase explaining why).\n\n"
        f"Review:\n{text}\n\n"
        f"Respond with JSON only, no explanation."
    )

    try:
        headers = {
            'Authorization': f'Bearer {Config.DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': 'deepseek-chat',
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.3,
            'max_tokens': 100
        }
        response = requests.post(Config.DEEPSEEK_API_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()
        content = result['choices'][0]['message']['content'].strip()

        import json
        parsed = json.loads(content)
        return {
            'label': parsed.get('label', 'neutral'),
            'score': float(parsed.get('score', 0.0)),
            'reason': parsed.get('reason', '')
        }
    except Exception as e:
        score = 0.0
        text_lower = text.lower()
        positive_words = ['amazing', 'beautiful', 'great', 'excellent', 'wonderful', 'fantastic', 'love', 'best', 'perfect', 'incredible']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'worst', 'boring', 'dirty', 'poor', 'disappointing', 'hate']

        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        total = pos_count + neg_count
        if total > 0:
            score = (pos_count - neg_count) / total
        else:
            score = 0.0

        if score > 0.2:
            label = 'positive'
        elif score < -0.2:
            label = 'negative'
        else:
            label = 'neutral'

        return {
            'label': label,
            'score': score,
            'reason': 'Fallback: keyword-based analysis'
        }
