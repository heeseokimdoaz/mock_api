# TapaCross Mock API

## Why does this project exist?

We needed a **fully functional API server** that mimics the real TapaCross OracleEye API **before the production API became available** (target: 2026-02-23).

Instead of waiting for the real API, we built this mock so that:

- **Frontend and backend development can proceed in parallel** without being blocked by the external API timeline.
- **The contract (request/response format) is locked down early**, so integration on launch day is just switching one URL — no code changes needed.
- **Demos and testing** can happen at any time using realistic data converted from actual Excel exports.
- **New team members** can spin up the entire stack locally in one command (`docker-compose up`) and start contributing immediately.

The architecture is intentionally designed so that **the only change required to go live is updating the `TAPACROSS_API_URL` environment variable** from `http://mock-api:8000` to the real production endpoint.

---

## Architecture Overview

```
┌────────────────────┐     ┌──────────────────────┐     ┌────────────────────┐
│                    │     │                      │     │                    │
│   Frontend (UI)    │────▶│   Backend (:3000)    │────▶│  Mock API (:8000)  │
│   Chart.js + HTML  │     │   FastAPI + httpx     │     │  FastAPI + JSON    │
│                    │     │                      │     │                    │
└────────────────────┘     └──────────────────────┘     └────────────────────┘
        │                          │                            │
        │  Served as static        │  Proxies requests          │  Serves pre-loaded
        │  files from backend      │  to mock (or real) API     │  JSON data
        └──────────────────────────┴────────────────────────────┘
```

**Why a separate backend and mock-api?**

The backend acts as a **gateway/proxy layer**. It holds credentials (`client_id`, `search_id`) and translates simplified frontend requests into the full TapaCross API format. When we switch to production, the backend stays exactly the same — only the target URL changes.

---

## Quick Start

```bash
# Clone and run
git clone <repo-url>
cd mock_api
docker-compose up
```

That's it. Two containers will start:

| Service    | URL                     | Description                  |
|------------|-------------------------|------------------------------|
| **Frontend** | http://localhost:3000    | Web dashboard UI             |
| **Backend**  | http://localhost:3000/api | API proxy layer              |
| **Mock API** | http://localhost:8000    | Mock TapaCross OracleEye API |

---

## Swagger / API Documentation

FastAPI auto-generates interactive API docs:

| Docs | URL |
|------|-----|
| **Mock API - Swagger UI** | http://localhost:8000/docs |
| **Mock API - ReDoc** | http://localhost:8000/redoc |
| **Backend - Swagger UI** | http://localhost:3000/docs |
| **Backend - ReDoc** | http://localhost:3000/redoc |

You can test every endpoint directly from the Swagger UI — click "Try it out", fill in parameters, and execute.

---

## API Endpoints

### Mock API (port 8000)

#### `GET /v1/oracleye/trend`

Returns aggregated document counts per source type per day.

| Parameter   | Required | Format             | Description                                    |
|-------------|----------|--------------------|------------------------------------------------|
| `client_id` | Yes      | string             | API client identifier                          |
| `search_id` | Yes      | integer            | Search configuration ID                        |
| `from`      | Yes      | `yyyyMMddHHmmss`   | Start datetime                                 |
| `to`        | Yes      | `yyyyMMddHHmmss`   | End datetime                                   |
| `site_type` | No       | string             | Filter: `media`, `comm`, `twitter`, `youtube`  |

**Response:**
```json
{
  "status": "success",
  "data": [
    { "create_date": "20260208", "site_type": "media", "doc_count": 15 },
    { "create_date": "20260208", "site_type": "twitter", "doc_count": 42 }
  ]
}
```

#### `GET /v1/oracleye/doc`

Returns individual documents (articles, posts, tweets, videos).

| Parameter   | Required | Default | Description                                    |
|-------------|----------|---------|------------------------------------------------|
| `client_id` | Yes      | —       | API client identifier                          |
| `search_id` | Yes      | —       | Search configuration ID                        |
| `from`      | Yes      | —       | Start datetime (`yyyyMMddHHmmss`)              |
| `to`        | Yes      | —       | End datetime (`yyyyMMddHHmmss`)                |
| `site_type` | No       | —       | Filter: `media`, `comm`, `twitter`, `youtube`  |
| `offset`    | No       | `0`     | Pagination offset                              |
| `size`      | No       | `100`   | Results per page                               |

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "create_date": "20260208143022",
      "site_type": "media",
      "site_name": "KBS News",
      "title": "Article title here",
      "content": "Full article content...",
      "url": "https://...",
      "polarity": "0"
    }
  ]
}
```

> **Polarity values:** `"0"` = Neutral, `"1"` = Positive, `"2"` = Negative

### Backend (port 3000)

| Endpoint          | Description                     | Key Params                              |
|-------------------|---------------------------------|-----------------------------------------|
| `GET /api/trend`  | Trend data (simplified params)  | `from_date`, `to_date`, `site_type`     |
| `GET /api/documents` | Document list (paginated)    | `from_date`, `to_date`, `site_type`, `offset`, `size` |
| `GET /`           | Serves frontend static files    | —                                       |

---

## Project Structure

```
mock_api/
├── docker-compose.yml         # Orchestrates both services
├── Dockerfile.mock-api        # Mock API container (Python 3.12)
├── Dockerfile.backend         # Backend container (Python 3.12)
├── requirements.txt           # Shared Python dependencies
│
├── mock_api/                  # Mock API application
│   ├── main.py                # FastAPI app setup + CORS
│   ├── models.py              # Pydantic response models (TrendItem, DocItem)
│   ├── data_store.py          # Loads JSON data + query/filter logic
│   └── routers/
│       ├── trend.py           # GET /v1/oracleye/trend
│       └── doc.py             # GET /v1/oracleye/doc
│
├── backend/                   # Backend proxy application
│   ├── app.py                 # FastAPI app + static file serving
│   ├── api_client.py          # httpx client for mock API calls
│   └── config.py              # Environment-based configuration
│
├── frontend/                  # Web dashboard
│   ├── index.html             # Main UI (date picker, filters, table)
│   ├── js/app.js              # Chart.js trend graph + document table
│   └── css/style.css          # Styling
│
├── converter/                 # Data pipeline
│   └── convert_excel.py       # Excel → JSON converter
│
└── data/converted/            # Pre-converted mock data
    ├── trend_data.json        # Daily aggregated counts
    └── all_documents.json     # Individual documents
```

---

## Data Sources

Mock data is converted from 4 Excel files covering **2026-02-08 ~ 2026-02-12**:

| Source File         | `site_type` | Description            |
|---------------------|-------------|------------------------|
| X(트위터).xlsx       | `twitter`   | Twitter/X posts        |
| 매스미디어.xlsx       | `media`     | Mass media news        |
| 유튜브 스크립트.xlsx   | `youtube`   | YouTube video scripts  |
| 커뮤니티.xlsx         | `comm`      | Community forum posts  |

To regenerate JSON data from updated Excel files:

```bash
python converter/convert_excel.py
```

---

## Switching to Production

When the real TapaCross API is ready, update **one environment variable**:

```yaml
# docker-compose.yml
environment:
  - TAPACROSS_API_URL=https://real-tapacross-api.example.com  # was http://mock-api:8000
```

No code changes required. The backend proxy layer handles the rest.

---

## Tech Stack

| Layer     | Technology                  | Why                                              |
|-----------|-----------------------------|--------------------------------------------------|
| API       | FastAPI (Python 3.12)       | Auto-generates OpenAPI docs, async support, fast  |
| Server    | Uvicorn                     | High-performance ASGI server                     |
| HTTP Client | httpx                     | Async HTTP client for backend → API calls        |
| Charts    | Chart.js 4.4.7              | Simple, no-build-step charting                   |
| Frontend  | Vanilla HTML/CSS/JS         | Zero build complexity, easy to understand        |
| Container | Docker Compose              | One-command setup for the full stack             |
| Data      | openpyxl                    | Excel → JSON conversion pipeline                 |
