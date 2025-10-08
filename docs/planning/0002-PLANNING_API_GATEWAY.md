# Planning: API Gateway (.NET 9)

This document describes the plan for building the **API Gateway** in
C#.\
The API Gateway will handle routing, authentication, and act as the
entry point for all requests. It will run locally via **Docker
Compose**.

------------------------------------------------------------------------

## 🔹 Goals

-   Use **YARP (Yet Another Reverse Proxy)** to route requests to
    backend services.
-   Forward `/auth/*` routes to the **Auth Service**.
-   Prepare for future services (Task Service in Go, Analytics in
    Python).
-   Support **JWT authentication** to validate requests before
    forwarding.

------------------------------------------------------------------------

## 🔹 Tech Stack

-   **.NET 8** (Minimal API)
-   **YARP (Microsoft.ReverseProxy)** for routing
-   **JWT Bearer Authentication**

------------------------------------------------------------------------

## 🔹 Project Structure

    api-gateway/
    │── ApiGateway.csproj
    │── Program.cs
    │── appsettings.json
    │── Dockerfile

------------------------------------------------------------------------

## 🔹 Step 1 -- Scaffold the Project

``` bash
dotnet new web -n ApiGateway
cd ApiGateway
```

------------------------------------------------------------------------

## 🔹 Step 2 -- Add Dependencies

``` bash
dotnet add package Yarp.ReverseProxy
dotnet add package Microsoft.AspNetCore.Authentication.JwtBearer
```

------------------------------------------------------------------------

## 🔹 Step 3 -- Configure Routes

**appsettings.json**

``` json
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
  },
  "Jwt": {
    "Issuer": "auth-service",
    "Audience": "polyglot-platform",
    "Key": "supersecretkey"
  }
}
```

------------------------------------------------------------------------

## 🔹 Step 4 -- Configure Program.cs

``` csharp
var builder = WebApplication.CreateBuilder(args);

// Add JWT Authentication
builder.Services.AddAuthentication("Bearer")
    .AddJwtBearer("Bearer", options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"]!))
        };
    });

// Add YARP
builder.Services.AddReverseProxy()
    .LoadFromConfig(builder.Configuration.GetSection("ReverseProxy"));

var app = builder.Build();

app.UseAuthentication();
app.UseAuthorization();

app.MapReverseProxy();

app.Run();
```

------------------------------------------------------------------------

## 🔹 Step 5 -- Docker Setup

**Dockerfile**

``` dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS base
WORKDIR /app
EXPOSE 5000

FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
COPY . .
RUN dotnet restore "./ApiGateway.csproj"
RUN dotnet publish "./ApiGateway.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "ApiGateway.dll"]
```

------------------------------------------------------------------------

## 🔹 Step 6 -- Docker Compose Integration

Extend your root `docker-compose.yml` to include the gateway:

``` yaml
  api-gateway:
    build: ./api-gateway
    ports:
      - "8080:5000"
    environment:
      - Jwt__Key=supersecretkey
      - Jwt__Issuer=auth-service
      - Jwt__Audience=polyglot-platform
    depends_on:
      - auth-service
```

Now:

``` bash
docker compose up --build
```

API Gateway available at: **http://localhost:8080**\
- Routes `/auth/*` → `auth-service`\
- Future: add routes for Task Service and Analytics

------------------------------------------------------------------------

## 🔹 Next Steps

-   Add rate limiting & caching policies.
-   Add OpenTelemetry tracing for distributed requests.
-   Configure HTTPS & production-ready security headers.
