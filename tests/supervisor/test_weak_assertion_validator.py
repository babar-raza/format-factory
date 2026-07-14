"""Tests for validate_weak_test_assertions() — TC-INT-003-C."""
from __future__ import annotations

import pytest
from pathlib import Path


def _make_decl(test_path: str) -> dict:
    return {
        "planned_work_items": [
            {
                "work_item_id": "WI-TEST",
                "test_references": [test_path],
            }
        ]
    }


def test_weak_assertion_detected(tmp_path):
    """WARN when a test function has only `assert result is not None`."""
    test_file = tmp_path / "tests" / "python" / "ndjson" / "test_weak.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text(
        "def test_probe_ndjson():\n"
        "    result = probe_ndjson(b'{}')\n"
        "    assert result is not None\n",
        encoding="utf-8",
    )
    # Build declaration relative to tmp_path
    rel = str(test_file.relative_to(tmp_path)).replace("\\", "/")
    decl = _make_decl(rel)

    from tools.supervisor.governance_validators_ext4 import validate_weak_test_assertions
    result = validate_weak_test_assertions(decl, repo_root=tmp_path)
    assert result["result"] == "WARN", f"Expected WARN, got: {result}"
    assert any("test_probe_ndjson" in item for item in result["items"])


def test_meaningful_assertion_clean(tmp_path):
    """PASS when a test function has a non-trivial assertion."""
    test_file = tmp_path / "tests" / "python" / "ndjson" / "test_strong.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text(
        "def test_probe_ndjson_count():\n"
        "    result = probe_ndjson(b'{}')\n"
        '    assert result["record_count"] == 1\n',
        encoding="utf-8",
    )
    rel = str(test_file.relative_to(tmp_path)).replace("\\", "/")
    decl = _make_decl(rel)

    from tools.supervisor.governance_validators_ext4 import validate_weak_test_assertions
    result = validate_weak_test_assertions(decl, repo_root=tmp_path)
    assert result["result"] == "PASS", f"Expected PASS, got: {result}"


def test_grace_exemption_suppresses_warn(tmp_path):
    """PASS (not WARN) when file is listed in backfill-gaps.yaml grace list."""
    test_file = tmp_path / "tests" / "python" / "ndjson" / "test_grace.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text(
        "def test_probe_ndjson_grace():\n"
        "    result = probe_ndjson(b'{}')\n"
        "    assert result is not None\n",
        encoding="utf-8",
    )
    rel = str(test_file.relative_to(tmp_path)).replace("\\", "/")

    # Write backfill-gaps.yaml with grace exemption
    bg_dir = tmp_path / "reports" / "drivers"
    bg_dir.mkdir(parents=True)
    (bg_dir / "backfill-gaps.yaml").write_text(
        f"backfill_gaps:\n  - file_path: {rel}\n    grace_class: weak_assertion_backfill\n",
        encoding="utf-8",
    )

    decl = _make_decl(rel)
    from tools.supervisor.governance_validators_ext4 import validate_weak_test_assertions
    result = validate_weak_test_assertions(decl, repo_root=tmp_path)
    assert result["result"] == "PASS", f"Expected PASS (grace-exempt), got: {result}"


def test_scaffold_markers_not_double_counted(tmp_path):
    """V19 and V-WEAK are independent — V-WEAK ignores scaffold-marker files outside tests/python/."""
    # File outside tests/python/ — should not be scanned by V-WEAK
    test_file = tmp_path / "tests" / "supervisor" / "test_scaffold.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text(
        "# FIXTURE_REQUIRED\n"
        "def test_something():\n"
        "    assert result is not None\n",
        encoding="utf-8",
    )
    rel = str(test_file.relative_to(tmp_path)).replace("\\", "/")
    decl = _make_decl(rel)

    from tools.supervisor.governance_validators_ext4 import validate_weak_test_assertions
    result = validate_weak_test_assertions(decl, repo_root=tmp_path)
    # Not in tests/python/ so V-WEAK should not flag it
    assert result["result"] == "PASS", (
        f"V-WEAK should not scan files outside tests/python/, got: {result}"
    )
