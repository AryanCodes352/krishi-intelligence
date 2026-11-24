import uuid
from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.database import Base

class Farm(Base):
    __tablename__ = "farms"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_name = Column(String)
    location = Column(String)
    district = Column(String)
    state = Column(String)
    crop = Column(String)
    crop_variety = Column(String)
    sowing_date = Column(String)
    farm_area_acres = Column(Float)
    soil_data_available = Column(Boolean)
    lat = Column(Float)
    lon = Column(Float)
    phone = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class FarmObservation(Base):
    __tablename__ = "farm_observations"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id = Column(String, ForeignKey("farms.id"))
    observed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    weather_risk_score = Column(Float)
    soil_risk_score = Column(Float)
    crop_risk_score = Column(Float)
    market_risk_score = Column(Float)
    overall_risk_score = Column(Float)
    current_price = Column(Float)
    recommendation_action = Column(String)
    recommendation_confidence = Column(String)
    snapshot_json = Column(JSON)

class PricePrediction(Base):
    __tablename__ = "price_predictions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id = Column(String, ForeignKey("farms.id"))
    predicted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    horizon_days = Column(Integer)
    point_estimate = Column(Float)
    min_price = Column(Float)
    max_price = Column(Float)
    confidence_pct = Column(Float)
    model_type = Column(String)
    mae = Column(Float)
    mape_pct = Column(Float)
    data_points_used = Column(Integer)

class FarmEvent(Base):
    __tablename__ = "farm_events"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id = Column(String, ForeignKey("farms.id"), nullable=False)
    event_type = Column(String, nullable=False)  # e.g., FARM_CREATED, PROFILE_UPDATED, ANALYSIS_RECORDED
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    source = Column(String, default="SYSTEM")  # USER_ACTION, INTELLIGENCE_ENGINE, SYSTEM


class SoilDocument(Base):
    __tablename__ = "soil_documents"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id = Column(String, ForeignKey("farms.id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # e.g., application/pdf, image/jpeg, image/png
    file_size_bytes = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    ocr_status = Column(String, default="REVIEW_REQUIRED")  # SUCCESS, PARTIAL_EXTRACTION, OCR_FAILED, REVIEW_REQUIRED
    extracted_data_json = Column(JSON, nullable=True)
    is_confirmed = Column(Boolean, default=False)
    confirmed_at = Column(DateTime, nullable=True)


class FarmSoilProfile(Base):
    __tablename__ = "farm_soil_profiles"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id = Column(String, ForeignKey("farms.id"), nullable=False, index=True)
    document_id = Column(String, ForeignKey("soil_documents.id"), nullable=True)
    provenance = Column(String, default="SOIL_HEALTH_CARD")  # SOIL_HEALTH_CARD, FARMER_ENTERED
    is_active = Column(Boolean, default=True, index=True)
    test_date = Column(String, nullable=True)
    confirmation_status = Column(String, default="CONFIRMED")
    confirmed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Core soil parameters (nullable floats, never forced to zero)
    ph = Column(Float, nullable=True)
    nitrogen = Column(Float, nullable=True)  # kg/ha
    phosphorus = Column(Float, nullable=True)  # kg/ha
    potassium = Column(Float, nullable=True)  # kg/ha
    organic_carbon = Column(Float, nullable=True)  # %
    ec = Column(Float, nullable=True)  # dS/m
    soil_texture = Column(String, nullable=True)

    # Micronutrients (nullable floats)
    sulphur = Column(Float, nullable=True)  # ppm or kg/ha
    zinc = Column(Float, nullable=True)  # ppm
    iron = Column(Float, nullable=True)  # ppm
    copper = Column(Float, nullable=True)  # ppm
    manganese = Column(Float, nullable=True)  # ppm
    boron = Column(Float, nullable=True)  # ppm

    # Field-level provenance mapping (e.g. {"ph": "SOIL_HEALTH_CARD", "zinc": "FARMER_ENTERED"})
    field_sources_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


