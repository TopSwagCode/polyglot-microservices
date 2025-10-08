from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from app.config import settings

_client: Optional[AsyncIOMotorClient] = None


async def connect_to_mongo():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGODB_URL)


async def close_mongo_connection():
    global _client
    if _client is not None:
        _client.close()
        _client = None


def get_database():
    if _client is None:
        raise RuntimeError("Mongo client not initialized. Call connect_to_mongo() first.")
    return _client[settings.DATABASE_NAME]