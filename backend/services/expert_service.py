"""
Expert / AI Agronomist Service — KRISHI Data Engine
===================================================
Generates contextual, truthful, farmer-friendly agricultural advice using:
- Farm profile (crop, variety, sowing date, phenological stage)
- Soil profile (parameters, deficits, provenance: REGIONAL_ESTIMATE vs on-farm test)
- Live weather conditions (Open-Meteo rain probability, risk score)
- Market prices and prediction (when question is market/selling related)
- HARD AGRONOMIC STAGE CONSTRAINTS:
  * Post-harvest: NEVER recommend fertilizer for the harvested crop. Recommend soil testing,
    field prep, FYM organic matter, and next-crop planning.
  * Pre-sowing / Basal: Basal DAP/NPK + tillage FYM.
  * Tillering / Vegetative: Split urea top-dressing with weather rain check.
  * Late Reproductive / Maturity: Cease soil fertilizer broadcasting.
  * Never mix stages in a single recommendation.
- Optional Gemini 1.5 API enhancement with deterministic fallback
"""

import os
import json
from datetime import datetime, timezone, date
from typing import Optional, Dict, Any, List

from backend.services.crop_model import get_crop_stage
from backend.services.soil_service import get_soil_intelligence
from backend.services.market_service import get_market_intelligence


def generate_expert_advice(
    question: str,
    farm_data: Optional[Dict[str, Any]] = None,
    weather_data: Optional[Dict[str, Any]] = None,
    soil_data: Optional[Dict[str, Any]] = None,
    market_data: Optional[Dict[str, Any]] = None,
    prediction_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate contextual guidance for farmer questions based on verified farm data and hard stage constraints.
    """
    # ── Normalize Farm Profile ──────────────────────────────────────────────
    farm = farm_data or {}
    crop = farm.get("crop") or "Wheat"
    variety = farm.get("crop_variety") or ""
    district = farm.get("district") or "Lucknow"
    state = farm.get("state") or "Uttar Pradesh"
    location = farm.get("location") or district
    soil_tested = bool(farm.get("soil_data_available", False))

    # Determine Crop Stage with hard consistency
    explicit_stage = farm.get("crop_stage")
    sowing_date_str = farm.get("sowing_date")
    days_after_sowing = 0
    if sowing_date_str:
        try:
            sowing_dt = datetime.strptime(sowing_date_str, "%Y-%m-%d")
            days_after_sowing = max(0, (datetime.now() - sowing_dt).days)
        except Exception:
            days_after_sowing = 0

    if explicit_stage:
        stage = explicit_stage
    else:
        stage = get_crop_stage(crop, days_after_sowing)

    # ── Normalize Soil Data ────────────────────────────────────────────────
    soil = soil_data or get_soil_intelligence(
        district=district,
        state=state,
        crop=crop,
        crop_stage=stage,
        soil_tested=soil_tested,
        farm_context=farm,
    )
    soil_params = soil.get("parameters", {})
    soil_source_type = soil.get("data_source", {}).get("type", "REGIONAL_ESTIMATE")
    n_val = soil_params.get("nitrogen", {}).get("value", 240)
    p_val = soil_params.get("phosphorus", {}).get("value", 18)
    k_val = soil_params.get("potassium", {}).get("value", 220)
    oc_val = soil_params.get("organic_carbon", {}).get("value", 0.45)
    soil_type = soil_params.get("soil_type", "Sandy Loam")

    # ── Normalize Weather Data ─────────────────────────────────────────────
    weather = weather_data or {}
    forecast = weather.get("forecast_7day", [])
    max_rain_prob = max((f.get("rain_probability_pct", 0) for f in forecast), default=0)
    agri_risk = weather.get("agricultural_risk", {})
    weather_risk_score = agri_risk.get("overall_score", 0) if isinstance(agri_risk, dict) else 0

    # ── Normalize Market Data & XGBoost Price Predictions ──────────────────
    market = market_data or {}
    current_market = market.get("current", {})
    current_modal = current_market.get("modal_price", 2605)
    market_data_type = current_market.get("data_type", "HISTORICAL_SEED")
    is_live_market = (market_data_type == "LIVE")
    market_date = current_market.get("date", "")
    market_name = current_market.get("market") or district

    hist_stats = market.get("historical", {}).get("statistics", {})
    hist_avg = hist_stats.get("mean_price", 2310)
    vs_avg_pct = hist_stats.get("current_vs_avg_pct", 12.8)

    # Format market reference string according to provenance
    if is_live_market and market_date:
        market_ref_str = f"The live {market_name} mandi spot price as of {market_date} is Rs.{int(current_modal):,}/q."
        market_provenance_label = "LIVE"
    else:
        market_ref_str = (
            f"The latest available {market_name} mandi reference price in the prototype market dataset is Rs.{int(current_modal):,}/q. "
            "This value is labelled HISTORICAL_SEED and should not be presented as a live mandi quote."
        )
        market_provenance_label = "HISTORICAL_SEED"

    # Resolve XGBoost predictions
    pred_7d_dict = {}
    pred_15d_dict = {}
    if prediction_data:
        pred_7d_dict = prediction_data.get("prediction_7d") or prediction_data.get("prediction") or {}
        pred_15d_dict = prediction_data.get("prediction_15d") or {}
    elif market and "prediction" in market:
        pred_7d_dict = market.get("prediction_7d") or market.get("prediction") or {}
        pred_15d_dict = market.get("prediction_15d") or {}
    else:
        # Dynamically query XGBoost model
        try:
            from ml.predict import predict_price
            from backend.services.market_service import get_historical_df
            hist_df = get_historical_df(crop)
            res7 = predict_price(current_price=float(current_modal), current_date=date.today(), historical_df=hist_df, horizon_days=7)
            if not res7.get("insufficient_data"):
                pred_7d_dict = res7.get("prediction", {})
            res15 = predict_price(current_price=float(current_modal), current_date=date.today(), historical_df=hist_df, horizon_days=15)
            if not res15.get("insufficient_data"):
                pred_15d_dict = res15.get("prediction", {})
        except Exception:
            pass

    p7_point = int(pred_7d_dict.get("point_estimate", current_modal)) if pred_7d_dict else int(current_modal)
    p7_min = int(pred_7d_dict.get("min_price", p7_point)) if pred_7d_dict else p7_point
    p7_max = int(pred_7d_dict.get("max_price", p7_point)) if pred_7d_dict else p7_point

    p15_point = int(pred_15d_dict.get("point_estimate", 0)) if pred_15d_dict else 0
    p15_min = int(pred_15d_dict.get("min_price", p15_point)) if pred_15d_dict else p15_point
    p15_max = int(pred_15d_dict.get("max_price", p15_point)) if pred_15d_dict else p15_point

    # Contextual Provenance String (Rule 5: Soil Intelligence Provenance)
    if soil_source_type == "SOIL_HEALTH_CARD":
        soil_provenance_note = f"Your Soil Health Card reports Nitrogen ({n_val} kg/ha), Phosphorus ({p_val} kg/ha), and Potassium ({k_val} kg/ha) based on laboratory measurement"
        soil_source_label = "SOIL_HEALTH_CARD"
    elif soil_source_type == "FARMER_ENTERED":
        soil_provenance_note = f"Based on your confirmed farmer-entered soil test values (Nitrogen: {n_val} kg/ha, Phosphorus: {p_val} kg/ha)"
        soil_source_label = "FARMER_ENTERED"
    elif soil_tested or soil_source_type == "FIELD_TEST":
        soil_provenance_note = "Based on your verified on-farm soil test"
        soil_source_label = "SOIL_HEALTH_CARD"
    else:
        soil_provenance_note = (
            "The current regional soil estimate indicates baseline Nitrogen "
            f"({n_val} kg/ha) and Phosphorus ({p_val} kg/ha) from ICAR-NBSS&LUP district maps (not an individual on-farm measurement). "
            "These values provide preliminary regional context; exact field dosages require an on-farm soil test"
        )
        soil_source_label = "REGIONAL_ESTIMATE"


    variety_str = f" ({variety})" if variety else ""
    q_lower = question.lower().strip()

    # ── Route Intent ────────────────────────────────────────────────────────
    is_fertilizer = any(w in q_lower for w in ["fertilizer", "fertiliser", "urea", "dap", "npk", "nutrient", "potash", "manure"])
    is_yellowing = any(w in q_lower for w in ["yellow", "yellowing", "pale", "chlorosis", "rust"])
    is_selling = any(w in q_lower for w in ["sell", "mandi", "market", "price", "hold", "store", "rate", "when to sell"])
    is_pest = any(w in q_lower for w in ["insect", "pest", "bug", "worm", "aphid", "termite", "borer", "larvae", "infest"])

    # ── Category A: Fertilizer Guidance (Stage-Specific Hard Constraints) ──
    if is_fertilizer:
        stage_lower = stage.lower()

        # 1. POST-HARVEST STAGE
        if "post-harvest" in stage_lower or "harvested" in stage_lower:
            answer = (
                f"Your {crop} crop is currently in the Post-harvest stage, so chemical fertilizer (such as Urea or DAP) "
                f"should NOT be applied to this harvested crop. Instead, focus on soil testing, field preparation, and "
                "planning nutrient management for your next upcoming crop."
            )
            why = (
                f"The current {crop} production cycle is complete (detected stage: Post-harvest). {soil_provenance_note}. "
                f"Applying top-dressing or basal chemical fertilizer to a finished crop field would result in complete "
                f"nutrient loss and economic waste. Upcoming seasonal rotation requires soil recharge."
            )
            what_to_do = [
                "Do not apply Urea, DAP, or chemical fertilizers now, as there is no standing wheat crop to absorb nutrients.",
                "Collect representative soil samples from 8–10 spots across the field and submit them to KVK Lucknow or your local agriculture lab for an updated Soil Health Card.",
                f"Incorporate crop residues and broadcast 2–3 tonnes/acre of well-rotted Farmyard Manure (FYM) or compost during primary summer tillage to build low organic carbon ({oc_val}% regional estimate).",
                "Plan basal fertilizer requirements (DAP, MOP, and balanced nutrients) for your NEXT rotation crop (such as summer moong, paddy, or maize) based on soil test results.",
                "Ensure deep summer ploughing to expose soil-borne pests and weed seeds to sun sterilization."
            ]
            when_to_escalate = (
                "Visit KVK Lucknow or consult your Block Agricultural Officer with soil samples to get precise, customized "
                "fertilizer recommendations for your next crop."
            )
            data_used = [
                f"Crop Stage Phenology Model ({crop}, Post-harvest)",
                f"Regional Soil Survey (ICAR-NBSS&LUP {district} District, {soil_type} — Regional Estimate)",
                "Department of Agriculture Soil Health Card Protocol"
            ]
            confidence = "HIGH"  # Agronomic stage determination is conclusive: do not fertilize harvested crop
            possible_causes = ["Crop cycle completed (Post-harvest)", "Fallow period nutrient replenishment required"]

        # 2. PRE-SOWING / BASAL / GERMINATION STAGE
        elif any(s in stage_lower for s in ["pre-sowing", "basal", "germination"]):
            answer = (
                f"For your {crop}{variety_str} at the {stage} stage in {location}, apply basal nutrients "
                "(full dose of Phosphorus and Potassium, plus one-third Nitrogen) placed 4–5 cm below the seed during final land preparation."
            )
            why = (
                f"{soil_provenance_note}. In the {stage} stage, wheat seedlings require readily available Phosphorus "
                f"({p_val} kg/ha regional baseline vs optimal 20–40 kg/ha) for root establishment and Potassium ({k_val} kg/ha) for early vigor."
            )
            what_to_do = [
                "Apply the full basal dose of Phosphorus: 50 kg/acre DAP or 60 kg/acre NPK (12:32:16) placed in seed furrows.",
                "Apply 20–25 kg/acre Muriate of Potash (MOP) as basal application if recommended by your soil test.",
                "Apply one-third of the total Nitrogen requirement as basal Urea (25–30 kg/acre) during final seedbed preparation.",
                f"Incorporate 2–3 tonnes/acre of well-rotted FYM or compost into the soil 2–3 weeks before sowing to improve organic carbon ({oc_val}% regional estimate).",
                "Treat seed with Azotobacter and PSB biofertilizers (20g/kg seed) to enhance nutrient availability."
            ]
            when_to_escalate = (
                "If your soil pH is above 8.0 or shows salinity, consult KVK Lucknow regarding gypsum application and zinc sulphate (25 kg/acre) basal supplementation."
            )
            data_used = [
                f"Crop Stage Phenology Model ({crop}, {stage})",
                f"Regional Soil Survey (ICAR-NBSS&LUP {district} District, {soil_type} — Regional Estimate)",
                f"Open-Meteo 7-Day Weather Forecast ({int(max_rain_prob)}% rain probability)"
            ]
            confidence = "MEDIUM"
            possible_causes = ["Initial seedbed nutrient replenishment", "Phosphorus requirement for seedling root development"]

        # 3. TILLERING / SEEDLING / JOINTING (ACTIVE VEGETATIVE STAGE)
        elif any(s in stage_lower for s in ["tillering", "seedling", "jointing"]):
            rain_warning = ""
            if max_rain_prob >= 50:
                rain_warning = (
                    f" Note: An elevated {int(max_rain_prob)}% rainfall probability is forecast over the next 7 days. "
                    "Do NOT broadcast urea immediately before heavy showers to prevent leaching and surface runoff."
                )
            answer = (
                f"For your standing {crop}{variety_str} in the {stage} stage in {location}, apply a Nitrogen top-dressing "
                f"(split Urea application), ensuring the field has adequate moisture but no standing water.{rain_warning}"
            )
            why = (
                f"{soil_provenance_note}. During active {stage}, wheat has high nitrogen demand for tiller initiation and canopy development "
                f"(regional soil Nitrogen is {n_val} kg/ha vs 280–400 kg/ha optimal). Forecasted 7-day rainfall probability is {int(max_rain_prob)}%."
            )
            what_to_do = [
                "Wait for any heavy forecasted rains to subside and field drainage to clear before broadcasting nitrogenous fertilizer.",
                "Apply Urea @ 25–30 kg/acre as first split top-dressing after first irrigation (Crown Root Initiation) or moist soil conditions.",
                "Broadcast fertilizer uniformly in the afternoon when dew has completely dried off leaves to prevent chemical leaf scorching.",
                "If plants appear pale or stunted, consider a supplementary foliar spray of 0.5% Zinc Sulphate + 0.25% Lime solution.",
                "Avoid excessive single-dose nitrogen application, which increases vegetative lodging risk."
            ]
            when_to_escalate = (
                "If leaves show yellow striping or tillers remain stunted 7 days after top-dressing, bring a plant sample to KVK Lucknow for leaf tissue diagnosis."
            )
            data_used = [
                f"Crop Stage Phenology Model ({crop}, {stage})",
                f"Regional Soil Survey (ICAR-NBSS&LUP {district} District, {soil_type} — Regional Estimate)",
                f"Open-Meteo 7-Day Weather Forecast ({int(max_rain_prob)}% max rain probability)"
            ]
            confidence = "MEDIUM"
            possible_causes = ["Nitrogen requirement for active tiller development", "Regional soil nitrogen deficit"]

        # 4. FLOWERING / HEADING / BOOTING / GRAIN FILLING / MATURITY
        else:
            answer = (
                f"Your {crop} crop is in the {stage} stage. Soil application of granular Urea or DAP is NOT recommended at this reproductive stage, "
                "as late soil nitrogen promotes excessive vegetative greening, delays grain maturity, and increases fungal disease risk."
            )
            why = (
                f"At the {stage} stage, root nitrogen uptake declines and the plant mobilizes existing assimilates into developing earheads. "
                f"{soil_provenance_note}."
            )
            what_to_do = [
                "Cease all soil broadcasting of granular Urea and DAP.",
                "If terminal heat stress or mild nitrogen deficiency is observed, apply a mild foliar spray of 2% Urea (20g/L water) or 1% Potassium Nitrate (13:0:45) on a clear afternoon.",
                "Ensure light terminal irrigation during grain filling if high temperatures occur, but stop irrigation 10–12 days prior to harvest.",
                "Prepare combine harvesting equipment and inspect grain moisture as crop reaches physical maturity."
            ]
            when_to_escalate = (
                "If earheads show shriveled grains or glume discoloration, contact KVK Lucknow to differentiate terminal heat stress from fungal ear blight."
            )
            data_used = [
                f"Crop Stage Phenology Model ({crop}, {stage})",
                f"Regional Soil Survey (ICAR-NBSS&LUP {district} District, {soil_type} — Regional Estimate)",
                "ICAR Reproductive Wheat Nutrient Management Protocol"
            ]
            confidence = "HIGH"
            possible_causes = ["Reproductive stage nitrogen remobilization", "Granular fertilizer contraindicated at late stages"]

    # ── Category B: Yellowing Leaves (Stage-Aware) ──────────────────────────
    elif is_yellowing:
        stage_lower = stage.lower()
        if "post-harvest" in stage_lower or "harvested" in stage_lower:
            answer = (
                f"Your {crop} crop is currently marked as Post-harvest. Yellowing or browning of remaining straw/stubble after harvest "
                "is expected and normally does not require crop treatment. If the crop is actually standing, leaf yellowing can have several "
                "possible causes, including nutrient deficiency, water-related stress, or diseases such as Yellow Rust. "
                "Field inspection is needed to distinguish the cause."
            )
            why = (
                f"Detected crop stage is Post-harvest. Natural drying and senescence of wheat straw after harvest is expected. "
                "The regional soil baseline provides preliminary context, but it cannot confirm a nutrient deficiency in this specific field. "
                "An on-farm soil test and crop inspection are needed before making field-specific fertilizer decisions."
            )
            what_to_do = [
                "No chemical sprays or fertilizers are needed for harvested stubble or straw residue.",
                "Incorporate yellowed stubble into the soil with a disc harrow or rotavator to add organic matter and prepare for the next crop cycle.",
                "If managing a standing crop rather than harvested stubble: conduct an in-person field inspection to examine leaf symptoms.",
                "Uniform lower-leaf yellowing may be consistent with nitrogen deficiency, while yellow/orange stripe pustules can indicate Yellow Rust.",
                "Check irrigation and field drainage for temporary waterlogging that may restrict root nutrient uptake.",
                "Avoid applying chemical sprays or fertilizers without verified diagnosis; obtain an on-farm soil test to guide future fertilization."
            ]
            when_to_escalate = (
                "If managing a standing crop showing rapidly spreading yellowing, wilting, or yellow/orange stripe pustules, "
                "bring fresh leaf samples to KVK Lucknow or consult the local Agriculture Extension Officer for disease diagnosis."
            )
            data_used = [
                f"Crop Stage Phenology Model ({crop}, Post-harvest)",
                f"Regional Soil Survey (ICAR-NBSS&LUP {district} District — Regional Estimate)",
                "ICAR Post-Harvest Stubble Management Protocol"
            ]
            confidence = "MEDIUM"
            possible_causes = [
                "Expected post-harvest straw senescence / drying",
                "Unverified foliar symptom if crop is standing (requires field inspection)"
            ]
        else:
            answer = (
                f"For standing {crop} in the {stage} stage in {district}, leaf yellowing can have several possible causes, "
                "including nutrient deficiency, water-related stress, or diseases such as Yellow Rust. "
                "Field inspection is needed to distinguish the cause before any treatment is applied."
            )
            why = (
                "The regional soil baseline provides preliminary context, but it cannot confirm a nutrient deficiency in this specific field. "
                f"Weather forecasts indicate {int(max_rain_prob)}% rainfall probability, which can cause temporary soil saturation or favor disease development. "
                "An on-farm soil test and crop inspection are needed before making field-specific fertilizer decisions."
            )
            what_to_do = [
                "Inspect leaf patterns carefully across the field to identify symptom distribution.",
                "Uniform lower-leaf yellowing may be consistent with nitrogen deficiency, while yellow/orange stripe pustules can indicate Yellow Rust.",
                "Check irrigation and drainage conditions: waterlogging from heavy rainfall can suffocate root zones and cause temporary leaf chlorosis.",
                "Do not apply blanket chemical sprays or fertilizers without a confirmed field diagnosis.",
                "If symptoms are severe, widespread, or spreading rapidly, consult KVK Lucknow or your local Agriculture Extension Officer for physical diagnosis."
            ]
            when_to_escalate = (
                "If yellow/orange powdery stripe pustules are observed, or if yellowing spreads to more than 20% of the field within 48 hours, "
                "alert KVK Lucknow or the nearest Agriculture Extension Officer immediately."
            )
            data_used = [
                f"Crop Stage Phenology Model ({crop}, {stage})",
                f"Regional Soil Survey (ICAR-NBSS&LUP {district} District — Regional Estimate)",
                f"Open-Meteo Weather Forecast ({int(max_rain_prob)}% rainfall probability)",
                "ICAR Wheat Pathology Diagnostic Protocol"
            ]
            confidence = "MEDIUM"
            possible_causes = [
                "Suspected nitrogen deficiency (unverified without soil/tissue test)",
                "Temporary root saturation / waterlogging",
                "Suspected Yellow Rust (Puccinia striiformis, requires field confirmation)"
            ]

    # ── Category C: Selling / Mandi Timing ───────────────────────────────────
    elif is_selling:
        diff_7d = p7_point - int(current_modal)
        
        # Determine model direction label
        if diff_7d < -15:
            model_direction = "lower"
        elif diff_7d > 15:
            model_direction = "higher"
        else:
            model_direction = "near-flat"

        # Dynamically formulate recommendation based on data signals
        if diff_7d < -15:
            recommendation_action = "Selling now or within a short window (1–3 days) is favoured based on the available market model"
            decision_summary = (
                f"{market_ref_str} The 7-day XGBoost model indicates lower prices (point estimate: Rs.{p7_point:,}/q, "
                f"range: Rs.{p7_min:,}–Rs.{p7_max:,}/q), which is Rs.{abs(diff_7d)}/q below the current reference price. "
                f"Holding produce adds cumulative storage expenses (approx. Rs.35/q over 7 days), while high rainfall probability "
                f"({int(max_rain_prob)}%) presents contextual storage moisture risk."
            )
            price_decision_impact = "Favours near-term selling (1–3 days) to protect realization against projected price erosion."
            holding_decision_impact = "Holding increases downside by adding Rs.35/q in cumulative storage expenses without offsetting price gain."
            weather_decision_impact = "Favours prompt disposal/marketing before potential moisture and storage damage occurs."
        elif diff_7d > 50 and max_rain_prob < 40:
            recommendation_action = "Holding produce for 7–15 days may be justified if you have secure, dry storage"
            decision_summary = (
                f"{market_ref_str} The 7-day XGBoost model projects higher prices (point estimate: Rs.{p7_point:,}/q, "
                f"range: Rs.{p7_min:,}–Rs.{p7_max:,}/q), offering potential price appreciation of +Rs.{diff_7d}/q "
                f"that exceeds storage costs (Rs.35/q/week) under favourable, low-risk weather conditions ({int(max_rain_prob)}% rain probability)."
            )
            price_decision_impact = "Supports holding for potential price appreciation."
            holding_decision_impact = "Projected gain exceeds estimated holding costs (Rs.35/q)."
            weather_decision_impact = "Low rain probability provides a safe window for dry storage."
        else:
            recommendation_action = "A hold or selective selling approach is indicated based on current data"
            decision_summary = (
                f"{market_ref_str} The 7-day XGBoost model indicates near-flat prices (point estimate: Rs.{p7_point:,}/q, "
                f"range: Rs.{p7_min:,}–Rs.{p7_max:,}/q). Farmers with certified dry, sealed storage may hold, "
                f"while those facing moisture risk from {int(max_rain_prob)}% forecast rain should consider selling to avoid storage expenses."
            )
            price_decision_impact = "Near-flat price outlook provides no clear appreciation margin."
            holding_decision_impact = "Holding costs accumulate without expected price compensation."
            weather_decision_impact = "Storage protection quality determines holding viability."

        answer = f"{recommendation_action}. {decision_summary}"

        pred_15_clause = f", 15-day range: Rs.{p15_min:,}–Rs.{p15_max:,}/q (point: Rs.{p15_point:,}/q)" if p15_point else ""
        weather_risk_note = (
            f"High rainfall probability ({int(max_rain_prob)}%) may increase storage/moisture-management risk if grain or storage facilities are not adequately protected."
            if max_rain_prob >= 50 else
            f"Forecasted rainfall probability is {int(max_rain_prob)}%, presenting low contextual storage moisture risk."
        )

        why = (
            f"• Signal: Reference Market Price | Value: Rs.{int(current_modal):,}/q ({market_provenance_label}) | Direction: {vs_avg_pct:+.1f}% relative to Historical dataset average (Rs.{int(hist_avg):,}/q across 349 observations) | Decision impact: Establishes current liquidation baseline.\n"
            f"• Signal: Price Volatility Range (7-day Model Range) | Value: Rs.{p7_min:,}–Rs.{p7_max:,}/q | Direction: Bounds expected market movement | Decision impact: Defines price volatility envelope.\n"
            f"• Signal: Price Outlook (7-day Model Point) | Value: Rs.{p7_point:,}/q{pred_15_clause} | Direction: {model_direction} ({diff_7d:+} Rs/q vs reference price) | Decision impact: {price_decision_impact}\n"
            f"• Signal: Storage Cost | Value: Rs.5/q/day (Rs.35/q over 7 days) | Direction: Cumulative carrying expense | Decision impact: {holding_decision_impact}\n"
            f"• Signal: Weather Risk | Value: {int(max_rain_prob)}% rainfall probability ({weather_risk_note}) | Direction: Contextual moisture risk | Decision impact: {weather_decision_impact}"
        )

        what_to_do = [
            f"Compare current local mandi quotes across {market_name} and nearby centers (such as Unnao or Kanpur Nagar) before arranging transport.",
            "Verify grain moisture is strictly below 10–12% before bagging or transport to avoid moisture deductions at the mandi.",
            "Factor in net margins after deducting transport costs (approx. Rs.18–45/q for nearby mandis) and loading expenses.",
            "Obtain official electronic gate passes and weighbridge slips through e-NAM / mandi counter for payment protection.",
            "If choosing to hold, ensure storage structures are elevated, dry, and hermetically sealed against forecasted rainfall moisture."
        ]
        when_to_escalate = (
            f"Contact the {market_name} Mandi Secretary or call the Kisan Call Centre (1800-180-1551) to verify live daily arrivals, active buyer participation, and actual spot transactions before dispatching trucks."
        )
        data_used = [
            f"{market_name} Mandi Reference Price (Rs.{int(current_modal):,}/q — {market_provenance_label})",
            f"XGBoost Price Prediction Horizon (7d: Rs.{p7_min:,}–Rs.{p7_max:,}/q, point: Rs.{p7_point:,}/q — MODEL_PREDICTION)",
            f"Mandi Price History (Historical dataset average: Rs.{int(hist_avg):,}/q — {market_provenance_label})",
            f"Open-Meteo Weather Forecast ({int(max_rain_prob)}% rainfall probability — Contextual Risk Signal)"
        ]
        confidence = "MEDIUM"  # Contextual decision support based on prototype seed and model prediction
        possible_causes = [
            f"Model-projected {model_direction} near-term price trend ({diff_7d:+} Rs/q)",
            "Storage and moisture-management holding risks offset potential gains" if diff_7d < 0 else "Holding margin assessment"
        ]

    # ── Category D: Insect Infestation ──────────────────────────────────────
    elif is_pest:
        stage_lower = stage.lower()
        if "post-harvest" in stage_lower or "harvested" in stage_lower:
            answer = (
                f"For harvested {crop} in storage in {district}, focus on non-chemical grain protection: "
                "proper grain drying, thorough storage sanitation, and regular inspection for stored-grain pests "
                "(such as Rice Weevil, Lesser Grain Borer, and Rust-red Flour Beetle). "
                "Do not apply unverified chemical treatments without authoritative product label or extension guidance."
            )
            rain_risk_note = (
                f"The current forecast shows a high rainfall probability ({int(max_rain_prob)}%). "
                "Poorly sealed or humid storage areas may therefore face increased moisture risk, so keeping grain and storage structures "
                "dry and well sealed is important."
            ) if max_rain_prob >= 40 else (
                f"The current forecast shows a rainfall probability of {int(max_rain_prob)}%. "
                "Keeping grain and storage structures dry, clean, and well sealed is important."
            )
            why = (
                f"Detected crop stage is Post-harvest. {rain_risk_note}"
            )
            what_to_do = [
                "Properly dry grain in the sun until moisture is below 10–12% before bagging or storage.",
                "Clean and sanitize the storage room, bins, and equipment before storing grain. If chemical treatment is required, use only a pesticide or fumigant registered and labelled for the identified stored-grain pest and storage situation, and follow the product label or guidance from the local KVK/Agriculture Department.",
                "Inspect grain regularly for insects, heating, powdering, or mould.",
                "Keep storage areas dry and well sealed against external rainwater ingress or damp ground moisture.",
                "Use appropriate sealed/hermetic storage where suitable (such as airtight metal bins or hermetic bags) to limit insect development.",
                "Plan field cleaning, residue management, and soil preparation for your next crop cycle without applying fertilizer to the harvested field."
            ]
            when_to_escalate = (
                "If severe insect infestation, visible grain heating, powdering, or mould occurs in storage, escalate to KVK Lucknow or the Agriculture Department for physical inspection and authorized chemical/fumigation decisions."
            )
            data_used = [
                f"Crop Stage Phenology Model ({crop}, Post-harvest)",
                "ICAR Stored Grain Integrated Pest Management Protocol",
                f"Open-Meteo Rainfall Forecast ({int(max_rain_prob)}% rain probability — storage moisture risk signal)"
            ]
            confidence = "MEDIUM"
            possible_causes = [
                "Stored grain insect presence (e.g. Rice Weevil, Lesser Grain Borer)",
                "Moisture risk in poorly sealed storage structures"
            ]
        else:
            answer = (
                f"For standing {crop} in the {stage} stage in {district}, monitor for sap-sucking insects (such as aphids) "
                "and subterranean root pests (such as termites). Regularly scout the field and prioritize cultural and non-chemical controls before considering chemical intervention."
            )
            why = (
                f"Forecasted rainfall probability is {int(max_rain_prob)}% with field microclimate variations. "
                f"Field scouting is required to verify actual insect pressure and determine if Economic Threshold Levels are exceeded in {crop}."
            )
            what_to_do = [
                "Scout 20 random plants across the field. Closely examine leaf undersides, central shoots, and earheads for insect colonies.",
                "Check Economic Threshold Levels (ETL): For aphids, intervention is generally warranted only if counts exceed 10–15 insects per earhead or tiller.",
                "Conserve beneficial natural predators such as ladybird beetles and hoverfly larvae that naturally regulate aphid populations.",
                "Maintain weed-free field borders and proper drainage to minimize pest harborage.",
                "If chemical intervention is deemed necessary after scouting, use only a pesticide registered and labelled for the target pest on wheat, strictly adhering to manufacturer product label instructions or guidance from KVK Lucknow / Agriculture Department."
            ]
            when_to_escalate = (
                "If pest populations exceed economic thresholds or cause rapid plant damage, bring plant specimens to KVK Lucknow or consult the local Agriculture Officer for diagnosis and approved intervention."
            )
            data_used = [
                f"Crop Stage Phenology Model ({crop}, {stage})",
                f"Wheat Entomological Pest Protocol ({district}, {state})",
                f"Open-Meteo Rainfall Forecast ({int(max_rain_prob)}% rain probability)"
            ]
            confidence = "MEDIUM"
            possible_causes = ["Potential aphid colony presence", "Subterranean root damage", "Field microclimate variation"]

    # ── General Fallback / Other Inquiries ──────────────────────────────────
    else:
        answer = (
            f"Based on your {crop} farm profile in {location}, {state} (current stage: {stage}), "
            f"maintain regular field scouting, ensure adequate drainage ahead of forecasted rain ({int(max_rain_prob)}% probability), "
            "and adhere to standard package of practices."
        )
        why = (
            f"Guidance is calibrated using your {soil_source_label.lower().replace('_', ' ')} soil data "
            f"(pH: {soil_params.get('ph', {}).get('value', 7.5)}, Nitrogen: {n_val} kg/ha) and Open-Meteo local weather forecasts."
        )
        what_to_do = [
            f"Inspect field weekly for moisture status, weeds, and signs of nutrient deficit in {crop}.",
            "Maintain soil organic carbon by incorporating crop residues and organic compost.",
            "Monitor local mandi arrivals and price trends before planning harvest disposal."
        ]
        when_to_escalate = (
            "For specialized crop protection or unexpected symptoms, consult local agricultural extension officers or call the national Kisan Call Centre."
        )
        data_used = [
            f"ICAR Soil Database ({district} — Regional Estimate)",
            f"Open-Meteo Weather Forecast ({int(max_rain_prob)}% rain probability)",
            f"Crop Phenology Model ({crop}, {stage})"
        ]
        confidence = "MEDIUM"
        possible_causes = ["General crop maintenance inquiry"]

    # ── Optional: Try Gemini Enhancement if API Key is Present ─────────────
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    engine_used = "krishi_data_engine"

    if gemini_key:
        try:
            import httpx
            prompt = (
                f"You are an expert Indian agricultural advisor (AI Agronomist). A farmer asks: '{question}'\n\n"
                f"HARD AGRONOMIC & SAFETY CONSTRAINTS:\n"
                f"- Crop: {crop}{variety_str}, Location: {location}, {district}, {state}\n"
                f"- DETECTED STAGE: {stage}. If stage is Post-harvest, NEVER recommend top-dressing or fertilizer as though the harvested crop is still growing. Recommend soil testing, field prep, and next-crop planning.\n"
                f"- MARKET PROVENANCE: Market reference price is Rs.{int(current_modal)}/q ({market_provenance_label}). Do NOT claim this is a live spot price if labelled HISTORICAL_SEED. Historical dataset average is Rs.{int(hist_avg)}/q (do NOT call it 5-year average).\n"
                f"- ML PREDICTION: 7-day model range is Rs.{p7_min}–Rs.{p7_max}/q (point: Rs.{p7_point}/q). Include these actual numbers in reasoning.\n"
                f"- WEATHER RISK: Treat {int(max_rain_prob)}% rain probability only as a contextual moisture risk signal.\n"
                f"- CONFIDENCE: If advising on selling based on prototype seed and model prediction, confidence must be MEDIUM.\n"
                f"- PEST SAFETY: Do NOT generate specific pesticide names, concentrations, mixing ratios, or application dosages. Prefer non-chemical guidance (drying, sanitation, inspection, hermetic storage).\n"
                f"- Soil Source: {soil_source_label} ({soil_provenance_note})\n"
                f"- Soil NPK: N={n_val} kg/ha (optimal 280-400), P={p_val} kg/ha, K={k_val} kg/ha, OC={oc_val}%\n"
                f"- Weather: 7-day max rain prob={int(max_rain_prob)}%\n\n"
                "Return a JSON object with keys: answer (short direct answer for farmer), why (data signals), "
                "what_to_do (array of 3-5 practical steps matching the detected stage), when_to_escalate (clear condition), "
                "data_used (array of sources), confidence ('HIGH' or 'MEDIUM'). No markdown code blocks."
            )
            resp = httpx.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=6.0,
            )
            if resp.status_code == 200:
                raw_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text.split("```json", 1)[1].split("```", 1)[0].strip()
                elif raw_text.startswith("```"):
                    raw_text = raw_text.split("```", 1)[1].split("```", 1)[0].strip()
                parsed = json.loads(raw_text)
                if parsed.get("answer"):
                    # Validate Gemini didn't violate stage constraint, pesticide dosage safety, or market provenance
                    gemini_answer = str(parsed["answer"]).strip()
                    gemini_text = (gemini_answer + " " + str(parsed.get("why", "")) + " " + " ".join(str(x) for x in parsed.get("what_to_do", []))).lower()
                    has_stage_violation = ("post-harvest" in stage.lower() and any(w in gemini_text for w in ["top-dress", "top dress", "tillering"]))
                    has_pesticide_violation = any(w in gemini_text for w in ["malathion", "chlorpyrifos", "thiamethoxam", "dimethoate", "ml/l", "g/l", "ml per", "g per", "1:100", "% ec", "% wg", "ec @", "wg @"])
                    has_seed_violation = (not is_live_market and any(w in gemini_text for w in ["today's lucknow mandi spot price", "live spot price"]))
                    has_five_year_violation = ("5-year average" in gemini_text or "5-year historical average" in gemini_text)
                    if has_stage_violation or has_pesticide_violation or has_seed_violation or has_five_year_violation:
                        pass  # Reject Gemini response if it violated safety or provenance
                    else:
                        answer = gemini_answer
                        why = str(parsed.get("why", why)).strip()
                        if isinstance(parsed.get("what_to_do"), list):
                            what_to_do = parsed["what_to_do"]
                        if parsed.get("when_to_escalate"):
                            when_to_escalate = str(parsed["when_to_escalate"]).strip()
                        confidence = str(parsed.get("confidence", confidence)).upper()
                        engine_used = "gemini"
        except Exception:
            engine_used = "krishi_data_engine"

    local_resources = [
    f"KVK / Agriculture Extension Office ({district}): Contact your nearest local office for field verification.",
    "Kisan Call Centre: 1800-180-1551 (Toll-Free)",
    f"District Agriculture Office ({district})"
]
    
    result = {
        "answer": answer,
        "why": why,
        "what_to_do": what_to_do,
        "when_to_escalate": when_to_escalate,
        "data_used": data_used,
        "confidence": confidence,
        "possible_causes": possible_causes,
        "recommended_actions": what_to_do,
        "farm_context": {
            "crop": crop + (f" ({variety})" if variety else ""),
            "stage": stage,
            "location": f"{location}, {district}",
            "soil_source": soil_source_label
        },
        "local_resources": local_resources,
        "expert_verification_required": True,
        "needs_field_verification": True,
        "verification_status": "Needs Field Verification",
        "engine": engine_used,
        "disclaimer": (
            "This guidance is generated for decision support using regional and remote data. "
            "Always consult your local Krishi Vigyan Kendra or Agriculture Officer before major chemical applications."
        ),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "response": {
            "answer": answer,
            "preliminary_guidance": answer,
            "possible_causes": possible_causes,
            "recommended_actions": what_to_do,
            "confidence": confidence,
            "why": why,
            "when_to_escalate": when_to_escalate,
            "data_used": data_used,
            "expert_verification_required": True,
            "local_resources": local_resources
        }
    }

    return result
