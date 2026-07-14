"""Negative control oracle test suite (TC-W5-002).

Validates that the oracle infrastructure correctly BLOCKS or FAILs when:
- Authority class is IMPLEMENTATION_OBSERVED (self-approval forbidden)
- Authority class is AI_DRAFT_UNVERIFIED (synthetic authority forbidden)
- Expected model property value is corrupted (wrong expected → FAIL, not PASS)
- Sample file does not exist (missing input → BLOCKED, not PASS)

Also includes a positive control to confirm the PASS path is reachable.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.oracle.execute_oracle import (  # noqa: E402
    RESULT_BLOCKED_MISSING_AUTHORITY,
    RESULT_BLOCKED_MISSING_SAMPLE,
    RESULT_FAIL,
    RESULT_PASS,
    check_authority,
    execute_csv_valid_case,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_minimal_pkg() -> dict:
    return {"oracle_id": "oracle-test-v1", "oracle_version": 1}


def _make_csv_case(
    case_id: str,
    authority_class: str,
    sample_ref: str | None = None,
    expected_model_properties: list | None = None,
) -> dict:
    case: dict = {"case_id": case_id, "authority_class": authority_class}
    if sample_ref is not None:
        case["sample_ref"] = sample_ref
    if expected_model_properties is not None:
        case["expected_model_properties"] = expected_model_properties
    return case


# ---------------------------------------------------------------------------
# Test 1 — IMPLEMENTATION_OBSERVED is blocked
# ---------------------------------------------------------------------------

def test_implementation_observed_authority_is_blocked():
    """check_authority must return BLOCKED_MISSING_AUTHORITY for IMPLEMENTATION_OBSERVED.

    The oracle cannot self-approve: a case whose authority_class is
    IMPLEMENTATION_OBSERVED must never produce a PASS verdict.
    """
    case = {"case_id": "nc-001", "authority_class": "IMPLEMENTATION_OBSERVED"}
    blocked, status = check_authority(case, result_pass_candidate=True)

    assert blocked == RESULT_BLOCKED_MISSING_AUTHORITY, (
        f"Expected BLOCKED_MISSING_AUTHORITY, got {blocked!r}"
    )
    assert status == "IMPLEMENTATION_OBSERVED"


def test_implementation_observed_blocks_executor_result():
    """execute_csv_valid_case must return BLOCKED_MISSING_AUTHORITY for IMPLEMENTATION_OBSERVED.

    Executor-level enforcement: authority block fires before any file I/O.
    """
    case = _make_csv_case(
        case_id="nc-001-exec",
        authority_class="IMPLEMENTATION_OBSERVED",
        sample_ref="samples/by-format/csv/minimal-2x2.csv",
    )
    verdict = execute_csv_valid_case(case, _make_minimal_pkg())

    assert verdict["result"] == RESULT_BLOCKED_MISSING_AUTHORITY, (
        f"Executor should block IMPLEMENTATION_OBSERVED, got {verdict['result']!r}"
    )


# ---------------------------------------------------------------------------
# Test 2 — AI_DRAFT_UNVERIFIED is blocked
# ---------------------------------------------------------------------------

def test_ai_draft_unverified_is_blocked():
    """check_authority must return BLOCKED_MISSING_AUTHORITY for AI_DRAFT_UNVERIFIED.

    Synthetic AI-generated authority without external verification must not
    be allowed to produce a PASS verdict.
    """
    case = {"case_id": "nc-002", "authority_class": "AI_DRAFT_UNVERIFIED"}
    blocked, status = check_authority(case, result_pass_candidate=True)

    assert blocked == RESULT_BLOCKED_MISSING_AUTHORITY, (
        f"Expected BLOCKED_MISSING_AUTHORITY, got {blocked!r}"
    )
    assert status == "AI_DRAFT_UNVERIFIED"


def test_ai_draft_unverified_does_not_block_fail_candidates():
    """check_authority must NOT block a non-PASS result (result_pass_candidate=False).

    Authority blocking only applies when a PASS would otherwise be issued.
    For FAIL candidates, the authority class is recorded but does not block.
    """
    case = {"case_id": "nc-002b", "authority_class": "AI_DRAFT_UNVERIFIED"}
    blocked, status = check_authority(case, result_pass_candidate=False)

    assert blocked is None, (
        "Authority block should not fire for result_pass_candidate=False"
    )
    assert status == "AI_DRAFT_UNVERIFIED"


# ---------------------------------------------------------------------------
# Test 3 — Corrupted expected value produces FAIL
# ---------------------------------------------------------------------------

def test_corrupted_expected_value_produces_fail():
    """Oracle must FAIL when expected_model_properties contains a wrong value.

    A corrupted oracle expectation (e.g. row_count=9999 for a 2-row file)
    must never silently produce PASS. This guards against soft assertions.
    """
    csv_sample = "samples/by-format/csv/minimal-2x2.csv"
    if not (REPO_ROOT / csv_sample).exists():
        pytest.skip("CSV sample not present")

    case = _make_csv_case(
        case_id="nc-003",
        authority_class="AUTHORITATIVE_REFERENCE_VECTOR",
        sample_ref=csv_sample,
        expected_model_properties=[
            {"property": "row_count", "value": 9999, "authority": "corrupted-test-value"},
        ],
    )
    verdict = execute_csv_valid_case(case, _make_minimal_pkg())

    assert verdict["result"] == RESULT_FAIL, (
        f"Corrupted expected value should produce FAIL, got {verdict['result']!r}"
    )
    deviations = verdict.get("deviations", [])
    assert any(d["property"] == "row_count" for d in deviations), (
        f"Expected a row_count deviation in verdict, got {deviations!r}"
    )


# ---------------------------------------------------------------------------
# Test 4 — Missing sample returns BLOCKED_MISSING_SAMPLE
# ---------------------------------------------------------------------------

def test_missing_sample_returns_blocked():
    """Oracle must return BLOCKED_MISSING_SAMPLE when the sample file does not exist.

    A missing sample is not a FAIL — it is a coverage gap that must be
    distinguished from a genuine product failure.
    """
    case = _make_csv_case(
        case_id="nc-004",
        authority_class="AUTHORITATIVE_REFERENCE_VECTOR",
        sample_ref="samples/by-format/csv/THIS_FILE_DOES_NOT_EXIST_9999.csv",
    )
    verdict = execute_csv_valid_case(case, _make_minimal_pkg())

    assert verdict["result"] == RESULT_BLOCKED_MISSING_SAMPLE, (
        f"Missing sample should yield BLOCKED_MISSING_SAMPLE, got {verdict['result']!r}"
    )


# ---------------------------------------------------------------------------
# Test 5 — Positive control: valid case with correct authority passes
# ---------------------------------------------------------------------------

def test_valid_case_with_correct_authority_passes():
    """Positive control: execute_csv_valid_case must return PASS for a well-formed case.

    Confirms the PASS path is reachable and that the negative controls above
    are not artifacts of a permanently-broken executor.
    """
    csv_sample = "samples/by-format/csv/minimal-2x2.csv"
    if not (REPO_ROOT / csv_sample).exists():
        pytest.skip("CSV sample not present")

    case = _make_csv_case(
        case_id="nc-005",
        authority_class="AUTHORITATIVE_REFERENCE_VECTOR",
        sample_ref=csv_sample,
        # No expected_model_properties → D0 (load-only), no property mismatch possible
    )
    verdict = execute_csv_valid_case(case, _make_minimal_pkg())

    assert verdict["result"] == RESULT_PASS, (
        f"Positive control should yield PASS, got {verdict['result']!r}. "
        f"Diagnostics: {verdict.get('diagnostics')}"
    )
