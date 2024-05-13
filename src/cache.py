import os
from dotenv import load_dotenv
import redis.asyncio as aioredis
import asyncio

load_dotenv('.env')


class RedisConnector:
    pool = aioredis.ConnectionPool.from_url(
        os.environ.get("REDIS_CONN_STRING")
    )
    redis_connection = None
    lock = asyncio.Lock()

    @classmethod
    async def connect(cls):
        async with cls.lock:
            cls.redis_connection = aioredis.Redis.from_pool(cls.pool)

    @classmethod
    async def disconnect(cls):
        async with cls.lock:
            if not cls.redis_connection:
                return
            await cls.redis_connection.close()

    async def __aenter__(self):
        async with self.lock:
            return self.redis_connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
