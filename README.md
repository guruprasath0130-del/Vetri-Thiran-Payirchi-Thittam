# PocketSmart AI

Complete FastAPI + Jinja2 implementation of the supplied PocketSmart AI project specification.

The source document describes a modular FastAPI backend, Gemini-based recommendation layer, authentication/session routes, Home/Party/Jewelry planners, frontend templates, recommendation history, and fallback recommendations. The application implements those requirements in a runnable project.

## Requirements

- Python 3.11+
- VS Code
- Gemini API key for live AI mode (optional; fallback mode works without it)

## Setup — Windows

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Setup — macOS/Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Gemini

Edit `.env`:

```env
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-2.5-flash
```

The supplied document refers to Gemini 1.5 Flash Pro. Model availability can change, so this project makes the model configurable rather than assuming an old model ID.

## Testing

```bash
pytest -q
```

## API docs

`http://127.0.0.1:8000/docs`

## Main routes

- `/`
- `/register`
- `/login`
- `/dashboard`
- `/home-planner`
- `/party-planner`
- `/jewelry-planner`
- `/history-page`
- `/health`
- `POST /register`
- `POST /login`
- `POST /token`
- `POST /api/generate-home`
- `POST /api/generate-party`
- `POST /api/generate-jewelry`
- `GET /api/history`
- `GET /api/recommendations-details/{record_id}`
- `GET /session-info`
- `GET /session-data`
- `POST /logout`

## Marketplace integration

The application uses generated search links for Amazon, Flipkart, IKEA, Swiggy, Zomato and OYO. It does not claim to scrape or access private marketplace data.

For production, replace `app/services/catalog_service.py` with official APIs/affiliate feeds where available and permitted.

## Security notes

- Passwords are bcrypt hashed.
- JWT authentication protects recommendation/history APIs.
- Uploaded jewelry images are limited to configured size and supported image MIME types.
- Raw uploaded images are not saved in recommendation history.
- Use HTTPS, a strong `SECRET_KEY`, a production database and rate limiting when deploying.
