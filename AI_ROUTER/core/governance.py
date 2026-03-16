import redis.asyncio as redis
from config.settings import settings
import json
import hashlib
from loguru import logger
import time

class RedisManager:
    """管理 Redis 连接和核心治理逻辑（限流、缓存、熔断）。"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisManager, cls).__new__(cls)
            cls._instance.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )
        return cls._instance

    # --- 限流 (Rate Limiting) ---
    async def is_rate_limited(self, api_key_id: int, limit: int) -> bool:
        """基于令牌桶或滑动窗口的简单计数限流。"""
        key = f"rate_limit:{api_key_id}:{int(time.time())}"
        count = await self.client.incr(key)
        if count == 1:
            await self.client.expire(key, 1)
        return count > limit

    # --- 缓存 (Caching) ---
    def generate_cache_key(self, model: str, messages: list, kwargs: dict) -> str:
        """生成请求的 MD5 缓存键。"""
        payload = json.dumps({"model": model, "messages": messages, **kwargs}, sort_keys=True)
        return f"cache:{hashlib.md5(payload.encode()).hexdigest()}"

    async def get_cache(self, cache_key: str) -> str:
        if not settings.CACHE_ENABLED:
            return None
        return await self.client.get(cache_key)

    async def set_cache(self, cache_key: str, response_data: str, ttl: int = None):
        if not settings.CACHE_ENABLED:
            return
        await self.client.set(cache_key, response_data, ex=ttl or settings.CACHE_TTL)

    # --- 熔断 (Circuit Breaker) ---
    async def record_error(self, model_name: str):
        """记录模型调用错误。"""
        key = f"circuit_breaker:errors:{model_name}"
        count = await self.client.incr(key)
        if count == 1:
            await self.client.expire(key, 60) # 1分钟窗口
        
        if count >= 10: # 错误率阈值
            await self.client.set(f"circuit_breaker:status:{model_name}", "open", ex=300) # 熔断5分钟
            logger.warning(f"Circuit breaker OPEN for model: {model_name}")

    async def is_circuit_open(self, model_name: str) -> bool:
        status = await self.client.get(f"circuit_breaker:status:{model_name}")
        return status == "open"

redis_manager = RedisManager()
