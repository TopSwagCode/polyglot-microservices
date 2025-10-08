import json
import asyncio
from datetime import datetime
from typing import Any, Dict
import structlog
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from app.config import settings
from app.analytics_service import AnalyticsService
from app.models import TaskEvent
from app.database import get_database

logger = structlog.get_logger()


class KafkaTaskEventConsumer:
    def __init__(self):
        self.consumer = None
        self.analytics_service = AnalyticsService()
        self.running = False

    async def start_consumer(self):
        logger.info("TASK CONSUMER STARTING", topic=settings.KAFKA_TOPIC_TASK)
        try:
            self.consumer = KafkaConsumer(
                settings.KAFKA_TOPIC_TASK,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=settings.KAFKA_GROUP_ID,
                value_deserializer=lambda x: json.loads(x.decode("utf-8")),
                auto_offset_reset="latest",
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                consumer_timeout_ms=1000,
            )
            self.running = True
            await self._consume()
        except KafkaError as e:
            logger.error("Kafka error", error=str(e))
            raise

    async def stop_consumer(self):
        self.running = False
        if self.consumer:
            self.consumer.close()

    async def _consume(self):
        message_count = 0
        while self.running:
            try:
                batch = self.consumer.poll(timeout_ms=1000)
                if batch:
                    for _, messages in batch.items():
                        for m in messages:
                            await self._process(m)
                            message_count += 1
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error("Consume loop error", error=str(e), exc_info=True)
                await asyncio.sleep(5)

    async def _process(self, message):
        envelope = message.value
        if not isinstance(envelope, dict):
            logger.warning("Skip non-dict message", raw=envelope)
            return
        data = envelope.get("data")
        if not isinstance(data, dict):
            logger.warning("Missing data object", envelope=envelope)
            return
        event_raw = envelope.get("event", "")
        if not event_raw.startswith("task."):
            logger.warning("Unexpected event type on task worker", event=event_raw)
            return
        # Normalize to underscore for internal metrics logic
        event_internal = event_raw.replace(".", "_")
        ts_raw = envelope.get("timestamp")
        timestamp = None
        if isinstance(ts_raw, str):
            try:
                timestamp = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
            except ValueError:
                logger.warning("Timestamp parse failed", raw=ts_raw)
        task_event = TaskEvent(
            event=event_internal,
            task_id=data.get("ID"),
            project_id=data.get("ProjectID"),
            user_id=str(data.get("UserID")),
            username=data.get("Username"),
            title=data.get("Title"),
            status=data.get("Status"),
            timestamp=timestamp or datetime.utcnow(),
        )
        # Persist raw event (task_events collection)
        db = get_database()
        await db.task_events.insert_one(task_event.model_dump())
        await self.analytics_service.update_task_metrics(task_event)
        logger.info("Task event processed", event_type=event_internal, task_id=task_event.task_id)