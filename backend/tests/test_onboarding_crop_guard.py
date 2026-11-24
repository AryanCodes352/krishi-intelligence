import unittest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

EXPECTED_UNSUPPORTED_MESSAGE = (
    "This prototype currently supports Wheat only. "
    "Market Intelligence and ML price prediction are available for Wheat. "
    "Rice, Mustard and other crops will be supported in a future version."
)

class TestOnboardingCropGuard(unittest.TestCase):
    """
    Validation tests for onboarding crop scope gating.
    Ensures that Wheat succeeds, whereas Rice, Mustard, and arbitrary future
    crops are dynamically blocked with the exact scope notice.
    """

    def _sample_payload(self, crop: str) -> dict:
        return {
            "farmer_name": "Ramesh Kumar",
            "location": "Malihabad",
            "district": "Lucknow",
            "state": "Uttar Pradesh",
            "crop": crop,
            "crop_variety": "Standard",
            "sowing_date": "2025-11-15",
            "farm_area_acres": 2.5,
            "soil_data_available": False,
            "phone": "9876543210",
        }

    def test_wheat_can_continue(self):
        """Wheat is supported: onboarding must succeed (HTTP 200) with a valid farm_id."""
        res = client.post("/api/farm/onboard", json=self._sample_payload("Wheat"))
        self.assertEqual(res.status_code, 200, f"Expected 200 for Wheat, got {res.status_code}: {res.text}")
        data = res.json()
        self.assertIn("farm_id", data)
        self.assertEqual(data["crop"], "Wheat")

    def test_wheat_case_insensitive_can_continue(self):
        """Wheat in lower or upper case should also be recognized as supported."""
        for w in ("wheat", "WHEAT", " Wheat "):
            res = client.post("/api/farm/onboard", json=self._sample_payload(w))
            self.assertEqual(res.status_code, 200, f"Expected 200 for '{w}', got {res.status_code}")

    def test_rice_is_blocked_with_unsupported_message(self):
        """Rice is blocked: must return HTTP 400 with the required scope notice."""
        res = client.post("/api/farm/onboard", json=self._sample_payload("Rice"))
        self.assertEqual(res.status_code, 400)
        detail = res.json().get("detail", "")
        self.assertEqual(detail, EXPECTED_UNSUPPORTED_MESSAGE)

    def test_mustard_is_blocked_with_unsupported_message(self):
        """Mustard is blocked: must return HTTP 400 with the required scope notice."""
        res = client.post("/api/farm/onboard", json=self._sample_payload("Mustard"))
        self.assertEqual(res.status_code, 400)
        detail = res.json().get("detail", "")
        self.assertEqual(detail, EXPECTED_UNSUPPORTED_MESSAGE)

    def test_arbitrary_future_unsupported_crops_are_dynamically_blocked(self):
        """Any crop other than Wheat (e.g. Cotton, Soybean, Barley, Sugarcane) must be blocked."""
        future_crops = ["Cotton", "Soybean", "Barley", "Sugarcane", "Maize", "Potato"]
        for crop in future_crops:
            res = client.post("/api/farm/onboard", json=self._sample_payload(crop))
            self.assertEqual(
                res.status_code, 400,
                f"Crop '{crop}' should have been blocked with 400, got {res.status_code}"
            )
            detail = res.json().get("detail", "")
            self.assertEqual(
                detail, EXPECTED_UNSUPPORTED_MESSAGE,
                f"Crop '{crop}' returned unexpected message: {detail}"
            )

if __name__ == "__main__":
    unittest.main()
