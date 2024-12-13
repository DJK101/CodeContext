import logging
import time
from types import TracebackType
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lib.constants import DB_URI
from lib.models import Base

engine = create_engine(DB_URI)
Base.metadata.create_all(engine)
Session = sessionmaker(engine)


class TimedSession:

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.logger: logging.Logger = logging.getLogger(__name__)

    def __enter__(self):
        self.start_time = time.perf_counter_ns()
        self.session = Session()
        self.session.begin()
        self.logger.debug("Session '%s' started", self.name)
        return self.session

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        # Stop the counter and calculate elapsed time
        self.end_time = time.perf_counter_ns()
        self.elapsed = self.end_time - self.start_time

        if exc_type is None:
            self.session.commit()
        else:
            self.session.rollback()
            self.logger.debug("Session '%s' rolled back due to an exception", self.name)

        self.session.close()
        self.logger.info(f"Session '{self.name}' completed in {self.elapsed} nano seconds")
