from dataclasses import dataclass
from typing import Any, Callable, Generic, Optional, TypeVar
from logging import getLogger

logger = getLogger(__name__)

T = TypeVar("T")


@dataclass
class CacheObject(Generic[T]):
    data: Optional[T]
    getter: Callable[..., T]
    args: list


class CacheClass:

    def __init__(self) -> None:
        self.objects: dict[str, CacheObject[Any]] = {}

    def cache_data(self, key: str, func: Callable[..., T], args: list = []) -> T:
        if not self.exists(key):
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
        if cache_obj.data is not None:
            return cache_obj.data
        else:
            new_data = cache_obj.getter()
            self.objects[key] = CacheObject(new_data, cache_obj.getter, cache_obj.args)
            return new_data

    def expire_data(self, key: str) -> None:
        self.objects[key].data = None

    def exists(self, key: str) -> bool:
        return key in self.objects


Cache = CacheClass()
