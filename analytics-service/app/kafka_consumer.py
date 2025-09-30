import json
import asyncio
from typing import Dict, Any
from datetime import datetime, timezone
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import structlog
from app.config import settings
from app.database import get_database
from app.models import TaskEvent, ProjectEvent
from app.services.analytics_service import AnalyticsService

logger = structlog.get_logger()


class KafkaEventConsumer:
    def __init__(self):
        self.consumer = None
        self.analytics_service = AnalyticsService()
        self.running = False

    async def start_consumer(self):
        """Start consuming events from Kafka"""
        try:
            logger.info("Initializing Kafka consumer", 
                       bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                       topics=[settings.KAFKA_TOPIC_TASK, settings.KAFKA_TOPIC_PROJECT])
            
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
        self.running = False
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer stopped")

    async def _consume_messages(self):
        """Main message consumption loop"""
        logger.info("Starting Kafka message consumption loop")
        
        while self.running:
            try:
                # Poll for messages with timeout
                message_batch = self.consumer.poll(timeout_ms=1000)
                
                if message_batch:
                    logger.debug("Received message batch", count=len(message_batch))
                    for topic_partition, messages in message_batch.items():
                        for message in messages:
                            await self._process_message(message)
                else:
                    # No messages received, log periodically
                    logger.debug("No messages received, continuing to poll")
                            
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
            
            logger.debug("Processing message", topic=topic, event=event_type, data=data)
            
            # Route based on event type rather than topic since both events come to task-events topic
            if event_type.startswith("task_"):
                await self._process_task_event(data)
            elif event_type.startswith("project_"):
                await self._process_project_event(data)
            else:
                logger.warning("Unknown event type", event=event_type, topic=topic)
                
        except Exception as e:
            logger.error("Error processing message", error=str(e), data=data)

    async def _process_task_event(self, data: Dict[str, Any]):
        """Process task event and store analytics data"""
        try:
            # Create task event document with the correct field mapping
            task_event = TaskEvent(
                event=data.get("event"),  # Changed from event_type to event
                task_id=data.get("task_id"),
                project_id=data.get("project_id"),
                user_id=str(data.get("user_id")),  # Ensure string type
                username=data.get("username"),
                title=data.get("title"),
                name=data.get("name"),
                status=data.get("status"),
                timestamp=datetime.fromisoformat(data.get("timestamp").replace("Z", "+00:00"))
            )
            
            # Store event in database
            db = get_database()
            await db.task_events.insert_one(task_event.model_dump())
            
            # Update analytics metrics
            await self.analytics_service.update_task_metrics(task_event)
            
            logger.info("Task event processed", 
                       event=task_event.event,
                       task_id=task_event.task_id,
                       user_id=task_event.user_id)
            
        except Exception as e:
            logger.error("Error processing task event", error=str(e), data=data)

    async def _process_project_event(self, data: Dict[str, Any]):
        """Process project event and store analytics data"""
        try:
            # Create project event document
            project_event = ProjectEvent(
                event=data.get("event"),
                project_id=data.get("project_id"),
                user_id=str(data.get("user_id")),
                username=data.get("username"),
                name=data.get("name"),
                timestamp=datetime.fromisoformat(data.get("timestamp").replace("Z", "+00:00"))
            )
            
            # Store event in database
            db = get_database()
            await db.project_events.insert_one(project_event.model_dump())
            
            # Update analytics metrics
            await self.analytics_service.update_project_metrics(project_event)
            
            logger.info("Project event processed",
                       event=project_event.event,
                       project_id=project_event.project_id,
                       user_id=project_event.user_id)
            
        except Exception as e:
            logger.error("Error processing project event", error=str(e), data=data)


# Global consumer instance
kafka_consumer = KafkaEventConsumer()