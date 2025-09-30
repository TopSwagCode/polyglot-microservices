# GitHub Copilot Instructions for Polyglot Microservices Platform

This is a **showcase polyglot microservices platform** demonstrating **.NET, Go, and Python** services with modern DevOps practices. The project is currently in **early development** - only the API Gateway exists; other services are planned.

## 🏗️ Current Architecture

**Implemented:**
- `src/Api-Gateway/` - .NET 9 minimal API (basic template, needs YARP implementation)
- Solution structure with `Api-Gateway.sln` at root
- HTTP test files using VS Code REST Client

**Planned Services (not yet implemented):**
- `auth-service/` - .NET 8 authentication with JWT and PostgreSQL  
- `task-service/` - Go service with Kafka/NATS event publishing
- `analytics-service/` - Python FastAPI with MongoDB
- Infrastructure: Docker Compose, Kubernetes manifests, CI/CD

## 🔧 Development Patterns

### Project Structure
```
polyglot-microservices/
├── Api-Gateway.sln          # Root solution file
├── src/Api-Gateway/         # Only implemented service
│   ├── Api-Gateway.http     # REST Client tests (port 5089)
│   └── Program.cs           # Minimal API template
└── .vscode/settings.json    # VS Code workspace config
```

### .NET Service Conventions
- **Target**: .NET 9 for new services (.NET 8 for auth-service per README)
- **API Style**: Minimal APIs with `app.MapGet()` pattern
- **Project Naming**: Use kebab-case with hyphens (e.g., `Api-Gateway`)
- **Namespace**: Convert hyphens to underscores (e.g., `Api_Gateway`)
- **HTTP Tests**: Include `.http` files with `@ServiceName_HostAddress` variables
- **Launch Settings**: Disable browser launch, use specific ports (5089 for gateway)

### Development Workflow
```bash
# Build and run from solution root
dotnet build Api-Gateway.sln
dotnet run --project src/Api-Gateway

# Test with HTTP files in VS Code REST Client extension
# Use @Api_Gateway_HostAddress = http://localhost:5089
```

## 🚀 Implementation Priorities

When extending this codebase:

1. **API Gateway Enhancement**: Replace weather template with YARP reverse proxy configuration
2. **Service Creation**: Follow the planned folder structure: `auth-service/`, `task-service/`, `analytics-service/`
3. **Infrastructure**: Add `docker-compose.yml`, Kubernetes manifests in `infra/k8s/`
4. **CI/CD**: Create `.github/workflows/` for multi-language pipeline

### Adding New Services
- Create service folders at root level (not in `src/`)
- Include language-specific `.http` test files
- Add README.md with service-specific setup instructions
- Update root solution for .NET services, or create language-specific build files

### API Gateway Implementation
The current `Program.cs` needs YARP configuration to route to:
- `/auth/*` → Auth Service
- `/tasks/*` → Task Service  
- `/analytics/*` → Analytics Service

## 📋 Language-Specific Guidelines

### .NET Services (.NET 8/9)
- Use minimal APIs, record DTOs, dependency injection
- Include `Microsoft.AspNetCore.OpenApi` for development
- Add `ILogger<T>` for structured logging
- Use `async Task` patterns consistently

### Go Services (Planned)
- Structure: `cmd/`, `pkg/`, `internal/` folders
- Use `context.Context`, `log/slog`, standard `testing`
- Implement Kafka/NATS event publishing with retries

### Python Services (Planned)  
- FastAPI with Python 3.11+, full type hints
- Use `pytest`, async/await patterns
- MongoDB integration for analytics data

## 🎯 Code Generation Prompts

**Immediate needs:**
- "Convert Api-Gateway to YARP reverse proxy with routes to auth, tasks, analytics services"
- "Add Docker Compose with PostgreSQL, MongoDB, Kafka services"
- "Create .NET auth service with JWT, PostgreSQL, user registration endpoints"

**Future development:**
- "Generate Go task service with CRUD operations and Kafka event publishing"
- "Create Python FastAPI analytics service consuming Kafka events"
- "Add Kubernetes manifests for all services with proper networking"

---
*This project showcases modern microservices patterns - focus on clean architecture, proper separation of concerns, and production-ready practices.*