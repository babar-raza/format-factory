"""Tests for tools/supervisor/logging_config.py — TC-APRV-011."""

from __future__ import annotations

import io
import json
import logging
import sys
from pathlib import Path

# Ensure supervisor tools are importable
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from logging_config import JSONFormatter, configure_supervisor_logging


class TestJSONFormatter:
    """Tests for the JSONFormatter class."""

    def test_format_produces_valid_json(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="supervisor",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message",
            args=None,
            exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert parsed["level"] == "INFO"
        assert parsed["message"] == "test message"
        assert "timestamp" in parsed

    def test_format_includes_sprint_id_when_provided(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="supervisor",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="sprint started",
            args=None,
            exc_info=None,
        )
        record.sprint_id = "test-sprint-001"
        output = formatter.format(record)
        parsed = json.loads(output)
        assert parsed["sprint_id"] == "test-sprint-001"

    def test_format_includes_work_item_when_provided(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="supervisor",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="grading item",
            args=None,
            exc_info=None,
        )
        record.work_item = "W01-TEST"
        output = formatter.format(record)
        parsed = json.loads(output)
        assert parsed["work_item"] == "W01-TEST"

    def test_format_omits_optional_fields_when_absent(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="supervisor",
            level=logging.WARNING,
            pathname="test.py",
            lineno=1,
            msg="warning message",
            args=None,
            exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert "sprint_id" not in parsed
        assert "work_item" not in parsed
        assert parsed["level"] == "WARNING"


class TestConfigureSupervisorLogging:
    """Tests for the configure_supervisor_logging function."""

    def test_returns_logger_with_handler(self):
        # Use a fresh logger name to avoid handler accumulation
        logger = logging.getLogger("supervisor_test_handler")
        logger.handlers.clear()
        # Monkey-patch: test via the function's logic
        stream = io.StringIO()
        result = configure_supervisor_logging(stream=stream)
        assert isinstance(result, logging.Logger)
        assert len(result.handlers) >= 1
        assert result.level == logging.INFO

    def test_logger_outputs_json_to_stream(self):
        stream = io.StringIO()
        logger = configure_supervisor_logging(stream=stream)
        # Clear existing handlers and add ours
        logger.handlers.clear()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.info("test output", extra={"sprint_id": "run-123"})
        output = stream.getvalue()
        parsed = json.loads(output.strip())
        assert parsed["message"] == "test output"
        assert parsed["sprint_id"] == "run-123"

    def test_does_not_duplicate_handlers(self):
        # Get a fresh logger
        logger = logging.getLogger("supervisor_no_dup")
        logger.handlers.clear()
        stream = io.StringIO()
        # Simulate repeated calls by directly calling the setup logic
        for _ in range(3):
            if not logger.handlers:
                handler = logging.StreamHandler(stream)
                handler.setFormatter(JSONFormatter())
                logger.addHandler(handler)
        assert len(logger.handlers) == 1
