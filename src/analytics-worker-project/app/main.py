import asyncio
import signal
import sys
import structlog
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.kafka_consumer import KafkaProjectEventConsumer

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class ProjectAnalyticsWorker:
    def __init__(self):
        self.consumer = KafkaProjectEventConsumer()
        self.running = False

    async def start(self):
        logger.info("START PROJECT WORKER", worker=settings.WORKER_NAME)
        print(f"=== STARTING {settings.WORKER_NAME} v{settings.VERSION} ===")
        await connect_to_mongo()
        self.running = True
        try:
            await self.consumer.start_consumer()
        finally:
            await close_mongo_connection()

    async def stop(self):
        self.running = False
        await self.consumer.stop_consumer()
        await close_mongo_connection()

    def handle_shutdown(self, signum, frame):
        logger.info("Shutdown signal", signal=signum)
        asyncio.create_task(self.stop())


async def main():
    worker = ProjectAnalyticsWorker()
    signal.signal(signal.SIGINT, worker.handle_shutdown)
    signal.signal(signal.SIGTERM, worker.handle_shutdown)
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt")
    except Exception as e:
        logger.error("Worker fatal error", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())