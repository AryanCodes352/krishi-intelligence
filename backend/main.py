"""
KRISHI Intelligence — Academic Mini Project API Server
======================================================
Multi-source agricultural decision intelligence platform combining:
- Living Farm Digital Twin state synchronization
- Live agro-meteorological forecasting (Open-Meteo)
- Mandi market intelligence & XGBoost price regression
- Granular Soil Health Card OCR extraction with human confirmation
- Multi-factor risk engine & Sell-vs-Wait economic simulator
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base
from backend.routers import farm, weather, market, soil, prediction, expert, data_sources, intelligence

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="KRISHI INTELLIGENCE API")

# Configure CORS for local development and cloud deployments (Vercel)
default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
env_origins = os.getenv("ALLOWED_ORIGINS", "")
if env_origins.strip():
    custom_origins = [orig.strip() for orig in env_origins.split(",") if orig.strip()]
    allowed_origins = list(dict.fromkeys(default_origins + custom_origins))
else:
    allowed_origins = default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https:\/\/.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(farm.router, prefix="/api/farm", tags=["farm"])
app.include_router(weather.router, prefix="/api/weather", tags=["weather"])
app.include_router(market.router, prefix="/api/market", tags=["market"])
app.include_router(soil.router, prefix="/api/soil", tags=["soil"])
app.include_router(prediction.router, prefix="/api/prediction", tags=["prediction"])
app.include_router(expert.router, prefix="/api/expert", tags=["expert"])
app.include_router(data_sources.router, prefix="/api/data-sources", tags=["data-sources"])
app.include_router(intelligence.router, prefix="/api/intelligence", tags=["intelligence"])

@app.get("/")
def read_root():
    return {"message": "Welcome to KRISHI INTELLIGENCE API"}
