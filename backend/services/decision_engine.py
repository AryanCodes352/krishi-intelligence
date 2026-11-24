def compute_scenarios(
    farm: dict,
    current_price: float,
    prediction_7d: dict | None,
    prediction_15d: dict | None,
    weather_risk: int,
    storage_cost_per_qtl_per_day: float = 5.0,
    market_source: str = "HISTORICAL_SEED",
    market_date: str | None = None,
) -> dict:
    crop = farm.get("crop", "this crop")
    acres = float(farm.get("farm_area_acres", 1.0))
    yield_qtl_per_acre = float(farm.get("yield_qtl_per_acre", 15.0))
    total_qtl = round(acres * yield_qtl_per_acre, 1)

    # ── Market unavailable guard ──────────────────────────────────────────
    # When current_price == 0 the caller has signalled that no market data
    # exists for this crop. Return a MARKET_UNAVAILABLE response so the
    # frontend can show an appropriate "not yet supported" state instead of
    # computing misleading numbers. Never use a Wheat price as a fallback.
    if current_price <= 0:
        _zero_scenario = {
            "label": "N/A",
            "expected_price": 0,
            "expected_revenue": 0,
            "storage_cost": 0,
            "weather_risk_penalty": 0,
            "transport_cost": 0,
            "net_realization": 0,
            "risk_score": 0,
            "risk_level": "MEDIUM",
            "confidence_pct": 0,
            "market_prediction_available": False,
        }
        return {
            "farm_area_acres": acres,
            "estimated_yield_qtl": total_qtl,
            "market_prediction_available": False,
            "scenarios": {
                "sell_now": _zero_scenario,
                "wait_7d": _zero_scenario,
                "wait_15d": _zero_scenario,
            },
            "recommendation": {
                "action": "MARKET_UNAVAILABLE",
                "confidence": "N/A",
                "headline": f"Market prediction not yet available for {crop}",
                "summary": (
                    f"Market Intelligence for {crop} is not yet available in this prototype. "
                    "Financial scenarios require crop-specific market price data. "
                    f"{crop} market prediction is planned for the next version."
                ),
                "risk_adjusted_best": "none",
                "key_factors": ["market_data_unavailable"],
            },
        }
    
    # 1. Sell Now
    rev_now = int(round(current_price * total_qtl))
    sn_net = rev_now
    
    # 2. Wait 7 Days
    p7 = float(prediction_7d.get("point_estimate") or prediction_7d.get("point") or current_price) if prediction_7d else current_price
    p7_min = float(prediction_7d.get("min_price") or prediction_7d.get("min") or p7) if prediction_7d else p7
    p7_max = float(prediction_7d.get("max_price") or prediction_7d.get("max") or p7) if prediction_7d else p7
    rev_7 = int(round(p7 * total_qtl))
    sc_7 = int(round(storage_cost_per_qtl_per_day * 7 * total_qtl))
    wp_7 = int(round(weather_risk * 0.002 * rev_7 * 1))
    w7_net = rev_7 - sc_7 - wp_7
    
    # 3. Wait 15 Days
    p15 = float(prediction_15d.get("point_estimate") or prediction_15d.get("point") or current_price) if prediction_15d else current_price
    p15_min = float(prediction_15d.get("min_price") or prediction_15d.get("min") or p15) if prediction_15d else p15
    p15_max = float(prediction_15d.get("max_price") or prediction_15d.get("max") or p15) if prediction_15d else p15
    rev_15 = int(round(p15 * total_qtl))
    sc_15 = int(round(storage_cost_per_qtl_per_day * 15 * total_qtl))
    wp_15 = int(round(weather_risk * 0.002 * rev_15 * 2))
    w15_net = rev_15 - sc_15 - wp_15
    
    scenarios = {
        "sell_now": {
            "label": "Sell Now",
            "expected_price": current_price,
            "expected_revenue": rev_now,
            "storage_cost": 0,
            "weather_risk_penalty": 0,
            "transport_cost": 0,
            "net_realization": sn_net,
            "risk_score": 18,
            "risk_level": "LOW",
            "confidence_pct": 90
        },
        "wait_7d": {
            "label": "Wait 7 Days",
            "expected_price_min": int(round(p7_min)),
            "expected_price_max": int(round(p7_max)),
            "expected_price": int(round(p7)),
            "expected_revenue": rev_7,
            "storage_cost": sc_7,
            "weather_risk_penalty": wp_7,
            "transport_cost": 0,
            "net_realization": w7_net,
            "risk_score": 55,
            "risk_level": "MEDIUM",
            "confidence_pct": int(prediction_7d.get("confidence_pct", 72)) if prediction_7d else 50
        },
        "wait_15d": {
            "label": "Wait 15 Days",
            "expected_price_min": int(round(p15_min)),
            "expected_price_max": int(round(p15_max)),
            "expected_price": int(round(p15)),
            "expected_revenue": rev_15,
            "storage_cost": sc_15,
            "weather_risk_penalty": wp_15,
            "transport_cost": 0,
            "net_realization": w15_net,
            "risk_score": 72,
            "risk_level": "HIGH",
            "confidence_pct": int(prediction_15d.get("confidence_pct", 57)) if prediction_15d else 40
        }
    }
    
    # Determine best scenario
    best_scenario = "sell_now"
    best_val = sn_net
    if w7_net > best_val:
        best_scenario = "wait_7d"
        best_val = w7_net
    if w15_net > best_val:
        best_scenario = "wait_15d"
        best_val = w15_net
        
    # Safety risk rule: razor-thin gain under heavy weather risk defaults to safe selling
    if abs(sn_net - best_val) / max(sn_net, 1) < 0.02 and weather_risk > 60:
        best_scenario = "sell_now"
        
    action_map = {"sell_now": "SELL_NOW", "wait_7d": "WAIT_7_DAYS", "wait_15d": "WAIT_15_DAYS"}
    
    # Contextual Decision Confidence (Rule 3)
    p7_conf = int(prediction_7d.get("confidence_pct", 70)) if prediction_7d else 50
    margin_ratio = abs(sn_net - w7_net) / max(sn_net, 1)
    
    if market_source.upper() == "HISTORICAL_SEED":
        decision_confidence = "MEDIUM"  # Capped at MEDIUM because market data is historical seed
    elif market_source.upper() == "LIVE":
        if p7_conf >= 75 and margin_ratio >= 0.02 and weather_risk < 70:
            decision_confidence = "HIGH"
        elif p7_conf >= 50:
            decision_confidence = "MEDIUM"
        else:
            decision_confidence = "LOW"
    elif market_source.upper() == "LATEST_AVAILABLE":
        decision_confidence = "MEDIUM"  # Official observation, but not current-day live
    else:
        decision_confidence = "LOW"
        
    # Provenance reference wording (Rule 1)
    if market_source.upper() == "LIVE":
        date_str = f" ({market_date})" if market_date else ""
        ref_label = f"today's live mandi reference price of Rs.{int(current_price):,}/q{date_str}"
    elif market_source.upper() == "LATEST_AVAILABLE":
        date_str = f" from {market_date}" if market_date else ""
        ref_label = f"the latest available official mandi price of Rs.{int(current_price):,}/q{date_str}"
    elif market_source.upper() == "STALE":
        date_str = f" from {market_date}" if market_date else ""
        ref_label = f"the stale official mandi price of Rs.{int(current_price):,}/q{date_str}"
    else:
        ref_label = f"the historical reference price of Rs.{int(current_price):,}/q ({market_source})"

    
    headlines = {
        "sell_now": "Sell within the next 3 days",
        "wait_7d": "Wait 7 days before selling",
        "wait_15d": "Wait up to 15 days for best price",
    }
    
    # Dynamic summary with strictly calculated numbers
    if best_scenario == "sell_now":
        net_advantage_7d = abs(int(sn_net - w7_net))
        price_diff_7d = int(round(p7 - current_price))

        if p7 < current_price:
            price_drop = abs(price_diff_7d)
            if weather_risk >= 40:
                summary = (
                    f"The predicted near-term price (Rs.{int(p7):,}/q) is Rs.{price_drop:,}/q below {ref_label}, "
                    f"while waiting also introduces higher weather risk ({weather_risk}/100) and storage costs (Rs.{int(sc_7):,}). "
                    f"Selling now protects against price decline and secures Rs.{net_advantage_7d:,} higher net realization."
                )
            else:
                summary = (
                    f"The predicted near-term price (Rs.{int(p7):,}/q) is Rs.{price_drop:,}/q below {ref_label}. "
                    f"Selling today avoids price depreciation and holding costs, achieving Rs.{net_advantage_7d:,} higher net realization."
                )
        elif p7 > current_price:
            summary = (
                f"While the 7-day predicted price rises to Rs.{int(p7):,}/q (+Rs.{price_diff_7d:,}/q), "
                f"weather risk penalties (Rs.{int(wp_7):,}, score: {weather_risk}/100) and storage costs (Rs.{int(sc_7):,}) "
                f"exceed the price gain. Selling now provides Rs.{net_advantage_7d:,} better net realization."
            )
        else:
            summary = (
                f"Prices are projected to hold flat near Rs.{int(current_price):,}/q over 7 days. "
                f"Holding adds storage costs (Rs.{int(sc_7):,}) and weather risk ({weather_risk}/100), "
                f"making immediate selling the optimal financial choice (net realization: Rs.{int(sn_net):,})."
            )
    elif best_scenario == "wait_7d":
        gain = int(round(w7_net - sn_net))
        price_diff_7d = int(round(p7 - current_price))
        summary = (
            f"Waiting 7 days is projected to improve net realization by Rs.{gain:,} "
            f"(expected price: Rs.{int(p7):,}/q, +Rs.{price_diff_7d:,}/q over {ref_label}). "
            f"Weather risk ({weather_risk}/100) remains within safe thresholds — monitor forecasts daily."
        )
    else:
        gain = int(round(w15_net - sn_net))
        price_diff_15d = int(round(p15 - current_price))
        summary = (
            f"Waiting 15 days is projected to improve net realization by Rs.{gain:,} "
            f"(expected price: Rs.{int(p15):,}/q, +Rs.{price_diff_15d:,}/q over {ref_label}). "
            f"Holding carries higher uncertainty; monitor weather and local market arrivals closely."
        )
    
    return {
        "farm_area_acres": acres,
        "estimated_yield_qtl": total_qtl,
        "scenarios": scenarios,
        "recommendation": {
            "action": action_map[best_scenario],
            "confidence": decision_confidence,
            "headline": headlines[best_scenario],
            "summary": summary,
            "risk_adjusted_best": best_scenario,
            "key_factors": [
                "high_rainfall_risk" if weather_risk > 60 else
                ("favourable_price_appreciation" if p7 > current_price else "price_depreciation_risk")
            ],
        }
    }
