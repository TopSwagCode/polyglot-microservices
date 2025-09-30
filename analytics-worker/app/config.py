import os
from typing import Optional

class Settings:
    # MongoDB Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://root:secret@mongo:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "analytics_db")
    
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    KAFKA_GROUP_ID: str = os.getenv("KAFKA_GROUP_ID", "analytics-worker")
    KAFKA_TOPIC_TASK: str = os.getenv("KAFKA_TOPIC_TASK", "task-events")
    KAFKA_TOPIC_PROJECT: str = os.getenv("KAFKA_TOPIC_PROJECT", "project-events")
    
    # Worker Configuration
    WORKER_NAME: str = "Analytics Worker"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Kafka consumer worker for analytics data processing"
    
    class Config:
        case_sensitive = True

settings = Settings()