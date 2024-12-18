import logging
from datetime import datetime, timedelta
from typing import Any, List

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    validates,
)

from lib.datamodels import (
    DTO_Aggregator,
    DTO_DataSnapshot,
    DTO_Device,
    DTO_Metric,
    DTO_Properties,
)

logger = logging.getLogger(__name__)


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


class Aggregator(Base):
    __tablename__ = "aggregator"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    devices: Mapped[List["Device"]] = relationship(
        back_populates="aggregator", cascade="all, delete-orphan"
    )

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "devices": [device.as_dict() for device in self.devices],
        }

    def as_dto(self, include_devices=False) -> DTO_Aggregator:
        return DTO_Aggregator(
            name=self.name,
            devices=[device.as_dto() for device in self.devices if include_devices],
        )


class Device(Base):
    __tablename__ = "device"

    id: Mapped[int] = mapped_column(primary_key=True)
    aggregator_id: Mapped[int] = mapped_column(ForeignKey("aggregator.id"))
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    aggregator: Mapped["Aggregator"] = relationship(back_populates="devices")
    properties: Mapped[List["DeviceProperty"]] = relationship(
        back_populates="device", cascade="all, delete-orphan"
    )
    snapshots: Mapped[List["DeviceSnapshot"]] = relationship(
        back_populates="device", cascade="all, delete-orphan"
    )

    def as_dict(self) -> dict[str, Any]:
        return {
            "aggregator": self.aggregator.name,
            "name": self.name,
            "properties": [prop.as_dict() for prop in self.properties],
        }

    def as_dto(
        self, include_properties=False, include_data_snapshots=False
    ) -> DTO_Device:
        return DTO_Device(
            name=self.name,
            properties=[
                prop.as_dto() for prop in self.properties if include_properties
            ],
            data_snapshots=[
                snapshot.as_dto()
                for snapshot in self.snapshots
                if include_data_snapshots
            ],
        )


class DeviceProperty(Base):
    __tablename__ = "device_property"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id"))
    name: Mapped[str] = mapped_column(String(32), unique=True)
    value: Mapped[int] = mapped_column(Integer)

    device: Mapped["Device"] = relationship(back_populates="properties")

    def as_dict(self) -> dict[str, str | int]:
        return {
            "name": self.name,
            "value": self.value,
        }

    def as_dto(self) -> DTO_Properties:
        return DTO_Properties(name=self.name, value=self.value)


class DeviceSnapshot(Base):
    __tablename__ = "device_snapshot"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id"))
    timestamp_utc: Mapped[datetime] = mapped_column(DateTime)
    utc_offset_mins: Mapped[int] = mapped_column(Integer)

    device: Mapped["Device"] = relationship(back_populates="snapshots")
    metrics: Mapped[List["DeviceMetric"]] = relationship(
        back_populates="snapshot", cascade="all, delete-orphan"
    )

    def as_dict(self) -> dict[str, Any]:
        return {
            "timestamp_utc": self.timestamp_utc.isoformat(),
            "metrics": [metric.as_dict() for metric in self.metrics],
        }

    def as_dto(self, include_metrics=True) -> DTO_DataSnapshot:
        return DTO_DataSnapshot(
            timestamp_utc=self.timestamp_utc,
            utc_offset_mins=self.utc_offset_mins,
            metrics=[metric.as_dto() for metric in self.metrics if include_metrics],
        )

    def local_time(self) -> datetime:
        return self.timestamp_utc + timedelta(minutes=self.utc_offset_mins)


class DeviceMetric(Base):
    __tablename__ = "device_metric"

    id: Mapped[int] = mapped_column(primary_key=True)
    snapshot_id: Mapped[int] = mapped_column(ForeignKey("device_snapshot.id"))
    name: Mapped[str] = mapped_column(String(32))
    value: Mapped[int] = mapped_column(Integer)

    snapshot: Mapped["DeviceSnapshot"] = relationship(back_populates="metrics")

    def as_dict(self) -> dict[str, str | int]:
        return {"name": self.name, "value": self.value}

    def as_dto(self) -> DTO_Metric:
        return DTO_Metric(name=self.name, value=self.value)
