from dataclasses import dataclass
from logging import getLogger
from typing import Any, Callable, Generic, Optional, TypeVar

from lib.config import Config

logger = getLogger(__name__)

T = TypeVar("T")

config = Config()


@dataclass
class CacheObject(Generic[T]):
    data: Optional[T]
    getter: Callable[..., T]
    args: list


class Cache:

    def __init__(self) -> None:
        self.objects: dict[str, CacheObject[Any]] = {}

    def cache_data(self, key: str, func: Callable[..., T], args: list = []) -> T:
        if not config.server_c.caching:
            logger.debug("Caching disabled, retrieving data")
            return func(*args)

        if not self.in_cache(key):
            logger.debug("No cache with key '%s'", key)
            initial_value = func(*args)
            self.objects[key] = CacheObject(initial_value, func, args)

        return self.get_data(key)

    def get_data(self, key: str) -> Any:
        """
        Retrieve the data associated with the given key from the cache.

        If the data has expired, it will refresh the cache with the
        corresponding `CacheObject` getter function.
        """
        cache_obj: CacheObject[Any] = self.objects[key]

        if cache_obj.data:
            logger.debug("Cache data found for key '%s'", key)
            return cache_obj.data

        return self.update_cache(key)

    def update_cache(self, key: str) -> Any:
        cache_obj: CacheObject[Any] = self.objects[key]
        new_data = cache_obj.getter(*cache_obj.args)
        self.objects[key] = CacheObject(new_data, cache_obj.getter, cache_obj.args)
        return new_data

    def expire_data(self, key: str) -> None:
        self.objects.pop(key, None)

    def in_cache(self, key: str) -> bool:
        return key in self.objects
