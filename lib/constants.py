from dataclasses import dataclass
from http.client import ACCEPTED

CONFIG_FILE = "config.json"
LOCAL_CONFIG_FILE = "local.config.json"
DB_URI = "sqlite:///dev.db"

GRAPH_COLUMN_NAMES = ("Recorded time", "RAM usage (Bytes)")


@dataclass
class HTTP:
    @dataclass
    class STATUS:
        OK = 200
        BAD_REQUEST = 400
        CONFLICT = 409
        ACCEPTED = 202

    @dataclass
    class METHOD:
        GET = "GET"
        PUT = "PUT"
        DELETE = "DELETE"
