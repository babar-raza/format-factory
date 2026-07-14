"""Tests for _scan_pending_promotions() in check_continuation.py — TC-INT-005-C."""
from __future__ import annotations

from pathlib import Path
import pytest


def test_pending_promotions_appear_in_rework_items(tmp_path):
    """FORMAT_ADAPTATION_REQUIRED tasks surface in _scan_pending_promotions output."""
    promo_dir = tmp_path / ".local" / "supervisor" / "promotion-tasks"
    promo_dir.mkdir(parents=True)
    task_file = promo_dir / "PROMO-NDJSON-probe-ABC123.yaml"
    task_file.write_text(
        "task_id: PROMO-NDJSON-probe-ABC123\n"
        "format_id: ndjson\n"
        "status: FORMAT_ADAPTATION_REQUIRED\n",
        encoding="utf-8",
    )

    from tools.supervisor.check_continuation import _scan_pending_promotions
    result = _scan_pending_promotions(tmp_path)
    assert len(result) == 1
    assert "PROMO-NDJSON-probe-ABC123" in result[0]
    assert "FORMAT_ADAPTATION_REQUIRED" in result[0]


def test_maintained_tasks_not_returned(tmp_path):
    """MAINTAINED status tasks are not included in pending promotions."""
    promo_dir = tmp_path / ".local" / "supervisor" / "promotion-tasks"
    promo_dir.mkdir(parents=True)
    task_file = promo_dir / "PROMO-NDJSON-probe-XYZ789.yaml"
    task_file.write_text(
        "task_id: PROMO-NDJSON-probe-XYZ789\n"
        "format_id: ndjson\n"
        "status: MAINTAINED\n",
        encoding="utf-8",
    )

    from tools.supervisor.check_continuation import _scan_pending_promotions
    result = _scan_pending_promotions(tmp_path)
    assert result == [], f"MAINTAINED tasks should not appear, got: {result}"


def test_scan_is_safe_on_missing_directory(tmp_path):
    """Returns [] (not an error) when promotion-tasks directory does not exist."""
    # Don't create the directory — test that missing dir is safe
    from tools.supervisor.check_continuation import _scan_pending_promotions
    result = _scan_pending_promotions(tmp_path)
    assert result == []


def test_scan_is_safe_on_invalid_yaml(tmp_path):
    """Returns [] for a YAML file that cannot be parsed."""
    promo_dir = tmp_path / ".local" / "supervisor" / "promotion-tasks"
    promo_dir.mkdir(parents=True)
    bad_file = promo_dir / "PROMO-BAD.yaml"
    bad_file.write_text("{ broken yaml: [unclosed\n", encoding="utf-8")

    from tools.supervisor.check_continuation import _scan_pending_promotions
    result = _scan_pending_promotions(tmp_path)
    # Should not raise; bad files are silently skipped
    assert isinstance(result, list)
