from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def data_sources():
    return {
      "sources": [
        {
          "name": "Weather Data",
          "provider": "Open-Meteo",
          "type": "LIVE",
          "variables": ["temperature", "precipitation", "humidity"],
          "coverage": "Global",
          "last_updated": "live",
          "status": "CONNECTED",
          "data_quality": "high",
          "url": "https://open-meteo.com"
        }
      ]
    }
