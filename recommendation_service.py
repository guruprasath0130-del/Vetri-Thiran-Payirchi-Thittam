import json
from sqlalchemy.orm import Session
from app.models.db_models import RecommendationHistory, User
from app.services.fallback_service import home_fallback, party_fallback, jewelry_fallback
from app.services.gemini_service import GeminiService


class RecommendationService:
    def __init__(self):
        self.ai = GeminiService()

    def generate(self, planner_type, data, db: Session, user: User, image_bytes=None, mime_type=None):
        fallbacks = {"home": home_fallback, "party": party_fallback, "jewelry": jewelry_fallback}
        result = self.ai.generate(planner_type, data, image_bytes, mime_type)
        if result is None:
            result = fallbacks[planner_type](data)

        record = RecommendationHistory(
            user_id=user.id,
            planner_type=planner_type,
            input_json=json.dumps(data, ensure_ascii=False),
            result_json=json.dumps(result, ensure_ascii=False),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        result["history_id"] = record.id
        result["ai_enabled"] = self.ai.enabled
        return result
