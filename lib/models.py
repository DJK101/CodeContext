import logging
from datetime import datetime
from typing import Any, List

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    validates,
)


class Base(DeclarativeBase):
    pass


class Log(Base):
    __tablename__ = "log"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(64))
    created_time: Mapped[datetime] = mapped_column(DateTime)
    message: Mapped[str] = mapped_column(String(256))
    level: Mapped[int] = mapped_column(Integer)

    @validates("level")
    def validate_level(self, key: str, level: Any):
        if not isinstance(level, int):
            raise ValueError("Level must be an integer.")
        return level

    def level_name(self) -> str:
        return logging.getLevelName(self.level)

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
    cores: Mapped[int] = mapped_column(Integer)
    ram_total: Mapped[int] = mapped_column(Integer)
    disk_total: Mapped[int] = mapped_column(Integer)
    metrics: Mapped[List["DeviceMetric"]] = relationship(
        cascade="all, delete-orphan"
    )


class DeviceMetric(Base):
    __tablename__ = "device_metric"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id"))
    recorded_time: Mapped[datetime] = mapped_column(DateTime)
    ram_usage: Mapped[int] = mapped_column(Integer)
    disk_usage: Mapped[int] = mapped_column(Integer)

    def as_dict(self) -> dict[str, str | int]:
        return {
            "id": self.id,
            "device_id": self.device_id,
            "recorded_time": self.recorded_time.isoformat(),
            "ram_usage": self.ram_usage,
            "disk_usage": self.disk_usage,
        }