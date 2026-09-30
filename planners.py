import json
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.db_models import RecommendationHistory, User
from app.models.schemas import HomeRequest, PartyRequest, JewelryRequest
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/api")
service = RecommendationService()
settings = get_settings()


async def read_image(upload: UploadFile | None):
    if not upload:
        return None, None
    allowed = {"image/jpeg", "image/png", "image/webp"}
    if upload.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG or WebP images are supported.")
    data = await upload.read()
    if len(data) > settings.max_image_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"Image must be <= {settings.max_image_mb} MB.")
    return data, upload.content_type


@router.post("/generate-home")
def generate_home(payload: HomeRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.generate("home", payload.model_dump(), db, user)


@router.post("/generate-party")
def generate_party(payload: PartyRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.generate("party", payload.model_dump(), db, user)


@router.post("/generate-jewelry")
async def generate_jewelry(
    budget: float = Form(...),
    occasion: str = Form(...),
    style: str = Form("Elegant"),
    metal: str = Form("Any"),
    outfit_color: str = Form(""),
    notes: str = Form(""),
    outfit_image: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    payload = JewelryRequest(
        budget=budget,
        occasion=occasion,
        style=style,
        metal=metal,
        outfit_color=outfit_color,
        notes=notes,
    )
    image_bytes, mime_type = await read_image(outfit_image)
    return service.generate("jewelry", payload.model_dump(), db, user, image_bytes, mime_type)


@router.get("/history")
def history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(RecommendationHistory).filter(
        RecommendationHistory.user_id == user.id
    ).order_by(RecommendationHistory.created_at.desc()).all()
    return [
        {"id": r.id, "planner_type": r.planner_type, "created_at": r.created_at.isoformat()}
        for r in rows
    ]


@router.get("/recommendations-details/{record_id}")
def recommendation_details(record_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(RecommendationHistory).filter(
        RecommendationHistory.id == record_id,
        RecommendationHistory.user_id == user.id,
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return {
        "id": row.id,
        "planner_type": row.planner_type,
        "input": json.loads(row.input_json),
        "result": json.loads(row.result_json),
        "created_at": row.created_at.isoformat(),
    }
