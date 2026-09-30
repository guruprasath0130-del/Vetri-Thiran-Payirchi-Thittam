from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SessionInfo(BaseModel):
    authenticated: bool
    user_id: int | None = None
    email: str | None = None
    full_name: str | None = None


class HomeItem(BaseModel):
    category: str = Field(min_length=2, max_length=80)
    quantity: int = Field(default=1, ge=1, le=100)
    notes: str = Field(default="", max_length=300)


class HomeRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    room_type: str = Field(min_length=2, max_length=80)
    style: str = Field(default="Modern", max_length=80)
    city: str = Field(default="Chennai", max_length=80)
    items: list[HomeItem] = Field(min_length=1, max_length=30)


class PartyRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    event_type: str = Field(min_length=2, max_length=80)
    guests: int = Field(gt=0, le=10000)
    city: str = Field(default="Chennai", max_length=80)
    venue_preference: str = Field(default="Budget-friendly", max_length=100)
    food_preference: str = Field(default="Mixed", max_length=100)
    duration_hours: int = Field(default=4, ge=1, le=24)


class JewelryRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    occasion: str = Field(min_length=2, max_length=100)
    style: str = Field(default="Elegant", max_length=100)
    metal: str = Field(default="Any", max_length=50)
    outfit_color: str = Field(default="", max_length=80)
    notes: str = Field(default="", max_length=500)


class RecommendationItem(BaseModel):
    title: str
    category: str
    estimated_price: float
    quantity: int = 1
    reason: str
    platform: str
    search_url: str


class RecommendationResponse(BaseModel):
    planner_type: Literal["home", "party", "jewelry"]
    title: str
    budget: float
    estimated_total: float
    remaining_budget: float
    summary: str
    budget_breakdown: list[dict[str, Any]]
    recommendations: list[RecommendationItem]
    tips: list[str] = []


class HistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    planner_type: str
    created_at: str
