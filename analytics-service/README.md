# Analytics Service

This service provides analytics and insights for the polyglot microservices platform. It consumes events from Kafka and stores analytical data in MongoDB.

## Features

- FastAPI REST API for analytics endpoints
- Kafka event consumption from task and project events
- MongoDB for storing analytical data
- JWT authentication integration
- User-scoped analytics and insights

## API Endpoints

- `GET /analytics/dashboard` - User dashboard metrics
- `GET /analytics/projects/{project_id}` - Project-specific analytics
- `GET /analytics/tasks/summary` - Task completion metrics
- `GET /analytics/productivity` - User productivity insights

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export MONGODB_URL=mongodb://mongo:27017
export KAFKA_BOOTSTRAP_SERVERS=kafka:9092
export JWT_SECRET_KEY=your-secret-key
export JWT_AUDIENCE=polyglot-platform
```

3. Run the service:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Docker

Build and run with Docker:
```bash
docker build -t analytics-service .
docker run -p 8000:8000 analytics-service
```

Or use the provided docker-compose.yml from the root directory.

## Testing

Run tests with:
```bash
pytest
```