"""logging_config.py — Structured JSON logging for the supervisor pipeline.

Provides a JSON log formatter with sprint correlation IDs and a one-call
setup function. Used by autonomous_cycle.py and other supervisor tools.

Usage:
    from logging_config import configure_supervisor_logging
    logger = configure_supervisor_logging()
    logger.info("Sprint started", extra={"sprint_id": run_id})
"""

from __future__ import annotations

import json
import logging
import sys


class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects.

    Supports optional extra fields: sprint_id, work_item.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage(),
        }
        # Optional correlation fields
        sprint_id = getattr(record, "sprint_id", None)
        if sprint_id is not None:
            log_entry["sprint_id"] = sprint_id
        work_item = getattr(record, "work_item", None)
        if work_item is not None:
            log_entry["work_item"] = work_item
        return json.dumps(log_entry, default=str)


def configure_supervisor_logging(
    level: int = logging.INFO,
    stream: object = None,
) -> logging.Logger:
    """Configure and return the 'supervisor' logger with JSON output.

    Args:
        level: Logging level (default INFO).
        stream: Output stream (default sys.stderr).

    Returns:
        Configured logger instance.
    """
    if stream is None:
        stream = sys.stderr
    logger = logging.getLogger("supervisor")
    # Avoid adding duplicate handlers on repeated calls
    if not logger.handlers:
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger
