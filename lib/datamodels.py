from datetime import datetime, timezone
from typing import List
from uuid import UUID
from dataclasses import dataclass, field
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
class DTO_Device:
    name: str
    data_snapshots: List[DTO_DataSnapshot] = field(default_factory=list)
    
@dataclass_json
@dataclass
class DTO_Aggregator:
    guid: UUID
    name: str
    devices: List[DTO_Device] = field(default_factory=list)

    def to_dict(self):
        """Convert the DTO_Aggregator to a dictionary for JSON serialization.
        Required because UUIDs are not serializable by default."""
        return {
            'guid': str(self.guid),
            'name': self.name,
            'devices': [device.to_dict() for device in self.devices] # type: ignore
        }