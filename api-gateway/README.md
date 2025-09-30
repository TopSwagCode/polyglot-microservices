# API Gateway

A .NET 9 API Gateway using YARP (Yet Another Reverse Proxy) to route requests to backend microservices in the polyglot platform.

## Features

- **Reverse Proxy**: Routes requests to backend services using YARP
- **JWT Authentication**: Validates JWT tokens for protected endpoints
- **Service Discovery**: Routes `/auth/*` requests to the Auth Service
- **Health Checks**: Built-in health monitoring
- **CORS Support**: Cross-origin request handling for development

## Architecture

```
Client → API Gateway (Port 8080) → Backend Services
         ├── /auth/* → Auth Service (Port 5000)
         ├── /tasks/* → Task Service (Future)
         └── /analytics/* → Analytics Service (Future)
```

## Endpoints

- `GET /` - API Gateway information and available routes
- `GET /health` - Health check endpoint
- `/auth/*` - Proxied to Auth Service
  - `POST /auth/api/auth/register` - User registration
  - `POST /auth/api/auth/login` - User login
  - `GET /auth/api/auth/me` - Get current user (requires JWT)

## Quick Start

### Running Locally (Development)

```bash
# Start the API Gateway (requires Auth Service running on localhost:5000)
cd api-gateway
dotnet run

# The gateway will be available at http://localhost:5000
```

### Running with Docker Compose

```bash
# From project root - starts gateway, auth service, and PostgreSQL
docker compose up --build

# API Gateway available at http://localhost:8080
# Direct Auth Service access at internal port (not exposed)
```

## Configuration

### JWT Settings

The gateway validates JWT tokens using the same configuration as the Auth Service:

```json
{
  "Jwt": {
    "Issuer": "auth-service-docker",
    "Audience": "polyglot-platform", 
    "Key": "docker_supersecretkey_that_is_at_least_32_characters_long"
  }
}
```

### YARP Routing Configuration

Routes are configured in `appsettings.json`:

```json
{
  "ReverseProxy": {
    "Clusters": {
      "auth": {
        "Destinations": {
          "auth1": { "Address": "http://auth-service:5000/" }
        }
      }
    },
    "Routes": [
      {
        "RouteId": "auth",
        "ClusterId": "auth", 
        "Match": { "Path": "/auth/{**catch-all}" }
      }
    ]
  }
}
```

## Testing

Use the `ApiGateway.http` file with VS Code REST Client extension to test routing:

### Basic Flow

1. **Check Gateway Health**:
   ```http
   GET http://localhost:8080/health
   ```

2. **Register User via Gateway**:
   ```http
   POST http://localhost:8080/auth/api/auth/register
   Content-Type: application/json
   
   {
     "username": "testuser",
     "password": "TestPassword123!"
   }
   ```

3. **Login via Gateway**:
   ```http
   POST http://localhost:8080/auth/api/auth/login
   Content-Type: application/json
   
   {
     "username": "testuser", 
     "password": "TestPassword123!"
   }
   ```

4. **Access Protected Endpoint**:
   ```http
   GET http://localhost:8080/auth/api/auth/me
   Authorization: Bearer <your-jwt-token>
   ```

## Environment Variables

When running with Docker:

- `Jwt__Key` - JWT signing key (must match Auth Service)
- `Jwt__Issuer` - JWT issuer (must match Auth Service)
- `Jwt__Audience` - JWT audience identifier
- `ASPNETCORE_ENVIRONMENT` - Environment (Development/Production)

## Development

### Adding New Routes

To route to additional services, update `appsettings.json`:

```json
{
  "ReverseProxy": {
    "Clusters": {
      "tasks": {
        "Destinations": {
          "tasks1": { "Address": "http://task-service:5001/" }
        }
      }
    },
    "Routes": [
      {
        "RouteId": "tasks",
        "ClusterId": "tasks",
        "Match": { "Path": "/tasks/{**catch-all}" }
      }
    ]
  }
}
```

### Monitoring

- YARP provides built-in metrics and health checks
- Logs show routing decisions and proxy performance
- Health endpoint can be integrated with monitoring systems

## Security

- JWT validation ensures only authenticated requests reach backend services
- CORS policies can be configured per environment
- Rate limiting and additional security policies can be added via YARP middleware