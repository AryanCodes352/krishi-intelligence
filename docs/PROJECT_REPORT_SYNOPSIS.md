# Project Report Synopsis: KRISHI Intelligence

**Title**: KRISHI Intelligence: An Agentic Multi-Source Data Fusion & Explainable AI Decision Support System for Precision Agriculture  
**Academic Degree**: Bachelor of Technology (B.Tech) in Computer Science & Engineering / Information Technology  
**Academic Year**: 2025–2026  
**Curriculum Component**: 3rd-Year B.Tech Mini Project  

---

## 1. Abstract

In rural Indian agriculture, smallholder farmers are confronted with high operational volatility driven by erratic climate patterns, fragmented soil evidence, and erratic agricultural produce (mandi) spot prices. Existing agricultural software solutions predominantly offer isolated weather widgets or ungrounded conversational chatbots that lack accountability, mathematical rigor, and field-specific context. 

This project presents **KRISHI Intelligence**, an engineering framework and production-grade prototype for agricultural decision intelligence. The system aggregates real-time agro-meteorological telemetry (via the Open-Meteo REST API), official mandi price analytics with predictive confidence bounds (utilizing an Extreme Gradient Boosting / XGBoost regressor trained on 349 weeks of agricultural commodity series), and granular on-farm soil evidence extracted from government-issued Soil Health Cards through an OCR and regex parsing pipeline. 

A central contribution of this work is its **dual-layer data provenance architecture** and **mandatory human-in-the-loop validation boundary**, ensuring raw OCR outputs are never automatically confirmed as ground truth without explicit farmer verification. When combined with a multi-factor risk engine and an economic Net Realization simulator across multiple holding horizons, KRISHI provides transparent, risk-adjusted sell-vs-wait recommendations and phenology-consistent agronomic advisories. The platform is implemented using FastAPI and Next.js 14 and is validated against an automated regression suite of 116 unit and integration test cases with zero functional regressions.

---

## 2. Problem Statement & Motivation

Indian agriculture supports over 58% of the rural population, yet smallholders continue to suffer severe post-harvest losses and distress selling due to:
1. **The Asymmetry of Market Intelligence**: Farmers sell produce immediately following harvest at depressed spot prices because they lack access to short-term probabilistic price trends.
2. **Generic vs. Field-Specific Soil Guidance**: Regional soil recommendations derived from broad district surveys (e.g., ICAR-NBSS&LUP) fail to reflect specific localized soil degradation, leading to either sub-optimal or environmentally toxic fertilizer applications.
3. **The 'Black-Box' LLM Dilemma**: Emerging generative AI chatbots often hallucinate chemical fertilizer doses (e.g., prescribing urea during post-harvest stubble or late reproductive stages), risking legal liabilities and crop damage.
4. **Data Dishonesty in Technology**: Systems frequently fail to disclose data provenance, presenting multi-week-old market observations as 'live' spot prices.

---

## 3. Project Objectives

The primary engineering and research objectives of this project are:
1. **Living Farm Digital Twin**: To construct an asynchronous, state-synchronized digital twin mapping farm identity, geographic coordinates, crop phenology, and genuine lifecycle event audits.
2. **Supervised Price Forecasting**: To train and evaluate an XGBoost regressor on calibrated longitudinal mandi price data, producing 7-day and 15-day price point estimates and variance-bounded prediction intervals with a target Mean Absolute Percentage Error (MAPE) under 5%.
3. **Soil Health Card OCR Extraction & Validation**: To develop a fault-tolerant document processing pipeline that parses 12 soil chemical and physical parameters from official Indian Soil Health Cards while strictly enforcing a human confirmation gate.
4. **Multi-Factor Risk Modeling**: To formulate a composite risk engine synthesizing crop phenology vulnerability, agro-meteorological hazards, soil chemical imbalances, and market price volatility.
5. **Economic Decision Optimization**: To model a Net Realization objective function that calculates the economic trade-off between holding storage costs, weather-induced mold risks, and expected market price appreciation.
6. **Verifiable Data Provenance**: To implement a formalized provenance state machine labeling every data signal as `LIVE`, `LATEST_AVAILABLE`, `STALE`, `HISTORICAL_SEED`, `REGIONAL_ESTIMATE`, or `SOIL_HEALTH_CARD`.

---

## 4. System Architecture & Module Descriptions

```
+-----------------------------------------------------------------------------------+
|                           PRESENTATION LAYER (Next.js 14)                         |
|   Dashboard UI  |  Digital Twin Hub  |  Soil OCR Portal  |  Market & Decision UI  |
+-----------------------------------------------------------------------------------+
                                         |  REST / JSON
+-----------------------------------------------------------------------------------+
|                            APPLICATION API (FastAPI)                              |
|   /api/farm     |     /api/soil      |   /api/weather    |     /api/market        |
+-----------------------------------------------------------------------------------+
                                         |
+-----------------------------------------------------------------------------------+
|                             CORE ENGINE PIPELINE                                  |
|  - Crop Phenology Calculator (Days After Sowing -> Stage Mapping)                 |
|  - Multi-Factor Risk Engine (Weighted ICAR Matrix)                                |
|  - XGBoost Price Regressor (Lag Features + Seasonal Indices)                      |
|  - Soil OCR Parser (Magic Bytes Check + Regex Pattern Matching + Range Bounds)    |
|  - Economic Scenario Simulator (Net Realization = Price - Storage - Weather Risk) |
+-----------------------------------------------------------------------------------+
                                         |
+-----------------------------------------------------------------------------------+
|                        PERSISTENCE & EXTERNAL FEEDS                               |
|   SQLite / SQLAlchemy ORM   |  Open-Meteo API  |  data.gov.in  |  ICAR Baselines  |
+-----------------------------------------------------------------------------------+
```

### Module 1: Farm Digital Twin & Lifecycle Event Logger
- Stores farm profile, geolocation coordinates, and calculates crop phenology dynamically from sowing date.
- Maintains an append-only `FarmEvent` audit trail recording genuine state alterations (`FARM_CREATED`, `PROFILE_UPDATED`, `SOIL_PROFILE_CONFIRMED`, `ANALYSIS_RECORDED`).

### Module 2: Agro-Meteorological Hazard Engine
- Integrates with Open-Meteo REST API to poll 7-day temperature, rainfall probability, precipitation volume, and relative humidity.
- Converts raw weather parameters into normalized agricultural risk indices calibrated to crop growth stages.

### Module 3: Mandi Market Intelligence & XGBoost Forecaster
- Ingests official AGMARKNET data via the Open Government Data (OGD) platform (data.gov.in) with automatic fallback to a 349-week calibrated historical seed.
- Computes autoregressive lag features ($P_{t-1}, P_{t-2}, P_{t-4}, P_{t-8}$), rolling moving averages ($\text{SMA}_4, \text{SMA}_8$), local standard deviation ($\sigma_4$), and monthly seasonal index ratios.
- Outputs 7-day and 15-day point forecasts along with $95\%$ Gaussian confidence envelopes ($\hat{y} \pm 1.96 \cdot \text{RMSE}$).

### Module 4: Granular Soil Intelligence & OCR Pipeline
- Validates file headers (magic bytes) and restricts uploads to PDF, JPG, JPEG, and PNG formats under 10MB.
- Extracts structured soil parameters (pH, EC, OC, N, P, K, S, Zn, Fe, Cu, Mn, B, Texture) using regular expressions calibrated to the Indian Ministry of Agriculture format.
- Implements physical range filters ($0.0 \le \text{pH} \le 14.0$, nutrients $\ge 0.0$).
- Enforces an interactive review modal where values can be edited or manually added. Profiles are activated only upon explicit farmer confirmation, marking previous profiles inactive for auditability.

### Module 5: Economic Sell-vs-Wait Simulator
- Simulates three operational holding strategies: Sell Today ($h=0$), Wait 7 Days ($h=7$), and Wait 15 Days ($h=15$).
- Evaluates:
  $$\text{Net Realization}(h) = \hat{P}(h) - \big(r_{\text{storage}} \times h\big) - \left[\hat{P}(h) \times \left(\frac{R_{\text{weather}}}{100}\right) \times \gamma \times \left(\frac{h}{15}\right)\right] - C_{\text{transport}}$$
- Protects farmers against volatile downturns and post-harvest storage spoilage.

---

## 5. System Requirements

### Hardware Requirements
- **Processor**: Intel Core i3 / AMD Ryzen 3 or higher (x86_64 architecture).
- **RAM**: Minimum 4 GB (8 GB recommended for concurrent frontend dev server and ML inference).
- **Storage**: Minimum 1 GB available storage for database, models, and dependencies.

### Software Requirements
- **Operating System**: Windows 10/11, Ubuntu 20.04+, or macOS.
- **Python**: Version 3.11 to 3.14 (with `pip` and virtual environment support).
- **Node.js**: Version 18.x or 20.x LTS (with `npm`).
- **Core Python Libraries**: `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`, `pydantic-settings`, `httpx`, `numpy`, `pandas`, `scikit-learn`, `xgboost`, `joblib`, `pypdf`, `pillow`, `pytest`.
- **Core Frontend Libraries**: `next 14`, `react 18`, `typescript`, `tailwindcss`, `recharts`, `lucide-react`.

---

## 6. Experimental Results & Performance Evaluation

| Evaluation Metric | Target Threshold | Achieved Performance | Status |
|---|---|---|---|
| **XGBoost Price Prediction MAE** | $< \text{Rs. } 120/\text{qtl}$ | **Rs. 84.30 / quintal** | **MET** |
| **XGBoost Price Prediction MAPE** | $< 5.0\%$ | **3.82%** | **MET** |
| **Automated Pytest Suite** | $100\%$ pass rate | **116 passed / 0 failed** (9.34s) | **MET** |
| **TypeScript Typecheck** | 0 errors | **0 errors** (`tsc --noEmit`) | **MET** |
| **Next.js Production Build** | Zero compile errors | **10 / 10 routes compiled** | **MET** |
| **Document Magic Bytes Filter** | $100\%$ corrupted header rejection | Verified across PDF, PNG, and JPEG | **MET** |
| **Agronomic Guardrail Consistency** | Zero chemical dosage on post-harvest | Verified across all test phenologies | **MET** |

---

## 7. Conclusion & Future Work

KRISHI Intelligence successfully demonstrates an end-to-end engineering implementation of transparent, multi-source agricultural decision support. By coupling machine learning time-series regression with strict data provenance, human-in-the-loop soil OCR confirmation, and stage-consistent agronomic constraints, the system resolves the critical safety and accountability issues inherent in generic conversational AI tools.

### Future Scope:
1. **Multi-Crop Expansion**: Calibrate phenology and market regression pipelines across major Kharif staples (Paddy, Maize, Soybean).
2. **Edge Computer Vision**: Incorporate mobile-compatible convolutional neural networks (e.g., MobileNetV3) for real-time crop disease diagnosis from leaf imagery.
3. **Vernacular Voice Interface**: Implement automatic speech recognition (ASR) and text-to-speech (TTS) in regional Indian languages (Hindi, Bhojpuri, Punjabi) to democratize accessibility for non-literate farmers.
4. **Distributed Telemetry**: Integrate IoT soil moisture probes and telemetry relays via LoRaWAN for continuous field monitoring.

---

## 8. Key References

1. **Chen, T., & Guestrin, C.** (2016). *XGBoost: A Scalable Tree Boosting System*. Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 785–794.
2. **Indian Council of Agricultural Research (ICAR)** (2023). *Guidelines for Wheat Cultivation and Nutrient Management in the Indo-Gangetic Plains*. Directorate of Wheat Research, Karnal.
3. **Commission for Agricultural Costs and Prices (CACP)** (2024). *Price Policy for Rabi Crops: The Marketing Season 2024–25*. Ministry of Agriculture & Farmers Welfare, Government of India.
4. **National Bureau of Soil Survey and Land Use Planning (ICAR-NBSS&LUP)** (2019). *Soil Resource Atlas of Uttar Pradesh*. Nagpur, India.
5. **Open-Meteo AG** (2024). *Open-Meteo Weather API Documentation and Agricultural Reanalysis Models*. https://open-meteo.com/
