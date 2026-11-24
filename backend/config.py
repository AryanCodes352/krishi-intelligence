from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./krishi.db"
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    DEBUG: bool = True
    CORS_ORIGINS: list[str] = ["*"]
    
    DATA_GOV_IN_API_KEY: str = ""
    DATA_GOV_IN_BASE_URL: str = "https://api.data.gov.in"
    
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"
    
    ML_MODEL_DIR: str = "./ml/models"
    PRICE_PREDICTION_MIN_OBSERVATIONS: int = 52
    STORAGE_COST_PER_QTL_PER_DAY: float = 5.0
    
    DEFAULT_LAT: float = 26.8467
    DEFAULT_LON: float = 80.9462
    
    class Config:
        env_file = ".env"

settings = Settings()

def get_settings():
    return settings
