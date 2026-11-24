"""
Explainability Service — Dynamic, Data-Driven Agricultural Intelligence
======================================================================
Generates fully dynamic, evidence-backed explanations from real data signals.

All outputs adapt dynamically to:
- User's farm context (crop, acreage, stage, location)
- Market data provenance (LIVE vs HISTORICAL_SEED)
- Actual averaging periods (dynamically calculated from observation count/years)
- ML model predictions and confidence
- Weather forecasts and risk scores
- Strict numerical reconciliation across financial scenarios

Zero hardcoded price, cost, or penalty figures.
"""

from __future__ import annotations
import os
from datetime import datetime, date


def _format_historical_avg_label(market: dict | None) -> str:
    """Dynamically determine the historical average label from actual dataset metadata."""
    if not market or not market.get("historical"):
        return "historical average (insufficient data)"
    hist = market.get("historical", {})
    years = hist.get("years")
    points = hist.get("data_points")
    if years == 5 and (not points or points <= 265):
        return "5-year historical average"
    elif points and points > 0:
        yr_clause = f" across {years} years" if years else ""
        return f"historical dataset average ({points} observations{yr_clause})"
    elif years and years > 0:
        return f"{years}-year historical average"
    return "historical dataset average"


def _format_market_reference_label(current_price: float, market: dict | None) -> tuple[str, str]:
    """
    Generate dynamic market reference label and short description based on provenance.
    Returns: (long_label, short_label)
    """
    data_source = market.get("data_source", {}) if market else {}
    src_type = str(data_source.get("type", "HISTORICAL_SEED")).upper()
    latest_date = (
        market.get("current", {}).get("date")
        or data_source.get("latest_date")
        or data_source.get("date_range", "").split(" to ")[-1]
        if market else None
    )
    date_str = f", record date: {latest_date}" if latest_date else ""

    if src_type == "LIVE":
        long_label = f"today's live mandi reference price of Rs.{int(current_price):,}/q{f' ({latest_date})' if latest_date else ''}"
        short_label = f"live mandi price (Rs.{int(current_price):,}/q)"
    else:
        long_label = f"the latest available reference price in the historical dataset of Rs.{int(current_price):,}/q (HISTORICAL_SEED{date_str})"
        short_label = f"historical reference price (Rs.{int(current_price):,}/q, HISTORICAL_SEED)"

    return long_label, short_label


def get_explanation(
    decision: dict,
    risk: dict,
    market: dict | None = None,
    price_prediction: dict | None = None,
    weather: dict | None = None,
    farm: dict | None = None,
) -> dict:
    """
    Build explainability content dynamically from real analysis data.
    """
    # ── Detect unsupported-market crops ──────────────────────────────────
    # When market data is MARKET_UNSUPPORTED we must not show any market
    # signals, prices, or predictions — they would all be fabricated.
    market_src_type = (market or {}).get("data_source", {}).get("type", "HISTORICAL_SEED")
    market_is_unsupported = market_src_type == "MARKET_UNSUPPORTED"

    crop_name = (farm or {}).get("crop") or "this crop"

    if market_is_unsupported:
        # Weather signals are still real and useful
        agri_risk = weather.get("agricultural_risk", {}) if weather else {}
        weather_level = agri_risk.get("overall_level", "UNKNOWN")
        forecast = weather.get("forecast_7day", []) if weather else []
        max_rain_prob = max((f.get("rain_probability_pct", 0) for f in forecast), default=0)
        weather_risk_score = risk.get("weather_risk", {}).get("score", 0)

        data_signals = []
        if weather and forecast:
            rain_label = "elevated risk" if max_rain_prob >= 60 else ("moderate risk" if max_rain_prob >= 30 else "low risk")
            data_signals.append({
                "signal": "7-day rainfall probability",
                "value": f"{int(max_rain_prob)}% ({rain_label})",
                "direction": "negative" if max_rain_prob >= 60 else ("neutral" if max_rain_prob >= 30 else "positive"),
                "weight": "HIGH",
                "impact": (
                    f"Forecasted rainfall creates storage and transport risk ({weather_risk_score}/100 weather risk score)."
                    if max_rain_prob >= 40 else
                    f"Favourable weather conditions ({weather_risk_score}/100 risk score)."
                ),
            })

        unsupported_reason = (market or {}).get("data_source", {}).get("reason", "")
        data_signals.append({
            "signal": "Market Intelligence",
            "value": "Not available in this prototype",
            "direction": "neutral",
            "weight": "HIGH",
            "impact": (
                f"Market Intelligence for {crop_name} is not yet available in this prototype. "
                f"{crop_name} market prediction is planned for the next version."
            ),
        })

        data_used = []
        if weather:
            w_status = weather.get("data_source", {}).get("status", "LIVE")
            data_used.append(f"7-day weather forecast — Open-Meteo GFS model ({w_status} data)")
        data_used.append(f"Market data for {crop_name}: NOT AVAILABLE (prototype limitation — Wheat only)")
        data_used.append("Regional soil database — ICAR-NBSS&LUP district survey")
        data_used.append("Crop phenological calendar — days-after-sowing stage model")

        return {
            "data_signals": data_signals,
            "data_used": data_used,
            "reasoning_steps": [
                f"Market Intelligence for {crop_name} is not yet available in this prototype.",
                f"{crop_name} market prediction is planned for the next version.",
                "Soil Intelligence, Weather Risk analysis, and Expert consultation are fully available.",
            ],
            "conclusion": (
                f"Market Intelligence for {crop_name} is not yet available in this prototype. "
                "Financial scenario analysis requires crop-specific market price data. "
                f"{crop_name} market prediction is planned for the next version. "
                "Please use Soil Intelligence and Expert consultation for agronomic guidance."
            ),
            "confidence": "N/A",
            "decision_confidence": "N/A",
            "prediction_confidence": "UNAVAILABLE",
            "data_quality_overall": "PARTIAL",
            "important_note": (
                "Market price data is not available for this crop in the current prototype version. "
                "Consult local mandi commission agents for current prices."
            ),
            "engine": "rule_based",
            "gemini_available": bool(os.getenv("GEMINI_API_KEY", "")),
            "market_prediction_available": False,
        }

    # ── Extract key signals from real data ───────────────────────────────
    recommendation = decision.get("recommendation", {})
    action = recommendation.get("action", "MONITOR")
    scenarios = decision.get("scenarios", {})

    # Weather signals
    agri_risk = weather.get("agricultural_risk", {}) if weather else {}
    rain_risk_score = agri_risk.get("rainfall_risk", {}).get("score", 0)
    weather_level = agri_risk.get("overall_level", "UNKNOWN")
    forecast = weather.get("forecast_7day", []) if weather else []
    max_rain_prob = max((f.get("rain_probability_pct", 0) for f in forecast), default=0)

    # Market signals & provenance
    hist_stats = market.get("historical", {}).get("statistics", {}) if market else {}
    seasonal = market.get("historical", {}).get("seasonal_trend", {}) if market else {}
    current_vs_avg = hist_stats.get("current_vs_avg_pct", 0)
    seasonal_direction = seasonal.get("direction", "STABLE")
    current_price = market.get("current", {}).get("modal_price", 0) if market else 0
    std_price = hist_stats.get("std_price", 0)
    market_source_type = market.get("data_source", {}).get("type", "HISTORICAL_SEED") if market else "HISTORICAL_SEED"

    # Provenance-sensitive wording
    long_market_ref, short_market_ref = _format_market_reference_label(current_price, market)
    hist_avg_label = _format_historical_avg_label(market)

    # Risk signals
    overall_risk = risk.get("overall_risk", {}).get("score", 50)
    weather_risk_score = risk.get("weather_risk", {}).get("score", 0)
    market_risk_score = risk.get("market_risk", {}).get("score", 0)

    # Decision financials
    sell_now_net = scenarios.get("sell_now", {}).get("net_realization", 0)
    wait_7d_net = scenarios.get("wait_7d", {}).get("net_realization", 0)
    wait_15d_net = scenarios.get("wait_15d", {}).get("net_realization", 0)
    weather_penalty_7d = scenarios.get("wait_7d", {}).get("weather_risk_penalty", 0)
    storage_cost_7d = scenarios.get("wait_7d", {}).get("storage_cost", 0)
    net_diff_7d = wait_7d_net - sell_now_net

    # Prediction signals
    pred_7d = (price_prediction or {}).get("prediction_7d", {}) if price_prediction and not price_prediction.get("insufficient_data") else {}
    pred_conf = pred_7d.get("confidence_pct", 0)
    pred_max = pred_7d.get("max_price") or pred_7d.get("max") or 0
    pred_min = pred_7d.get("min_price") or pred_7d.get("min") or 0
    pred_point = float(pred_7d.get("point_estimate") or pred_7d.get("point") or 0)
    model_mape = (price_prediction or {}).get("model_info", {}).get("mape_pct", 0) if price_prediction else 0

    # Total quantity
    total_qtl = float(decision.get("estimated_yield_qtl", 0))
    if total_qtl <= 0 and farm:
        acres = float(farm.get("farm_area_acres", 1.0))
        total_qtl = acres * 15.0
    elif total_qtl <= 0 and current_price > 0:
        total_qtl = float(sell_now_net / current_price) if current_price else 15.0

    # ── 1. Dynamic Key Signals (Signal → Value → Weight → Direction → Decision Impact) ─
    data_signals = []

    # Signal A: Seasonal price trend
    month_name = datetime.now().strftime("%B")
    if seasonal_direction:
        trend_labels = {
            "INCREASING": f"Rising ({month_name} historical strength)",
            "DECREASING": f"Declining ({month_name} seasonal pressure)",
            "STABLE": f"Stable ({month_name} flat seasonal trend)"
        }
        seasonal_val = trend_labels.get(seasonal_direction, f"{seasonal_direction.capitalize()} trend")
        seasonal_dir = "positive" if seasonal_direction == "INCREASING" else ("negative" if seasonal_direction == "DECREASING" else "neutral")
        seasonal_impact = (
            "Seasonal supply contraction supports price appreciation over holding horizons."
            if seasonal_direction == "INCREASING" else
            ("Seasonal market arrivals exert downward pressure, favouring prompt liquidation."
             if seasonal_direction == "DECREASING" else
             "Seasonal patterns show minimal directional bias.")
        )
    else:
        seasonal_val = "DATA UNAVAILABLE"
        seasonal_dir = "neutral"
        seasonal_impact = "No seasonal trend data available."
    data_signals.append({
        "signal": "Seasonal price trend",
        "value": seasonal_val,
        "direction": seasonal_dir,
        "weight": "HIGH",
        "impact": seasonal_impact,
    })

    # Signal B: 7-day rainfall probability / weather risk
    if weather and forecast and max_rain_prob is not None:
        rain_label = "elevated risk" if max_rain_prob >= 60 else ("moderate risk" if max_rain_prob >= 30 else "low risk")
        rain_val = f"{int(max_rain_prob)}% ({rain_label})"
        rain_dir = "negative" if max_rain_prob >= 60 else ("neutral" if max_rain_prob >= 30 else "positive")
        weather_impact = (
            f"Forecasted rainfall creates storage moisture and transport risk ({weather_risk_score}/100 weather risk score)."
            if max_rain_prob >= 40 else
            f"Favourable weather conditions minimize grain storage and handling hazards ({weather_risk_score}/100 risk score)."
        )
    else:
        rain_val = "DATA UNAVAILABLE"
        rain_dir = "neutral"
        weather_impact = "Weather forecast signals unavailable."
    data_signals.append({
        "signal": "7-day rainfall probability",
        "value": rain_val,
        "direction": rain_dir,
        "weight": "HIGH",
        "impact": weather_impact,
    })

    # Signal C: Price vs Historical Dataset Average
    if market and current_price > 0 and current_vs_avg is not None:
        pct_prefix = "+" if current_vs_avg > 0 else ""
        comp_str = "above mean" if current_vs_avg > 0 else ("below mean" if current_vs_avg < 0 else "at mean")
        avg_val = f"{pct_prefix}{current_vs_avg:.1f}% ({comp_str})"
        avg_dir = "positive" if current_vs_avg > 0 else ("negative" if current_vs_avg < 0 else "neutral")
        avg_impact = (
            f"Current price is {abs(current_vs_avg):.1f}% above {hist_avg_label}, offering an attractive exit window."
            if current_vs_avg > 5 else
            (f"Current price is {abs(current_vs_avg):.1f}% below {hist_avg_label}; holding could recover towards the mean if carrying costs permit."
             if current_vs_avg < -5 else
             f"Current price aligns closely with {hist_avg_label}.")
        )
    else:
        avg_val = "DATA UNAVAILABLE"
        avg_dir = "neutral"
        avg_impact = "Historical price comparison unavailable."
    data_signals.append({
        "signal": f"Current price vs {hist_avg_label}",
        "value": avg_val,
        "direction": avg_dir,
        "weight": "MEDIUM",
        "impact": avg_impact,
    })

    # Signal D: ML Price Prediction Horizon
    if pred_point > 0 and current_price > 0:
        pred_diff = int(round(pred_point - current_price))
        pred_val = f"Rs.{int(pred_point):,}/q ({pred_diff:+} Rs/q)"
        pred_dir = "positive" if pred_diff > 0 else ("negative" if pred_diff < 0 else "neutral")
        pred_impact = (
            f"7-day ML projection indicates price appreciation (+Rs.{pred_diff:,}/q) towards Rs.{int(pred_point):,}/q."
            if pred_diff > 0 else
            (f"7-day ML projection indicates price decline (-Rs.{abs(pred_diff):,}/q) towards Rs.{int(pred_point):,}/q."
             if pred_diff < 0 else
             f"7-day ML projection indicates flat price movement near Rs.{int(current_price):,}/q.")
        )
    else:
        pred_val = f"Rs.{int(std_price)}/q std dev" if std_price > 0 else "DATA UNAVAILABLE"
        pred_dir = "neutral"
        pred_impact = "Model projection signal unavailable."
    data_signals.append({
        "signal": "7-day model price outlook",
        "value": pred_val,
        "direction": pred_dir,
        "weight": "HIGH" if pred_point > 0 else "MEDIUM",
        "impact": pred_impact,
    })

    # ── 2. Traceable Verified Data Sources ────────────────────────────────
    data_used = []
    if market and market.get("data_source"):
        pts = market.get("historical", {}).get("data_points", "N/A")
        dr = market.get("data_source", {}).get("date_range", "")
        dr_clause = f" ({dr})" if dr else ""
        source_prov = market.get("data_source", {}).get("type", "HISTORICAL_SEED")
        prov_desc = "live mandi feed" if source_prov == "LIVE" else "AGMARKNET calibrated historical seed"
        data_used.append(f"{pts} historical mandi observations{dr_clause} — {prov_desc}")
    if weather:
        w_status = weather.get("data_source", {}).get("status", "LIVE")
        data_used.append(f"7-day weather forecast — Open-Meteo GFS model ({w_status} data)")
    if price_prediction and not price_prediction.get("insufficient_data"):
        model_type = price_prediction.get("model_info", {}).get("type", "XGBoost Regressor")
        data_used.append(f"Price prediction model ({model_type}) — trained on verified historical arrivals")
    data_used.append("Regional soil database — ICAR-NBSS&LUP district survey")
    data_used.append("Crop phenological calendar — days-after-sowing stage model")
    data_used.append("Seasonal price index — month-of-year multi-year distribution")

    # ── 3. Step-by-Step Numerical Reasoning (Fully Reconciled) ───────────
    reasoning_steps = _build_reasoning_steps(
        action=action,
        current_price=current_price,
        current_vs_avg=current_vs_avg,
        seasonal_direction=seasonal_direction,
        weather_risk_score=weather_risk_score,
        max_rain_prob=max_rain_prob,
        weather_penalty_7d=weather_penalty_7d,
        storage_cost_7d=storage_cost_7d,
        net_diff_7d=net_diff_7d,
        sell_now_net=sell_now_net,
        wait_7d_net=wait_7d_net,
        pred_conf=pred_conf,
        pred_min=pred_min,
        pred_max=pred_max,
        pred_point=pred_point,
        total_qtl=total_qtl,
        overall_risk=overall_risk,
        market_source_type=market_source_type,
        hist_avg_label=hist_avg_label,
        long_market_ref=long_market_ref,
        month_name=month_name,
    )

    # ── 4. Recommendation Rationale (Conclusion) ──────────────────────────
    conclusion = _build_conclusion(
        action=action,
        weather_level=weather_level,
        seasonal_direction=seasonal_direction,
        current_vs_avg=current_vs_avg,
        net_diff_7d=net_diff_7d,
        current_price=current_price,
        pred_point=pred_point,
        weather_risk_score=weather_risk_score,
        sell_now_net=sell_now_net,
        wait_7d_net=wait_7d_net,
        market_source_type=market_source_type,
        hist_avg_label=hist_avg_label,
        long_market_ref=long_market_ref,
    )

    # ── 5. Confidence Disaggregation ──────────────────────────────────────
    # Concept A: ML model prediction confidence
    if price_prediction and not price_prediction.get("insufficient_data"):
        if model_mape < 5 or pred_conf >= 80:
            pred_confidence = "HIGH"
        elif model_mape <= 10 or pred_conf >= 55:
            pred_confidence = "MEDIUM"
        else:
            pred_confidence = "LOW"
    else:
        pred_confidence = "UNAVAILABLE"

    # Concept B: Overall data quality rating
    is_weather_live = (weather or {}).get("data_source", {}).get("status") == "LIVE"
    is_market_live = market_source_type == "LIVE"
    if is_weather_live and is_market_live:
        data_quality = "HIGH"
    elif is_weather_live or is_market_live:
        data_quality = "MEDIUM"
    else:
        data_quality = "MEDIUM"

    # Concept C: Decision confidence (from decision engine or synthesized)
    decision_confidence = recommendation.get("confidence")
    if not decision_confidence:
        if data_quality == "HIGH" and pred_confidence == "HIGH":
            decision_confidence = "HIGH"
        elif data_quality == "LOW" or pred_confidence == "LOW":
            decision_confidence = "LOW"
        else:
            decision_confidence = "MEDIUM"

    # ── 6. Optional Gemini Enhancement ────────────────────────────────────
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    gemini_available = bool(gemini_key)
    if gemini_available:
        try:
            conclusion = _gemini_explanation(conclusion, reasoning_steps, action, gemini_key)
        except Exception:
            pass

    return {
        "data_signals": data_signals,
        "data_used": data_used,
        "reasoning_steps": reasoning_steps,
        "conclusion": conclusion,
        "confidence": decision_confidence,
        "decision_confidence": decision_confidence,
        "prediction_confidence": pred_confidence,
        "data_quality_overall": data_quality,
        "important_note": (
            "This is a decision-support estimate, not financial advice. "
            "Actual market prices, weather conditions, and crop outcomes may differ. "
            "Consult local agricultural officers and mandi commission agents before major decisions."
        ),
        "engine": "gemini" if (gemini_available and gemini_key) else "rule_based",
        "gemini_available": gemini_available,
    }


def _build_reasoning_steps(
    action: str,
    current_price: float,
    current_vs_avg: float,
    seasonal_direction: str,
    weather_risk_score: int,
    max_rain_prob: int,
    weather_penalty_7d: float,
    storage_cost_7d: float,
    net_diff_7d: float,
    sell_now_net: float,
    wait_7d_net: float,
    pred_conf: int,
    pred_min: int,
    pred_max: int,
    pred_point: float,
    total_qtl: float = 0.0,
    overall_risk: int = 50,
    market_source_type: str = "HISTORICAL_SEED",
    hist_avg_label: str = "historical dataset average",
    long_market_ref: str = "",
    month_name: str = "September",
) -> list[str]:
    steps = []

    # Step 1: Market reference price context
    if current_price > 0:
        position = "above" if current_vs_avg > 0 else ("below" if current_vs_avg < 0 else "at")
        if market_source_type == "LIVE":
            mkt_desc = "Current live mandi price"
        elif market_source_type == "LATEST_AVAILABLE":
            mkt_desc = "Latest available official mandi price"
        elif market_source_type == "STALE":
            mkt_desc = "Stale official mandi price"
        else:
            mkt_desc = "Historical reference price"
        qualifier = (
            "a favourable liquidation window"
            if current_vs_avg > 5 else
            ("near historical benchmark levels" if abs(current_vs_avg) <= 5 else "below typical historical levels")
        )
        steps.append(
            f"{mkt_desc} (Rs.{int(current_price):,}/q) is {abs(current_vs_avg):.1f}% {position} the {hist_avg_label} — {qualifier}."
        )


    # Step 2: Seasonal trend
    trend_text = {
        "INCREASING": f"{month_name} historically sees rising prices as post-harvest market stocks decline",
        "DECREASING": f"{month_name} historically sees downward price pressure from regional market arrivals",
        "STABLE": f"{month_name} mandi prices are historically stable for this commodity",
    }
    steps.append(trend_text.get(seasonal_direction, f"{month_name} seasonal trend is stable."))

    # Step 3: Model Prediction Outlook
    if pred_conf > 0 and pred_max > 0:
        conf_str = f"confidence: {pred_conf}%"
        if pred_point > 0 and pred_point < current_price:
            price_drop = int(round(current_price - pred_point))
            steps.append(
                f"Price prediction model ({conf_str}) projects Rs.{pred_min:,}–Rs.{pred_max:,}/q "
                f"(point estimate: Rs.{int(pred_point):,}/q, which is Rs.{price_drop:,}/q below the reference price of Rs.{int(current_price):,}/q)."
            )
        elif pred_point > current_price:
            price_rise = int(round(pred_point - current_price))
            steps.append(
                f"Price prediction model ({conf_str}) projects Rs.{pred_min:,}–Rs.{pred_max:,}/q "
                f"(point estimate: Rs.{int(pred_point):,}/q, which is Rs.{price_rise:,}/q above the reference price of Rs.{int(current_price):,}/q)."
            )
        else:
            steps.append(
                f"Price prediction model ({conf_str}) projects prices to remain flat near Rs.{int(current_price):,}/q "
                f"(range: Rs.{pred_min:,}–Rs.{pred_max:,}/q)."
            )

    # Step 4: Weather Risk
    if max_rain_prob > 0:
        risk_desc = (
            "HIGH risk of storage moisture losses and transport disruption"
            if weather_risk_score >= 70 else
            ("moderate weather risk to stored produce" if weather_risk_score >= 40 else "low weather risk")
        )
        steps.append(
            f"Weather forecast indicates {int(max_rain_prob)}% rain probability over 7 days — {risk_desc}."
        )

    # Step 5: Numerical Financial Reconciliation
    if sell_now_net > 0:
        sc_val = int(round(storage_cost_7d))
        wp_val = int(round(weather_penalty_7d))
        holding_costs = sc_val + wp_val
        qty_text = f" across {total_qtl:g} quintals" if total_qtl > 0 else ""

        if pred_point > 0 and pred_point < current_price:
            price_drop_per_q = int(round(current_price - pred_point))
            price_downside_total = int(round(price_drop_per_q * total_qtl)) if total_qtl > 0 else int(round(abs(net_diff_7d) - holding_costs))
            total_reduction = price_downside_total + sc_val + wp_val
            diff_stated = abs(int(round(sell_now_net - wait_7d_net)))

            # Strict numerical reconciliation check
            reconciled = abs(diff_stated - total_reduction) <= 2
            if reconciled:
                steps.append(
                    f"Holding exposes produce to an estimated Rs.{price_drop_per_q:,}/q price downside (Rs.{price_downside_total:,}{qty_text}), "
                    f"plus Rs.{sc_val:,} storage costs and Rs.{wp_val:,} weather risk penalties, "
                    f"reducing 7-day net realization by Rs.{diff_stated:,}."
                )
            else:
                steps.append(
                    f"Holding reduces 7-day net realization by Rs.{diff_stated:,} "
                    f"(breakdown: price downside Rs.{price_downside_total:,}, storage Rs.{sc_val:,}, weather penalty Rs.{wp_val:,}; "
                    f"reconciliation delta: Rs.{abs(diff_stated - total_reduction):,})."
                )
        elif pred_point > current_price:
            price_gain_per_q = int(round(pred_point - current_price))
            price_gain_total = int(round(price_gain_per_q * total_qtl)) if total_qtl > 0 else 0
            net_impact = price_gain_total - holding_costs

            if net_impact < 0:
                steps.append(
                    f"Although price is projected to rise by Rs.{price_gain_per_q:,}/q (+Rs.{price_gain_total:,}{qty_text}), "
                    f"combined holding deductions of Rs.{holding_costs:,} (storage: Rs.{sc_val:,}, weather penalty: Rs.{wp_val:,}) "
                    f"exceed the price gain by Rs.{abs(net_impact):,}, reducing net realization."
                )
            else:
                steps.append(
                    f"Projected price increase of Rs.{price_gain_per_q:,}/q (+Rs.{price_gain_total:,}{qty_text}) "
                    f"exceeds combined holding deductions of Rs.{holding_costs:,} (storage: Rs.{sc_val:,}, weather penalty: Rs.{wp_val:,}), "
                    f"yielding an expected net advantage of Rs.{net_impact:,} by waiting 7 days."
                )
        else:
            steps.append(
                f"With prices projected flat near Rs.{int(current_price):,}/q (no price gain), "
                f"holding adds Rs.{sc_val:,} storage costs and Rs.{wp_val:,} weather risk penalties, "
                f"reducing 7-day net realization by Rs.{holding_costs:,}."
            )

    # Step 6: Final Decision Reconciliation
    if action == "SELL_NOW":
        advantage = abs(int(round(sell_now_net - wait_7d_net)))
        steps.append(
            f"Risk-adjusted net realization favours selling now: Rs.{int(sell_now_net):,} "
            f"vs Rs.{int(wait_7d_net):,} (wait 7 days), delivering a net advantage of Rs.{advantage:,}."
        )
    elif action in ("WAIT_7_DAYS", "WAIT_7D"):
        advantage = abs(int(round(wait_7d_net - sell_now_net)))
        steps.append(
            f"Expected price appreciation exceeds carrying costs — "
            f"waiting 7 days is projected to deliver Rs.{advantage:,} higher net realization (Rs.{int(wait_7d_net):,} vs Rs.{int(sell_now_net):,})."
        )
    elif action in ("WAIT_15_DAYS", "WAIT_15D"):
        steps.append(
            "Extended holding over 15 days is projected to maximize net realization based on price trend models."
        )
    else:
        steps.append("Risk signals are balanced — continue monitoring weather and mandi arrivals.")

    return steps


def _build_conclusion(
    action: str,
    weather_level: str,
    seasonal_direction: str,
    current_vs_avg: float,
    net_diff_7d: float,
    current_price: float = 0,
    pred_point: float = 0,
    weather_risk_score: int = 0,
    sell_now_net: float = 0,
    wait_7d_net: float = 0,
    market_source_type: str = "HISTORICAL_SEED",
    hist_avg_label: str = "historical dataset average",
    long_market_ref: str = "",
) -> str:
    avg_clause = (
        f" Reference price is {abs(current_vs_avg):.1f}% above the {hist_avg_label}, presenting an advantageous liquidation opportunity."
        if current_vs_avg > 5 else
        f" Reference price is aligned with the {hist_avg_label}."
    )

    if action == "SELL_NOW":
        advantage = abs(int(round(sell_now_net - wait_7d_net)))
        if pred_point > 0 and pred_point < current_price:
            price_drop = int(round(current_price - pred_point))
            if market_source_type == "LIVE":
                ref_mention = "today's price"
            elif market_source_type == "LATEST_AVAILABLE":
                ref_mention = f"the latest available official price of Rs.{int(current_price):,}/q"
            else:
                ref_mention = f"the reference price of Rs.{int(current_price):,}/q ({market_source_type})"

            return (
                f"Selling now is recommended. The predicted near-term price (Rs.{int(pred_point):,}/q) is "
                f"Rs.{price_drop:,}/q below {ref_mention}, while waiting also introduces "
                f"weather risk (score: {weather_risk_score}/100) and storage costs. "
                f"Selling now secures Rs.{advantage:,} higher net realization.{avg_clause}"
            )
        elif weather_risk_score >= 60:
            return (
                f"Selling now is recommended. Elevated rainfall risk (score: {weather_risk_score}/100) over the next 7 days makes "
                f"holding crop financially uncertain after accounting for storage costs and moisture damage penalties (net advantage: Rs.{advantage:,}).{avg_clause}"
            )
        else:
            return (
                f"Selling now offers the best risk-adjusted outcome based on current market and weather conditions (net difference: Rs.{advantage:,}).{avg_clause}"
            )
    elif action in ("WAIT_7_DAYS", "WAIT_7D"):
        gain = abs(int(round(wait_7d_net - sell_now_net)))
        return (
            f"Waiting 7 days is projected to improve net realization by approximately Rs.{gain:,}. "
            f"Expected price appreciation covers storage costs with weather risk (score: {weather_risk_score}/100) within safe thresholds. "
            "Monitor weather forecasts and market arrivals daily."
        )
    elif action in ("WAIT_15_DAYS", "WAIT_15D"):
        return (
            "Waiting 15 days appears optimal based on current market models, projecting higher net realization. "
            f"Ensure grain is protected against weather risk (score: {weather_risk_score}/100) and re-evaluate if local mandi arrivals surge."
        )
    else:
        return (
            "Conditions are mixed. Monitor weather forecasts and mandi prices daily before committing to sales or extended storage."
        )


def _gemini_explanation(base_conclusion: str, reasoning_steps: list, action: str, api_key: str) -> str:
    """Optional: Use Gemini API to enhance the explanation text."""
    try:
        import httpx
        prompt = (
            "You are an agricultural advisor assistant. Based on this analysis:\n"
            f"Recommendation: {action}\n"
            f"Reasoning: {'; '.join(reasoning_steps)}\n\n"
            "Write a clear, friendly 2-3 sentence explanation for a farmer in plain English. "
            "Be specific about the key reason for the recommendation. "
            "Do not use technical jargon. Do not add any caveats not already in the reasoning."
        )
        resp = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=8.0,
        )
        resp.raise_for_status()
        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        return text.strip()
    except Exception:
        return base_conclusion
