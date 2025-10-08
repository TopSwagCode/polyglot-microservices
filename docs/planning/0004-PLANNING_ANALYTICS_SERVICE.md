# Planning: Analytics Service (Python)

This document describes the plan for building the **Analytics Service**
in Python.\
The service will consume events from Kafka/NATS, store aggregated data
in MongoDB, and expose analytics endpoints via **FastAPI**.

------------------------------------------------------------------------

## 🔹 Goals

-   Consume **task events** (`task_created`, `task_updated`) from
    Kafka.
-   Process events into aggregated analytics (e.g., tasks per user,
    completion time averages).
-   Store results in **MongoDB** for fast queries.
-   Expose analytics via **REST API** with FastAPI.

------------------------------------------------------------------------

## 🔹 Tech Stack

-   **Python 3.11+**
-   **FastAPI** for REST API
-   **Pydantic** for request/response validation
-   **Kafka-Python** for message consumption
-   **Motor** (async MongoDB client)
-   **Pytest** for testing
-   **Docker & Docker Compose**

------------------------------------------------------------------------

## 🔹 Project Structure

    analytics-service/
    │── app/
    │    ├── main.py          # FastAPI entrypoint
    │    ├── api.py           # Routes
    │    ├── consumer.py      # Kafka/NATS consumer
    │    ├── models.py        # Pydantic schemas
    │    ├── db.py            # MongoDB connection
    │    └── services.py      # Analytics logic
    │── tests/
    │── requirements.txt
    │── Dockerfile

------------------------------------------------------------------------

## 🔹 Step 1 -- Setup Project

``` bash
mkdir analytics-service && cd analytics-service
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn[standard] motor pydantic kafka-python
```

**requirements.txt**

    fastapi
    uvicorn[standard]
    motor
    pydantic
    kafka-python
    pytest

------------------------------------------------------------------------

## 🔹 Step 2 -- MongoDB Connection

**db.py**

``` python
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://mongo:27017")
db = client["analyticsdb"]
```

------------------------------------------------------------------------

## 🔹 Step 3 -- Event Consumer

**consumer.py**

``` python
from kafka import KafkaConsumer
import json
from .db import db

consumer = KafkaConsumer(
    "tasks",
    bootstrap_servers="kafka:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

async def consume():
    for msg in consumer:
        event = msg.value
        if event["event"] == "task_created":
            await db.tasks_per_user.update_one(
                {"user_id": event["user_id"]},
                {"$inc": {"count": 1}},
                upsert=True
            )
```

------------------------------------------------------------------------

## 🔹 Step 4 -- FastAPI Endpoints

**api.py**

``` python
from fastapi import APIRouter
from .db import db

router = APIRouter()

@router.get("/analytics/tasks-per-user")
async def tasks_per_user():
    cursor = db.tasks_per_user.find()
    results = []
    async for doc in cursor:
        results.append(doc)
    return results
```

**main.py**

``` python
from fastapi import FastAPI
from .api import router

app = FastAPI(title="Analytics Service")
app.include_router(router)
```

------------------------------------------------------------------------

## 🔹 Step 5 -- Docker Setup

**Dockerfile**

``` dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

------------------------------------------------------------------------

## 🔹 Step 6 -- Docker Compose Integration

Add to `docker-compose.yml`:

``` yaml
  analytics-service:
    build: ./analytics-service
    ports:
      - "8000:8000"
    depends_on:
      - mongo
      - kafka

  mongo:
    image: mongo:6
    ports:
      - "27017:27017"
    volumes:
      - mongodata:/data/db
```

------------------------------------------------------------------------

## 🔹 Step 7 -- Run Locally

``` bash
docker compose up --build
```

Analytics service available at **http://localhost:8000**.

Try:

``` bash
curl http://localhost:8000/analytics/tasks-per-user
```

------------------------------------------------------------------------

## 🔹 Next Steps

-   Add more analytics (average completion time, tasks by status).
-   Add authentication/authorization via API Gateway.
-   Implement OpenTelemetry tracing.
-   Add unit tests for analytics logic.
