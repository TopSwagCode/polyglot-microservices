# GitHub Copilot Instructions for Polyglot Microservices Platform

This repository is a **showcase polyglot microservices platform** demonstrating **.NET (API Gateway & Auth)**, **Go (Task Service)**, **Python (Analytics API & Worker)**, plus a **SvelteKit Frontend**, all wired together via an **event-driven architecture (Kafka)** and diverse datastores (PostgreSQL & MongoDB). It is now beyond the initial scaffold phase: multiple services are implemented with HTTP test files, Dockerfiles, and early cross‑service integration patterns.

## 🏗️ Current Architecture (Implemented)

Services (all under `src/`):
- `api-gateway/` (.NET 9) – YARP reverse proxy & cross-cutting concerns (auth forwarding, future rate limiting). Currently proxies core service routes and hosts minimal health/config endpoints.
- `auth-service/` (.NET 9 currently / targeting .NET 8 baseline per ADR) – Issues JWT bearer tokens; includes EF Core `AppDbContext`, simple `User` model, and `AuthController` (login/register placeholder). Uses PostgreSQL (planned wiring via connection string env vars).
- `task-service/` (Go) – CRUD for tasks/projects (`internal/api/handlers.go`), publishes domain events via Kafka producer (`internal/events/producer.go`), persistence layer abstraction (`internal/db/db.go`).
- `analytics-service/` (Python FastAPI) – Exposes analytics endpoints (`app/api/analytics.py`), uses MongoDB via `database.py`, includes tests (`tests/` + `test_api.py`). Auth integration stub in `auth.py` for validating gateway-provided tokens.
- `analytics-worker/` (Python) – Dedicated Kafka consumer (`kafka_consumer.py`) processing task events and updating analytics aggregates via `analytics_service.py`.
- `frontend/` (SvelteKit) – UI consuming gateway APIs; demonstrates polyglot UI layer.

Infrastructure & Tooling:
- `docker-compose.yml` – Multi-container orchestration (services + supporting infra placeholders; extend for Postgres, Kafka, MongoDB if not already specified).
- `.http` files – One per service for local testing (`ApiGateway.http`, `AuthService.http`, `Analytics-Service.http`, root `api-tests.http`).
- ADRs (`docs/adr/`) – Architectural decisions for gateway (YARP), auth (JWT), events (Kafka), datastore diversity, frontend, etc.
- Testing – Python tests in analytics service; room to add Go + .NET test projects.

Planned / Next Enhancements:
- Harden YARP config (auth propagation, circuit breaking, resiliency policies).
- Implement persistent storage wiring (PostgreSQL for auth & tasks, MongoDB for analytics) with migrations/seed.
- Add structured observability (OpenTelemetry tracing, metrics, centralized logging).
- CI/CD workflows in `.github/workflows/` (build matrix: .NET, Go, Python, Node). Currently missing.
- Kubernetes manifests (`infra/k8s/`) for production-like deployment (not yet present).

## 🔧 Development Patterns

### Project Structure (Representative Snapshot)
```
polyglot-microservices/
├── docker-compose.yml
├── src/
│   ├── api-gateway/            # YARP reverse proxy (.NET)
│   ├── auth-service/           # JWT issuance (.NET)
│   ├── task-service/           # Go CRUD + Kafka events
│   ├── analytics-service/      # FastAPI + MongoDB
│   ├── analytics-worker/       # Python Kafka consumer
│   └── frontend/               # SvelteKit UI
├── docs/adr/                   # Decision records
└── api-tests.http              # Cross-service smoke tests
```

### .NET Service Conventions
- Target: .NET 9.
- Style: Minimal APIs + Controllers (auth currently uses controller pattern for clarity around auth flows).
- Naming: Kebab-case directories; namespaces PascalCase (avoid hyphens in namespaces; keep consistency across services).
- HTTP Tests: Include service host variable (`@ApiGateway_HostAddress`, `@AuthService_HostAddress`).
- Ports (suggested defaults – verify `launchSettings.json`): Gateway 5089, Auth 5091, Task 8082 (Go), Analytics API 8000, Frontend 5173.
- Add `Serilog` or built-in structured logging enrichment (future improvement).

### Development Workflow
```bash
# .NET (Gateway & Auth)
dotnet build polygot-microservices.sln
dotnet run --project src/api-gateway
dotnet run --project src/auth-service

# Go (Task Service)
go run ./src/task-service/cmd

# Python (Analytics API)
pip install -r src/analytics-service/requirements.txt
uvicorn app.main:app --app-dir src/analytics-service/app --reload --port 8000

# Python (Analytics Worker)
python src/analytics-worker/app/main.py

# Frontend
cd src/frontend
npm install
npm run dev

# REST Client Testing (.http files)
# Use variables defined at top of each .http file.
```

## 🚀 Implementation Priorities

When extending this codebase (ordered for highest platform leverage):

1. Observability: Introduce OpenTelemetry (traces + metrics) and centralized logging.
2. Resilience: Enhance YARP config (timeouts, retries, circuit breakers) & propagate correlation IDs.
3. Auth Hardening: Password hashing, token expiry/refresh pattern (short-lived access + optional refresh), role/claims enrichment.
4. Persistence: Wire real PostgreSQL + migrations (EF Core & Go migrations tool) and MongoDB indices.
5. Event Schema Governance: Define versioned Avro/JSON schemas for Kafka topics (task.events.v1, etc.).
6. CI/CD: Add GitHub Actions matrix (dotnet / go / python / node) + lint + test + docker build.
7. Security: Add basic rate limiting, input validation, dependency vulnerability scanning.
8. Kubernetes Manifests: `infra/k8s/` with Kustomize overlays (dev/stage/prod).
9. Frontend Integration: Auth login flow + real-time updates (SSE/WebSocket) for analytics stream (future enhancement).
10. Documentation: Add architecture diagrams & sequence flows for task creation → event → analytics update.

### Adding New Services
- Create service folders at root level (not in `src/`)
- Include language-specific `.http` test files
- Add README.md with service-specific setup instructions
- Update root solution for .NET services, or create language-specific build files

### API Gateway Routing (Target State)
- `/auth/*` → Auth Service (strip prefix, forward Authorization header)
- `/tasks/*` → Task Service (JWT validated at gateway then forwarded claims context)
- `/analytics/*` → Analytics Service (read-only endpoints; potential caching layer later)
- Health endpoints: `/healthz`, `/readyz` aggregated checks.
- Future: Add rate limiting & quota policies per route cluster.

## 📋 Language-Specific Guidelines

### .NET Services (.NET 9)
- Prefer minimal APIs unless complexity (auth controller) warrants MVC controllers.
- DTOs as records; map persistence entities separately.
- Enable Swagger in Development only.
- Central exception handling middleware for consistent problem details responses.
- Use `ILogger<T>` with structured properties (`TaskId`, `UserId`, `CorrelationId`).
- Async throughout; avoid sync-over-async.
- Consider FluentValidation or minimal manual guards for inputs.

### Go Services (Task Service Implemented)
- Layout: `cmd/main.go`, `internal/api`, `internal/services`, `internal/events`, `internal/db`.
- Always pass `context.Context` down stack.
- Logging: adopt `slog` with JSON handler for structured logs.
- Add unit tests (`testing` + table-driven) for handlers & service layer.
- Retry semantics for Kafka producer (exponential backoff) and idempotent event publishing.
- Graceful shutdown: capture signals, flush producer, close DB.

### Python Services (Analytics API & Worker Implemented)
- FastAPI with Pydantic models, async motor client for MongoDB.
- Test strategy: unit tests for service logic + API tests using `TestClient`.
- Background worker isolates consumer from API (scaling independently).
- Introduce schema validation for consumed Kafka events (pydantic models / fastjsonschema).
- Add Alembic-equivalent? (Not needed for Mongo; ensure migration scripts for index creation at startup).

### Frontend (SvelteKit)
- Use environment variables for API base (pointing to gateway).
- Implement auth store (JWT in memory + refresh logic; avoid localStorage for long term until hardened).
- Plan WebSocket/SSE subscription for analytics live updates.

## 🎯 Code Generation Prompts

**Immediate / Near-Term Enhancements:**
- "Add OpenTelemetry tracing across gateway, auth, task, analytics (propagate traceparent)."
- "Implement YARP routes with retry + timeout + circuit breaker policies (Polly)."
- "Add EF Core migrations and PostgreSQL docker service for auth-service."
- "Implement password hashing & JWT refresh token flow in auth-service."
- "Add Kafka event schema validation and DLQ handling in analytics-worker."
- "Create GitHub Actions workflow: build & test all languages + docker build & push."
- "Add task-service unit tests (handlers, service, event emission)."
- "Add MongoDB index setup & analytics aggregation endpoints (e.g., /analytics/activity/daily)."

**Future / Stretch:**
- "Introduce WebSocket/SSE push from analytics-service to frontend."
- "Add rate limiting & API key support at gateway layer."
- "Generate k8s manifests with Helm chart for each service + umbrella chart."
- "Implement saga or outbox pattern for reliable event publishing in task-service."
- "Add RBAC / roles claims and route-based authorization policies."
- "Add canary & blue/green deployment workflows in CI/CD."
- "Integrate security scanning (Trivy, Snyk) into pipeline." 

---
*Focus on clarity, composability, and demonstrable cross-language patterns. Keep changes incremental, observable, and well-documented.*