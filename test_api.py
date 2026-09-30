import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./test_pocketsmart.db"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["GEMINI_API_KEY"] = ""

from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def setup_module():
    path = Path("test_pocketsmart.db")
    if path.exists():
        path.unlink()
    # Importing the app does not require a request; lifespan initializes DB.


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_and_session():
    response = client.post(
        "/register",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    session = client.get(
        "/session-info",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert session.status_code == 200
    assert session.json()["email"] == "test@example.com"


def test_home_requires_auth():
    response = client.post(
        "/api/generate-home",
        json={
            "budget": 50000,
            "room_type": "Living Room",
            "style": "Modern",
            "city": "Chennai",
            "items": [{"category": "Sofa", "quantity": 1, "notes": ""}],
        },
    )
    assert response.status_code == 401


def test_home_fallback():
    login = client.post(
        "/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]

    response = client.post(
        "/api/generate-home",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "budget": 50000,
            "room_type": "Living Room",
            "style": "Modern",
            "city": "Chennai",
            "items": [
                {"category": "Sofa", "quantity": 1, "notes": ""},
                {"category": "Ceiling Light", "quantity": 2, "notes": ""},
            ],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["planner_type"] == "home"
    assert body["estimated_total"] <= body["budget"]
    assert len(body["recommendations"]) >= 1


def teardown_module():
    path = Path("test_pocketsmart.db")
    if path.exists():
        path.unlink()
