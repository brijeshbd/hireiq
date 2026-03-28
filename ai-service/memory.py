import redis
import json
import os

# Connect to Redis
# Java equivalent: RedisTemplate<String, String>
try:
    # Support both direct connection and Railway URL format
    redis_url = os.getenv("REDIS_URL")
    
    if redis_url:
        # Railway provides REDIS_URL with format: redis://:password@host:port
        r = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=2)
    else:
        # Fallback to individual env vars
        r = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            password=os.getenv("REDIS_PASSWORD"),  # Add password support
            decode_responses=True,  # Return strings not bytes
            socket_connect_timeout=2,
            socket_keepalive=True
        )
    
    # Test connection
    r.ping()
    print("✅ Redis connection successful")
    REDIS_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Redis connection failed: {e}")
    print("Using in-memory fallback for conversation history")
    REDIS_AVAILABLE = False
    r = None

# How long to keep conversation — 24 hours
MEMORY_TTL = 60 * 60 * 24  # seconds

# In-memory fallback for when Redis is unavailable
_in_memory_store = {}


def get_history(session_id: str) -> list:
    """
    Get conversation history for a session.
    Java equivalent: redisTemplate.opsForValue().get(sessionId)
    """
    if REDIS_AVAILABLE:
        try:
            data = r.get(f"hireiq:session:{session_id}")
            if data:
                return json.loads(data)
            return []
        except Exception as e:
            print(f"Redis get failed: {e}, using in-memory fallback")
            return _in_memory_store.get(f"hireiq:session:{session_id}", [])
    else:
        # Use in-memory fallback
        return _in_memory_store.get(f"hireiq:session:{session_id}", [])


def save_history(session_id: str, history: list):
    """
    Save conversation history to Redis.
    Java equivalent: redisTemplate.opsForValue().set(key, ttl)
    """
    if REDIS_AVAILABLE:
        try:
            r.setex(
                f"hireiq:session:{session_id}",
                MEMORY_TTL,
                json.dumps(history)
            )
        except Exception as e:
            print(f"Redis save failed: {e}, using in-memory fallback")
            _in_memory_store[f"hireiq:session:{session_id}"] = history
    else:
        # Use in-memory fallback
        _in_memory_store[f"hireiq:session:{session_id}"] = history


def add_message(session_id: str, role: str, content: str):
    """
    Add a single message to conversation history.
    Automatically saves back to Redis.
    """
    history = get_history(session_id)

    history.append({
        "role": role,
        "content": content
    })

    save_history(session_id, history)
    return history


def clear_history(session_id: str):
    """Clear conversation for a session — like logout"""
    key = f"hireiq:session:{session_id}"
    if REDIS_AVAILABLE:
        try:
            r.delete(key)
        except Exception as e:
            print(f"Redis delete failed: {e}")
            if key in _in_memory_store:
                del _in_memory_store[key]
    else:
        # Use in-memory fallback
        if key in _in_memory_store:
            del _in_memory_store[key]