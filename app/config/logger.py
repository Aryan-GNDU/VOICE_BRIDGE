"""Structured logging configuration."""

import logging
import sys


class JsonLikeFormatter(logging.Formatter):
    """Small structured formatter without extra runtime dependencies."""

    def format(self, record: logging.LogRecord) -> str:
        base = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key.startswith("_") or key in {
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            }:
                continue
            base[key] = value
        if record.exc_info:
            base["exception"] = self.formatException(record.exc_info)
        return str(base)


def configure_logging(level: str) -> None:
    """Configure root logging once."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLikeFormatter())
    logging.basicConfig(level=level, handlers=[handler], force=True)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)
