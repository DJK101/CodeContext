from dataclasses import dataclass

CONFIG_FILE = "config.json"
LOCAL_CONFIG_FILE = "local.config.json"


@dataclass
class HTTP:
    @dataclass
    class STATUS:
        OK = 200
        BAD_REQUEST = 400
    
    @dataclass
    class METHOD:
        GET = "GET"
        PUT = "PUT"