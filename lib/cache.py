from dataclasses import dataclass
from logging import getLogger
from typing import Any, Callable, Generic, Optional, TypeVar
from datetime import datetime, timedelta
import time

import threading
from lib.block_timer import timed_function
from lib.config import CacheConfig

logger = getLogger(__name__)

T = TypeVar("T")


@dataclass
class CacheObject(Generic[T]):
    data: Optional[T]
    getter: Callable[..., T]
    args: list
    expiry_time: datetime


class Cache:

    def __init__(self, config: CacheConfig) -> None:
        self.config = config
        self.objects: dict[str, CacheObject[Any]] = {}
        self.lock = threading.RLock()
        self.expiration_thread = threading.Thread(
            target=self._expiration_worker, daemon=True
        )
        self.expiration_thread.start()

    def cache_data(
        self, key: str, func: Callable[..., T], args: list = [], ttl: int = 30
    ) -> T:
        if not self.config.enabled:
            logger.debug("Caching disabled, retrieving data")
            return func(*args)

        if not self.in_cache(key):
            logger.debug("Cache data NOT found for key '%s'", key)
            initial_value = func(*args)
            expiry_time = datetime.now() + timedelta(seconds=ttl)
            with self.lock:
                self.objects[key] = CacheObject(initial_value, func, args, expiry_time)
            return initial_value

        return self.get_data(key)

    @timed_function("Cache Execution")
    def get_data(self, key: str) -> Any:
        """
        Retrieve the data associated with the given key from the cache.

        If the data has expired, it will refresh the cache with the
        corresponding `CacheObject` getter function.
        """
        with self.lock:
            cache_obj: CacheObject[Any] = self.objects[key]

            if cache_obj.data:
                logger.debug("Cache data found for key '%s'", key)
                return cache_obj.data

            return self.update_cache(key)

    def update_cache(self, key: str, ttl: int = 30) -> Any:
        """
        Refresh the cache for the given key by calling the `getter` function.
        """
        with self.lock:
            cache_obj: CacheObject[Any] = self.objects[key]
            new_data = cache_obj.getter(*cache_obj.args)
            expiry_time = datetime.now() + timedelta(seconds=ttl)
            self.objects[key] = CacheObject(
                new_data, cache_obj.getter, cache_obj.args, expiry_time
            )
            return new_data

    def expire_data(self, key: str) -> None:
        """
        Remove the cached object associated with the given key.
        """
        with self.lock:
            self.objects.pop(key, None)
            logger.debug("Cache key '%s' expired", key)

    def in_cache(self, key: str) -> bool:
        """
        Check if the key exists in the cache and has not expired.
        """
        with self.lock:
            if key not in self.objects:
                return False

            cache_obj = self.objects[key]
            if datetime.now() >= cache_obj.expiry_time:
                self.expire_data(key)
                return False

            return True

    def _expiration_worker(self) -> None:
        """
        A background thread that periodically checks and removes expired cache objects.
        """
        while True:
            time.sleep(self.config.clear_period)
            with self.lock:
                logger.debug("Scanning for expired cache keys, %s key(s) to check", len(self.objects))
                expired_keys = [
                    key
                    for key, obj in self.objects.items()
                    if datetime.now() >= obj.expiry_time
                ]
                for key in expired_keys:
                    logger.debug("Removing expired cache for key '%s'", key)
                    self.expire_data(key)
