import os


class Settings:
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://root:secret@mongo:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "analytics")

    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    KAFKA_GROUP_ID: str = os.getenv("KAFKA_GROUP_ID", "analytics-worker-project")
    KAFKA_TOPIC_PROJECT: str = os.getenv("KAFKA_TOPIC_PROJECT", "project-events")

    WORKER_NAME: str = "Analytics Project Worker"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Kafka consumer worker for project analytics processing"


settings = Settings()