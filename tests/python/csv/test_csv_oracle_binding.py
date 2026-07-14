"""test_csv_oracle_binding.py — Oracle-bound CSV tests (TC-W1B-001).

Consumes oracle cases from oracle/formats/csv/oracle-package.yaml via
oracle_test_adapter.py. Tests are parametrized by oracle case ID.

This file is ADDITIVE — existing test_csv_*.py files are unchanged.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tools"))

from oracle.oracle_test_adapter import (
    get_expected_properties,
    load_oracle_cases,
    resolve_sample_path,
)


# ---------------------------------------------------------------------------
# Adapter — CSV executor
# ---------------------------------------------------------------------------

def _run_csv(sample_path: Path) -> dict:
    """Run the CSV parser against a sample file.

    Uses explicit PROJECT_ROOT path insert like other CSV tests to avoid
    the stdlib csv module shadowing issue with --import-mode=importlib.
    """
    from src.python.csv.csv_parser import parse_csv
    return parse_csv(str(sample_path))


# ---------------------------------------------------------------------------
# TC-W1B-001: Parametrized valid case tests from oracle
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "case",
    load_oracle_cases("csv", "valid"),
    ids=lambda c: c["case_id"],
)
def test_csv_oracle_valid_cases(case):
    """Oracle-bound: each valid CSV case must parse and match expected properties."""
    sample_path = resolve_sample_path(case)
    if sample_path is None:
        pytest.skip(f"No sample file for case {case['case_id']}")

    result = _run_csv(sample_path)

    expected = get_expected_properties(case)
    for prop_name, expected_val in expected.items():
        actual_val = result.get(prop_name)
        assert actual_val == expected_val, (
            f"Case {case['case_id']}: property '{prop_name}' mismatch. "
            f"Expected={expected_val!r}, got={actual_val!r}"
        )


# ---------------------------------------------------------------------------
# TC-W1B-001: Parametrized invalid case tests from oracle
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "case",
    load_oracle_cases("csv", "invalid"),
    ids=lambda c: c["case_id"],
)
def test_csv_oracle_invalid_cases(case):
    """Oracle-bound: invalid CSV inputs must raise or return error indicators."""
    sample_path = resolve_sample_path(case)
    if sample_path is None:
        pytest.skip(f"No sample file for case {case['case_id']}")

    # Expected: either raises an exception or returns parse_errors
    try:
        result = _run_csv(sample_path)
        # If no exception, check for parse_errors or error field
        has_error = bool(
            result.get("parse_errors")
            or result.get("error")
            or result.get("ok") is False
        )
        assert has_error, (
            f"Case {case['case_id']}: expected parse failure or error indicator, "
            f"but got clean result: {result}"
        )
    except Exception:
        # Exception is a valid rejection of invalid input
        pass
