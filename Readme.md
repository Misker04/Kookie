# Kookie — Voice‑Controlled Smart Retail Store

Kookie is a voice-interactive “smart retail store” assistant that helps shoppers **find products**, **discover promotions**, **get recommendations**, **navigate store sections**, **ask support questions (returns/refunds)**, and **leave feedback**—all through natural language / voice-style commands.

This repository contains the Django-based web application that powers the core experience and integrates with Google Cloud Dialogflow for intent detection.


## Project context

**Course/Project:** DCSC Final Project — Voice-Controlled Smart Retail Store  

High-level goals:
- Voice-activated product search (e.g., “Find me a black shirt in size small”)
- Promotions/discount discovery (e.g., “What promotions do you have today?”)
- In-store navigation (e.g., “Take me to the clothing section”)
- Customer support Q&A (e.g., “How can I return a product?”)
- Feedback collection via voice/chat style interaction


## Architecture (high level)

**Voice/command flow:**
1. User speaks/types a command
2. Command is sent to the backend
3. Intent + entities are extracted via **Dialogflow**
4. Backend queries the database for products/promotions/sections/support content
5. Backend returns a response (optionally TTS in a full deployment)

**Core cloud components (as designed for the full system):**
- **Dialogflow** for NLU (intents/entities)
- **Google Cloud Speech-to-Text / Text-to-Speech** for voice input/output (full pipeline design)
- **Google Cloud SQL (PostgreSQL)** for structured store data (catalog, inventory, layouts, etc.)
- **Redis** for caching frequently requested results
- **Cloud Logging / Monitoring** for observability
- **Docker + Kubernetes (GKE)** for scalable deployment

> Note: This repo primarily includes the Django app and its Dialogflow integration. Some infrastructure elements (e.g., Redis, STT/TTS device pipeline) are part of the broader project design.


## What’s in this repo

Top-level structure (main):
- `smart_retail_store/` — Django project configuration
- `store/` — Django app with models + request handlers
- `manage.py` — Django CLI entrypoint
- `requirements.txt` — Python dependencies
- `build.sh` — helper script (install deps, collectstatic, migrate)
- `db.sqlite3` — a local SQLite DB snapshot (useful for quick local demo)


## Features (implemented in code)

### 1) Product Search
Supports commands like:
- `find me a black shirt in size small`

Backend queries the `Product` model by name/color/size and responds with matched items.

### 2) Promotions
Supports:
- `promotions`

Fetches currently active promotions using `start_date` / `end_date`.

### 3) Recommendations
Supports basic “suggest” flows for common use-cases:
- `suggest trekking shoes`
- `suggest running shoes`
- `suggest sports clothes`
- `suggest formal clothes`

Filters products by category and `use_case`.

### 4) Navigation (store sections)
Supports:
- `take me to the clothing section`

Looks up `StoreSection` records and returns a location/description.

### 5) Customer Support
Supports queries containing keywords like:
- `return`, `refund`

Fetches best matching `Support` record.

### 6) Feedback Collection
Supports multi-turn feedback:
- Start: `feedback`
- Then: user submits a comment message
- Stored in `Feedback`


## Data model

Defined in `store/models.py`:

- `Product`: name, description, category, size, color, price, stock, material, style, use_case
- `Promotion`: title, description, discount_percentage, start_date, end_date
- `StoreSection`: name, description, location
- `Support`: query, response
- `Feedback`: comments, created_at

## Getting started (local development)

### Prerequisites
- Python 3.10+ recommended
- (Optional) Google Cloud credentials for Dialogflow (only needed if you call `dialogflow_query`)

### 1) Clone
```bash
git clone https://github.com/Misker04/Kookie.git
cd Kookie
```

### 2) Create & activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Configure the database

This project includes **SQLite** (`db.sqlite3`) for quick local runs, but the `smart_retail_store/settings.py`
is currently configured to use **PostgreSQL / Cloud SQL**.

#### Option A (quickest): use SQLite locally
In `smart_retail_store/settings.py`, replace the `DATABASES = {...}` block with:
```python
DATABASES = {
  "default": {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": BASE_DIR / "db.sqlite3",
  }
}
```

#### Option B: use PostgreSQL (recommended for “real” deployment)
Set up a Postgres instance and configure Django using either:
- a `DATABASE_URL` environment variable (recommended), or
- direct `NAME/USER/PASSWORD/HOST/PORT` settings.

If you use Dialogflow, also set:
- `GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account.json`

> ⚠️ Security note: never commit real secrets/credentials. Use environment variables or secret managers.

### 5) Run migrations + start the server
```bash
python manage.py migrate
python manage.py runserver
```

Then open:
- http://127.0.0.1:8000/


## Usage examples

Try POSTing commands to the `process_command` endpoint (or use the UI, depending on how templates are wired):

- `find me a black shirt in size small`
- `promotions`
- `suggest trekking shoes`
- `take me to the clothing section`
- `return policy`
- `feedback` → then send your feedback message


## Testing & observability (project design)

The broader project design includes:
- Unit tests + integration tests + UAT
- Logging and monitoring via Google Cloud Logging/Monitoring
- Load/performance considerations and bottlenecks:
  - Speech-to-text latency under heavy concurrency
  - Database query performance on large inventories
  - Scaling microservices under high traffic

## Deployment notes

A full cloud deployment design includes containerization (Docker) and orchestration (Kubernetes/GKE), with API exposure secured via IAM/OAuth2/JWT and fronted by managed endpoints.

This repo also includes a `build.sh` script that performs:
- dependency install
- `collectstatic`
- `migrate`

If you deploy to a platform like Render/Heroku/GKE, adapt `ALLOWED_HOSTS`, `DEBUG`, and secrets accordingly.


## Acknowledgments

Built as a course project to explore practical voice+cloud integration for retail experiences.
