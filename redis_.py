import json

import aioredis


_async_redis = None


async def create_async_redis():
    pool = aioredis.ConnectionPool.from_url(
        "redis://localhost", decode_responses=True
    )
    return aioredis.Redis(connection_pool=pool)


async def async_redis():
    global _async_redis
    if _async_redis is None:
        _async_redis = await create_async_redis()

    return _async_redis


async def pop_async(queue):
    encoded_message = await (await async_redis()).rpop(queue)
    return json.loads(encoded_message) if encoded_message else None


async def push_async(queue: str, message: str):
    await (await async_redis()).lpush(queue, json.dumps(message))


async def dispose_async():
    global _async_redis
    if _async_redis and not _async_redis.closed and \
            _async_redis.connection._loop.is_running():
        _async_redis.close()
    _async_redis = None


async def flush_all_async():
    await (await async_redis()).flushdb()

