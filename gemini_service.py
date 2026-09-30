import json
import logging
from typing import Any

from google import genai
from google.genai import types

from app.config import get_settings
from app.services.catalog_service import enrich_item

logger = logging.getLogger(__name__)

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "budget": {"type": "number"},
        "estimated_total": {"type": "number"},
        "summary": {"type": "string"},
        "budget_breakdown": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "amount": {"type": "number"},
                },
                "required": ["category", "amount"],
            },
        },
        "recommendations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "category": {"type": "string"},
                    "estimated_price": {"type": "number"},
                    "quantity": {"type": "integer"},
                    "reason": {"type": "string"},
                    "platform": {"type": "string"},
                },
                "required": [
                    "title", "category", "estimated_price",
                    "quantity", "reason", "platform"
                ],
            },
        },
        "tips": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "title", "budget", "estimated_total", "summary",
        "budget_breakdown", "recommendations", "tips"
    ],
}


class GeminiService:
    def __init__(self):
        settings = get_settings()
        self.enabled = bool(settings.gemini_api_key)
        self.model = settings.gemini_model
        self.client = (
            genai.Client(api_key=settings.gemini_api_key)
            if self.enabled else None
        )

    def _prompt(self, planner_type: str, data: dict) -> str:
        common = """
You are PocketSmart AI, a budget-aware lifestyle recommendation assistant.
Return ONLY valid JSON matching the requested schema.
Do not invent live stock, exact current prices, ratings, reviews, or guaranteed availability.
All prices are estimates and must be treated as such.
Keep the estimated total at or below the user's budget whenever reasonably possible.
Use these platform names when useful: Amazon, Flipkart, IKEA, Swiggy, Zomato, OYO.
Do not claim that you directly accessed these platforms.
"""

        if planner_type == "home":
            domain = """
Planner: Home Interior.
Create a cost-conscious plan for the requested room, style, quantities and city.
Balance function, style and price.
"""
        elif planner_type == "party":
            domain = """
Planner: Party.
Allocate the budget across catering, venue, decoration and entertainment.
Consider guest count, city, event type, duration, food preference and venue preference.
"""
        else:
            domain = """
Planner: Jewelry.
Recommend coordinated jewelry for the occasion and style.
Consider outfit color, metal preference and notes.
If an image is supplied, use it only for broad visual coordination.
Do not identify the person in the image.
"""

        return common + domain + "\nUser data:\n" + json.dumps(
            data, ensure_ascii=False
        )

    def generate(
        self,
        planner_type: str,
        data: dict,
        image_bytes: bytes | None = None,
        mime_type: str | None = None,
    ) -> dict | None:
        if not self.enabled:
            return None

        try:
            parts: list[Any] = [self._prompt(planner_type, data)]

            if image_bytes and mime_type:
                parts.append(
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=mime_type,
                    )
                )

            response = self.client.models.generate_content(
                model=self.model,
                contents=parts,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=RESPONSE_SCHEMA,
                    temperature=0.35,
                ),
            )

            parsed = json.loads(response.text)
            budget = float(data["budget"])
            recommendations = [
                enrich_item(item)
                for item in parsed.get("recommendations", [])
            ]

            # Never allow AI output to report a total above the user budget.
            raw_total = sum(
                item["estimated_price"] * item.get("quantity", 1)
                for item in recommendations
            )
            total = round(min(raw_total, budget), 2)

            parsed.update(
                {
                    "planner_type": planner_type,
                    "budget": budget,
                    "estimated_total": total,
                    "remaining_budget": round(budget - total, 2),
                    "recommendations": recommendations,
                }
            )
            return parsed

        except Exception as exc:
            logger.exception("Gemini generation failed: %s", exc)
            return None
