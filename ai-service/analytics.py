import redis
import json
import os
from datetime import datetime, date

# Connect to Redis for analytics storage (with fallback for missing Redis)
try:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    r = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=2)
    r.ping()
    REDIS_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Analytics: Redis connection failed: {e}")
    print("Analytics tracking disabled - will not store metrics")
    REDIS_AVAILABLE = False
    r = None


def track_request(feature: str, success: bool, latency_ms: float):
    """
    Track every API request.
    Stores daily counts per feature in Redis.

    Java equivalent:
    metricsService.track(feature, success, latencyMs);
    """
    if not REDIS_AVAILABLE:
        return  # Silently skip if Redis not available
    
    try:
        today = date.today().isoformat()  # e.g. "2026-03-27"

        # Increment total requests for this feature today
        r.hincrby(f"hireiq:stats:{today}", f"{feature}:requests", 1)

        # Increment success/failure count
        status = "success" if success else "error"
        r.hincrby(f"hireiq:stats:{today}", f"{feature}:{status}", 1)

        # Track total latency for average calculation
        r.hincrbyfloat(f"hireiq:stats:{today}", f"{feature}:latency_total", latency_ms)
        
        # Set expiry — keep stats for 30 days
        r.expire(f"hireiq:stats:{today}", 60 * 60 * 24 * 30)
    except Exception as e:
        # Log but don't crash if tracking fails
        print(f"Analytics tracking failed: {e}")
        pass


def get_daily_stats(target_date: str = None) -> dict:
    """
    Get usage statistics for a specific day.
    Default: today
    """
    if not REDIS_AVAILABLE:
        return {"error": "Analytics not available - Redis not connected"}
    
    try:
        if not target_date:
            target_date = date.today().isoformat()

        raw = r.hgetall(f"hireiq:stats:{target_date}")

        if not raw:
            return {"date": target_date, "message": "No data for this date"}

        # Parse into structured format
        features = {}
        for key, value in raw.items():
            parts = key.split(":")
            if len(parts) == 2:
                feature, metric = parts
                if feature not in features:
                    features[feature] = {}
                features[feature][metric] = float(value)

        # Calculate averages
        for feature, metrics in features.items():
            if "latency_total" in metrics and "requests" in metrics:
                total   = metrics.get("latency_total", 0)
                count   = metrics.get("requests", 1)
                metrics["avg_latency_ms"] = round(total / count, 1)
    except Exception as e:
        print(f"Failed to get daily stats: {e}")
        return {"error": "Failed to retrieve analytics"}

    return {
        "date":     target_date,
        "features": features
    }


def get_total_requests_today() -> int:
    """Get total requests across all features today"""
    if not REDIS_AVAILABLE:
        return 0
    
    try:
        today = date.today().isoformat()
        raw   = r.hgetall(f"hireiq:stats:{today}")
        total = sum(
            int(v) for k, v in raw.items()
            if k.endswith(":requests")
        )
        return total
    except Exception as e:
        print(f"Failed to get total requests: {e}")
        return 0