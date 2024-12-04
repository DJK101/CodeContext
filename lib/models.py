from datetime import datetime
from logging import getLevelName

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Log(Base):
    __tablename__ = "log"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    source: Mapped[str] = mapped_column(String(64))
    created_time: Mapped[datetime] = mapped_column(DateTime)
    message: Mapped[str] = mapped_column(String(256))
    level: Mapped[int] = mapped_column(Integer)

    def level_name(self) -> str:
        return getLevelName(self.level)

    def as_dict(self) -> dict[str, str | int]:
        return {
            "id": self.id,
            "source": self.source,
            "created_time": self.created_time.isoformat(),
            "message": self.message,
            "level": self.level,
            "level_name": self.level_name(),
        }


class Device(Base):
    __tablename__ = "device"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
