import time
import logging
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

from app.config import get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self):
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._redis = None
        self._redis_retry_after = 0.0

    def _redis_client(self):
        settings = get_settings()
        if not settings.redis_url or time.monotonic() < self._redis_retry_after:
            return None
        if self._redis is None:
            from redis import Redis

            self._redis = Redis.from_url(
                settings.redis_url,
                socket_connect_timeout=1,
                socket_timeout=1,
                decode_responses=True,
            )
        return self._redis

    def _client_ip(self, request: Request) -> str:
        settings = get_settings()
        if settings.trust_proxy_headers:
            forwarded_for = request.headers.get("x-forwarded-for")
            if forwarded_for:
                return forwarded_for.split(",", 1)[0].strip()
        return request.client.host if request.client else "unknown"

    def _limit_for_path(self, path: str) -> int:
        settings = get_settings()
        if path in {"/auth/login", "/auth/refresh"}:
            return settings.auth_rate_limit_requests
        return settings.rate_limit_requests

    def check(self, request: Request):
        settings = get_settings()
        if not settings.rate_limit_enabled:
            return

        try:
            redis = self._redis_client()
        except Exception:
            logger.exception("Redis no disponible para rate limiting; usando memoria local")
            self._redis = None
            self._redis_retry_after = time.monotonic() + 30
            redis = None
        if redis:
            try:
                self._check_redis(request, redis)
                return
            except Exception:
                logger.exception("Redis no disponible para rate limiting; usando memoria local")
                self._redis = None
                self._redis_retry_after = time.monotonic() + 30

        now = time.monotonic()
        window = settings.rate_limit_window_seconds
        key = f"{self._client_ip(request)}:{request.url.path}"
        bucket = self._requests[key]
        while bucket and now - bucket[0] > window:
            bucket.popleft()

        if len(bucket) >= self._limit_for_path(request.url.path):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiadas solicitudes. Intenta nuevamente en unos minutos.",
            )

        bucket.append(now)

    def _check_redis(self, request: Request, redis):
        settings = get_settings()
        window = settings.rate_limit_window_seconds
        key = f"hcd:rate:{self._client_ip(request)}:{request.url.path}"
        count = redis.incr(key)
        if count == 1:
            redis.expire(key, window)
        if count > self._limit_for_path(request.url.path):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiadas solicitudes. Intenta nuevamente en unos minutos.",
            )
