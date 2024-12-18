import logging
from types import TracebackType

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lib.block_timer import BlockTimer
from lib.constants import DB_URI
from lib.models import Base

engine = create_engine(DB_URI)
Base.metadata.create_all(engine)
Session = sessionmaker(engine)


class TimedSession:

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.block_timer = BlockTimer(f"DB session '{name}'")
        self.logger: logging.Logger = logging.getLogger(__name__)

    def __enter__(self):
        self.block_timer.__enter__()
        self.session = Session()
        self.session.begin()
        return self.session

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        if exc_type is None:
            self.session.commit()
        else:
            self.session.rollback()
            self.logger.debug(
                "DB session '%s' rolled back due to an exception", self.name
            )

        self.session.close()
        self.block_timer.__exit__(exc_type, exc_val, exc_tb)
