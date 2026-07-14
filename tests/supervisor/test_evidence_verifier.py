"""Tests for TC-OCRD-A5: Evidence spot-check via AST test count.

Covers:
  - 30 declared, 30 actual functions → no warning, ratio ~1.0
  - 100 declared, 10 actual → WARN_TEST_COUNT_MISMATCH
  - declared_passed=0 → ratio=1.0, no warning
  - non-existent file in changed_files → actual_count=0, no exception
  - syntactically broken test file → skipped gracefully
  - no test files in changed_files (only non-test .py files) → actual_count=0
"""
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO / "tools" / "supervisor") not in sys.path:
    sys.path.insert(0, str(REPO / "tools" / "supervisor"))

from evidence_verifier import spot_check_test_count


def _make_test_file(tmp_path: Path, name: str, test_count: int) -> Path:
    """Create a temporary Python test file with `test_count` test_ functions."""
    p = tmp_path / name
    lines = [f"def test_case_{i}(): pass" for i in range(test_count)]
    p.write_text("\n".join(lines), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Test 1: 30 declared, 30 actual → no warning, ratio=1.0
# ---------------------------------------------------------------------------

def test_matching_count_no_warning(tmp_path):
    test_file = _make_test_file(tmp_path, "test_foo.py", 30)
    rel_path = str(test_file.relative_to(tmp_path))

    result = spot_check_test_count(
        repo_root=tmp_path,
        changed_files=[rel_path],
        declared_passed=30,
        declared_failed=0,
    )
    assert result["actual_count"] == 30
    assert result["declared_count"] == 30
    assert result["ratio"] == 1.0
    assert result["warning"] is None


# ---------------------------------------------------------------------------
# Test 2: 100 declared, 10 actual → WARN_TEST_COUNT_MISMATCH
# ---------------------------------------------------------------------------

def test_overclaim_triggers_warning(tmp_path):
    test_file = _make_test_file(tmp_path, "test_bar.py", 10)
    rel_path = str(test_file.relative_to(tmp_path))

    result = spot_check_test_count(
        repo_root=tmp_path,
        changed_files=[rel_path],
        declared_passed=100,
        declared_failed=0,
    )
    assert result["actual_count"] == 10
    assert result["declared_count"] == 100
    assert result["ratio"] < 0.5
    assert result["warning"] is not None
    assert "WARN_TEST_COUNT_MISMATCH" in result["warning"]


# ---------------------------------------------------------------------------
# Test 3: declared_passed=0 → ratio=1.0, no warning
# ---------------------------------------------------------------------------

def test_zero_declared_returns_one_ratio_no_warning(tmp_path):
    result = spot_check_test_count(
        repo_root=tmp_path,
        changed_files=[],
        declared_passed=0,
        declared_failed=0,
    )
    assert result["ratio"] == 1.0
    assert result["warning"] is None
    assert result["actual_count"] == 0
    assert result["declared_count"] == 0


# ---------------------------------------------------------------------------
# Test 4: non-existent file in changed_files → actual_count=0, no exception
# ---------------------------------------------------------------------------

def test_nonexistent_file_no_exception(tmp_path):
    result = spot_check_test_count(
        repo_root=tmp_path,
        changed_files=["tests/test_doesnotexist.py"],
        declared_passed=10,
        declared_failed=0,
    )
    assert result["actual_count"] == 0
    # No exception raised, warning may be None (actual=0 check)
    # The function only warns when actual > 0 and ratio < 0.5
    assert result["warning"] is None  # actual=0, so no false positive warning


# ---------------------------------------------------------------------------
# Test 5: syntactically broken test file → skipped gracefully
# ---------------------------------------------------------------------------

def test_broken_syntax_file_skipped(tmp_path):
    broken_file = tmp_path / "test_broken.py"
    broken_file.write_text("def test_ok(): pass\ndef test_broken(: INVALID SYNTAX", encoding="utf-8")
    rel_path = str(broken_file.relative_to(tmp_path))

    result = spot_check_test_count(
        repo_root=tmp_path,
        changed_files=[rel_path],
        declared_passed=5,
        declared_failed=0,
    )
    # Broken file is skipped — actual_count=0, no exception
    assert result["actual_count"] == 0
    assert result["warning"] is None  # actual=0, so no MISMATCH warning


# ---------------------------------------------------------------------------
# Test 6: no test files (only non-test .py names) → actual_count=0
# ---------------------------------------------------------------------------

def test_no_test_files_in_changed(tmp_path):
    non_test = tmp_path / "my_module.py"
    non_test.write_text("def test_something(): pass\ndef helper(): pass", encoding="utf-8")
    rel_path = str(non_test.relative_to(tmp_path))

    result = spot_check_test_count(
        repo_root=tmp_path,
        changed_files=[rel_path],
        declared_passed=20,
        declared_failed=0,
    )
    # my_module.py has no 'test_' in its filename, so it's excluded
    assert result["actual_count"] == 0
    assert result["warning"] is None  # actual=0, so no MISMATCH warning
