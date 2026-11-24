# KRISHI Intelligence

**Multi-Factor Agro-Climatic Digital Twin with Dynamic Provenance Guardrails and Market Price Forecasting**



[![Live App](https://img.shields.io/badge/Live_App-Vercel-000000?style=for-the-badge&logo=vercel)](https://krishi-intelligence.vercel.app)

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI_0.115-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)

[![Next.js](https://img.shields.io/badge/Frontend-Next.js_14-000000?style=for-the-badge&logo=next.js)](https://nextjs.org/)

[![XGBoost](https://img.shields.io/badge/ML-XGBoost_2.1-150458?style=for-the-badge&logo=python)](https://xgboost.readthedocs.io/)

[![Tests](https://img.shields.io/badge/Pytest-116_Passed-2EA44F?style=for-the-badge&logo=pytest)](backend/tests)



KRISHI Intelligence is a full-stack **Agricultural Decision Support System (ADSS)** built to solve three decoupled operational challenges in smallholder wheat farming: localized agro-climatic volatility, opaque APMC market price swings, and uncalibrated soil fertilization.



---



## Core Architecture & Engineering Highlights



1. **Living Farm Digital Twin (`DigitalTwinEngine`)**

   - Maintains a synchronized state model of the farm, accumulating daily **Growing Degree Days (GDD)** ($T_{\text{base}} = 4.0^\circ\text{C}$) across 8 wheat phenological stages (Germination to Post-Harvest).

   - Fuses multi-depth soil moisture, FAO-56 reference evapotranspiration ($ET_0$), and thermal stress vectors.



2. **Dynamic Data Provenance Guardrails**

   - Prevents silent data degradation and hallucinated outputs by tagging every observation with an auditable integrity state (`LIVE`, `LATEST_AVAILABLE`, `STALE`, `HISTORICAL_SEED`, `VERIFIED_LAB_TEST`, `REGIONAL_BASELINE`).

   - Gracefully falls back to calibrated historical APMC baselines when upstream government feeds (`data.gov.in`) are unavailable.



3. **Soil Health Card OCR + Human-in-the-Loop Confirmation Gate**

   - Parses uploaded Soil Health Cards (`pH`, `N`, `P`, `K`, `OC`, `EC`) into a locked `PENDING_REVIEW` state.

   - Enforces physical chemical feasibility bounds and refuses to update active farm soil profiles or generate fertilizer advisories until the farmer reviews and explicitly confirms the extracted values.



4. **XGBoost Mandi Price Forecaster & Net Realization Engine**

   - Forecasts 30-day commodity modal prices with **80% and 95% confidence intervals** (Out-of-sample validation: **MAE ₹84.30/qtl**, **MAPE 3.82%**, **$R^2 = 0.887$**).

   - Evaluates **Sell Today vs. Wait 7 Days vs. Wait 15 Days** by accounting for godown storage carrying costs, weather dampness risk penalties, and distance-adjusted mandi transport costs.



---



## Tech Stack



- **Backend:** FastAPI, Uvicorn, SQLAlchemy 2.0, Pydantic v2, SQLite / PostgreSQL

- **ML & Data:** XGBoost, Scikit-Learn, Pandas, NumPy, Custom Soil OCR Pipeline

- **Frontend:** Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, Lucide Icons

- **Testing:** Pytest & Pytest-Asyncio (**116 automated unit & integration tests**)



---



## Project Structure



```text

krishi-intelligence/

├── backend/              # FastAPI routers, Digital Twin engine, provenance guardrails, OCR & tests

├── frontend/             # Next.js 14 App Router UI, interactive charts & data provenance badges

├── ml/                   # Feature engineering, XGBoost training & evaluation pipeline

├── data/                 # Calibrated APMC seed datasets & district soil baselines

├── render.yaml           # Render deployment blueprint

├── requirements.txt      # Python runtime dependencies

└── run.bat               # One-click local startup script (Windows)

```



---



## Local Setup



```powershell

# 1. Clone the repository

git clone https://github.com/AryanCodes352/krishi-intelligence.git

cd krishi-intelligence



# 2. Launch FastAPI (:8000) and Next.js (:3000)

.\run.bat

```



### Running the Test Suite



```powershell

pytest backend/tests

```



---



## Author



Built by **[Aryan](https://github.com/AryanCodes352)**