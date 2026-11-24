import unittest

from backend.services.market_service import (
    MARKET_SUPPORTED_CROPS,
    is_market_supported,
    get_current_price,
    get_historical_df,
    get_market_intelligence,
)
from backend.services.decision_engine import compute_scenarios


class TestMarketCropSupport(unittest.TestCase):
    """
    Guardrail tests ensuring that Rice and Mustard never receive Wheat market data,
    and that Wheat continues to work exactly as before.
    """

    # ── Supported-crops registry ──────────────────────────────────────────

    def test_wheat_is_supported(self):
        self.assertTrue(is_market_supported("Wheat"))
        self.assertTrue(is_market_supported("wheat"))
        self.assertTrue(is_market_supported("WHEAT"))

    def test_rice_is_not_supported(self):
        self.assertFalse(is_market_supported("Rice"))
        self.assertFalse(is_market_supported("rice"))
        self.assertFalse(is_market_supported("RICE"))

    def test_mustard_is_not_supported(self):
        self.assertFalse(is_market_supported("Mustard"))
        self.assertFalse(is_market_supported("mustard"))

    def test_unknown_crop_is_not_supported(self):
        self.assertFalse(is_market_supported("Soybean"))
        self.assertFalse(is_market_supported(""))
        self.assertFalse(is_market_supported("   "))

    # ── get_current_price ─────────────────────────────────────────────────

    def test_get_current_price_wheat_returns_int(self):
        """Wheat must return a positive integer price."""
        price = get_current_price("Wheat")
        self.assertIsNotNone(price)
        self.assertIsInstance(price, int)
        self.assertGreater(price, 0, "Wheat price must be positive")

    def test_get_current_price_rice_returns_none(self):
        """Rice must return None — never a Wheat fallback."""
        price = get_current_price("Rice")
        self.assertIsNone(price, "Rice should return None, not a Wheat fallback price")

    def test_get_current_price_mustard_returns_none(self):
        """Mustard must return None — never a Wheat fallback."""
        price = get_current_price("Mustard")
        self.assertIsNone(price, "Mustard should return None, not a Wheat fallback price")

    def test_get_current_price_never_returns_2445_for_unsupported(self):
        """The old hardcoded fallback 2445 must never appear for unsupported crops."""
        for crop in ("Rice", "Mustard", "Soybean", "Maize"):
            price = get_current_price(crop)
            self.assertNotEqual(
                price, 2445,
                f"crop={crop}: get_current_price must not return 2445 (Wheat fallback)",
            )

    # ── get_historical_df ─────────────────────────────────────────────────

    def test_get_historical_df_wheat_returns_dataframe(self):
        """Wheat must return a non-empty DataFrame."""
        df = get_historical_df("Wheat")
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0, "Wheat historical DataFrame must not be empty")

    def test_get_historical_df_rice_returns_none(self):
        """Rice must return None — never an empty DataFrame that mimics no-data."""
        df = get_historical_df("Rice")
        self.assertIsNone(df, "Rice should return None from get_historical_df")

    def test_get_historical_df_mustard_returns_none(self):
        """Mustard must return None."""
        df = get_historical_df("Mustard")
        self.assertIsNone(df, "Mustard should return None from get_historical_df")

    # ── get_market_intelligence ───────────────────────────────────────────

    def test_get_market_intelligence_wheat_has_current(self):
        """Wheat market intelligence must have a non-None current price."""
        data = get_market_intelligence("Wheat", "Lucknow", "Uttar Pradesh")
        self.assertIsNotNone(data)
        self.assertIn("current", data)
        self.assertIsNotNone(data["current"], "Wheat current price must not be None")
        self.assertIsNotNone(data["current"].get("modal_price"), "Wheat modal_price must not be None")

    def test_get_market_intelligence_wheat_data_source_type(self):
        """Wheat must return HISTORICAL_SEED type, not MARKET_UNSUPPORTED."""
        data = get_market_intelligence("Wheat", "Lucknow", "Uttar Pradesh")
        src_type = data.get("data_source", {}).get("type", "")
        self.assertNotEqual(src_type, "MARKET_UNSUPPORTED")
        self.assertEqual(src_type, "HISTORICAL_SEED")

    def test_get_market_intelligence_rice_returns_unsupported(self):
        """Rice must return MARKET_UNSUPPORTED type with null current."""
        data = get_market_intelligence("Rice", "Lucknow", "Uttar Pradesh")
        self.assertIsNone(data.get("current"), "Rice current must be None")
        src_type = data.get("data_source", {}).get("type", "")
        self.assertEqual(src_type, "MARKET_UNSUPPORTED",
                         f"Rice data_source.type must be MARKET_UNSUPPORTED, got {src_type}")

    def test_get_market_intelligence_mustard_returns_unsupported(self):
        """Mustard must return MARKET_UNSUPPORTED type with null current."""
        data = get_market_intelligence("Mustard", "Lucknow", "Uttar Pradesh")
        self.assertIsNone(data.get("current"), "Mustard current must be None")
        src_type = data.get("data_source", {}).get("type", "")
        self.assertEqual(src_type, "MARKET_UNSUPPORTED",
                         f"Mustard data_source.type must be MARKET_UNSUPPORTED, got {src_type}")

    def test_get_market_intelligence_rice_does_not_use_wheat_data(self):
        """
        CRITICAL: Verify that Rice market data does not contain Wheat prices.
        The modal_price for Rice must be None — not the Wheat MSP range.
        """
        wheat_data = get_market_intelligence("Wheat", "Lucknow", "Uttar Pradesh")
        rice_data = get_market_intelligence("Rice", "Lucknow", "Uttar Pradesh")
        wheat_price = wheat_data.get("current", {}).get("modal_price") if wheat_data.get("current") else None
        rice_price = rice_data.get("current", {}) or {}
        rice_modal = rice_price.get("modal_price") if rice_price else None
        self.assertIsNone(rice_modal, "Rice must NEVER have a modal_price — it must be None")
        if wheat_price:
            self.assertNotEqual(rice_modal, wheat_price, "Rice modal_price must not equal Wheat modal_price")

    # ── compute_scenarios (decision_engine) ───────────────────────────────

    def test_compute_scenarios_returns_market_unavailable_when_price_is_zero(self):
        """
        When current_price=0 (unsupported market crop), the decision engine must
        return MARKET_UNAVAILABLE action and not compute misleading scenarios.
        """
        farm = {"crop": "Rice", "farm_area_acres": 2.0, "yield_qtl_per_acre": 15.0}
        result = compute_scenarios(
            farm=farm,
            current_price=0,
            prediction_7d=None,
            prediction_15d=None,
            weather_risk=30,
        )
        action = result.get("recommendation", {}).get("action", "")
        self.assertEqual(action, "MARKET_UNAVAILABLE",
                         f"Expected MARKET_UNAVAILABLE, got {action}")
        self.assertFalse(result.get("market_prediction_available", True),
                         "market_prediction_available must be False for unsupported crops")

    def test_compute_scenarios_wheat_works_normally(self):
        """
        Wheat with a valid price must return SELL_NOW, WAIT_7D, or WAIT_15D — never MARKET_UNAVAILABLE.
        """
        farm = {"crop": "Wheat", "farm_area_acres": 3.0, "yield_qtl_per_acre": 15.0}
        result = compute_scenarios(
            farm=farm,
            current_price=2605,
            prediction_7d={"point_estimate": 2571, "min_price": 2511, "max_price": 2631, "confidence_pct": 80},
            prediction_15d={"point_estimate": 2572, "min_price": 2494, "max_price": 2650, "confidence_pct": 70},
            weather_risk=62,
        )
        action = result.get("recommendation", {}).get("action", "")
        self.assertIn(action, ("SELL_NOW", "WAIT_7D", "WAIT_15D", "MONITOR"),
                      f"Wheat with valid price should not return MARKET_UNAVAILABLE, got {action}")

    def test_compute_scenarios_zero_price_scenario_fields_are_zero(self):
        """When price=0, all financial scenario fields must be 0 (no fabricated values)."""
        farm = {"crop": "Mustard", "farm_area_acres": 1.5, "yield_qtl_per_acre": 10.0}
        result = compute_scenarios(
            farm=farm, current_price=0, prediction_7d=None, prediction_15d=None, weather_risk=20
        )
        for scenario_key in ("sell_now", "wait_7d", "wait_15d"):
            s = result.get("scenarios", {}).get(scenario_key, {})
            self.assertEqual(s.get("expected_revenue", -1), 0,
                             f"{scenario_key}.expected_revenue must be 0 for unsupported crop")
            self.assertEqual(s.get("net_realization", -1), 0,
                             f"{scenario_key}.net_realization must be 0 for unsupported crop")

    # ── supported_crops frozenset ─────────────────────────────────────────

    def test_supported_crops_frozenset_is_immutable(self):
        """MARKET_SUPPORTED_CROPS must be a frozenset (immutable)."""
        self.assertIsInstance(MARKET_SUPPORTED_CROPS, frozenset)

    def test_supported_crops_contains_only_lowercase(self):
        """All entries in MARKET_SUPPORTED_CROPS must be lowercase for consistent matching."""
        for crop in MARKET_SUPPORTED_CROPS:
            self.assertEqual(crop, crop.lower(),
                             f"MARKET_SUPPORTED_CROPS entry '{crop}' must be lowercase")


if __name__ == "__main__":
    unittest.main()
