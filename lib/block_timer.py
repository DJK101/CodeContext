import logging
import time
from types import TracebackType
from functools import wraps


class BlockTimer:
    """A reusable class that times a code block using RAII pattern."""

    def __init__(self, name: str = "BlockTimer"):
        self.name = name
        self.logger = logging.getLogger(__name__)

    def __enter__(self):
        # Start the performance counter at the beginning of the block
        self.start_time = time.perf_counter_ns()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        # Stop the counter and calculate elapsed time
        self.end_time = time.perf_counter_ns()
        self.elapsed = self.end_time - self.start_time
        self.logger.debug(
            f"{self.name} elapsed time: {self.elapsed:,}ns/{self.elapsed//1_000_000:,}ms"
        )


def timed_function(name: str = "TimedFunction"):
    """A decorator to time the execution of a function."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with BlockTimer(name):
                return func(*args, **kwargs)

        return wrapper

    return decorator
