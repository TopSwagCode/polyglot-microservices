# Auth Service

A .NET 8 Web API providing JWT-based authentication for the polyglot microservices platform.

## Features

- User registration
- User login with JWT token generation
- Protected endpoints with JWT authentication
- PostgreSQL database storage
- BCrypt password hashing

## API Endpoints

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and receive JWT token
- `GET /api/auth/me` - Get current user info (requires JWT token)

## Quick Start

### Running Locally

```bash
# Run the service directly (requires PostgreSQL running on localhost:5432)
cd auth-service
dotnet run

# The service will be available at http://localhost:5000
```

### Running with Docker Compose

```bash
# From project root
docker compose up --build

# The service will be available at http://localhost:5000
# PostgreSQL will be available at localhost:5432
```

## Testing

Use the `AuthService.http` file with VS Code REST Client extension to test all endpoints.

### Example Usage

1. Register a user:
```json
POST /api/auth/register
{
  "username": "testuser",
  "password": "TestPassword123!"
}
```

2. Login:
```json
POST /api/auth/login
{
  "username": "testuser", 
  "password": "TestPassword123!"
}
```

3. Access protected endpoint:
```http
GET /api/auth/me
Authorization: Bearer <your-jwt-token>
```

## Configuration

Key configuration options in `appsettings.json`:

- `ConnectionStrings:Default` - PostgreSQL connection string
- `Jwt:Key` - JWT signing key (minimum 32 characters)
- `Jwt:Issuer` - JWT issuer identifier

## Environment Variables

When running with Docker:

- `ConnectionStrings__Default` - Database connection
- `Jwt__Key` - JWT signing key
- `Jwt__Issuer` - JWT issuer
- `ASPNETCORE_ENVIRONMENT` - Environment (Development/Production)

## Database

The service automatically creates the database and tables on startup using Entity Framework Core with PostgreSQL.