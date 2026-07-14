"""Tests for SAL authority class enforcement in oracle execution (TC-GFB-024-01, FF-MR-2026-001).

Requirements: REQ-TEST-002 — Negative control: invalid SAL authority blocks oracle pass.

Tests check_authority(case, result_pass_candidate) from tools/oracle/execute_oracle.py.
Signature: (case: dict, result_pass_candidate: bool) -> tuple[str | None, str]
Returns (RESULT_BLOCKED_MISSING_AUTHORITY, auth_class) if blocking + would-be-PASS.
Returns (None, auth_class) if authority is valid OR result would not be PASS.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "oracle"))


class TestSALAuthorityEnforcement:
    """SAL authority class must gate oracle case execution."""

    def test_ai_draft_unverified_blocks_when_pass_candidate(self) -> None:
        """AI_DRAFT_UNVERIFIED must block when the result would be PASS."""
        from execute_oracle import check_authority, RESULT_BLOCKED_MISSING_AUTHORITY

        case = {
            "case_id": "test-ai-draft-001",
            "authority_class": "AI_DRAFT_UNVERIFIED",
        }
        status, auth_class = check_authority(case, result_pass_candidate=True)
        assert status == RESULT_BLOCKED_MISSING_AUTHORITY, (
            f"AI_DRAFT_UNVERIFIED must produce BLOCKED_MISSING_AUTHORITY when pass candidate, got: {status}"
        )
        assert auth_class == "AI_DRAFT_UNVERIFIED"

    def test_unknown_authority_blocks_when_pass_candidate(self) -> None:
        """UNKNOWN authority must block when result would be PASS."""
        from execute_oracle import check_authority, RESULT_BLOCKED_MISSING_AUTHORITY

        case = {"case_id": "test-unknown-001", "authority_class": "UNKNOWN"}
        status, _ = check_authority(case, result_pass_candidate=True)
        assert status == RESULT_BLOCKED_MISSING_AUTHORITY, (
            f"UNKNOWN authority must produce BLOCKED_MISSING_AUTHORITY when pass candidate, got: {status}"
        )

    def test_rejected_authority_blocks_when_pass_candidate(self) -> None:
        """REJECTED authority must block when result would be PASS."""
        from execute_oracle import check_authority, RESULT_BLOCKED_MISSING_AUTHORITY

        case = {"case_id": "test-rejected-001", "authority_class": "REJECTED"}
        status, _ = check_authority(case, result_pass_candidate=True)
        assert status == RESULT_BLOCKED_MISSING_AUTHORITY, (
            f"REJECTED authority must produce BLOCKED_MISSING_AUTHORITY, got: {status}"
        )

    def test_spec_normative_is_not_blocked(self) -> None:
        """SPEC_NORMATIVE authority must NOT be blocked by authority check."""
        from execute_oracle import check_authority, RESULT_BLOCKED_MISSING_AUTHORITY

        case = {"case_id": "test-spec-normative-001", "authority_class": "SPEC_NORMATIVE"}
        status, auth_class = check_authority(case, result_pass_candidate=True)
        assert status != RESULT_BLOCKED_MISSING_AUTHORITY, (
            f"SPEC_NORMATIVE must not be blocked, got: {status}"
        )
        assert status is None, f"SPEC_NORMATIVE should return None status: {status}"

    def test_spec_informative_is_not_blocked(self) -> None:
        """SPEC_INFORMATIVE authority must NOT be blocked."""
        from execute_oracle import check_authority, RESULT_BLOCKED_MISSING_AUTHORITY

        case = {"case_id": "test-spec-informative-001", "authority_class": "SPEC_INFORMATIVE"}
        status, _ = check_authority(case, result_pass_candidate=True)
        assert status != RESULT_BLOCKED_MISSING_AUTHORITY, (
            f"SPEC_INFORMATIVE must not be blocked, got: {status}"
        )

    def test_blocking_classes_constant_contains_required(self) -> None:
        """BLOCKING_AUTHORITY_CLASSES must include required blocking classes."""
        from execute_oracle import BLOCKING_AUTHORITY_CLASSES

        required = {"AI_DRAFT_UNVERIFIED", "IMPLEMENTATION_OBSERVED", "UNKNOWN", "REJECTED"}
        missing = required - BLOCKING_AUTHORITY_CLASSES
        assert not missing, (
            f"BLOCKING_AUTHORITY_CLASSES is missing required entries: {missing}"
        )

    def test_ai_draft_does_not_block_fail_candidate(self) -> None:
        """AI_DRAFT_UNVERIFIED must NOT block when the result would NOT be PASS."""
        from execute_oracle import check_authority, RESULT_BLOCKED_MISSING_AUTHORITY

        case = {"case_id": "test-ai-draft-fail-002", "authority_class": "AI_DRAFT_UNVERIFIED"}
        status, _ = check_authority(case, result_pass_candidate=False)
        # When pass_candidate=False, authority blocking does not apply
        assert status != RESULT_BLOCKED_MISSING_AUTHORITY, (
            f"Authority should not block a FAIL candidate: {status}"
        )
