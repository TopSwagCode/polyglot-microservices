# Planning: Task Service (Go)

This document describes the plan for building the **Task Service** in
Go.\
The Task Service will provide CRUD operations for projects and tasks,
publish events, and run locally with **Docker Compose**.

------------------------------------------------------------------------

## 🔹 Goals

-   Expose a REST API with endpoints for managing tasks and projects:
    -   `POST /projects`
    -   `GET /projects/{id}`
    -   `POST /tasks`
    -   `GET /tasks/{id}`
-   Store tasks in **PostgreSQL**
-   Publish task events (`task_created`, `task_updated`) to **Kafka**
-   Run locally with **Docker Compose**

------------------------------------------------------------------------

## 🔹 Tech Stack

-   **Go 1.22+**
-   **Gin** or **Chi** for HTTP routing
-   **GORM** or **sqlx** for PostgreSQL access
-   **Sarama** (Kafka)
-   **log/slog** for structured logging
-   **Docker & Docker Compose**

------------------------------------------------------------------------

## 🔹 Project Structure

    task-service/
    │── cmd/
    │    └── main.go
    │── internal/
    │    ├── api/
    │    │    └── handlers.go
    │    ├── db/
    │    │    ├── db.go
    │    │    └── migrations.go
    │    ├── models/
    │    │    ├── project.go
    │    │    └── task.go
    │    ├── events/
    │    │    └── producer.go
    │    └── services/
    │         └── task_service.go
    │── go.mod
    │── Dockerfile

------------------------------------------------------------------------

## 🔹 Step 1 -- Scaffold the Project

``` bash
mkdir task-service && cd task-service
go mod init github.com/yourname/task-service
go get github.com/go-chi/chi/v5
go get gorm.io/gorm
go get gorm.io/driver/postgres
go get github.com/IBM/sarama   # Kafka client
```

------------------------------------------------------------------------

## 🔹 Step 2 -- Data Models

**project.go**

``` go
type Project struct {
    ID        uint   `gorm:"primaryKey"`
    Name      string
    CreatedAt time.Time
}
```

**task.go**

``` go
type Task struct {
    ID        uint   `gorm:"primaryKey"`
    Title     string
    ProjectID uint
    Status    string
    CreatedAt time.Time
}
```

------------------------------------------------------------------------

## 🔹 Step 3 -- Database Connection

**db.go**

``` go
dsn := "host=postgres user=taskuser password=secret dbname=taskdb port=5432 sslmode=disable"
db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
if err != nil {
    log.Fatal(err)
}
db.AutoMigrate(&Project{}, &Task{})
```

------------------------------------------------------------------------

## 🔹 Step 4 -- REST API Handlers

-   `POST /projects` → create project
-   `GET /projects/{id}` → get project
-   `POST /tasks` → create task (publish event)
-   `GET /tasks/{id}` → get task

------------------------------------------------------------------------

## 🔹 Step 5 -- Event Publishing

Use **Kafka producer** (Sarama) or **NATS client** to publish messages
like:

``` json
{
  "event": "task_created",
  "taskId": 1,
  "title": "First Task"
}
```

------------------------------------------------------------------------

## 🔹 Step 6 -- Docker Setup

**Dockerfile**

``` dockerfile
FROM golang:1.22 AS builder
WORKDIR /app
COPY . .
RUN go mod download
RUN go build -o task-service ./cmd

FROM gcr.io/distroless/base-debian12
WORKDIR /
COPY --from=builder /app/task-service /
ENTRYPOINT ["/task-service"]
```

------------------------------------------------------------------------

## 🔹 Step 7 -- Docker Compose Integration

Add service to `docker-compose.yml`:

``` yaml
  task-service:
    build: ./task-service
    ports:
      - "5001:8080"
    environment:
      - DB_DSN=host=postgres user=taskuser password=secret dbname=taskdb port=5432 sslmode=disable
      - BROKER_URL=kafka:9092
    depends_on:
      - postgres
      - kafka

  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: taskuser
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: taskdb
    ports:
      - "5433:5432"
    volumes:
      - taskdb_data:/var/lib/postgresql/data

  kafka:
    image: bitnami/kafka:latest
    environment:
      - KAFKA_ENABLE_KRAFT=yes
      - KAFKA_CFG_NODE_ID=0
      - KAFKA_CFG_PROCESS_ROLES=controller,broker
      - KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093
      - KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092
      - KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER
      - KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@kafka:9093
    ports:
      - "9092:9092"

volumes:
  taskdb_data:
```

------------------------------------------------------------------------

## 🔹 Step 8 -- Run Locally

``` bash
docker compose up --build
```

Task service will be available at **http://localhost:5001**.

------------------------------------------------------------------------

## 🔹 Next Steps

-   Add request validation
-   Add unit/integration tests
-   Add pagination & filtering for tasks
-   Implement retries & dead-letter for event publishing
