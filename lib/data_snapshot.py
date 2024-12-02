import time
import json
import psutil
import logging
from dataclasses import dataclass, asdict
import datetime
import sys


@dataclass
class CPUStats:
    cores: int
    # usage_per_core: list[float]
    total_usage: float


@dataclass
class MemoryStats:
    total: int
    available: int
    used: int
    percent: float


@dataclass
class DiskStats:
    total: int
    used: int
    free: int
    percent: float


@dataclass
class ProcessInfo:
    pid: int
    name: str
    status: str
    cpu_usage: float
    memory_usage: float


@dataclass
class SystemMetrics:
    timestamp: str
    cpu: CPUStats
    memory: MemoryStats
    disk: DiskStats
    processes: list[ProcessInfo]


class DataSnapshot:
    """A class to capture and store application metrics."""

    def __init__(self):
        self.metrics = {"request_count": 0, "average_processing_time": 0.0}

    def record_request(self, processing_time):
        """Update metrics with the latest request processing time."""
        self.metrics["request_count"] += 1
        # Calculate new average processing time
        count = self.metrics["request_count"]
        current_avg = self.metrics["average_processing_time"]
        self.metrics["average_processing_time"] = (
            (current_avg * (count - 1)) + processing_time
        ) / count

    def get_metrics(self):
        """Return metrics as a dictionary."""
        return self.metrics

    def gather_system_metrics(self):
        # Collect CPU stats
        cpu_stats = CPUStats(
            cores=psutil.cpu_count(),
            # usage_per_core=psutil.cpu_percent(percpu=True),
            total_usage=psutil.cpu_percent(),
        )

        # Collect Memory stats
        virtual_memory = psutil.virtual_memory()
        memory_stats = MemoryStats(
            total=virtual_memory.total,
            available=virtual_memory.available,
            used=virtual_memory.used,
            percent=virtual_memory.percent,
        )

        # Collect Disk stats (for main partition only)
        disk_usage = psutil.disk_usage("/")
        disk_stats = DiskStats(
            total=disk_usage.total,
            used=disk_usage.used,
            free=disk_usage.free,
            percent=disk_usage.percent,
        )

        # Collect running processes (top 5 by memory usage for brevity)
        processes = []
        for proc in sorted(
            psutil.process_iter(
                ["pid", "name", "status", "cpu_percent", "memory_percent"]
            ),
            key=lambda p: p.info["memory_percent"],
            reverse=True,
        )[:5]:
            try:
                processes.append(
                    ProcessInfo(
                        pid=proc.info["pid"],
                        name=proc.info["name"],
                        status=proc.info["status"],
                        cpu_usage=proc.info["cpu_percent"],
                        memory_usage=proc.info["memory_percent"],
                    )
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Timestamp
        timestamp = datetime.datetime.now().isoformat()

        # Create SystemMetrics object
        system_metrics = SystemMetrics(
            timestamp=timestamp,
            cpu=cpu_stats,
            memory=memory_stats,
            disk=disk_stats,
            processes=processes,
        )

        return system_metrics

    def serialize_metrics(metrics):
        """Serialize system metrics to JSON."""
        print(metrics)
        return json.dumps(asdict(metrics), indent=4)

    def deserialize_metrics(json_data):
        """Deserialize JSON back into SystemMetrics object."""
        data = json.loads(json_data)
        processes = [ProcessInfo(**proc) for proc in data["processes"]]
        cpu = CPUStats(**data["cpu"])
        memory = MemoryStats(**data["memory"])
        disk = DiskStats(**data["disk"])
        return SystemMetrics(
            timestamp=data["timestamp"],
            cpu=cpu,
            memory=memory,
            disk=disk,
            processes=processes,
        )
