from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, List, Type, TypeVar

T = TypeVar("T", bound="BaseDTO")

class BaseDTO:
    @classmethod
    def from_dict(cls: Type[T], data: dict[str, Any]) -> T: ...
    def to_dict(self) -> dict[str, Any]: ...
    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T: ...
    def to_json(self) -> str: ...

@dataclass
class DTO_Metric(BaseDTO):
    name: str
    value: float

@dataclass
class DTO_DataSnapshot(BaseDTO):
    timestamp_utc: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metrics: List[DTO_Metric] = field(default_factory=list)

@dataclass
class DTO_Properties:
    name: str
    value: float

@dataclass
class DTO_Device(BaseDTO):
    name: str
    properties: List[DTO_Properties] = field(default_factory=list)
    data_snapshots: List[DTO_DataSnapshot] = field(default_factory=list)

@dataclass
class DTO_Aggregator(BaseDTO):
    name: str
    devices: List[DTO_Device] = field(default_factory=list)
