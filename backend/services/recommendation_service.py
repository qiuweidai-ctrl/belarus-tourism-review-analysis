import requests
import json
from config import Config


class RecommendationService:
    """
    Business logic layer for AI-powered attraction recommendations.
    Uses DeepSeek API to generate personalized recommendations based on user history.
    """
    MODEL = 'deepseek-chat'
    TIMEOUT = 15

    def get_recommendations(self, user_id: int, rated_attraction_ids: list,
                           all_attractions: list, limit: int = 5) -> list:
        if not all_attractions:
            return []

        candidates = [a for a in all_attractions if a.id not in rated_attraction_ids]
        if not candidates:
            candidates = all_attractions[:limit]
        if len(candidates) <= limit:
            return self._build_fallback_recs(candidates, 'Popular choice')

        try:
            return self._ai_recommend(user_id, candidates, limit)
        except Exception:
            return self._build_fallback_recs(candidates[:limit], 'Top rated by users')

    def _ai_recommend(self, user_id: int, candidates: list, limit: int) -> list:
        rated_info = self._get_user_rating_context(user_id)

        prompt_text = "You are a travel recommendation assistant for Belarus tourism.\n"
        if rated_info:
            prompt_text += "The user has rated these attractions:\n" + "\n".join(rated_info) + "\n\n"
        else:
            prompt_text += "The user has no rating history yet.\n\n"

        prompt_text += f"Based on this user's preferences, recommend exactly {limit} attractions from this list:\n"
        for a in candidates[:20]:
            prompt_text += (f"- ID:{a.id} | {a.name} in {a.location} "
                            f"(avg rating: {float(a.avg_rating or 0):.1f}, "
                            f"reviews: {a.total_reviews or 0}, category: {a.category})\n")

        prompt_text += (
            f"\nRespond ONLY with a JSON array (no markdown, no explanation) with exactly {limit} items.\n"
            "Each item must have: {{\"id\": number, \"reason\": \"1-2 sentence reason in English\"}}"
        )

        headers = {
            'Authorization': f'Bearer {Config.DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': self.MODEL,
            'messages': [{'role': 'user', 'content': prompt_text}],
            'temperature': 0.7,
            'max_tokens': 300
        }

        response = requests.post(
            Config.DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=self.TIMEOUT
        )
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content'].strip()
        recs = json.loads(content)

        attraction_map = {a.id: a for a in candidates}
        result = []
        for rec in recs:
            aid = rec.get('id')
            if aid in attraction_map:
                a = attraction_map[aid]
                result.append(self._format_attraction(a, rec.get('reason', 'Recommended for you')))

        if not result:
            raise ValueError('No valid recommendations parsed')
        return result

    def predict_rating(self, user_id: int, attraction_id: int,
                      attraction_name: str, attraction_avg: float,
                      user_history: list) -> dict:
        if not user_history:
            return {
                'predicted_rating': round(float(attraction_avg), 2),
                'method': 'attraction_avg',
                'reason': 'Based on average rating of this attraction'
            }
        try:
            return self._ai_predict(attraction_name, attraction_avg, user_history)
        except Exception:
            return self._statistical_predict(user_history, float(attraction_avg))

    def _ai_predict(self, attraction_name: str, attraction_avg: float,
                    user_history: list) -> dict:
        lines = [f"- You rated '{h['name']}' {h['score']}/5" for h in user_history]
        prompt = (
            "Based on the user's rating history:\n" + "\n".join(lines) + "\n\n"
            f"Estimate the user's likely rating (1-5) for '{attraction_name}' "
            f"(currently avg rated {float(attraction_avg):.1f}).\n\n"
            "Respond with ONLY JSON: {\"predicted_rating\": float, \"reason\": string}"
        )

        headers = {
            'Authorization': f'Bearer {Config.DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': self.MODEL,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.3,
            'max_tokens': 80
        }

        response = requests.post(
            Config.DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=self.TIMEOUT
        )
        response.raise_for_status()
        parsed = json.loads(response.json()['choices'][0]['message']['content'].strip())
        predicted = max(1.0, min(5.0, float(parsed.get('predicted_rating', attraction_avg))))
        return {
            'predicted_rating': round(predicted, 2),
            'method': 'ai_prediction',
            'reason': parsed.get('reason', '')
        }

    def _statistical_predict(self, user_history: list, attraction_avg: float) -> dict:
        avg_user = sum(h['score'] for h in user_history) / len(user_history)
        diff = avg_user - 3.0
        predicted = max(1.0, min(5.0, attraction_avg + diff * 0.5))
        return {
            'predicted_rating': round(predicted, 2),
            'method': 'statistical_fallback',
            'reason': 'Based on your rating tendency vs average'
        }

    def _build_fallback_recs(self, attractions: list, reason: str) -> list:
        sorted_att = sorted(
            attractions,
            key=lambda a: float(a.avg_rating or 0) * (a.total_reviews or 0 + 1),
            reverse=True
        )
        return [self._format_attraction(a, reason) for a in sorted_att]

    def _format_attraction(self, a, reason: str = '') -> dict:
        return {
            'id': a.id,
            'name': a.name,
            'location': a.location,
            'category': a.category,
            'avg_rating': round(float(a.avg_rating or 0), 2),
            'description': a.short_desc or (a.description or '')[:150],
            'image_url': a.image_url,
            'reason': reason
        }

    def _get_user_rating_context(self, user_id: int) -> list:
        from repositories import RatingRepository, AttractionRepository
        rating_repo = RatingRepository()
        att_repo = AttractionRepository()
        ratings = rating_repo.get_user_ratings(user_id)
        att_map = {a.id: a for a in att_repo.get_all(limit=1000)}
        result = []
        for r in ratings:
            a = att_map.get(r.attraction_id)
            if a:
                result.append(f"- {a.name} (rating: {r.score}/5)")
        return result
