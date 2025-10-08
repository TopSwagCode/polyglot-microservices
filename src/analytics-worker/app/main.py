import asyncio
import signal
import sys
import structlog
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.kafka_consumer import KafkaEventConsumer

# Configure structured logging
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
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class AnalyticsWorker:
    def __init__(self):
        self.kafka_consumer = KafkaEventConsumer()
        self.running = False

    async def start(self):
        """Start the analytics worker"""
        logger.info("=== STARTING ANALYTICS WORKER ===")
        print(f"=== STARTING {settings.WORKER_NAME} v{settings.VERSION} ===")
        
        try:
            # Connect to MongoDB
            logger.info("Connecting to MongoDB")
            print("Connecting to MongoDB...")
            await connect_to_mongo()
            
            # Start Kafka consumer
            logger.info("Starting Kafka consumer")
            print("Starting Kafka consumer...")
            self.running = True
            
            # Start consumer in background task
            consumer_task = asyncio.create_task(self.kafka_consumer.start_consumer())
            
            # Wait for shutdown signal
            logger.info("Analytics worker started successfully")
            print("Analytics worker is running. Press Ctrl+C to stop.")
            
            # Keep the worker running
            await consumer_task
            
        except Exception as e:
            logger.error("Failed to start analytics worker", error=str(e))
            print(f"ERROR: Failed to start worker: {e}")
            raise

    async def stop(self):
        """Stop the analytics worker"""
        logger.info("Stopping analytics worker")
        print("Stopping analytics worker...")
        
        self.running = False
        await self.kafka_consumer.stop_consumer()
        await close_mongo_connection()
        
        logger.info("Analytics worker stopped")
        print("Analytics worker stopped")

    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Received shutdown signal", signal=signum)
        print(f"Received shutdown signal: {signum}")
        asyncio.create_task(self.stop())


async def main():
    """Main entry point"""
    worker = AnalyticsWorker()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, worker.handle_shutdown)
    signal.signal(signal.SIGTERM, worker.handle_shutdown)
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        print("Received keyboard interrupt")
    except Exception as e:
        logger.error("Worker error", error=str(e))
        print(f"Worker error: {e}")
        sys.exit(1)
    finally:
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())