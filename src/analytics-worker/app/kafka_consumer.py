import json
import asyncio
from typing import Dict, Any
from datetime import datetime
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import structlog
from app.config import settings
from app.database import get_database
from app.models import TaskEvent, ProjectEvent
from app.analytics_service import AnalyticsService

logger = structlog.get_logger()


class KafkaEventConsumer:
    def __init__(self):
        self.consumer = None
        self.analytics_service = AnalyticsService()
        self.running = False

    async def start_consumer(self):
        """Start consuming events from Kafka"""
        logger.info("=== KAFKA CONSUMER STARTING ===")
        try:
            logger.info("Initializing Kafka consumer", 
                       bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                       topics=[settings.KAFKA_TOPIC_TASK, settings.KAFKA_TOPIC_PROJECT],
                       group_id=settings.KAFKA_GROUP_ID)
            
            # Create Kafka consumer
            self.consumer = KafkaConsumer(
                settings.KAFKA_TOPIC_TASK,
                settings.KAFKA_TOPIC_PROJECT,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=settings.KAFKA_GROUP_ID,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                consumer_timeout_ms=1000
            )
            
            self.running = True
            logger.info("Kafka consumer initialized successfully", 
                       topics=[settings.KAFKA_TOPIC_TASK, settings.KAFKA_TOPIC_PROJECT])
            
            # Start consuming messages
            await self._consume_messages()
            
        except KafkaError as e:
            logger.error("Kafka consumer error", error=str(e))
            raise
        except Exception as e:
            logger.error("Failed to start Kafka consumer", error=str(e), exc_info=True)
            raise

    async def stop_consumer(self):
        """Stop consuming events"""
        logger.info("Stopping Kafka consumer")
        self.running = False
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer stopped")

    async def _consume_messages(self):
        """Main message consumption loop"""
        logger.info("Starting Kafka message consumption loop")
        
        message_count = 0
        while self.running:
            try:
                # Poll for messages with timeout
                message_batch = self.consumer.poll(timeout_ms=1000)
                
                if message_batch:
                    batch_size = sum(len(messages) for messages in message_batch.values())
                    message_count += batch_size
                    logger.info("Received message batch", 
                              batch_size=batch_size, 
                              total_processed=message_count)
                    
                    for topic_partition, messages in message_batch.items():
                        for message in messages:
                            await self._process_message(message)
                else:
                    # Log every 30 seconds when no messages
                    if message_count % 30 == 0:
                        logger.debug("No messages received, continuing to poll", 
                                   total_processed=message_count)
                            
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error("Error consuming messages", error=str(e), exc_info=True)
                await asyncio.sleep(5)  # Wait before retrying

    async def _process_message(self, message):
        """Process a single Kafka message (new schema only).

        Expected schema:
        {
            "event": "task.created" | "project.created" | ...,
            "key": "task:1",               # optional for analytics currently
            "timestamp": "2025-10-08T19:14:42.082390932Z",
            "data": {                        # domain payload
                "ID": 1,                     # task id (task events)
                "ProjectID": 2,
                "Title": "a",
                "Status": "open",
                "UserID": "1",
                "Username": "admin"
            }
        }
        Project events use analogous fields (ID, Name, UserID, Username).
        """
        envelope = message.value
        topic = getattr(message, "topic", "")
        try:
            # Strict validation
            if not isinstance(envelope, dict):
                logger.warning("Skipping non-dict message", raw=envelope)
                return
            if "data" not in envelope or not isinstance(envelope["data"], dict):
                logger.warning("Envelope missing data object", envelope=envelope)
                return
            event_type = envelope.get("event", "")
            payload: Dict[str, Any] = envelope["data"]

            # Extract fields (capitalized Go struct JSON keys expected). We do NOT fallback to old snake_case.
            task_id = payload.get("ID") if event_type.startswith("task.") else None
            project_id = payload.get("ProjectID")
            user_id = payload.get("UserID")
            username = payload.get("Username")
            title = payload.get("Title")
            status = payload.get("Status")
            name = payload.get("Name")  # project name
            ts_raw = envelope.get("timestamp")

            logger.info(
                "=== EVENT RECEIVED (strict) ===",
                topic=topic,
                event_type=event_type,
                user_id=user_id,
                username=username,
                task_id=task_id,
                project_id=project_id,
                timestamp=ts_raw,
            )
            logger.debug("Envelope payload", envelope=envelope, data=payload)

            if event_type.startswith("task."):
                await self._process_task_event({
                    "event": event_type,
                    "task_id": task_id,
                    "project_id": project_id,
                    "user_id": user_id,
                    "username": username,
                    "title": title,
                    "status": status,
                    "timestamp": ts_raw,
                })
            elif event_type.startswith("project."):
                await self._process_project_event({
                    "event": event_type,
                    "project_id": payload.get("ID"),  # For project events ID refers to project ID
                    "user_id": user_id,
                    "username": username,
                    "name": name,
                    "timestamp": ts_raw,
                })
            else:
                logger.warning("Unknown event type (strict mode)", event_type=event_type, topic=topic)
        except Exception as e:
            logger.error("Error processing message (strict)", error=str(e), envelope=envelope, exc_info=True)

    async def _process_task_event(self, data: Dict[str, Any]):
        """Process task event and store analytics data"""
        try:
            logger.info("=== PROCESSING TASK EVENT ===", 
                       event_type=data.get("event"),
                       task_id=data.get("task_id"),
                       project_id=data.get("project_id"),
                       user_id=data.get("user_id"),
                       title=data.get("title"),
                       status=data.get("status"))
            
            # Create task event document with the correct field mapping
            # Parse timestamp (strict)
            ts_raw = data.get("timestamp")
            timestamp = None
            if isinstance(ts_raw, str):
                try:
                    timestamp = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                except ValueError:
                    logger.warning("Failed ISO parse task timestamp", raw=ts_raw)
            task_event = TaskEvent(
                event=data.get("event"),
                task_id=data.get("task_id"),
                project_id=data.get("project_id"),
                user_id=str(data.get("user_id")),
                username=data.get("username"),
                title=data.get("title"),
                name=data.get("name"),
                status=data.get("status"),
                timestamp=timestamp or datetime.utcnow()
            )
            
            logger.info("Created task event object", task_event_id=task_event.task_id)
            
            # Store event in database
            db = get_database()
            result = await db.task_events.insert_one(task_event.model_dump())
            logger.info("Stored task event in database", inserted_id=str(result.inserted_id))
            
            # Update analytics metrics
            logger.info("Updating analytics metrics for task event")
            await self.analytics_service.update_task_metrics(task_event)
            
            logger.info("Task event processed successfully", 
                       event_type=task_event.event,
                       task_id=task_event.task_id,
                       user_id=task_event.user_id)
            
        except Exception as e:
            logger.error("Error processing task event", error=str(e), message_data=data, exc_info=True)

    async def _process_project_event(self, data: Dict[str, Any]):
        """Process project event and store analytics data"""
        try:
            logger.info("=== PROCESSING PROJECT EVENT ===", 
                       event_type=data.get("event"),
                       project_id=data.get("project_id"),
                       user_id=data.get("user_id"),
                       name=data.get("name"))
            
            # Create project event document
            ts_raw = data.get("timestamp")
            timestamp = None
            if isinstance(ts_raw, str):
                try:
                    timestamp = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                except ValueError:
                    logger.warning("Failed ISO parse project timestamp", raw=ts_raw)
            project_event = ProjectEvent(
                event=data.get("event"),
                project_id=data.get("project_id"),
                user_id=str(data.get("user_id")),
                username=data.get("username"),
                name=data.get("name"),
                timestamp=timestamp or datetime.utcnow()
            )
            
            logger.info("Created project event object", project_event_id=project_event.project_id)
            
            # Store event in database
            db = get_database()
            result = await db.project_events.insert_one(project_event.model_dump())
            logger.info("Stored project event in database", inserted_id=str(result.inserted_id))
            
            # Update analytics metrics
            logger.info("Updating analytics metrics for project event")
            await self.analytics_service.update_project_metrics(project_event)
            
            logger.info("Project event processed successfully",
                       event_type=project_event.event,
                       project_id=project_event.project_id,
                       user_id=project_event.user_id)
            
        except Exception as e:
            logger.error("Error processing project event", error=str(e), message_data=data, exc_info=True)