import json
import logging
import logging.handlers
import os
from dataclasses import dataclass
from typing import Any

import colorlog

from lib.constants import CONFIG_FILE, LOCAL_CONFIG_FILE
from lib.sqlalchemy_handler import SQLAlchemyHandler


@dataclass
class ServerConfig:
    port: int = 5050

@dataclass
class DatabaseConfig:
    connection_string: str = "sqlite:///dev.db"


@dataclass
class ConsoleLoggingConfig:
    enabled: bool = True
    level: str = "WARNING"
    format: str = "%(levelname).1s:[%(name)s]> %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"


@dataclass
class FileLoggingConfig(ConsoleLoggingConfig):
    output_dir: str = "logs"
    filename: str = "app.log"
    max_bytes: int = 10485760
    backup_count: int = 5

@dataclass
class DatabaseLoggingConfig(ConsoleLoggingConfig):
    pass


@dataclass
class LoggingConfig:
    console: ConsoleLoggingConfig
    file: FileLoggingConfig
    db: DatabaseLoggingConfig


class Config:
    server_c: ServerConfig
    db_c: DatabaseConfig
    logging_c: LoggingConfig

    def __init__(self, script_path: str):
        if script_path:
            self._set_working_directory(script_path)

        if os.path.exists(LOCAL_CONFIG_FILE):
            self._config = self._load_config(LOCAL_CONFIG_FILE)
        else:
            self._config = self._load_config(CONFIG_FILE)

        server_config_dict = self._config.get("server", {})
        self.server_c = ServerConfig(**server_config_dict)

        db_config_dict = self._config.get("db", {})
        self.db_c = DatabaseConfig(**db_config_dict)

        logging_config_dict = self._config.get("logging", {})
        self.logging_c = LoggingConfig(
            console=ConsoleLoggingConfig(**logging_config_dict.get("console", {})),
            file=FileLoggingConfig(**logging_config_dict.get("file", {})),
            db=DatabaseLoggingConfig(**logging_config_dict.get("db", {}))
        )
        self._setup_logging()

    @staticmethod
    def _set_working_directory(script_path: str) -> None:
        os.chdir(os.path.dirname(os.path.abspath(script_path)))

    @staticmethod
    def _load_config(configpath: str) -> dict[str, Any]:
        if not os.path.exists(configpath):
            raise FileNotFoundError(f"Config file not found: {configpath}")

        with open(configpath, "r") as f:
            return json.load(f)

    def _get_lowest_level(self) -> int:
        root_level = logging.NOTSET
        enabled_levels: list[int] = []
        if self.logging_c.console.enabled:
            logging_num = logging.getLevelName(self.logging_c.console.level) # type: ignore
            enabled_levels.append(logging_num)
        if self.logging_c.file.enabled:
            logging_num = logging.getLevelName(self.logging_c.file.level) # type: ignore
            enabled_levels.append(logging_num)
        if enabled_levels:
            root_level = min(enabled_levels)
        return root_level

    def _setup_console_logging(self, root_logger: logging.Logger) -> None:
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

    def _setup_file_logging(self, root_logger: logging.Logger) -> None:
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

    def _setup_db_logging(self, root_logger: logging.Logger) -> None:
        connection_string = self.db_c.connection_string
        db_handler = SQLAlchemyHandler(connection_string)
        db_formatter = logging.Formatter(
            fmt=self.logging_c.db.format,
            datefmt=self.logging_c.db.date_format,
        )
        db_handler.setFormatter(db_formatter)
        db_handler.setLevel(self.logging_c.db.level)

        root_logger.addHandler(db_handler)

    def _setup_logging(self) -> logging.Logger:
        if self.logging_c.file.enabled:
            os.makedirs(self.logging_c.file.output_dir, exist_ok=True)

        lowest_log_level = self._get_lowest_level()
        root_logger = logging.getLogger()
        root_logger.setLevel(lowest_log_level)

        root_logger.handlers.clear()

        if self.logging_c.console.enabled:
            self._setup_console_logging(root_logger)
        if self.logging_c.file.enabled:
            self._setup_file_logging(root_logger)
        if self.logging_c.db.enabled:
            self._setup_db_logging(root_logger)

        return root_logger
