from __future__ import annotations

import logging
from datetime import datetime, timezone, date
from typing import Optional

logger = logging.getLogger(__name__)

RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"

# ── Freshness thresholds ───────────────────────────────────────────────────────
# Mandi data is posted daily. Thresholds below reflect how "current" a record is.
#
#  LIVE             : market_date is today or yesterday (≤ 1 day old)
#                     Data is genuinely current market intelligence.
#
#  LATEST_AVAILABLE : market_date is 2–7 days old
#                     Valid, official-source record; not current enough for LIVE.
#                     The most recent observation available from the source.
#
#  STALE            : market_date is > 7 days old
#                     Too old for reliable current-market intelligence.
#                     market_service falls back to HISTORICAL_SEED for STALE data.
#
LIVE_THRESHOLD_DAYS = 1              # ≤ 1 day → LIVE
LATEST_AVAILABLE_THRESHOLD_DAYS = 7  # 2-7 days → LATEST_AVAILABLE
# > LATEST_AVAILABLE_THRESHOLD_DAYS → STALE

# Keep the old name as an alias so existing test references don't break
STALENESS_DAYS = LATEST_AVAILABLE_THRESHOLD_DAYS

REQUEST_TIMEOUT_SECONDS = 8
MAX_RECORDS = 10


_COMMODITY_ALIASES = {
    "wheat": "Wheat",
    "gehun": "Wheat",
    "gehu": "Wheat",
    "rice": "Rice",
    "paddy": "Rice",
    "mustard": "Mustard",
    "sarson": "Mustard",
}


def _normalize_commodity(raw):
    return _COMMODITY_ALIASES.get(raw.strip().lower(), raw.strip().title())


def _parse_price(value):
    try:
        price = float(str(value).replace(",", "").strip())
        return price if price >= 0 else None
    except (ValueError, TypeError):
        return None


def _parse_date(value):
    if not value:
        return None
    raw = str(value).strip()
    for fmt in ("%d-%b-%Y", "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def _validate_record(record, expected_commodity, expected_state):
    try:
        raw_commodity = str(record.get("Commodity") or record.get("commodity") or "").strip()
        norm_commodity = _normalize_commodity(raw_commodity)
        if norm_commodity.lower() != expected_commodity.strip().lower():
            return None
        raw_state = str(record.get("State") or record.get("state") or "").strip()
        if raw_state.lower() != expected_state.strip().lower():
            return None
        min_price = _parse_price(record.get("Min_Price") or record.get("min_price"))
        max_price = _parse_price(record.get("Max_Price") or record.get("max_price"))
        modal_price = _parse_price(record.get("Modal_Price") or record.get("modal_price"))
        if modal_price is None:
            return None
        if min_price is None:
            min_price = modal_price
        if max_price is None:
            max_price = modal_price
        if min_price > max_price:
            min_price, max_price = max_price, min_price
        if not (min_price <= modal_price <= max_price):
            logger.warning("AGMARKNET price logic violation: min=%s modal=%s max=%s", min_price, modal_price, max_price)
            return None
        raw_date = record.get("Price_Date") or record.get("price_date") or record.get("Arrival_Date")
        price_date = _parse_date(raw_date)
        if price_date is None:
            return None
        arrivals_raw = record.get("Arrivals_Tonnes") or record.get("arrivals_tonnes") or 0
        try:
            arrivals = float(str(arrivals_raw).replace(",", "").strip())
        except (ValueError, TypeError):
            arrivals = 0.0
        market = str(record.get("Market_Name") or record.get("market_name") or record.get("District_Name") or record.get("district_name") or "").strip()
        district = str(record.get("District_Name") or record.get("district_name") or "").strip()
        variety = str(record.get("Variety") or record.get("variety") or "").strip()
        return {
            "commodity": norm_commodity,
            "market": market,
            "district": district,
            "state": raw_state,
            "variety": variety,
            "min_price": int(round(min_price)),
            "modal_price": int(round(modal_price)),
            "max_price": int(round(max_price)),
            "arrivals_tonnes": int(round(arrivals)),
            "price_date": price_date,
        }
    except Exception as exc:
        logger.debug("AGMARKNET record validation error: %s", exc)
        return None


async def fetch_live_mandi_data(crop, state, district):
    try:
        from backend.config import settings
        api_key = settings.DATA_GOV_IN_API_KEY.strip()
        base_url = settings.DATA_GOV_IN_BASE_URL.strip().rstrip("/")
    except Exception:
        return None
    if not api_key:
        logger.debug("AGMARKNET: DATA_GOV_IN_API_KEY not set - using historical fallback")
        return None
    url = f"{base_url}/{RESOURCE_ID}"
    params = {
        "api-key": api_key,
        "format": "json",
        "limit": MAX_RECORDS,
        "filters[commodity]": crop.strip().title(),
        "filters[state]": state.strip(),
    }
    if district.strip():
        params["filters[district]"] = district.strip()
    try:
        import httpx
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.get(url, params=params)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        logger.warning("AGMARKNET API request failed: %s", exc)
        return None
    records = []
    if isinstance(payload, list):
        records = payload
    elif isinstance(payload, dict):
        records = payload.get("records") or payload.get("data") or []
    if not records:
        logger.info("AGMARKNET: Empty response for crop=%s state=%s district=%s", crop, state, district)
        return None
    validated = []
    for raw_record in records:
        if not isinstance(raw_record, dict):
            continue
        result = _validate_record(raw_record, crop, state)
        if result:
            validated.append(result)
    if not validated:
        logger.info("AGMARKNET: No valid records after validation")
        return None
    district_lower = district.strip().lower()
    def _score(rec):
        district_match = int(district_lower in rec["district"].lower() or district_lower in rec["market"].lower())
        return (district_match, rec["price_date"])
    validated.sort(key=_score, reverse=True)
    best = validated[0]
    days_old = (date.today() - best["price_date"]).days
    if days_old < 0:
        days_old = 0
    if days_old <= LIVE_THRESHOLD_DAYS:
        status = "LIVE"
    elif days_old <= LATEST_AVAILABLE_THRESHOLD_DAYS:
        status = "LATEST_AVAILABLE"
    else:
        status = "STALE"

    retrieved_at = datetime.now(timezone.utc).isoformat()
    return {
        "crop": best["commodity"],
        "market": best["market"] or district,
        "district": best["district"] or district,
        "state": best["state"],
        "variety": best["variety"],
        "min_price": best["min_price"],
        "modal_price": best["modal_price"],
        "max_price": best["max_price"],
        "arrivals_tonnes": best["arrivals_tonnes"],
        "market_date": best["price_date"].strftime("%Y-%m-%d"),
        "days_old": days_old,
        "source": "AGMARKNET",
        "status": status,
        "retrieved_at": retrieved_at,
    }
