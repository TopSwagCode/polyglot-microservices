import json
import asyncio
from datetime import datetime
import structlog
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from app.config import settings
from app.analytics_service import AnalyticsService
from app.models import ProjectEvent
from app.database import get_database

logger = structlog.get_logger()


class KafkaProjectEventConsumer:
    def __init__(self):
        self.consumer = None
        self.analytics_service = AnalyticsService()
        self.running = False

    async def start_consumer(self):
        logger.info("PROJECT CONSUMER STARTING", topic=settings.KAFKA_TOPIC_PROJECT)
        try:
            self.consumer = KafkaConsumer(
                settings.KAFKA_TOPIC_PROJECT,
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
        while self.running:
            try:
                batch = self.consumer.poll(timeout_ms=1000)
                if batch:
                    for _, messages in batch.items():
                        for m in messages:
                            await self._process(m)
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
        if not event_raw.startswith("project."):
            logger.warning("Unexpected event type on project worker", event=event_raw)
            return
        event_internal = event_raw.replace(".", "_")
        ts_raw = envelope.get("timestamp")
        timestamp = None
        if isinstance(ts_raw, str):
            try:
                timestamp = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
            except ValueError:
                logger.warning("Timestamp parse failed", raw=ts_raw)
        project_event = ProjectEvent(
            event=event_internal,
            project_id=data.get("ID"),
            user_id=str(data.get("UserID")),
            username=data.get("Username"),
            name=data.get("Name"),
            timestamp=timestamp or datetime.utcnow(),
        )
        db = get_database()
        await db.project_events.insert_one(project_event.model_dump())
        await self.analytics_service.update_project_metrics(project_event)
        logger.info("Project event processed", event_type=event_internal, project_id=project_event.project_id)