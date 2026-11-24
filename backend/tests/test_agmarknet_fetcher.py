"""
Tests for AGMARKNET live mandi data fetcher and market service integration.
Covers 3-tier provenance classification: LIVE, LATEST_AVAILABLE, STALE,
along with HISTORICAL_SEED, DATA_UNAVAILABLE, and MARKET_UNSUPPORTED guards.

All HTTP calls are mocked — no API key required.
"""
import asyncio
import unittest
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from backend.services.agmarknet_fetcher import (
    _normalize_commodity,
    _parse_date,
    _parse_price,
    _validate_record,
    LIVE_THRESHOLD_DAYS,
    LATEST_AVAILABLE_THRESHOLD_DAYS,
    STALENESS_DAYS,
)


def run_async(coro):
    return asyncio.run(coro)


# ── Helper to build a minimal valid record ────────────────────────────────────

def _make_record(
    commodity="Wheat",
    state="Uttar Pradesh",
    district="Lucknow",
    market="Lucknow",
    min_price="2350",
    max_price="2550",
    modal_price="2450",
    price_date=None,
    arrivals="120",
):
    if price_date is None:
        price_date = date.today().strftime("%d-%b-%Y")
    return {
        "Commodity": commodity,
        "State": state,
        "District_Name": district,
        "Market_Name": market,
        "Min_Price": min_price,
        "Max_Price": max_price,
        "Modal_Price": modal_price,
        "Price_Date": price_date,
        "Arrivals_Tonnes": arrivals,
        "Variety": "Dara",
    }


# ── Unit tests: pure helpers ──────────────────────────────────────────────────

class TestHelpers(unittest.TestCase):

    def test_normalize_commodity_wheat(self):
        self.assertEqual(_normalize_commodity("wheat"), "Wheat")
        self.assertEqual(_normalize_commodity("WHEAT"), "Wheat")
        self.assertEqual(_normalize_commodity("gehun"), "Wheat")

    def test_normalize_commodity_unknown_title_cased(self):
        self.assertEqual(_normalize_commodity("soybean"), "Soybean")

    def test_parse_price_valid(self):
        self.assertEqual(_parse_price("2450"), 2450.0)
        self.assertEqual(_parse_price("2,450"), 2450.0)
        self.assertEqual(_parse_price(2350), 2350.0)

    def test_parse_price_negative_returns_none(self):
        self.assertIsNone(_parse_price("-100"))

    def test_parse_price_non_numeric_returns_none(self):
        self.assertIsNone(_parse_price("N/A"))
        self.assertIsNone(_parse_price(None))

    def test_parse_date_agmarknet_format(self):
        d = _parse_date("14-Sep-2026")
        self.assertIsNotNone(d)
        self.assertEqual(d.year, 2026)
        self.assertEqual(d.month, 9)
        self.assertEqual(d.day, 14)

    def test_parse_date_iso_format(self):
        d = _parse_date("2026-09-14")
        self.assertEqual(d, date(2026, 9, 14))

    def test_parse_date_invalid_returns_none(self):
        self.assertIsNone(_parse_date("not-a-date"))
        self.assertIsNone(_parse_date(None))


# ── Unit tests: record validation ─────────────────────────────────────────────

class TestValidateRecord(unittest.TestCase):

    def test_valid_record_accepted(self):
        rec = _make_record()
        result = _validate_record(rec, "Wheat", "Uttar Pradesh")
        self.assertIsNotNone(result)
        self.assertEqual(result["modal_price"], 2450)
        self.assertEqual(result["min_price"], 2350)
        self.assertEqual(result["max_price"], 2550)

    def test_commodity_mismatch_rejected(self):
        rec = _make_record(commodity="Rice")
        result = _validate_record(rec, "Wheat", "Uttar Pradesh")
        self.assertIsNone(result)

    def test_state_mismatch_rejected(self):
        rec = _make_record(state="Punjab")
        result = _validate_record(rec, "Wheat", "Uttar Pradesh")
        self.assertIsNone(result)

    def test_negative_price_rejected(self):
        rec = _make_record(modal_price="-500")
        result = _validate_record(rec, "Wheat", "Uttar Pradesh")
        self.assertIsNone(result)

    def test_modal_outside_min_max_rejected(self):
        rec = _make_record(min_price="2300", max_price="2400", modal_price="2600")
        result = _validate_record(rec, "Wheat", "Uttar Pradesh")
        self.assertIsNone(result)

    def test_missing_date_rejected(self):
        rec = _make_record()
        rec["Price_Date"] = None
        result = _validate_record(rec, "Wheat", "Uttar Pradesh")
        self.assertIsNone(result)

    def test_missing_modal_price_rejected(self):
        rec = _make_record()
        rec["Modal_Price"] = None
        result = _validate_record(rec, "Wheat", "Uttar Pradesh")
        self.assertIsNone(result)

    def test_inverted_min_max_swapped_and_accepted(self):
        rec = _make_record(min_price="2550", max_price="2350", modal_price="2450")
        result = _validate_record(rec, "Wheat", "Uttar Pradesh")
        self.assertIsNotNone(result)
        self.assertLessEqual(result["min_price"], result["modal_price"])
        self.assertLessEqual(result["modal_price"], result["max_price"])


# ── Provenance Semantics & Freshness Tests (1 to 7) ───────────────────────────

class TestProvenanceSemantics(unittest.TestCase):

    def _run_fetch_with_mocked_response(self, price_date_str):
        """Helper: mock HTTP client and settings for fetch_live_mandi_data."""
        record = _make_record(price_date=price_date_str)
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock(return_value={"records": [record]})

        settings_mock = MagicMock()
        settings_mock.DATA_GOV_IN_API_KEY = "test-key-123"
        settings_mock.DATA_GOV_IN_BASE_URL = "https://api.data.gov.in/resource"

        async def _fetch():
            import backend.services.agmarknet_fetcher as mod
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)
            with patch("backend.config.settings", settings_mock):
                with patch("httpx.AsyncClient", return_value=mock_client):
                    return await mod.fetch_live_mandi_data("Wheat", "Uttar Pradesh", "Lucknow")

        return asyncio.run(_fetch())

    def _run_market_intelligence_async_with_mocked_record(self, price_date_str):
        """Helper: mock HTTP client and settings for get_market_intelligence_async."""
        record = _make_record(price_date=price_date_str)
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock(return_value={"records": [record]})

        settings_mock = MagicMock()
        settings_mock.DATA_GOV_IN_API_KEY = "test-key-123"
        settings_mock.DATA_GOV_IN_BASE_URL = "https://api.data.gov.in/resource"

        async def _get():
            from backend.services.market_service import get_market_intelligence_async
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)
            with patch("backend.config.settings", settings_mock):
                with patch("httpx.AsyncClient", return_value=mock_client):
                    return await get_market_intelligence_async("Wheat", "Lucknow", "Uttar Pradesh")

        return asyncio.run(_get())

    # 1. Fresh official data -> LIVE (<= 1 day old)
    def test_1_fresh_official_data_returns_live(self):
        # Today's date -> 0 days old -> LIVE
        today_str = date.today().strftime("%d-%b-%Y")
        fetch_res = self._run_fetch_with_mocked_response(today_str)
        self.assertIsNotNone(fetch_res)
        self.assertEqual(fetch_res["status"], "LIVE")

        # In market service async response:
        market_res = self._run_market_intelligence_async_with_mocked_record(today_str)
        self.assertEqual(market_res["data_source"]["type"], "LIVE")
        self.assertEqual(market_res["current"]["data_type"], "LIVE")
        self.assertEqual(market_res["current"]["status"], "LIVE")

        # Yesterday's date -> 1 day old -> LIVE
        yesterday_str = (date.today() - timedelta(days=1)).strftime("%d-%b-%Y")
        fetch_yesterday = self._run_fetch_with_mocked_response(yesterday_str)
        self.assertEqual(fetch_yesterday["status"], "LIVE")

    # 2. Valid but older official data -> LATEST_AVAILABLE (2 to 7 days old)
    def test_2_valid_older_official_data_returns_latest_available(self):
        # 4 days old -> LATEST_AVAILABLE
        four_days_ago_str = (date.today() - timedelta(days=4)).strftime("%d-%b-%Y")
        fetch_res = self._run_fetch_with_mocked_response(four_days_ago_str)
        self.assertIsNotNone(fetch_res)
        self.assertEqual(fetch_res["status"], "LATEST_AVAILABLE")

        market_res = self._run_market_intelligence_async_with_mocked_record(four_days_ago_str)
        self.assertEqual(market_res["data_source"]["type"], "LATEST_AVAILABLE")
        self.assertEqual(market_res["current"]["data_type"], "LATEST_AVAILABLE")
        self.assertEqual(market_res["current"]["status"], "LATEST_AVAILABLE")
        self.assertIn("not current enough", market_res["current"]["note"].lower())

    # 3. Too-old official data -> STALE (> 7 days old)
    def test_3_too_old_official_data_returns_stale(self):
        # 10 days old -> STALE
        ten_days_ago_str = (date.today() - timedelta(days=10)).strftime("%d-%b-%Y")
        fetch_res = self._run_fetch_with_mocked_response(ten_days_ago_str)
        self.assertIsNotNone(fetch_res)
        self.assertEqual(fetch_res["status"], "STALE")

        market_res = self._run_market_intelligence_async_with_mocked_record(ten_days_ago_str)
        self.assertEqual(market_res["data_source"]["type"], "STALE")
        self.assertEqual(market_res["current"]["data_type"], "STALE")
        self.assertEqual(market_res["current"]["status"], "STALE")
        self.assertIn("too old", market_res["data_source"]["note"].lower())

    # 4. Historical CSV fallback -> HISTORICAL_SEED on API failure
    def test_4_api_failure_falls_back_to_historical_seed(self):
        settings_mock = MagicMock()
        settings_mock.DATA_GOV_IN_API_KEY = "test-key"
        settings_mock.DATA_GOV_IN_BASE_URL = "https://api.data.gov.in/resource"

        async def _get():
            from backend.services.market_service import get_market_intelligence_async
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(side_effect=Exception("Connection refused"))
            with patch("backend.config.settings", settings_mock):
                with patch("httpx.AsyncClient", return_value=mock_client):
                    return await get_market_intelligence_async("Wheat", "Lucknow", "Uttar Pradesh")

        result = asyncio.run(_get())
        self.assertIsNotNone(result)
        self.assertEqual(result["data_source"]["type"], "HISTORICAL_SEED")
        self.assertIsNotNone(result.get("current"))

    # 5. No trustworthy data -> DATA_UNAVAILABLE
    def test_5_no_trustworthy_data_returns_data_unavailable(self):
        from backend.services.market_service import get_market_intelligence, get_market_intelligence_async
        
        # When _load_df fails or returns unreadable data
        with patch("backend.services.market_service._load_df", side_effect=RuntimeError("CSV file missing or corrupted")):
            res = get_market_intelligence("Wheat", "Lucknow", "Uttar Pradesh")
            self.assertEqual(res["data_source"]["type"], "DATA_UNAVAILABLE")
            self.assertIsNone(res["current"])

            # Also in async path
            settings_mock = MagicMock()
            settings_mock.DATA_GOV_IN_API_KEY = ""
            with patch("backend.config.settings", settings_mock):
                async_res = asyncio.run(get_market_intelligence_async("Wheat", "Lucknow", "Uttar Pradesh"))
                self.assertEqual(async_res["data_source"]["type"], "DATA_UNAVAILABLE")
                self.assertIsNone(async_res["current"])

    # 6. Existing no-API-key fallback remains HISTORICAL_SEED
    def test_6_no_api_key_remains_historical_seed(self):
        settings_mock = MagicMock()
        settings_mock.DATA_GOV_IN_API_KEY = ""
        settings_mock.DATA_GOV_IN_BASE_URL = "https://api.data.gov.in/resource"

        async def _get():
            from backend.services.market_service import get_market_intelligence_async
            with patch("backend.config.settings", settings_mock):
                return await get_market_intelligence_async("Wheat", "Lucknow", "Uttar Pradesh")

        result = asyncio.run(_get())
        self.assertIsNotNone(result)
        self.assertEqual(result["data_source"]["type"], "HISTORICAL_SEED")

    # 7. Unsupported crops remain MARKET_UNSUPPORTED
    def test_7_unsupported_crop_remains_market_unsupported(self):
        from backend.services.market_service import get_market_intelligence_async
        from backend.services.decision_engine import compute_scenarios

        # Market service async returns MARKET_UNSUPPORTED
        res = asyncio.run(get_market_intelligence_async("Rice", "Lucknow", "Uttar Pradesh"))
        self.assertEqual(res["data_source"]["type"], "MARKET_UNSUPPORTED")
        self.assertIsNone(res.get("current"))

        # Decision engine returns MARKET_UNAVAILABLE action when price=0
        farm = {"crop": "Rice", "farm_area_acres": 2.0}
        dec = compute_scenarios(farm=farm, current_price=0, prediction_7d=None, prediction_15d=None, weather_risk=20)
        self.assertEqual(dec["recommendation"]["action"], "MARKET_UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
