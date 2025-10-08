# Task Service (Refactored Domain-Centric Layout)

This service provides Task & Project management plus domain event emission. The codebase was refactored from a generic *models / services / events* layout to a **domain / platform** oriented structure for clarity, testability, and scalability.

## Package Layout

```
internal/
  platform/
    events/          # Event abstraction + Kafka producer
  project/           # Project domain (entity, repo, service, errors)
  task/              # Task domain (entity, repo, service, errors)
  http/
    dto/             # Transport-facing request/response shapes
    handlers/        # HTTP handlers per domain
  db/                # Bootstrap (GORM setup + migrations)
```

### Why This Layout?
- Encapsulates domain logic near its data model (task, project).
- Repositories abstract persistence (clean unit tests with mocks/stubs).
- Events decoupled via a Publisher interface (supports alternative backends).
- HTTP layer translated into DTOs so domain structs stay persistence‑focused.
- Avoids *god packages* (e.g., `models`, `services`, `events`) that accumulate unrelated code.

### Event Topics
- Task events → `task-events` (override: `KAFKA_TOPIC`).
- Project events → `project-events` (override: `KAFKA_PROJECT_TOPIC`).

### Environment Variables
| Variable | Purpose | Default |
|----------|---------|---------|
| `DB_DSN` | PostgreSQL DSN | host=postgres user=taskuser password=secret dbname=taskdb port=5432 sslmode=disable |
| `KAFKA_BROKER` | Kafka bootstrap | kafka:9092 |
| `KAFKA_TOPIC` | Task events topic | task-events |
| `KAFKA_PROJECT_TOPIC` | Project events topic | project-events |
| `PORT` | HTTP server port | 8080 |

### Extending
- Add new domain: create `internal/<domain>` with `domain.go`, `repository.go`, `service.go`, `errors.go`.
- Emit events: implement `events.Event` (Name, Key, Payload) and publish via injected `Publisher`.
- Add transports: create parallel folder `internal/http/handlers/<domain>_handlers.go` and wire in router.

### Testing Strategy (Planned)
- Unit tests for project & task services using in-memory or mock repositories.
- Publisher mock to assert event emission.
- Table-driven handler tests (chi router + httptest) for HTTP layer.

### Migration Notes
Legacy packages removed:
- `internal/models`, `internal/services`, `internal/events` (old producer), `internal/api` (monolithic handlers).

### Next Improvements
- Add request validation (e.g., go-playground/validator) in handlers.
- Add OpenTelemetry tracing (span per request + event publish annotation).
- Implement structured error responses (problem+json).
- Graceful Kafka producer health check & metrics.

---
Refactor goal: make the service easier to reason about, safer to evolve, and simpler to test. Contributions should follow the domain-first structure illustrated above.
