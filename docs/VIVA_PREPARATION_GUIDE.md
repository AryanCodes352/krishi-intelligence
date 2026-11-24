# KRISHI Intelligence: Academic Viva & Oral Examination Guide

> **Target Audience**: 3rd-Year B.Tech Student preparing for Mini Project Viva / External Evaluation  
> **Examiner Focus**: System Architecture, Machine Learning Rigor, Data Engineering, Agronomic Soundness, Error Boundaries  

---

## SECTION 1: Core Project Overview & Motivation

### Q1: What is KRISHI Intelligence in one sentence?
**Answer**:  
"KRISHI Intelligence is an AI-powered agricultural decision support platform that combines live agro-meteorological forecasting, machine-learning-based mandi price analytics, and OCR-extracted soil intelligence into a synchronized **Farm Digital Twin** to provide stage-consistent, risk-adjusted crop and selling advisories."

### Q2: How does KRISHI differ from common agricultural chatbots or simple price trackers?
**Answer**:  
"Most existing systems are either simple chatbots that hallucinate general advice or static weather apps. KRISHI differs in three fundamental architectural ways:
1. **Multi-Source Data Fusion**: It calculates a quantitative multi-factor risk score integrating real-time weather, soil chemistry, crop phenology, and market dynamics simultaneously.
2. **Strict Data Provenance**: Every output carries an auditable data provenance tag (`LIVE`, `LATEST_AVAILABLE`, `HISTORICAL_SEED`, `REGIONAL_ESTIMATE`, or `SOIL_HEALTH_CARD`). It never fabricates numbers or presents historical data as live.
3. **Evidence-Based Economic Simulation**: Rather than giving qualitative advice, it evaluates mathematical Net Realization across 0, 7, and 15-day horizons by subtracting storage carrying costs and weather hazard penalties from projected prices."

---

## SECTION 2: Architecture & Technology Stack

### Q3: Why did you choose FastAPI for the backend instead of Django or Flask?
**Answer**:  
"FastAPI was selected for three technical reasons:
1. **Native Asynchronous I/O (`async/await`)**: Essential for concurrently polling external weather APIs (Open-Meteo) and government market portals (data.gov.in) without blocking the main event loop.
2. **Pydantic v2 Schema Enforcement**: Provides strict compile-time and runtime data validation, ensuring missing, negative, or corrupted soil and market parameters are caught immediately.
3. **High Performance & Auto-Documented APIs**: FastAPI performs on par with NodeJS/Go and automatically generates interactive OpenAPI/Swagger documentation (`/docs`), streamlining testing and integration."

### Q4: Why is SQLite used for the database, and how does it scale?
**Answer**:  
"For this 3rd-year mini project implementation, SQLite via SQLAlchemy 2.0 ORM provides zero-configuration, self-contained persistence with transactional ACID compliance. Because our database schema is completely decoupled through SQLAlchemy ORM models (`Farm`, `FarmObservation`, `SoilDocument`, `FarmSoilProfile`, `FarmEvent`), migrating to PostgreSQL or TimescaleDB for production requires changing only the `DATABASE_URL` connection string without rewriting query logic."

### Q5: Why Next.js 14 App Router instead of a plain React SPA?
**Answer**:  
"Next.js 14 App Router gives us server-side rendering (SSR), optimized bundle splitting, and robust static page generation. The dashboard loads instantaneously with optimized First Load JS (~87 kB shared), while dynamic routes (`/farm/[id]/soil`, `/farm/[id]/digital-twin`) hydrate state efficiently."

---

## SECTION 3: Machine Learning & Predictive Modeling

### Q6: Why did you choose XGBoost over Deep Learning (LSTM) or ARIMA for mandi price prediction?
**Answer**:  
"We evaluated our dataset characteristics: 349 weekly historical mandi price records (~6.7 years of Lucknow wheat data).
1. **Dataset Size**: Deep Learning architectures like LSTMs require tens of thousands of data points to avoid severe overfitting. With 349 observations, an LSTM would overparameterize.
2. **Non-Linear Interactions**: Classical ARIMA/SARIMA models assume linear relationships and struggle with sudden market shocks or multi-feature interactions (e.g., price momentum combined with seasonal indices).
3. **XGBoost Tree Ensemble**: XGBoost excels on tabular agricultural datasets. It naturally models non-linear interactions, provides $L_1$ and $L_2$ regularization to prevent overfitting, and outputs interpretable feature importances."

### Q7: What features does the XGBoost model use?
**Answer**:  
"The feature vector consists of:
- **Calendar Seasonality**: Month index, day of year, and ISO week of year.
- **Autoregressive Lags**: Price at $t-1$, $t-2$, $t-4$, and $t-8$ weeks (capturing inertia).
- **Rolling Statistics**: 4-week and 8-week Simple Moving Averages ($\text{SMA}_4, \text{SMA}_8$) and 4-week standard deviation ($\sigma_4$, measuring local market volatility).
- **Normalized Seasonal Index**: Monthly historical price median divided by the overall annual median.
- **Momentum Rate**: 4-week percentage rate-of-change ($\Delta P_{\text{4w}}$)."

### Q8: What are your model evaluation metrics, and what do they signify?
**Answer**:  
"On the held-out test split, the model achieves:
- **MAE (Mean Absolute Error)**: $\approx \text{Rs. } 80\text{--}90/\text{quintal}$, indicating average absolute deviation.
- **MAPE (Mean Absolute Percentage Error)**: $\approx 3.5\%\text{--}4.0\%$, showing high relative predictive accuracy.
- **RMSE (Root Mean Squared Error)**: Penalizes larger outliers to verify the model avoids wild predictions.
- **Confidence Calibration**: If MAE exceeds $15\%$ of average price, the system automatically downgrades the prediction confidence tag to `LOW`."

---

## SECTION 4: Soil Health Card OCR & Document Intelligence

### Q9: Walk me through the Soil Health Card OCR pipeline.
**Answer**:  
"The Soil Health Card pipeline follows a five-stage architecture:
1. **File Validation & Magic Bytes Check**: Inspects file headers to prevent corrupted or malicious uploads (verifying `%PDF` for PDFs, `\xFF\xD8\xFF` for JPEGs, `\x89PNG` for PNGs) with a 10MB limit.
2. **Text Extraction**: Uses `pypdf` for digital/scanned PDFs and image preprocessing via PIL with OCR heuristics.
3. **Regex Pattern Parsing**: Employs flexible regular expressions calibrated to the Ministry of Agriculture & Farmers Welfare's standard Soil Health Card formats for 12 parameters (pH, EC, OC, N, P, K, S, Zn, Fe, Cu, Mn, B) and Soil Texture.
4. **Physical Range & Sanity Check**: Rejects physically impossible values ($0 \le \text{pH} \le 14$, nutrients $\ge 0$). Impossible values are flagged as `INVALID` and set to `None`.
5. **Human-in-the-Loop Confirmation Gate**: Extraction state is strictly set to `REVIEW_REQUIRED`. Values are rendered in a frontend review modal where the farmer inspects, edits, or adds missing values before clicking **CONFIRM SOIL DATA**."

### Q10: Why do you never automatically save OCR results as the farm's active soil profile?
**Answer**:  
"In real-world rural India, Soil Health Cards can suffer from poor scan quality, low lighting, or folding creases. Silently treating raw OCR output as truth would risk generating incorrect fertilizer recommendations (e.g., misreading pH 7.2 as 1.2 could trigger massive, destructive gypsum applications). Requiring explicit farmer confirmation guarantees safety, legal compliance, and farmer trust."

### Q11: What happens if a soil parameter is missing from the card? Do you fill it with 0?
**Answer**:  
"**Crucially, no.** Missing fields remain `None` in Python and `null` in JSON. Coercing a missing nitrogen value to `0` would falsely indicate severe nitrogen starvation, causing the system to prescribe hazardous chemical dosages. If a parameter is unrecorded, the UI displays *'Not recorded'* and the risk engine gracefully skips that sub-index without crashing."

---

## SECTION 5: Multi-Factor Risk & Decision Engine

### Q12: How does the Multi-Factor Risk Engine compute its score?
**Answer**:  
"It computes a composite score $R \in [0, 100]$ using ICAR-calibrated agronomic weights:
$$R_{\text{overall}} = 0.35 \cdot R_{\text{crop}} + 0.30 \cdot R_{\text{weather}} + 0.20 \cdot R_{\text{market}} + 0.15 \cdot R_{\text{soil}}$$
- **Crop Risk (35%)**: Evaluates baseline stage vulnerability ($15$ for post-harvest up to $75$ for flowering) compounded by precipitation and humidity hazard multipliers.
- **Weather Risk (30%)**: Derived from live Open-Meteo 7-day precipitation probability, extreme temperatures, and moisture.
- **Market Risk (20%)**: Driven by price volatility and directional price erosion.
- **Soil Risk (15%)**: Driven by pH deviations from $[6.5, 7.5]$ and macro/micronutrient deficiencies."

### Q13: Explain the mathematical logic behind the Sell-Now vs. Wait Decision Simulator.
**Answer**:  
"For each horizon $h \in \{0, 7, 15\}$ days, the engine calculates:
$$\text{Net Realization}(h) = \hat{P}(h) - C_{\text{storage}}(h) - \text{Loss}_{\text{weather}}(h) - C_{\text{transport}}$$
- **Storage Cost**: Accrues at Rs. $5.00/\text{qtl/day}$. Over 7 days, holding grain costs Rs. $35/\text{qtl}$.
- **Weather Loss Penalty**: High rainfall probability during holding introduces mold/spoilage risk:
  $$\text{Loss}_{\text{weather}} = \hat{P}(h) \times \left(\frac{R_{\text{weather}}}{100}\right) \times 0.08 \times \left(\frac{h}{15}\right)$$
- If the projected price gain does not significantly exceed cumulative storage and weather depreciation, the simulator recommends **SELL_NOW** to protect farm capital."

---

## SECTION 6: Agronomic Guardrails & Provenance

### Q14: What is an agronomic guardrail in KRISHI? Give a concrete example.
**Answer**:  
"An agronomic guardrail is a hard constraint that overrides software recommendations to prevent dangerous farming practices.  
**Example**: If a farmer's crop is at the **Post-harvest** or **Reproductive (Grain Filling)** stage, the system strictly halts all granular chemical fertilizer recommendations (Urea/DAP), even if the soil test shows nitrogen deficiency. Applying urea to harvested stubble causes runoff pollution, while late-stage application causes vegetative greening, lodging, delayed grain maturity, and fungal vulnerability."

### Q15: Explain the provenance hierarchy for Mandi prices.
**Answer**:  
"Market observations are dynamically tagged based on verification freshness:
- `LIVE`: Retrieved from official data.gov.in API with observation age $\le 1$ day.
- `LATEST_AVAILABLE`: Official data retrieved successfully, but observation is $2\text{--}7$ days old.
- `STALE`: Official data retrieved, but observation is $> 7$ days old (triggers a visual warning).
- `HISTORICAL_SEED`: Fallback to our calibrated 349-week CSV dataset when the API key is unconfigured or the endpoint is unreachable.
- `DATA_UNAVAILABLE`: Neither API nor seed data exists for the commodity."

---

## SECTION 7: Viva "Tough Questions" & Rapid-Fire Defense

| Question from Examiner | Strategic Defensive Answer |
|------------------------|----------------------------|
| *"Why only Wheat and Lucknow in the prototype?"* | "Wheat in Lucknow provides a tightly controlled, deeply validated testbed. We intentionally avoided superficial multi-crop breadth in order to achieve mathematical depth: calibrated 349-week mandi series, ICAR stage vulnerability curves, and verified Soil Health Card bounds." |
| *"What happens if the internet goes down during the viva demo?"* | "The platform is fully resilient offline. Weather falls back to cached observations, market prices run off `data/seed/wheat_lucknow_mandi.csv`, soil defaults to ICAR-NBSS&LUP regional maps, and AI explanations execute via deterministic agronomic rule templates." |
| *"Can a farmer accidentally submit an impossible pH of 25?"* | "No. Dual-layer validation prevents this: the backend rejects values outside $0.0 \le \text{pH} \le 14.0$ with HTTP 400 Bad Request, and the frontend review modal flags it with an instant red error indicator, disabling the confirmation button." |
| *"How do you test your software?"* | "We have an automated regression suite of **116 automated pytest tests** covering unit models, API routers, OCR extraction, edge cases, crop guardrails, and cross-farm data isolation, complemented by `tsc --noEmit` with zero TypeScript errors." |
