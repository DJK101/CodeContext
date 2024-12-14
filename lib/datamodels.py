from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class DTO_Metric:
    name: str
    value: float


@dataclass_json
@dataclass
class DTO_DataSnapshot:
    timestamp_utc: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metrics: List[DTO_Metric] = field(default_factory=list)


@dataclass_json
@dataclass
class DTO_Properties:
    name: str
    value: float


@dataclass_json
@dataclass
class DTO_Device:
    name: str
    properties: List[DTO_Properties] = field(default_factory=list)
    data_snapshots: List[DTO_DataSnapshot] = field(default_factory=list)


@dataclass_json
@dataclass
class DTO_Aggregator:
    name: str
    devices: List[DTO_Device] = field(default_factory=list)
