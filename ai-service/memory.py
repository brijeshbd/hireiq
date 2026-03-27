import redis
import json
import os

# Connect to Redis
# Java equivalent: RedisTemplate<String, String>
r = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True  # Return strings not bytes
)

# How long to keep conversation — 24 hours
MEMORY_TTL = 60 * 60 * 24  # seconds


def get_history(session_id: str) -> list:
    """
    Get conversation history for a session.
    Java equivalent: redisTemplate.opsForValue().get(sessionId)
    """
    data = r.get(f"hireiq:session:{session_id}")
    if data:
        return json.loads(data)
    return []  # New session — empty history


def save_history(session_id: str, history: list):
    """
    Save conversation history to Redis.
    Java equivalent: redisTemplate.opsForValue().set(key, value, ttl)
    """
    r.setex(
        f"hireiq:session:{session_id}",  # Key
        MEMORY_TTL,                       # TTL — expires in 24hrs
        json.dumps(history)               # Value — serialized list
    )


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
    r.delete(f"hireiq:session:{session_id}")