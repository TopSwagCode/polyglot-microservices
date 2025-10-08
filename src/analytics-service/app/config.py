import os
from typing import Optional

class Settings:
    # MongoDB Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://root:secret@mongo:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "analytics")
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Analytics Service"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Analytics and insights for the polyglot microservices platform"
    
    # CORS Configuration
    ALLOWED_HOSTS: list = ["*"]
    
    class Config:
        case_sensitive = True

settings = Settings()