from typing import AsyncGenerator
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.services.redis_queue import RedisJobQueue

# Database
engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# Redis
async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    client = redis.from_url(settings.REDIS_URL)
    try:
        yield client
    finally:
        await client.close()

async def get_job_queue(redis_client: redis.Redis = None) -> RedisJobQueue:
    if redis_client is None:
        # If called directly without dependency injection handling redis lifecycle
        client = redis.from_url(settings.REDIS_URL)
        return RedisJobQueue(client)
    return RedisJobQueue(redis_client)
