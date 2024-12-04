import logging
from datetime import datetime
import re

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lib.models import Base, Log


class ANSIColorStripperFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter out ANSI escape sequences from log message.
        This method modifies the log record message in place.
        """
        ansi_escape = re.compile(r"(?:\x1B[@-Z\\-_]|\x1B\[[0-?]*[ -/]*[@-~])")
        record.message = ansi_escape.sub("", record.getMessage())
        print(record.message)
        return True


class SQLAlchemyHandler(logging.Handler):
    def __init__(self, db_uri: str) -> None:
        super().__init__()

        self.engine = create_engine(db_uri)
        self.Session = sessionmaker(self.engine)
        Base.metadata.create_all(self.engine)

        self.addFilter(ANSIColorStripperFilter())

    def emit(self, record: logging.LogRecord) -> None:
        with self.Session.begin() as session:
            log = Log(
                source=record.name,
                created_time=datetime.fromtimestamp(record.created),
                message=record.message,
                level=record.levelname,
            )
            session.add(log)
