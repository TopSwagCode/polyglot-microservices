# Planning: Auth Service (.NET 9)

This document describes the plan for building the **Auth Service** in
C#.\
The Auth Service will handle user registration, login, and JWT
authentication, and will run locally via **Docker Compose**.

------------------------------------------------------------------------

## 🔹 Goals

-   Expose a **REST API** with endpoints for:
    -   `POST /register` → create user
    -   `POST /login` → authenticate and issue JWT
    -   `GET /me` → get current user info (protected endpoint)
-   Store users in **PostgreSQL**
-   Use **JWT tokens** for authentication
-   Make it **easy to run locally** with Docker Compose

------------------------------------------------------------------------

## 🔹 Tech Stack

-   **.NET 9** Web API (Minimal APIs or Controllers)
-   **Entity Framework Core** (with PostgreSQL provider)
-   **ASP.NET Core Identity** or lightweight custom user model
-   **JWT Bearer Authentication**
-   **Docker & Docker Compose**

------------------------------------------------------------------------

## 🔹 Project Structure

    auth-service/
    │── AuthService.csproj
    │── Program.cs
    │── appsettings.json
    │── Controllers/
    │    └── AuthController.cs
    │── Models/
    │    └── User.cs
    │── Data/
    │    └── AppDbContext.cs
    │── Services/
    │    └── TokenService.cs
    │── Migrations/
    │── Dockerfile

------------------------------------------------------------------------

## 🔹 Step 1 -- Scaffold the Project

``` bash
dotnet new webapi -n AuthService
cd AuthService
```

------------------------------------------------------------------------

## 🔹 Step 2 -- Add Dependencies

``` bash
dotnet add package Microsoft.EntityFrameworkCore
dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL
dotnet add package Microsoft.AspNetCore.Authentication.JwtBearer
dotnet add package BCrypt.Net-Next
```

------------------------------------------------------------------------

## 🔹 Step 3 -- Data Model & DbContext

**User.cs**

``` csharp
public class User
{
    public int Id { get; set; }
    public string Username { get; set; } = string.Empty;
    public string PasswordHash { get; set; } = string.Empty;
}
```

**AppDbContext.cs**

``` csharp
public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }
    public DbSet<User> Users => Set<User>();
}
```

------------------------------------------------------------------------

## 🔹 Step 4 -- Token Service

Create `TokenService.cs` to generate JWT tokens using a signing key from
configuration.

------------------------------------------------------------------------

## 🔹 Step 5 -- Auth Controller

**Endpoints:** - `POST /register` → hash password (BCrypt), save user -
`POST /login` → validate user, return JWT - `GET /me` → requires JWT,
returns username/id

------------------------------------------------------------------------

## 🔹 Step 6 -- Configure Services in Program.cs

-   Add EF Core with PostgreSQL connection string
-   Configure JWT authentication
-   Map controller endpoints

------------------------------------------------------------------------

## 🔹 Step 7 -- Docker Setup

**Dockerfile**

``` dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS base
WORKDIR /app
EXPOSE 5000

FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
COPY . .
RUN dotnet restore "./AuthService.csproj"
RUN dotnet publish "./AuthService.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "AuthService.dll"]
```

**docker-compose.yml**

``` yaml
version: '3.9'
services:
  auth-service:
    build: ./auth-service
    ports:
      - "5000:5000"
    environment:
      - ConnectionStrings__Default=Host=postgres;Database=authdb;Username=authuser;Password=secret
      - Jwt__Key=supersecretkey
      - Jwt__Issuer=auth-service
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: authuser
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: authdb
    ports:
      - "5432:5432"
    volumes:
      - authdb_data:/var/lib/postgresql/data

volumes:
  authdb_data:
```

------------------------------------------------------------------------

## 🔹 Step 8 -- Run Locally

``` bash
docker compose up --build
```

Auth service will be available at **http://localhost:5000**.

------------------------------------------------------------------------

## 🔹 Next Steps

-   Add refresh tokens & roles
-   Add unit/integration tests
-   Connect API Gateway to Auth Service
