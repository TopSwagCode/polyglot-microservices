from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
import structlog

logger = structlog.get_logger()

class MongoDB:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None

mongodb = MongoDB()


async def connect_to_mongo():
    """Create database connection"""
    try:
        mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb.database = mongodb.client[settings.DATABASE_NAME]
        
        # Test the connection
        await mongodb.client.admin.command('ping')
        logger.info("Connected to MongoDB", database=settings.DATABASE_NAME)
        
        # Create indexes for better performance
        await create_indexes()
        
    except Exception as e:
        logger.error("Failed to connect to MongoDB", error=str(e))
        raise


async def close_mongo_connection():
    """Close database connection"""
    if mongodb.client:
        mongodb.client.close()
        logger.info("Disconnected from MongoDB")


async def create_indexes():
    """Create database indexes for better query performance"""
    try:
        # Task events indexes
        await mongodb.database.task_events.create_index([("user_id", 1), ("created_at", -1)])
        await mongodb.database.task_events.create_index([("project_id", 1), ("created_at", -1)])
        await mongodb.database.task_events.create_index([("task_id", 1)])
        await mongodb.database.task_events.create_index([("event_type", 1)])
        
        # Project events indexes
        await mongodb.database.project_events.create_index([("user_id", 1), ("created_at", -1)])
        await mongodb.database.project_events.create_index([("project_id", 1)])
        await mongodb.database.project_events.create_index([("event_type", 1)])
        
        # User metrics indexes
        await mongodb.database.user_metrics.create_index([("user_id", 1)], unique=True)
        await mongodb.database.user_metrics.create_index([("last_activity", -1)])
        
        # Project metrics indexes
        await mongodb.database.project_metrics.create_index([("project_id", 1), ("user_id", 1)], unique=True)
        await mongodb.database.project_metrics.create_index([("user_id", 1), ("last_activity", -1)])
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error("Failed to create database indexes", error=str(e))


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return mongodb.database