"""test_toml_oracle_binding.py — Oracle-bound TOML tests (TC-W5-003).

Consumes oracle cases from oracle/formats/toml/oracle-package.yaml via
the oracle executor. Tests are parametrized by oracle case ID.

This file is ADDITIVE — existing test_toml_*.py files are unchanged.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tools"))

from oracle.oracle_test_adapter import load_oracle_cases, load_oracle_package
from tools.oracle.execute_oracle import execute_toml_valid_case

_NON_FAIL_RESULTS = {
    "PASS",
    "SKIPPED_MISSING_PROVIDER",
    "SKIPPED_MISSING_DEPENDENCY",
    "BLOCKED_MISSING_SAMPLE",
    "NOT_APPLICABLE",
    "INCONCLUSIVE",
}


@pytest.mark.parametrize(
    "case",
    load_oracle_cases("toml", "valid"),
    ids=lambda c: c["case_id"],
)
def test_toml_oracle_valid_cases(case):
    """Oracle-bound: each TOML valid case must not produce a FAIL verdict."""
    pkg = load_oracle_package("toml")
    verdict = execute_toml_valid_case(case, pkg)
    result = verdict["result"]

    assert result in _NON_FAIL_RESULTS, (
        f"Case {case['case_id']} produced unexpected result {result!r}. "
        f"Diagnostics: {verdict.get('diagnostics')}"
    )
