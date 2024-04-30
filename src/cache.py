import os
from dotenv import load_dotenv
import redis.asyncio as aioredis


load_dotenv('.env')


class RedisConnector:
    pool = aioredis.ConnectionPool.from_url(
        os.environ.get("REDIS_CONN_STRING")
    )

    def __init__(self):
        self.redis_connection = aioredis.Redis.from_pool(self.pool)

    async def __aenter__(self):
        return self.redis_connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.redis_connection.close()
