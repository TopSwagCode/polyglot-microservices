# Planning: Developer Tooling (Mongo Express, pgAdmin, Kafka UI)

This document describes how to extend the polyglot microservices
platform with **developer tooling** for easier inspection of databases
and event streams.

------------------------------------------------------------------------

## 🔹 Goals

-   Add **Mongo Express** for browsing MongoDB data.
-   Add **pgAdmin** for managing PostgreSQL databases.
-   Add a **Kafka UI** for inspecting topics, partitions, and messages.

------------------------------------------------------------------------

## 🔹 Mongo Express

Web UI for MongoDB.

**docker-compose.yml**

``` yaml
  mongo-express:
    image: mongo-express:1.0.0-alpha.4
    ports:
      - "8081:8081"
    environment:
      - ME_CONFIG_MONGODB_SERVER=mongo
      - ME_CONFIG_MONGODB_ADMINUSERNAME=root
      - ME_CONFIG_MONGODB_ADMINPASSWORD=secret
    depends_on:
      mongo:
        condition: service_healthy
    networks:
      - auth-network
```

Access: **http://localhost:8081**\
Login with: `root / secret`

------------------------------------------------------------------------

## 🔹 pgAdmin

Web UI for PostgreSQL.

**docker-compose.yml**

``` yaml
  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@admin.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    depends_on:
      - postgres
      - task-postgres
    networks:
      - auth-network
```

Access: **http://localhost:5050**\
Login with: `admin@admin.com / admin`\
Add connections manually to:\
- `postgres:5432` → `authdb`\
- `task-postgres:5432` → `taskdb`

------------------------------------------------------------------------

## 🔹 Kafka UI

Several options exist (Kafdrop, Redpanda Console, Provectus Kafka UI).
We'll use **Provectus Kafka UI**.

**docker-compose.yml**

``` yaml
  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka-ui
    ports:
      - "8082:8080"
    environment:
      - KAFKA_CLUSTERS_0_NAME=local
      - KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS=kafka:9092
    depends_on:
      kafka:
        condition: service_healthy
    networks:
      - auth-network
```

Access: **http://localhost:8082**\
Inspect topics like `task-events` and `project-events`.

------------------------------------------------------------------------

## 🔹 Updated Ports Overview

-   API Gateway → **http://localhost:8080**
-   Auth Service → internal only
-   Task Service → internal only
-   Analytics Service → **http://localhost:8000**
-   Mongo Express → **http://localhost:8081**
-   pgAdmin → **http://localhost:5050**
-   Kafka UI → **http://localhost:8082**

------------------------------------------------------------------------

## 🔹 Next Steps

-   Configure pgAdmin server groups for easier DB browsing.
-   Add role-based auth to Mongo Express / Kafka UI in production.
-   Optionally add **Grafana + Prometheus** for metrics dashboards.
