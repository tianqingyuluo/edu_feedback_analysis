# app/utils/model_cache.py

import functools
import pickle
import redis
from app.core.config import settings

# 创建全局Redis客户端
redis_client = redis.from_url(settings.redis_url)

def cached_model_load(expire_time: int = 1800):
    """
    模型加载缓存装饰器

    Args:
        expire_time: 缓存过期时间（秒），默认30分钟
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(model_name: str, task_id: str, version: int = None):
            # 生成缓存键
            cache_key = f"model_cache:{model_name}:{task_id}:{'latest' if version is None else f'v{version}'}"

            # 尝试从缓存获取模型
            try:
                cached_model = redis_client.get(cache_key)
                if cached_model:
                    # 刷新过期时间
                    redis_client.expire(cache_key, expire_time)
                    return pickle.loads(cached_model)
            except Exception:
                pass  # 缓存读取失败，继续执行函数

            # 执行原函数加载模型
            model = await func(model_name, task_id, version)

            # 将模型存入缓存
            try:
                redis_client.setex(cache_key, expire_time, pickle.dumps(model))
            except Exception:
                pass  # 缓存存储失败不影响主流程

            return model
        return wrapper
    return decorator
