import json
import os

import aioredis


class RedisMessage:

    def __init__(self):
        self.redis_connect = aioredis.from_url(
            os.getenv("REDIS_URI", "redis://localhost:6379"))

    async def get_message(self, user_id: int, battle_id: int):
        _, msg = await self.redis_connect.blpop(
            f"battle:{user_id}:{battle_id}")
        return json.loads(msg)

    async def remove_queue(self, user_id: int, battle_id: int):
        return await self.redis_connect.delete(f"battle:{user_id}:{battle_id}")

    async def put_message(self, user_id: int, battle_id: int, msg: dict):
        return await self.redis_connect.rpush(f"battle:{user_id}:{battle_id}",
                                              json.dumps(msg))

