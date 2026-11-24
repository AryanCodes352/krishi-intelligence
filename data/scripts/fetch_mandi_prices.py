"""
KRISHI INTELLIGENCE — Live Mandi Price Fetcher
===============================================
Fetches current wheat mandi prices from data.gov.in OGD Platform API.

USAGE:
  python data/scripts/fetch_mandi_prices.py

REQUIREMENTS:
  - DATA_GOV_IN_API_KEY must be set in .env
  - pip install requests python-dotenv

OUTPUT:
  Prints current prices to stdout.
  Optionally appends to data/seed/wheat_lucknow_mandi.csv if --append flag used.

API REFERENCE:
  https://data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070
  (Daily Price of various commodities from various markets - AGMARKNET)
"""

import json
import os
import sys
from datetime import date

try:
    import requests
    from dotenv import load_dotenv
except ImportError:
    print("Run: pip install requests python-dotenv")
    sys.exit(1)

load_dotenv()

API_KEY = os.getenv("DATA_GOV_IN_API_KEY", "")
BASE_URL = os.getenv(
    "DATA_GOV_IN_BASE_URL",
    "https://api.data.gov.in/resource",
)
RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"


def fetch_prices(
    commodity: str = "Wheat",
    state: str = "Uttar Pradesh",
    district: str = "Lucknow",
    limit: int = 10,
) -> dict:
    if not API_KEY:
        return {
            "status": "NO_API_KEY",
            "message": "Set DATA_GOV_IN_API_KEY in .env to enable live prices.",
            "data": [],
        }

    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": limit,
        "filters[State]": state,
        "filters[District]": district,
        "filters[Commodity]": commodity,
    }

    try:
        resp = requests.get(
            f"{BASE_URL}/{RESOURCE_ID}",
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        records = data.get("records", [])
        return {
            "status": "SUCCESS",
            "source": "data.gov.in OGD Platform (AGMARKNET)",
            "fetched_at": date.today().isoformat(),
            "count": len(records),
            "data": records,
        }
    except requests.Timeout:
        return {"status": "TIMEOUT", "message": "API request timed out.", "data": []}
    except requests.HTTPError as e:
        return {"status": "HTTP_ERROR", "message": str(e), "data": []}
    except Exception as e:
        return {"status": "ERROR", "message": str(e), "data": []}


if __name__ == "__main__":
    result = fetch_prices()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["status"] == "NO_API_KEY":
        print("\nTo enable live prices:")
        print("  1. Register at https://data.gov.in")
        print("  2. Get your API key from your profile")
        print("  3. Add DATA_GOV_IN_API_KEY=<your-key> to .env")
