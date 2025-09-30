# Developer Tools

This document describes the developer tools available in the polyglot microservices platform for database and message queue inspection.

## Available Tools

### 1. Mongo Express (MongoDB Web UI)
- **URL**: http://localhost:8081
- **Purpose**: MongoDB database administration and data browsing
- **Database**: `analytics_db` (Analytics Service data)
- **Collections**: 
  - `task_events` - Kafka events consumed by Analytics Service
  - Any other analytics collections

### 2. pgAdmin (PostgreSQL Web UI)
- **URL**: http://localhost:5050
- **Purpose**: PostgreSQL database administration
- **Login**: admin@admin.com / admin
- **Databases to Connect**:
  - **Auth Database**: 
    - Host: `postgres` (container name)
    - Port: `5432`
    - Database: `authdb`
    - Username: `auth_user`
    - Password: `auth_password`
  - **Task Database**:
    - Host: `task-postgres` (container name)  
    - Port: `5432`
    - Database: `taskdb`
    - Username: `task_user`
    - Password: `task_password`

### 3. Kafka UI
- **URL**: http://localhost:8082
- **Purpose**: Kafka cluster monitoring and topic management
- **Kafka Cluster**: Connected to `kafka:9092`
- **Topics**:
  - `task-events` - Task creation/update events
  - `project-events` - Project-related events (if implemented)

## Usage Instructions

### Setting up pgAdmin Database Connections

1. Open pgAdmin at http://localhost:5050
2. Login with admin@admin.com / admin
3. Right-click "Servers" → "Register" → "Server"
4. For Auth Database:
   - General tab: Name = "Auth Service DB"
   - Connection tab: 
     - Host name/address = `postgres`
     - Port = `5432`
     - Maintenance database = `authdb`
     - Username = `auth_user`
     - Password = `auth_password`
5. For Task Database:
   - General tab: Name = "Task Service DB"
   - Connection tab:
     - Host name/address = `task-postgres`
     - Port = `5432`
     - Maintenance database = `taskdb`
     - Username = `task_user`
     - Password = `task_password`

### Viewing Kafka Topics

1. Open Kafka UI at http://localhost:8082
2. Topics are automatically listed
3. Click on topic name to view messages
4. Use "Produce Message" to send test messages

### Browsing MongoDB Data

1. Open Mongo Express at http://localhost:8081
2. Click on `analytics_db` database
3. Browse collections to see consumed Kafka events
4. View individual documents and their structure

## Development Workflow

These tools enhance the development experience by providing:

1. **Database Inspection**: Verify data persistence and relationships
2. **Event Monitoring**: Track Kafka message flow between services  
3. **Debugging Support**: Inspect data state during development
4. **Schema Validation**: Ensure data structures match expectations

## Security Notes

- These tools are for **development only**
- Do not expose these ports in production
- Default credentials are used for convenience
- Consider adding authentication for team environments