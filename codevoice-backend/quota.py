import os
import time
import logging

try:
    import importlib
    _redis_mod = importlib.import_module('redis')
    aioredis = getattr(_redis_mod, 'asyncio', None)
except Exception:
    aioredis = None

logger = logging.getLogger(__name__)

# Simple quota configuration
DEFAULT_QUOTA = int(os.getenv('USER_QUOTA_DEFAULT', '100'))
_redis_url = os.getenv('REDIS_URL') or os.getenv('REDIS_URI')
_redis_client = None
if aioredis and _redis_url:
    try:
        _redis_client = aioredis.from_url(_redis_url)
    except Exception:
        _redis_client = None

# In-memory fallback (non-persistent)
_local_quota = {}

async def check_and_debit_user_quota(user_id: str, cost: int = 1) -> bool:
    """Check quota for user and decrement by cost if available.

    Returns True if allowed and quota was decremented, False otherwise.
    """
    if not user_id:
        return True

    # Redis-backed quota (atomic)
    if _redis_client is not None:
        try:
            key = f"quota:{user_id}"
            # Initialize if not exists
            exists = await _redis_client.exists(key)
            if not exists:
                await _redis_client.set(key, DEFAULT_QUOTA)
            # Use Lua script to atomically check and decrement when >= cost
            script = """
            local val = tonumber(redis.call('GET', KEYS[1]) or '-1')
            if val < tonumber(ARGV[1]) then
                return -1
            end
            redis.call('DECRBY', KEYS[1], ARGV[1])
            return val - tonumber(ARGV[1])
            """
            res = await _redis_client.eval(script, 1, key, cost)
            return int(res) >= 0
        except Exception as e:
            logger.warning(f"Redis quota check failed: {e}")

    # In-memory fallback
    try:
        entry = _local_quota.get(user_id)
        if entry is None:
            _local_quota[user_id] = DEFAULT_QUOTA - cost
            return True
        if entry < cost:
            return False
        _local_quota[user_id] = entry - cost
        return True
    except Exception:
        return True

def get_remaining_quota(user_id: str) -> int:
    if not user_id:
        return DEFAULT_QUOTA
    if _redis_client is not None:
        try:
            key = f"quota:{user_id}"
            val = _redis_client.get(key)
            return int(val) if val is not None else DEFAULT_QUOTA
        except Exception:
            pass
    return _local_quota.get(user_id, DEFAULT_QUOTA)
