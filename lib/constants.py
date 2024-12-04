from dataclasses import dataclass

CONFIG_FILE = "config.json"
LOCAL_CONFIG_FILE = "local.config.json"


@dataclass
class HTTP:
    OK = 200
