import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Civic AI Backend"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Database Configuration (PostgreSQL default with fallback for tests)
    DATABASE_URL: str = "postgresql://civic_user:civic_password@localhost:5432/civic_ai_db"

    # Security & Authentication (JWT)
    JWT_SECRET: str = "civic-ai-super-secret-key-change-in-production-min32chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Phase 2: Image Upload Configuration
    # UPLOAD_DIR is relative to the backend/ directory at runtime
    UPLOAD_DIR: str = "uploads"
    MAX_IMAGE_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/jpg,image/png"
    AI_INFERENCE_TIMEOUT_SECONDS: int = 30

    # Map Provider & Geolocation (Phase 6 Placeholder)
    MAP_PROVIDER_KEY: str = "your-maps-api-key-placeholder"
    MAP_DEFAULT_LATITUDE: float = 12.9716
    MAP_DEFAULT_LONGITUDE: float = 77.5946

    # Push Notifications (Phase 8 Placeholder)
    PUSH_NOTIFICATION_CONFIG: Optional[str] = '{"provider": "fcm"}'

    # ─────────────────────────────────────────────────────
    # Phase 6: Centralized Risk Engine Configuration
    # All weights and thresholds are configurable via environment variable.
    # Do NOT scatter these values throughout the codebase.
    # ─────────────────────────────────────────────────────
    RISK_CONFIG: Optional[str] = """{
        "crisis_severity": {
            "open_manhole": 95,
            "flooding": 90,
            "pothole": 70,
            "water_leakage": 60,
            "broken_streetlight": 50,
            "garbage": 40
        },
        "weights": {
            "severity": 0.40,
            "confidence": 0.30,
            "citizen_rating": 0.20,
            "location": 0.10
        },
        "thresholds": {
            "low_max": 25,
            "medium_max": 60,
            "high_max": 85
        },
        "priority_map": {
            "LOW": "LOW",
            "MEDIUM": "NORMAL",
            "HIGH": "HIGH",
            "CRITICAL": "URGENT"
        }
    }"""

    # Community Verification Radius in meters (Phase 7 Placeholder)
    COMMUNITY_RADIUS: float = 500.0

    # Gamification Point Values (Phase 9 Placeholder)
    POINT_VALUES: Optional[str] = '{"report_created": 10, "verification_submitted": 5, "issue_resolved": 25}'

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

settings = Settings()
