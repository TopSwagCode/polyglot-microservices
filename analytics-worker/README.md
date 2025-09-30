# Analytics Worker

This service consumes Kafka events and processes them for analytics.

## Purpose

The Analytics Worker is a dedicated Kafka consumer that:
- Consumes task and project events from Kafka topics
- Processes events and stores them in MongoDB  
- Updates analytics metrics (user metrics, project metrics)
- Runs independently from the Analytics API service

## Architecture

- **Pure Kafka Consumer**: No HTTP endpoints, just event processing
- **MongoDB Integration**: Stores raw events and computed metrics
- **Async Processing**: Efficient event processing with asyncio
- **Graceful Shutdown**: Handles SIGINT/SIGTERM signals properly

## Events Processed

### Task Events
- `task_created` - New task created
- `task_updated` - Task updated (status, title, etc.)
- `task_completed` - Task marked as completed
- `task_deleted` - Task deleted

### Project Events  
- `project_created` - New project created
- `project_updated` - Project updated
- `project_deleted` - Project deleted

## Environment Variables

```env
MONGODB_URL=mongodb://root:secret@mongo:27017
DATABASE_NAME=analytics_db
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_GROUP_ID=analytics-worker
KAFKA_TOPIC_TASK=task-events
KAFKA_TOPIC_PROJECT=project-events
```

## Running

```bash
# Build
docker build -t analytics-worker .

# Run
docker run -e MONGODB_URL=mongodb://root:secret@mongo:27017 analytics-worker
```