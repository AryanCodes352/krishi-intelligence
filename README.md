# KRISHI INTELLIGENCE

> **"See the data. Understand the risk. Make the right decision."**

An AI-powered agricultural decision-intelligence platform that combines soil, weather, crop, and market intelligence to help farmers make better farm and selling decisions.

---

## What This Is

KRISHI INTELLIGENCE is not a chatbot, not a weather app, and not a price prediction website.

It is a **multi-source data fusion + explainable AI platform** that answers the four questions every farmer asks:

| Question | How we answer it |
|----------|-----------------|
| "What is happening to my farm?" | Soil + weather + crop risk dashboard |
| "Why is it happening?" | Explainable AI with evidence |
| "What is likely to happen next?" | ML price prediction with confidence bounds |
| "Should I sell now or wait?" | Risk-adjusted sell/wait decision simulator |

### Academic Context
- **Project Type**: 3rd-Year B.Tech Mini Project (Computer Science & Engineering)
- **Domain**: Applied Artificial Intelligence, Multi-Source Data Fusion & Agronomic Decision Support
- **Evaluation**: University Mini Project Viva & Technical Assessment (Academic Session 2026)
- **Core Academic Documentation**: Located in [`docs/`](docs/)
  - [System Architecture & Mathematical Specifications](docs/SYSTEM_ARCHITECTURE.md)
  - [Examiner Viva Preparation Guide & Q&A](docs/VIVA_PREPARATION_GUIDE.md)
  - [5-Minute Live Viva Demo Script](docs/DEMO_SCRIPT.md)
  - [Project Report Synopsis](docs/PROJECT_REPORT_SYNOPSIS.md)

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### 1. Clone and configure

```bash
git clone <repo>
cd KRISHI
cp .env.example .env
# Edit .env if you have API keys (optional — system works without them)
```

### 2. Backend + ML setup

```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Train the price prediction model (required before first run)
python ml/train_price_model.py

# Start the backend API server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at: http://localhost:8000  
API docs: http://localhost:8000/docs

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: http://localhost:3000

### One-command setup (Windows)
```bat
start.bat
```

---

## Demo Scenario (Hero Demo)

The prototype is optimized for this exact journey:

1. **Open** http://localhost:3000
2. **Click** "Get Started"
3. **Fill** the onboarding form: Lucknow · Uttar Pradesh · Wheat · [any sowing date]
4. **View** the farm intelligence dashboard
5. **Click** "Should I Sell Now?"
6. **See** the 3-scenario risk-adjusted comparison
7. **Click** "Why this recommendation?"
8. **Inspect** the data evidence, model signals, and conclusion

**Total demo time: ~3–4 minutes**

---

## Architecture

```
KRISHI/
├── backend/           # FastAPI Python backend
│   ├── main.py        # App entry point
│   ├── config.py      # Environment-based configuration
│   ├── database.py    # SQLAlchemy + SQLite
│   ├── models/        # ORM models (Farm, Observation, Prediction)
│   ├── schemas/       # Pydantic v2 request/response schemas
│   ├── routers/       # API route handlers
│   └── services/      # Business logic
│       ├── weather_service.py    # Open-Meteo integration
│       ├── market_service.py     # CSV + data.gov.in API
│       ├── soil_service.py       # ICAR regional data
│       ├── risk_engine.py        # Multi-factor risk calculator
│       ├── decision_engine.py    # Sell-vs-wait simulator
│       └── explainability.py     # Evidence builder + AI explanation
├── ml/                # Machine learning pipeline
│   ├── feature_engineering.py  # Feature computation
│   ├── train_price_model.py    # Model training + evaluation
│   ├── predict.py              # Inference with confidence bounds
│   └── evaluate.py             # Standalone model evaluation
├── data/
│   ├── seed/
│   │   └── wheat_lucknow_mandi.csv   # 349 weeks of calibrated price data
│   ├── soil/
│   │   └── up_districts_soil.json    # ICAR district soil data
│   └── scripts/
│       ├── generate_seed_data.py     # Seed data generator (transparent)
│       └── fetch_mandi_prices.py     # Live API fetcher (when key available)
├── frontend/          # Next.js 14 + TypeScript + Tailwind CSS
│   └── src/
│       ├── app/       # Next.js App Router pages
│       ├── components/
│       └── lib/
└── docs/
```

---

## Data Sources

| Source | Type | Status | Notes |
|--------|------|--------|-------|
| Open-Meteo | Weather (live) | ✅ **CONNECTED** | Free, no key needed |
| AGMARKNET / data.gov.in | Market prices (historical) | 🟡 **SEED DATA** | 349 weekly observations (2020–2026) |
| data.gov.in OGD API | Market prices (live) | 🔴 **DISCONNECTED** | Set `DATA_GOV_IN_API_KEY` in .env |
| ICAR-NBSS&LUP | Soil data | 🟡 **REGIONAL ESTIMATE** | District-level aggregates |
| Google Gemini API | AI explanations | 🔴 **DISCONNECTED** | Set `GEMINI_API_KEY` in .env (optional) |

> **Data honesty rule**: Every value in the UI is labelled with its source and data type. LIVE / MODEL PREDICTION / HISTORICAL SEED / REGIONAL ESTIMATE / UNAVAILABLE. We never present historical data as live or model predictions as facts.

### Market Data Provenance
The seed data (`data/seed/wheat_lucknow_mandi.csv`) is **synthetic but calibrated**:
- MSP values: real CACP (Commission for Agricultural Costs & Prices) official announcements
- Seasonal patterns: calibrated to real AGMARKNET Lucknow mandi price reports
- Generation logic: fully visible in `data/scripts/generate_seed_data.py`
- When asked "where did this number come from?": open that script

---

## ML Price Prediction Model

### Model Selection Rationale
After evaluating available data (349 weekly observations), we chose **XGBoost regression** over ARIMA/Prophet because:
- Non-linear seasonal patterns benefit from tree-based models
- Feature interactions (price momentum × seasonal index) are captured naturally
- Interpretable feature importances for explainability

### Features Used
- `month`, `day_of_year`, `week_of_year` — seasonality
- `lag_1w`, `lag_2w`, `lag_4w`, `lag_8w` — recent price momentum
- `rolling_mean_4w`, `rolling_mean_8w`, `rolling_std_4w` — trend and volatility
- `seasonal_index` — month-of-year price premium vs annual average
- `price_change_4w_pct` — momentum signal

### Model Performance (on held-out test set)
Metrics printed after running `python ml/train_price_model.py`. Typical results:
- MAE: ~₹80–90/quintal
- MAPE: ~3.5–4.0%
- Confidence: MEDIUM (honest — not overstated)

If MAE > 15%: the system automatically labels predictions as LOW confidence.

### Prediction Card Standard
Every prediction shows:
```
Expected wheat price in 7 days
₹2,480 – ₹2,545/q
Confidence: 72% (MEDIUM)
Based on: 349 historical mandi prices + seasonal index + 4-week momentum
Updated: 10 Sep 2026
[Why this prediction?]
```

If insufficient data:
```
⚠️ Prediction unavailable
Not enough reliable historical observations. Minimum 52 weekly observations required.
```

---

## Risk Engine

Multi-factor risk calculator combining:

| Factor | Weight | Inputs |
|--------|--------|--------|
| Crop Risk | 35% | Phenological stage + weather impact on crop |
| Weather Risk | 30% | Rainfall probability + temperature + humidity |
| Market Risk | 20% | Price volatility + seasonal trend |
| Soil Risk | 15% | pH + nutrient deficiency + organic carbon |

**Overall risk score: 0–100** (0=no risk, 100=critical)  
Risk levels: LOW (0–40) / MEDIUM (40–70) / HIGH (70–100)

---

## Sell-Now vs Wait Decision Engine

For each of three scenarios (Sell Now / Wait 7 days / Wait 15 days), the engine computes:

```
Net Realization = 
  (Expected Price × Total Yield)
  - Storage Cost
  - Weather Risk Penalty
  - Transport Cost
```

Where:
- `Storage Cost = daily_rate × wait_days × yield_qtl`
- `Weather Risk Penalty = weather_risk_score × risk_factor × expected_revenue × wait_factor`

The recommendation is the scenario with **highest risk-adjusted net realization**, with a preference for SELL_NOW when differences are within 2% and weather risk is HIGH.

> This is **not financial advice**. It is a decision-support estimate clearly labelled as such.

---

## API Reference

Full interactive API docs: http://localhost:8000/docs

Key endpoints:
- `POST /api/farm/onboard` — create farm profile
- `GET /api/farm/{id}` — retrieve farm
- `GET /api/weather/intelligence` — weather + agricultural risk
- `GET /api/soil/intelligence` — soil parameters + crop suitability
- `GET /api/market/intelligence` — price history + seasonal analysis
- `POST /api/intelligence/analyze` — **THE CORE ENGINE** — full analysis
- `POST /api/prediction/price` — price prediction
- `POST /api/expert/ask` — AI expert consultation
- `GET /api/data-sources` — data source transparency

---

## Optional API Keys

The system works fully without any API keys. To unlock additional features:

### data.gov.in (Live Market Prices)
1. Register at https://data.gov.in
2. Get your API key from your profile
3. Add `DATA_GOV_IN_API_KEY=<key>` to `.env`

### Google Gemini (Enhanced AI Explanations)
1. Get a free key at https://aistudio.google.com
2. Add `GEMINI_API_KEY=<key>` to `.env`
3. Add `GEMINI_MODEL=gemini-1.5-flash` to `.env`

---

## Core Engineering Challenges Addressed

| Agricultural Challenge | KRISHI Solution Architecture |
|------------------------|------------------------------|
| Farmers lack field-specific soil evidence | Granular Soil Health Card OCR with mandatory confirmation |
| Volatile mandi spot prices mislead selling decisions | XGBoost price forecasting with 7-day/15-day confidence bounds |
| Dynamic weather risks cause post-harvest storage losses | Open-Meteo live hazard engine + composite multi-factor risk scoring |
| Fragmented farm data across spreadsheets and isolated systems | Unified Farm Digital Twin with authentic event auditing |

---

## Future Scope & Production Roadmap

- [ ] Multi-state / multi-district expansion across non-wheat major crops
- [ ] Kharif crop extension (rice, maize, soybean) with calibrated phenology
- [ ] Edge computer vision disease diagnosis via leaf image classification
- [ ] Multilingual speech-to-text / text-to-speech for regional vernacular access
- [ ] WhatsApp / SMS automated early-warning telemetry
- [ ] PostgreSQL / TimescaleDB migration for high-frequency sensor ingestion

---

## Tech Stack

| Layer | Technology | Description |
|-------|------------|-------------|
| Backend API | FastAPI (Python 3.11+) | Async REST API with Pydantic v2 validation |
| Database | SQLite + SQLAlchemy 2.0 | Relational store for farms, profiles, observations & events |
| Machine Learning | XGBoost + scikit-learn | Supervised regression with lag & seasonal feature engineering |
| Document OCR | pypdf + PIL + regex | Soil Health Card extraction with range safety checks |
| Weather Feed | Open-Meteo REST API | Live agro-meteorological forecasting without API key dependency |
| Mandi Data | AGMARKNET / data.gov.in | Calibrated historical seed + real-time official OGD API |
| Frontend | Next.js 14 + TypeScript | App Router architecture with client-side state hydration |
| Styling & UI | Tailwind CSS + Lucide Icons | Responsive agricultural UI with high-contrast accessibility |
| Charts | Recharts | Dynamic risk gauges and historical price time-series |

---

## License & Academic Disclaimer

Developed as a 3rd-Year B.Tech Mini Project in Computer Science & Engineering. Designed for academic demonstration, technical evaluation, and educational research use.
