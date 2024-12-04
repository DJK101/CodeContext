import logging
import re


class ANSIColorStripperFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter out ANSI escape sequences from log message.
        This method modifies the log record message in place.
        """
        ansi_escape = re.compile(r"(?:\x1B[@-Z\\-_]|\x1B\[[0-?]*[ -/]*[@-~])")
        record.message = ansi_escape.sub("", record.getMessage())
        print(record.message)
        return True
