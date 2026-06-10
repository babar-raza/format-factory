"""Tests for tools/health_check.py — TC-APRV-012."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

# Ensure health_check is importable
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

from health_check import check_health, _run_cmd


class TestCheckHealth:
    """Tests for the check_health function."""

    def test_returns_dict_with_expected_keys(self):
        """check_health returns a dict with all required keys."""
        with patch("health_check._run_cmd") as mock_run:
            # Mock pytest --version
            mock_run.side_effect = [
                (0, "pytest 7.0.0"),      # pytest check
                (0, "ruff 0.4.0"),        # ruff check
                (0, "5 passed"),          # test run
            ]
            result = check_health(quick=True)

        assert isinstance(result, dict)
        assert "python_version" in result
        assert "pytest" in result
        assert "ruff" in result
        assert "tests_pass" in result
        assert "test_summary" in result
        assert "healthy" in result

    def test_healthy_when_all_pass(self):
        """check_health reports healthy when pytest available and tests pass."""
        with patch("health_check._run_cmd") as mock_run:
            mock_run.side_effect = [
                (0, "pytest 7.0.0"),
                (0, "ruff 0.4.0"),
                (0, "100 passed"),
            ]
            result = check_health(quick=True)

        assert result["healthy"] is True
        assert result["tests_pass"] is True
        assert result["pytest"] == "available"

    def test_unhealthy_when_tests_fail(self):
        """check_health reports unhealthy when tests fail."""
        with patch("health_check._run_cmd") as mock_run:
            mock_run.side_effect = [
                (0, "pytest 7.0.0"),
                (0, "ruff 0.4.0"),
                (1, "3 failed, 97 passed"),
            ]
            result = check_health(quick=True)

        assert result["healthy"] is False
        assert result["tests_pass"] is False

    def test_unhealthy_when_pytest_missing(self):
        """check_health reports unhealthy when pytest is not available."""
        with patch("health_check._run_cmd") as mock_run:
            mock_run.side_effect = [
                (-1, "NOT_FOUND"),        # pytest missing
                (0, "ruff 0.4.0"),
                (0, "5 passed"),
            ]
            result = check_health(quick=True)

        assert result["pytest"] == "missing"
        # healthy requires both pytest available AND tests pass
        # tests_pass is True but pytest is "missing"
        assert result["healthy"] is False


class TestRunCmd:
    """Tests for the _run_cmd helper — zero network calls."""

    def test_run_cmd_with_valid_command(self):
        """_run_cmd runs a simple command successfully."""
        rc, out = _run_cmd([sys.executable, "--version"])
        assert rc == 0
        assert "Python" in out or "python" in out.lower()

    def test_run_cmd_with_missing_command(self):
        """_run_cmd returns NOT_FOUND for nonexistent commands."""
        rc, out = _run_cmd(["nonexistent_command_xyz"])
        assert rc == -1
        assert out == "NOT_FOUND"
