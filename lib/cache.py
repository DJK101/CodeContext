from dataclasses import dataclass
from typing import Any, Callable, Generic, Optional, TypeVar, Iterable
from logging import getLogger
from sys import getsizeof

logger = getLogger(__name__)

T = TypeVar("T")

def get_recursive_size(obj: Any) -> int:
    """
    Recursively calculate the size of an object, including nested objects like lists, dicts, etc.
    """
    size = getsizeof(obj)

    # If the object is iterable (like a list or a dictionary), calculate the size of its elements
    if isinstance(obj, Iterable) and not isinstance(obj, str):
        size += sum(get_recursive_size(item) for item in obj)
    
    # If the object is a dictionary, calculate the size of the keys and values
    if isinstance(obj, dict):
        size += sum(get_recursive_size(key) + get_recursive_size(value) for key, value in obj.items())

    return size
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

        if cache_obj.data:
            logger.debug("Cache data found for key '%s'", key)
            return cache_obj.data
        
        new_data = cache_obj.getter()
        self.objects[key] = CacheObject(new_data, cache_obj.getter, cache_obj.args)
        return new_data

    def expire_data(self, key: str) -> None:
        self.objects.pop(key, None)

    def exists(self, key: str) -> bool:
        return key in self.objects
    
    def get_total_size(self) -> int:
        return get_recursive_size(self.objects)


Cache = CacheClass()
