from lib.models import Base, Log
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import datetime

class SQLAlchemyHandler(logging.Handler):
    def __init__(self, db_uri: str) -> None:
        super().__init__()

        self.engine = create_engine(db_uri)
        Base.metadata.create_all(self.engine)

    def emit(self, record: logging.LogRecord) -> None:
        print("logging time")
        with Session(self.engine) as session:
            log = Log(
                source=record.name,
                created_time=datetime.fromtimestamp(record.created),
                message=record.message,
                level=record.levelname,
            )
            print(record.__dict__)
            session.add(log)
            session.commit()