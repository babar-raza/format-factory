"""Tests for validate_suspended_rotation_stubs() (TC-SGOV-007)."""
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "validators"))

from source_structure_validator import validate_suspended_rotation_stubs


def test_no_config_returns_pass(tmp_path):
    """No known_suspended_rotations key → PASS."""
    baseline = {"schema_version": 1, "known_violations": {}}
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry" / "source-structure-baseline.json").write_text(
        json.dumps(baseline), encoding="utf-8"
    )
    result = validate_suspended_rotation_stubs(tmp_path)
    assert result["result"] == "PASS"
    assert result["orphaned_stubs"] == []


def test_detects_orphaned_stub(tmp_path):
    """Test file matching suspended pattern → WARN with orphan entry."""
    baseline = {
        "schema_version": 1,
        "known_violations": {},
        "known_suspended_rotations": [
            {
                "file_pattern": "src/python/zst/zst_analytics.py",
                "test_pattern": "_mod_\\d+_times_\\d+",
                "suspended_since": "2026-06-18",
                "reason": "no spec backing",
            }
        ],
    }
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry" / "source-structure-baseline.json").write_text(
        json.dumps(baseline), encoding="utf-8"
    )
    # Create a matching test file
    test_dir = tmp_path / "tests" / "python" / "zst"
    test_dir.mkdir(parents=True)
    (test_dir / "test_r500_zst_arithmetic.py").write_text(
        "def test_zst_foo_mod_3_times_7():\n    pass\n", encoding="utf-8"
    )
    result = validate_suspended_rotation_stubs(tmp_path)
    assert result["result"] == "WARN"
    assert len(result["orphaned_stubs"]) == 1
    assert "zst" in result["orphaned_stubs"][0]["file"]


def test_non_matching_test_passes(tmp_path):
    """Test file that does NOT match suspended pattern → PASS."""
    baseline = {
        "schema_version": 1,
        "known_violations": {},
        "known_suspended_rotations": [
            {
                "file_pattern": "src/python/zst/zst_analytics.py",
                "test_pattern": "_mod_\\d+_times_\\d+",
                "suspended_since": "2026-06-18",
                "reason": "no spec backing",
            }
        ],
    }
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry" / "source-structure-baseline.json").write_text(
        json.dumps(baseline), encoding="utf-8"
    )
    test_dir = tmp_path / "tests" / "python" / "zst"
    test_dir.mkdir(parents=True)
    (test_dir / "test_zst_normal.py").write_text(
        "def test_zst_row_count():\n    pass\n", encoding="utf-8"
    )
    result = validate_suspended_rotation_stubs(tmp_path)
    assert result["result"] == "PASS"
    assert result["orphaned_stubs"] == []


def test_real_repo_runs_without_error():
    """Smoke test: runs against the real repo without crashing."""
    result = validate_suspended_rotation_stubs(_REPO)
    assert result["result"] in ("PASS", "WARN")
    assert isinstance(result["orphaned_stubs"], list)
