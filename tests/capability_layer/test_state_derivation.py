"""Regression tests for capability state derivation (TC-CL-001).

Tests verify the fix for the false example_verified assignment bug:
  - example_verified must only be assigned when the specific function name
    appears in an example file, not when ANY example file exists for the format.
  - No example_verified record should have empty example_refs.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "capability_layer"))

from capability_map_generator import (  # type: ignore[import]
    _determine_state,
    _scan_example_file_refs,
)


# ---------------------------------------------------------------------------
# Tests for _scan_example_file_refs
# ---------------------------------------------------------------------------

def test_scan_example_file_refs_finds_function(tmp_path: Path) -> None:
    """_scan_example_file_refs returns file name when fn_name( appears in content."""
    ex_file = tmp_path / "demo_csv.py"
    ex_file.write_text("result = load('file.csv')\nprint(result)\n", encoding="utf-8")
    refs = _scan_example_file_refs(tmp_path, "load")
    assert refs == ["demo_csv.py"], f"Expected ['demo_csv.py'], got {refs}"


def test_scan_example_file_refs_no_false_positive(tmp_path: Path) -> None:
    """_scan_example_file_refs returns [] when fn_name is NOT called in any example."""
    ex_file = tmp_path / "demo_csv.py"
    # Only calls load(), NOT write() — 'write' string does not appear as 'write('
    ex_file.write_text("result = load('file.csv')\nprint(result)\n", encoding="utf-8")
    refs = _scan_example_file_refs(tmp_path, "write")
    assert refs == [], f"Expected [], got {refs}"


def test_scan_example_file_refs_missing_dir(tmp_path: Path) -> None:
    """_scan_example_file_refs returns [] when directory does not exist."""
    refs = _scan_example_file_refs(tmp_path / "nonexistent", "load")
    assert refs == [], f"Expected [], got {refs}"


# ---------------------------------------------------------------------------
# Tests for _determine_state with the fixed example_count logic
# ---------------------------------------------------------------------------

def test_determine_state_no_false_example_verified() -> None:
    """example_verified must NOT be assigned when example_count=0 (function not in examples).

    The legacy fallback uses filename substring matching. Use a test file name that contains
    the function name substring so has_matching_test=True, isolating the example_count=0 case.
    """
    # "test_write_csv.py" contains "write" substring → has_matching_test=True via legacy fallback
    # example_count=0 → function NOT found in any example file → must NOT be example_verified
    state, reason, confidence = _determine_state(
        fn_name="write",
        implemented=True,
        test_files=["test_write_csv.py"],
        example_count=0,  # fixed: function-level count — function not in any example
        authority_state="spec_fact",
        test_dir=None,
    )
    assert state != "example_verified", (
        f"BUG REGRESSION: example_verified assigned with example_count=0 — state={state!r}"
    )
    assert state == "test_verified", f"Expected test_verified (has test, no example), got {state!r}"


def test_determine_state_correct_example_verified() -> None:
    """example_verified IS assigned when example_count>0 (function found in example file)."""
    # "test_load_csv.py" contains "load" substring → has_matching_test=True
    # example_count=1 → function found in an example file → must be example_verified
    state, reason, confidence = _determine_state(
        fn_name="load",
        implemented=True,
        test_files=["test_load_csv.py"],
        example_count=1,  # function-level: load() found in example file
        authority_state="spec_fact",
        test_dir=None,
    )
    assert state == "example_verified", (
        f"Expected example_verified when example_count=1 and has_matching_test=True, got {state!r}"
    )


# ---------------------------------------------------------------------------
# Integration test: verify generated map has no bad example_verified records
# ---------------------------------------------------------------------------

def test_no_example_verified_with_empty_example_refs() -> None:
    """Unified map must have 0 records with state=example_verified and empty example_refs.

    This is the VAL-011 invariant. If the unified map has not been regenerated yet,
    this test is skipped (not failed) to allow development without blocking CI.
    """
    unified_path = _REPO_ROOT / "reports" / "capability-layer" / "unified-capability-map.json"
    if not unified_path.exists():
        pytest.skip("unified-capability-map.json not yet generated")
    data = json.loads(unified_path.read_text(encoding="utf-8"))
    caps = data.get("capabilities", [])
    bad = [
        c for c in caps
        if c.get("current_state") == "example_verified" and not c.get("example_refs")
    ]
    assert len(bad) == 0, (
        f"VAL-011 REGRESSION: {len(bad)} records have current_state=example_verified "
        f"with empty example_refs. First: {bad[0].get('capability_id') if bad else 'n/a'}"
    )
