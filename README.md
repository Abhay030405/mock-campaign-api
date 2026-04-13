# Mock Campaign API

A standalone FastAPI-based REST API for the **CampaignX Hackathon**. Simulates email campaign management and returns realistic, gamified performance metrics based on customer demographics, email content quality, and send timing.

## Features

- **Customer Cohort API** — Serve 5,000 customers from CSV with pagination and filtering
- **Campaign Scheduling** — Schedule email campaigns targeting customer segments
- **Realistic Metrics Simulation** — Open/click rates driven by:
  - Customer demographics (age, gender, occupation, credit score)
  - Email content quality (subject line, body, CTAs, formatting)
  - Send timing (day of week, time of day)
  - Random noise for natural variance
- **Content Analysis** — Detect emojis, spam patterns, urgency cues, personalization
- **Instant Results** — Metrics calculated immediately upon scheduling (no waiting)

## Tech Stack

- **Framework:** FastAPI
- **Server:** Uvicorn
- **Data Validation:** Pydantic v2
- **Data Processing:** Pandas
- **Config:** python-dotenv

## Local Setup

### Prerequisites

- Python 3.10+

### Installation

```bash
# Clone repository
git clone <repo-url>
cd mock-campaign-api

# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Copy or edit the `.env` file:

```
API_TITLE="Mock Campaign API"
API_VERSION="1.0.0"
API_KEY="your-secret-api-key-here"
HOST="0.0.0.0"
PORT=8000
```

### Add Customer Data

Place your `customers.csv` in `app/database/`. The CSV must have these columns:

```
customer_id, Full_name, email, Age, Gender, Marital_Status, Family_Size,
Dependent count, Occupation, Occupation_type, Monthly_Income, KYC status,
City, Kids_in_Household, App_Installed, Existing_Customer, Credit_score,
Social_Media_Active
```

### Run the API

```bash
# Option 1
python -m app.main

# Option 2
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## API Endpoints

### Health & Root

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check with customer count |

### Customers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/customers` | List customers (params: `limit`, `offset`) |
| GET | `/api/customers/count` | Total customer count |
| GET | `/api/customers/{customer_id}` | Get customer by ID |
| POST | `/api/customers/validate` | Validate customer IDs exist |

### Campaigns

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/campaigns/schedule` | Schedule a campaign (201) |
| GET | `/api/campaigns/{campaign_id}` | Campaign details + metrics |
| GET | `/api/campaigns/{campaign_id}/metrics` | Aggregated performance metrics |
| GET | `/api/campaigns/{campaign_id}/results` | Per-customer outcomes (param: `limit`) |

### Example: Schedule a Campaign

```bash
curl -X POST http://localhost:8000/api/campaigns/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "customer_ids": ["CUST_001", "CUST_002"],
    "subject": "🎉 Exclusive Offer: XDeposit - Higher Returns Await!",
    "body": "Discover <b>XDeposit</b>, our flagship term deposit offering <b>1% higher returns</b>. Click here: https://superbfsi.com/xdeposit/explore/ - Limited time!",
    "scheduled_time": "2026-04-15T10:00:00Z",
    "segment_name": "young_professionals",
    "variant_id": "var_1"
  }'
```

### Example: Get Metrics

```bash
curl http://localhost:8000/api/campaigns/<campaign_id>/metrics
```

Response:
```json
{
  "campaign_id": "...",
  "total_sent": 2,
  "unique_opens": 1,
  "unique_clicks": 0,
  "open_rate": 0.5,
  "click_rate": 0.0,
  "click_through_rate": 0.0,
  "calculated_at": "2026-04-13T..."
}
```

## Metrics Calculation Logic

| Factor | Open Rate Modifier | Click Rate Modifier |
|--------|--------------------|---------------------|
| **Base rate** | 35% | 8% |
| Age 18–25 | +5% | +3% |
| Age 26–40 | +3% | +2% |
| Age 56+ | −8% | −5% |
| Female, age 60+ | — | +10% |
| Social media active | +5% | +2% |
| Professional | +8% | — |
| App installed | — | +10% |
| Credit score > 750 | — | +5% |
| Good subject (40–60 chars) | +5% | — |
| Has CTA link | — | +10% |
| Tue/Wed send | +8% | +8% |
| 8–10 AM send | +10% | +10% |
| Spam detected | −15% | −10% |
| Random noise | ±3% | ±3% |

## Usage from Main CampaignX Project

```python
import requests

BASE_URL = "https://mock-campaign-api.onrender.com"

# Get customers
customers = requests.get(f"{BASE_URL}/api/customers", params={"limit": 50}).json()

# Schedule campaign
campaign = requests.post(f"{BASE_URL}/api/campaigns/schedule", json={
    "customer_ids": [c["customer_id"] for c in customers],
    "subject": "Special Offer on XDeposit!",
    "body": "Get 1% higher returns... https://example.com/offer",
    "scheduled_time": "2026-04-15T10:00:00Z",
    "segment_name": "test_segment",
    "variant_id": "var_1"
}).json()

# Get metrics
metrics = requests.get(
    f"{BASE_URL}/api/campaigns/{campaign['campaign_id']}/metrics"
).json()

print(f"Open Rate: {metrics['open_rate']*100:.1f}%")
print(f"Click Rate: {metrics['click_rate']*100:.1f}%")
```

## Deployment to Render

1. Push your code to a GitHub repository
2. Sign up at [render.com](https://render.com)
3. Create a new **Web Service** and connect your GitHub repo
4. Render auto-detects `render.yaml` and configures the service
5. Deploy — your API will be live at `https://mock-campaign-api.onrender.com`

**Notes:**
- Free tier sleeps after ~15 min of inactivity (first request takes ~30s to wake)
- `render.yaml` sets the region to Singapore — change if needed
- `API_KEY` is auto-generated by Render

## Project Structure

```
mock-campaign-api/
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── routers/
│   │   ├── customers.py         # Customer endpoints
│   │   └── campaigns.py         # Campaign endpoints
│   ├── services/
│   │   ├── customer_service.py  # Customer business logic
│   │   ├── campaign_service.py  # Campaign orchestration
│   │   └── metrics_calculator.py# Metrics simulation engine
│   ├── models/
│   │   └── schemas.py           # Pydantic models
│   ├── database/
│   │   ├── customers.csv        # Customer cohort data
│   │   ├── campaigns.json       # Stored campaigns
│   │   ├── results.json         # Per-customer outcomes
│   │   └── db_manager.py        # File-based data layer
│   └── utils/
│       ├── content_analyzer.py  # Email content scoring
│       └── probability_calculator.py  # Customer probability engine
├── test_api.py                  # Manual test script
├── requirements.txt
├── .env
├── render.yaml
└── README.md
```

## Testing

```bash
# Run the manual test script (server must be running)
python test_api.py
```

Or use the interactive Swagger UI at `/docs`.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `customers.csv not found` | Place your CSV in `app/database/` |
| `0 customers loaded` | Check CSV column names match the schema |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Render deploy fails | Check `render.yaml` and Python version |
| Slow first request on Render | Free tier cold start — wait ~30s |

## License

MIT

