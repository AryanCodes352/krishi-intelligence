# KRISHI Intelligence: 5-Minute Live Viva Demonstration Script

> **Objective**: Conduct a flawless, high-impact 5-minute academic presentation and live software walkthrough for university evaluators and external examiners.  
> **Key Message**: *"KRISHI is not a chatbot; it is a multi-source data fusion engine that grounds agricultural decisions in verifiable on-farm evidence and strict data provenance."*

---

## Pre-Demo Checklist (Do This 5 Minutes Before Viva)

1. **Start Backend**:
   ```powershell
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   *(Verify `http://localhost:8000/docs` is accessible)*
2. **Start Frontend**:
   ```powershell
   cd frontend
   npm run dev
   ```
   *(Open `http://localhost:3000` in Google Chrome)*
3. **Have a Test Soil Card Ready**:
   - Location: `data/uploads/soil/...` or create a sample PDF/PNG for the upload test.
4. **Browser Tab Layout**:
   - Tab 1: `http://localhost:3000` (KRISHI Homepage)
   - Tab 2: `http://localhost:8000/docs` (FastAPI Swagger Interactive Documentation)
   - Tab 3: `docs/SYSTEM_ARCHITECTURE.md` (Architecture diagram ready to show if requested)

---

## Timed 5-Minute Demonstration Walkthrough

```
[00:00 - 01:00]  Problem Context, Differentiation & Digital Twin Architecture
[01:00 - 02:00]  Farmer Onboarding & Live Digital Twin Synchronization
[02:00 - 03:00]  Soil Health Card OCR Upload, Review & Confirmation Gate
[03:00 - 04:00]  Mandi Market Intelligence, Provenance & XGBoost Forecast
[04:00 - 05:00]  Sell-vs-Wait Decision Simulator & Explainability Evidence Panel
```

---

### Minute 0:00 – 01:00 | The Hook & Architectural Overview

**What to do on screen**:
- Start on the Homepage (`http://localhost:3000`).
- Point to the tagline: *"See the data. Understand the risk. Make the right decision."*

**What to say**:
> "Good morning, respected professors and examiners. Today, I am demonstrating **KRISHI Intelligence**, our 3rd-year B.Tech Mini Project in Computer Science and Engineering.
>
> In India, farmers face fragmented data: regional weather reports are generalized, mandi prices fluctuate unpredictably, and soil test results remain trapped in paper cards. Existing solutions are often simple conversational chatbots that hallucinate generalized advice.
> 
> KRISHI solves this through an **agentic data fusion architecture**. It synchronizes real-time agro-meteorology from Open-Meteo, machine-learning-based mandi forecasting using XGBoost, and computer-vision Soil Health Card extraction into a single living **Farm Digital Twin**. Most importantly, it enforces **strict data provenance**—every recommendation discloses whether it is based on live official feeds, regional ICAR baselines, or verified laboratory tests."

---

### Minute 01:00 – 02:00 | Onboarding & Farm Digital Twin

**What to do on screen**:
1. Click **"Get Started"** or **"Onboard Farm"** (`/onboard`).
2. Enter:
   - Farmer Name: `Ramesh Kumar`
   - Location: `Malihabad`
   - District: `Lucknow`, State: `Uttar Pradesh`
   - Crop: `Wheat` (Variety: `HD-2967`)
   - Sowing Date: `2025-11-15` (or a recent date)
   - Acreage: `5.0`
3. Click **"Register & Analyze Farm"**.
4. The dashboard loads. Click **"Digital Twin"** in the navigation bar (`/digital-twin`).

**What to say**:
> "Here, our system registers the farm and creates its **Living Digital Twin**.
> 
> Notice the top branch hub: the system has calculated the crop's exact phenological growth stage (**Tillering**, Day 45) based on days after sowing. It has pulled live meteorological conditions for Malihabad coordinates via Open-Meteo, initialized baseline soil suitability, and established price trends.
>
> Down below, you can see the **Activity Timeline**. Every critical state change—from registration to parameter updates—is committed to an immutable event audit log (`FARM_CREATED`)."

---

### Minute 02:00 – 03:00 | Granular Soil Health Card OCR & Confirmation Gate

**What to do on screen**:
1. In the navigation bar, click **"Soil"** (`/farm/[id]/soil`).
2. Point out the banner: `REGIONAL_ESTIMATE` (ICAR-NBSS&LUP baseline active).
3. Click **"Upload Soil Health Card"**.
4. Select a sample PDF or PNG Soil Health Card.
5. Click **"Extract with OCR"**.
6. Show the **Review & Confirmation Modal**:
   - Point out the extracted parameters (pH: `7.2`, Nitrogen: `275 kg/ha`, etc.) tagged with green `[CARD]` badges.
   - Edit one parameter (e.g., change Phosphorus from `24` to `28`): notice the badge instantly updates to blue `[FARMER]`.
   - Test validation: enter `pH: 19` and show the instant red error: *"pH must be between 0.0 and 14.0"*, with the confirm button disabled.
   - Fix the pH back to `7.2`.
7. Click the prominent green button: **"CONFIRM SOIL DATA"**.
8. Show the updated page: badge is now emerald `SOIL_HEALTH_CARD`, crop suitability is recalculated, and advisories are now calibrated to this exact field!

**What to say**:
> "This is Feature 3: Granular Soil Intelligence. Initially, the farm relied on regional district estimates.
>
> When the farmer uploads their physical Soil Health Card, our backend verifies magic bytes and file headers to reject corrupt uploads, extracts structured parameters via regex heuristics, and bounds-checks all physical ranges ($0 \le \text{pH} \le 14$).
>
> **Crucially, the system NEVER auto-confirms OCR output.** We enforce a mandatory human-in-the-loop review. Notice that when I modified Phosphorus, the provenance dynamically flipped to `FARMER_ENTERED`, while untouched fields remain `SOIL_HEALTH_CARD`. Upon confirmation, the Digital Twin immediately switches from regional estimates to verified field-specific data, recalculating nutrient suitability and stage-consistent fertilizer advice."

---

### Minute 03:00 – 04:00 | Mandi Market Intelligence & XGBoost Price Forecasting

**What to do on screen**:
1. In the navigation bar, click **"Market"** (`/farm/[id]/market`).
2. Show the Market Intelligence Card:
   - Reference modal price: `Rs. 2,605/quintal` (labeled `HISTORICAL_SEED` or `LIVE` depending on API key).
   - XGBoost Forecast: `7-Day Expected Price: Rs. 2,544/quintal` with range envelope (`Rs. 2,484 – Rs. 2,604`).
   - 15-day projected price trajectory.
   - Point to the confidence level badge: `MEDIUM` (Honest, un-inflated confidence).

**What to say**:
> "Now turning to market economics:
>
> Smallholder farmers often fall victim to distress selling because they lack price visibility. Our Market Service integrates both official AGMARKNET feeds from data.gov.in and a calibrated 349-week historical dataset.
>
> To forecast prices over 7 and 15-day horizons, we trained an **XGBoost Regressor** incorporating lag features, 4-week rolling volatility, and monthly seasonal indices. On our held-out test split, the model delivers a Mean Absolute Percentage Error (MAPE) of under 4%.
>
> Notice our transparency: if no live API key is set, the system explicitly labels the data as `HISTORICAL_SEED`. We never pretend historical data is a live spot price."

---

### Minute 04:00 – 05:00 | Decision Engine & Agronomic Explainability

**What to do on screen**:
1. Click **"Decision"** in the navigation bar (`/farm/[id]/decision`).
2. Show the **Sell-vs-Wait Simulator**:
   - Compare the 3 scenarios: **Sell Now** vs **Wait 7 Days** vs **Wait 15 Days**.
   - Point out the math: Expected Price minus Storage Cost (`Rs. 5/qtl/day`) minus Weather Risk Penalty.
   - Recommendation: `SELL_NOW` (or wait depending on price).
3. Click **"Why this recommendation?"** to open the **Explainability Panel**.
4. Show the transparent signals:
   - Market Price Signal
   - Storage Cost Signal
   - Weather Risk Signal
   - Crop Stage Guardrail Notice

**What to say**:
> "Finally, how does KRISHI answer the farmer's ultimate question: *'Should I sell today or wait?'*
>
> Our **Economic Decision Simulator** calculates Net Realization for Sell Today, Wait 7 Days, and Wait 15 Days. It factors in holding storage expenses at Rs. 5 per quintal per day and applies a moisture depreciation penalty if heavy rainfall is forecast during storage.
>
> When the farmer clicks *'Why this recommendation?'*, the system generates an auditable explainability breakdown showing each signal's exact mathematical contribution. Furthermore, our agronomic safety guardrails ensure that if the crop is in post-harvest or flowering stages, dangerous fertilizer recommendations are strictly halted.
>
> In conclusion, KRISHI Intelligence demonstrates how computer science, machine learning, and human-in-the-loop validation can be engineered into an authentic, truthful decision engine for Indian agriculture. Thank you, and I welcome your questions."

---

## Offline Fallback Cheat Sheet (If WiFi Fails During Viva)

If the university WiFi drops or external APIs timeout, remain calm and use this defense:

| Scenario | What to explain to examiners |
|---|---|
| **Open-Meteo unreachable** | *"Our backend implements automatic fallback to cached meteorological averages for Lucknow district, ensuring the risk engine computes without interruption."* |
| **data.gov.in API key missing/blocked** | *"The system automatically engages the calibrated 349-week AGMARKNET historical dataset, tagging the source transparently as `HISTORICAL_SEED`."* |
| **Examiner asks to test OCR with manual entry** | Click *'Enter Manually'* in the modal: *"Our system supports manual digitization for farmers holding paper Soil Health Cards without scanners."* |
| **Examiner asks about test coverage** | Open terminal and run: `python -m pytest backend/tests -q` to show **116 automated tests passing in under 10 seconds**. |
