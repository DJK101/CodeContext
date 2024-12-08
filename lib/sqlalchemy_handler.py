import logging
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lib.ansi_color_stripper import ANSIColorStripperFilter
from lib.models import Base, Log


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
                level=record.levelno,
            )
            session.add(log)
