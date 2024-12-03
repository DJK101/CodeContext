import json
import logging
import logging.handlers
import os
from dataclasses import dataclass

import colorlog

import constants


@dataclass
class ServerConfig:
    port: int = 5050


@dataclass
class ConsoleLoggingConfig:
    enabled: bool = True
    level: str = "WARNING"
    format: str = "%(levelname).1s:[%(name)s]> %(message)s",
    date_format: str = "%Y-%m-%d %H:%M:%S"


@dataclass
class FileLoggingConfig(ConsoleLoggingConfig):
    output_dir: str = "logs"
    filename: str = "app.log"
    max_bytes: int = 10485760
    backup_count: int = 5


@dataclass
class LoggingConfig:
    console: ConsoleLoggingConfig
    file: FileLoggingConfig


class Config:
    server_c: ServerConfig
    logging_c: LoggingConfig

    def __init__(self, script_path: str = None, config_path: str = None):
        if script_path:
            self._set_working_directory(script_path)
        
        if os.path.exists(constants.CONFIG_FILE):
            self._config = self._load_config(constants.CONFIG_FILE)
        else:
            self._config = self._load_config(constants.LOCAL_CONFIG_FILE)

        server_config_dict = self._config.get("server", {})
        self.server_c = ServerConfig(**server_config_dict)

        logging_config_dict = self._config.get("logging", {})
        self.logging_c = LoggingConfig(
            console=ConsoleLoggingConfig(**logging_config_dict.get("console", {})),
            file=FileLoggingConfig(**logging_config_dict.get("file", {})),
        )
        self._setup_logging()

    @staticmethod
    def _set_working_directory(script_path: str) -> None:
        os.chdir(os.path.dirname(os.path.abspath(script_path)))

    @staticmethod
    def _load_config(configpath: str) -> dict:
        if not os.path.exists(configpath):
            raise FileNotFoundError(f"Config file not found: {configpath}")

        with open(configpath, "r") as f:
            return json.load(f)

    @staticmethod
    def _get_lowest_level(logging_config: LoggingConfig) -> int:
        root_level = logging.NOTSET
        enabled_levels = []
        if logging_config.console.enabled:
            enabled_levels.append(logging_config.console.level)
        if logging_config.file.enabled:
            enabled_levels.append(logging_config.file.level)
        if enabled_levels:
            root_level = min(enabled_levels)
        return root_level

    def _setup_logging(self) -> logging.Logger:
        if self.logging_c.file.enabled:
            os.makedirs(self.logging_c.file.output_dir, exist_ok=True)

        lowest_log_level = self._get_lowest_level(self.logging_c)
        root_logger = logging.getLogger()
        root_logger.setLevel(lowest_log_level)

        root_logger.handlers.clear()

        if self.logging_c.console.enabled:
            console_handler = logging.StreamHandler()
            console_formatter = colorlog.ColoredFormatter(
                fmt="%(log_color)s" + self.logging_c.console.format,
                datefmt=self.logging_c.console.date_format,
                reset=True,
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
            )
            console_handler.setFormatter(console_formatter)
            console_handler.setLevel(self.logging_c.console.level)
            root_logger.addHandler(console_handler)

        if self.logging_c.file.enabled:
            file_path = os.path.join(
                self.logging_c.file.output_dir, self.logging_c.file.filename
            )
            file_handler = logging.handlers.RotatingFileHandler(
                file_path,
                maxBytes=self.logging_c.file.max_bytes,
                backupCount=self.logging_c.file.backup_count,
            )
            file_formatter = logging.Formatter(
                fmt=self.logging_c.file.format,
                datefmt=self.logging_c.file.date_format,
            )
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(self.logging_c.file.level)
            root_logger.addHandler(file_handler)

        return root_logger
