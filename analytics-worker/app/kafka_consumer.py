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
        """Process a single Kafka message"""
        try:
            topic = message.topic
            data = message.value
            event_type = data.get("event", "")
            
            # Comprehensive logging for every event received
            logger.info("=== EVENT RECEIVED ===", 
                       topic=topic, 
                       event_type=event_type, 
                       user_id=data.get("user_id"),
                       username=data.get("username"),
                       task_id=data.get("task_id"),
                       project_id=data.get("project_id"),
                       timestamp=data.get("timestamp"))
            
            logger.debug("Full event payload", payload=data)
            
            # Route based on event type rather than topic since both events come to task-events topic
            if event_type.startswith("task_"):
                logger.info("Routing to task event processor", event_type=event_type)
                await self._process_task_event(data)
            elif event_type.startswith("project_"):
                logger.info("Routing to project event processor", event_type=event_type)
                await self._process_project_event(data)
            else:
                logger.warning("Unknown event type received", event_type=event_type, topic=topic)
                
        except Exception as e:
            logger.error("Error processing message", error=str(e), message_data=data, exc_info=True)

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
            task_event = TaskEvent(
                event=data.get("event"),
                task_id=data.get("task_id"),
                project_id=data.get("project_id"),
                user_id=str(data.get("user_id")),
                username=data.get("username"),
                title=data.get("title"),
                name=data.get("name"),
                status=data.get("status"),
                timestamp=datetime.fromisoformat(data.get("timestamp").replace("Z", "+00:00"))
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
            project_event = ProjectEvent(
                event=data.get("event"),
                project_id=data.get("project_id"),
                user_id=str(data.get("user_id")),
                username=data.get("username"),
                name=data.get("name"),
                timestamp=datetime.fromisoformat(data.get("timestamp").replace("Z", "+00:00"))
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