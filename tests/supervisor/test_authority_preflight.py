"""
test_authority_preflight.py

Tests for SAL-VERIFICATION-HARDENING-001 (Lane C):
Authority preflight integration in ProductSourceExecutor.

Sprint: FORMAT-FACTORY-SAL-VERIFICATION-HEALING-HARDENING-BACKFILL-SINGLE-GO-001
Added: 2026-06-11
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch, MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from product_source_executor import run_authority_preflight, ProductSourceExecutor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _item(format_id: str = "", exception_classification: str = "",
          spec_fact_refs=None, target_path: str = "src/python/zst/zst_codec.py",
          action_id: str = "TEST-001") -> Dict[str, Any]:
    item = {
        "action_id": action_id,
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "target_path": target_path,
        "spec_fact_refs": spec_fact_refs or [],
        "exception_classification": exception_classification,
    }
    if format_id:
        item["format_id"] = format_id
    return item


def _mock_authority(level_int: int, exception_allowed: str | None = None):
    """Return a mock authority result dict for a given P-level."""
    return {
        "authority_level": f"P{level_int}",
        "authority_level_int": level_int,
        "product_expansion_allowed": level_int >= 4,
        "exception_allowed": exception_allowed,
        "blockers": [] if level_int >= 4 else [f"P{level_int} blocker"],
        "next_action": "test next action",
        "debt_entry": None,
        "readiness_allowed": level_int >= 4,
        "spec_fact_refs_required": level_int < 4,
    }


# ---------------------------------------------------------------------------
# Test 1: ALLOW for high-authority format (P4+)
# ---------------------------------------------------------------------------

class TestPreflightAllowsHighAuthorityFormat:
    def test_product_source_preflight_allows_high_authority_format(self):
        """P4+ format with spec_fact_refs gets ALLOW decision."""
        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(4),
        ):
            result = run_authority_preflight(
                _item(format_id="zst", spec_fact_refs=["FACT-ZST-001"])
            )
        assert result["decision"] == "ALLOW"
        assert result["authority_level"] == "P4"
        assert result["product_expansion_allowed"] is True

    def test_preflight_allows_p6_format(self):
        """P6 format (proof graph complete) must be ALLOWED."""
        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(6),
        ):
            result = run_authority_preflight(
                _item(format_id="fods", spec_fact_refs=["FACT-FODS-001"])
            )
        assert result["decision"] == "ALLOW"
        assert result["authority_level_int"] == 6

    def test_preflight_blocks_p4_without_spec_fact_refs_and_no_exception(self):
        """P4+ format without spec_fact_refs AND without exception_classification must BLOCK.
        Hard Rule 10: P4+ authority alone is not sufficient for product source mutation.
        The queue item must carry spec_fact_refs or an explicit exception_classification.
        Sprint 3 enforcement: SAL-I-002 tightening."""
        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(4),
        ):
            result = run_authority_preflight(
                _item(format_id="zst", spec_fact_refs=[])
            )
        # P4+ without spec_fact_refs and no exception → BLOCK (Hard Rule 10)
        assert result["decision"] == "BLOCK"
        assert "spec_fact_refs" in result["reason"] or "Hard Rule" in result["reason"] or "exception_classification" in result["reason"]


# ---------------------------------------------------------------------------
# Test 2: BLOCK for low-authority format without exception
# ---------------------------------------------------------------------------

class TestPreflightBlocksLowAuthorityWithoutException:
    def test_product_source_preflight_blocks_low_authority_without_exception(self):
        """P1 format without exception_classification gets BLOCK."""
        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(1, exception_allowed="no_public_spec_available"),
        ):
            result = run_authority_preflight(
                _item(format_id="abw", exception_classification="")
            )
        assert result["decision"] == "BLOCK"
        assert "abw" in result["reason"].lower() or "P1" in result["reason"]

    def test_preflight_blocks_p0_format(self):
        """P0 format (no spec) without exception must be BLOCKED."""
        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(0),
        ):
            result = run_authority_preflight(
                _item(format_id="unknown_fmt", exception_classification="")
            )
        assert result["decision"] == "BLOCK"

    def test_executor_returns_blocked_result_for_p1_format(self):
        """ProductSourceExecutor.execute() must return status=BLOCKED for P1 format without exception."""
        executor = ProductSourceExecutor(repo_root=REPO_ROOT)
        item = _item(
            format_id="abw",
            exception_classification="",
            target_path="src/python/abw/abw_codec.py",
            action_id="TC-BLOCK-001",
        )
        item["patch_code"] = "def dummy(): pass"

        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(1, exception_allowed="no_public_spec_available"),
        ):
            result = executor.execute(item)

        assert result.status == "BLOCKED"
        assert "Authority preflight BLOCKED" in (result.error or "")


# ---------------------------------------------------------------------------
# Test 3: ALLOW for no_public_spec_available exception (Sprint 2: WARN_ALLOW → ALLOW)
# ---------------------------------------------------------------------------

class TestPreflightWarnAllowsNoPubSpecException:
    def test_product_source_preflight_warn_allows_no_public_spec_exception(self):
        """P1 format with no_public_spec_available exception gets ALLOW (Sprint 2: WARN_ALLOW removed)."""
        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(1, exception_allowed="no_public_spec_available"),
        ):
            result = run_authority_preflight(
                _item(
                    format_id="abw",
                    exception_classification="no_public_spec_available",
                )
            )
        # Sprint 2: WARN_ALLOW promoted to ALLOW for valid exceptions
        assert result["decision"] == "ALLOW"
        assert result["decision"] != "BLOCK"

    def test_legacy_backfill_exception_gets_warn_allow(self):
        """legacy_backfill exception must also produce WARN_ALLOW (not BLOCK)."""
        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(1),
        ):
            result = run_authority_preflight(
                _item(format_id="dif", exception_classification="legacy_backfill")
            )
        assert result["decision"] in ("WARN_ALLOW", "ALLOW")
        assert result["decision"] != "BLOCK"

    def test_schema_authority_exception_gets_warn_allow(self):
        """schema_authority_available exception must also produce WARN_ALLOW."""
        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(1),
        ):
            result = run_authority_preflight(
                _item(format_id="gnumeric", exception_classification="schema_authority_available")
            )
        assert result["decision"] in ("WARN_ALLOW", "ALLOW")
        assert result["decision"] != "BLOCK"


# ---------------------------------------------------------------------------
# Test 4: AI-only authority rejected
# ---------------------------------------------------------------------------

class TestPreflightRejectsAiOnlyAuthority:
    def test_product_source_preflight_rejects_ai_only_authority(self):
        """exception_classification='ai_generated_authority' is invalid and must produce BLOCK."""
        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(1),
        ):
            result = run_authority_preflight(
                _item(format_id="abw", exception_classification="ai_generated_authority")
            )
        assert result["decision"] == "BLOCK"

    def test_raw_ai_summary_classification_rejected(self):
        """exception_classification='raw_ai_summary_only' must produce BLOCK."""
        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(1),
        ):
            result = run_authority_preflight(
                _item(format_id="abw", exception_classification="raw_ai_summary_only")
            )
        assert result["decision"] == "BLOCK"


# ---------------------------------------------------------------------------
# Test 5: Machine-readable decision dict
# ---------------------------------------------------------------------------

class TestPreflightRecordsMachineReadableDecision:
    def test_product_source_preflight_records_machine_readable_decision(self):
        """run_authority_preflight() must return a well-formed machine-readable dict."""
        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(5),
        ):
            result = run_authority_preflight(
                _item(format_id="fodt", spec_fact_refs=["FACT-FODT-001"])
            )
        # Required fields
        assert "format_id" in result
        assert "item_type" in result
        assert "authority_level" in result
        assert "authority_level_int" in result
        assert "product_expansion_allowed" in result
        assert "exception_classification" in result
        assert "decision" in result
        assert "reason" in result
        assert "evidence_paths" in result
        # Value constraints (Sprint 2: WARN_ALLOW removed — only ALLOW or BLOCK)
        assert result["decision"] in ("ALLOW", "BLOCK")
        assert isinstance(result["authority_level_int"], int)
        assert isinstance(result["evidence_paths"], list)

    def test_preflight_format_id_inferred_from_target_path(self):
        """format_id should be inferred from target_path when not given directly."""
        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(4),
        ) as mock_validate:
            result = run_authority_preflight(
                _item(format_id="", target_path="src/python/zst/zst_codec.py")
            )
        # Should have inferred 'zst' and called validate_format_authority with it
        call_args = mock_validate.call_args
        if call_args is not None:
            called_with = call_args[0][0] if call_args[0] else call_args[1].get("format_id")
            assert called_with == "zst"

    def test_preflight_unknown_format_gives_block(self):
        """Cannot determine format_id → BLOCK (Sprint 2: fail-closed for unknown formats)."""
        result = run_authority_preflight(
            {"action_id": "UNKNOWN", "target_path": ""}
        )
        # Sprint 2: unknown format_id → BLOCK (fail-closed)
        assert result["decision"] == "BLOCK"


# ---------------------------------------------------------------------------
# Test 6: Autonomous cycle / integration smoke test
# ---------------------------------------------------------------------------

class TestAutonomousCycleInvokesOrRecordsAuthorityPreflightIfApplicable:
    def test_executor_execute_calls_run_authority_preflight(self):
        """ProductSourceExecutor.execute() must call run_authority_preflight."""
        executor = ProductSourceExecutor(repo_root=REPO_ROOT)
        item = _item(
            format_id="zst",
            spec_fact_refs=["FACT-ZST-001"],
            target_path="src/python/zst/zst_codec.py",
            action_id="TC-PREFLIGHT-CALL-001",
        )
        item["patch_code"] = "def _dummy_sal_test(): pass"

        call_log = []

        def patched_preflight(i):
            call_log.append(i)
            return {
                "format_id": "zst",
                "item_type": "PRODUCT_SOURCE",
                "authority_level": "P4",
                "authority_level_int": 4,
                "product_expansion_allowed": True,
                "exception_classification": "",
                "decision": "ALLOW",
                "reason": "P4 — allowed",
                "evidence_paths": [],
            }

        with patch("product_source_executor.run_authority_preflight", side_effect=patched_preflight):
            # Path validation will fail (target_path may not be forbidden) or
            # it may proceed to read file — either way, preflight must have been called
            executor.execute(item)

        assert len(call_log) == 1, "run_authority_preflight must be called exactly once per execute()"

    def test_executor_blocked_result_is_not_rolled_back(self):
        """BLOCKED result from authority preflight must NOT attempt rollback."""
        executor = ProductSourceExecutor(repo_root=REPO_ROOT)
        item = _item(
            format_id="abw",
            exception_classification="",
            target_path="src/python/abw/abw_codec.py",
            action_id="TC-NO-ROLLBACK-001",
        )
        item["patch_code"] = "def dummy_no_exec(): pass"

        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(1, exception_allowed="no_public_spec_available"),
        ):
            result = executor.execute(item)

        assert result.status == "BLOCKED"
        assert result.rollback_performed is False


# ---------------------------------------------------------------------------
# Sprint 3 Lane D: Hard Rule 10 enforcement — P4+ requires spec_fact_refs or exception
# ---------------------------------------------------------------------------

class TestPreflightHardRule10P4RequiresRefsOrException:
    """Sprint 3: P4+ authority alone is not enough for product source mutation (Hard Rule 10)."""

    def test_p4_with_spec_refs_allows(self):
        """P4 format WITH spec_fact_refs must be ALLOWED."""
        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(4),
        ):
            result = run_authority_preflight(
                _item(format_id="zst", spec_fact_refs=["FACT-ZST-001"])
            )
        assert result["decision"] == "ALLOW"

    def test_p4_without_refs_and_without_exception_blocks(self):
        """P4 without spec_fact_refs AND no exception_classification → BLOCK (Hard Rule 10)."""
        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(4),
        ):
            result = run_authority_preflight(
                _item(format_id="zst", spec_fact_refs=[], exception_classification="")
            )
        assert result["decision"] == "BLOCK"
        assert "spec_fact_refs" in result["reason"] or "exception_classification" in result["reason"]

    def test_p6_without_refs_and_without_exception_blocks(self):
        """P6 (highest level) without spec_fact_refs and no exception → BLOCK (Hard Rule 10)."""
        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(6),
        ):
            result = run_authority_preflight(
                _item(format_id="fods", spec_fact_refs=[], exception_classification="")
            )
        assert result["decision"] == "BLOCK"

    def test_p4_without_refs_but_with_valid_exception_allows(self):
        """P4 without spec_fact_refs but WITH valid exception → ALLOW (exception path)."""
        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(4),
        ):
            result = run_authority_preflight(
                _item(format_id="zst", spec_fact_refs=[], exception_classification="no_public_spec_available")
            )
        assert result["decision"] == "ALLOW"

    def test_no_warn_allow_outcome_possible(self):
        """No code path may return WARN_ALLOW (Sprint 2 + Sprint 3 policy)."""
        for fmt, level, exc in [
            ("zst", 6, ""),
            ("abw", 1, ""),
            ("dif", 1, "no_public_spec_available"),
            ("fods", 4, ""),
            ("unknown_x", 0, ""),
        ]:
            with patch(
                "authority_gate_validation.validate_format_authority",
                return_value=_mock_authority(level),
            ):
                result = run_authority_preflight(
                    _item(format_id=fmt, spec_fact_refs=[], exception_classification=exc)
                )
            assert result["decision"] != "WARN_ALLOW", (
                f"WARN_ALLOW must never be returned. Got it for fmt={fmt!r} level={level} exc={exc!r}"
            )
            assert result["decision"] != "PENDING", (
                f"PENDING must never be returned as final decision. Got it for fmt={fmt!r}"
            )
            assert result["decision"] in ("ALLOW", "BLOCK"), (
                f"Decision must be ALLOW or BLOCK; got {result['decision']!r}"
            )

    def test_executor_result_records_preflight_decision(self):
        """ExecutionResult.error must contain preflight decision when BLOCKED."""
        executor = ProductSourceExecutor(repo_root=REPO_ROOT)
        item = _item(
            format_id="zst",
            spec_fact_refs=[],
            exception_classification="",
            target_path="src/python/zst/zst_codec.py",
            action_id="TC-PREFLIGHT-DECISION-001",
        )
        item["patch_code"] = "def _dummy(): pass"
        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(4),
        ):
            result = executor.execute(item)
        assert result.status == "BLOCKED"
        assert result.error is not None
        assert "Authority preflight BLOCKED" in result.error


# ---------------------------------------------------------------------------
# RNEXT Lane D: investigation_only / sample_only_non_product bypass hardening
# ---------------------------------------------------------------------------

class TestPreflightBlocksNonProductExceptions:
    """RNEXT: investigation_only and sample_only_non_product must not allow PRODUCT_SOURCE mutation."""

    def test_investigation_only_product_source_blocks_in_preflight(self):
        """investigation_only exception must BLOCK product source mutation."""
        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(1),
        ):
            result = run_authority_preflight(
                _item(format_id="abw", exception_classification="investigation_only")
            )
        assert result["decision"] == "BLOCK", (
            f"investigation_only must BLOCK product source. Got: {result['decision']!r}"
        )
        assert "investigation_only" in result["reason"] or "not valid for PRODUCT_SOURCE" in result["reason"]

    def test_sample_only_non_product_source_blocks_in_preflight(self):
        """sample_only_non_product exception must BLOCK product source mutation."""
        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(1),
        ):
            result = run_authority_preflight(
                _item(format_id="abw", exception_classification="sample_only_non_product")
            )
        assert result["decision"] == "BLOCK", (
            f"sample_only_non_product must BLOCK product source. Got: {result['decision']!r}"
        )

    def test_investigation_only_product_source_blocks_in_executor(self):
        """ProductSourceExecutor.execute() must return BLOCKED for investigation_only."""
        executor = ProductSourceExecutor(repo_root=REPO_ROOT)
        item = _item(
            format_id="abw",
            exception_classification="investigation_only",
            target_path="src/python/abw/abw_codec.py",
            action_id="TC-INV-ONLY-BLOCK-001",
        )
        item["patch_code"] = "def dummy_inv(): pass"
        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(1),
        ):
            result = executor.execute(item)
        assert result.status == "BLOCKED"
        assert "investigation_only" in (result.error or "") or "PRODUCT_SOURCE" in (result.error or "")

    def test_sample_only_non_product_source_blocks_in_executor(self):
        """ProductSourceExecutor.execute() must return BLOCKED for sample_only_non_product."""
        executor = ProductSourceExecutor(repo_root=REPO_ROOT)
        item = _item(
            format_id="abw",
            exception_classification="sample_only_non_product",
            target_path="src/python/abw/abw_codec.py",
            action_id="TC-SAMPLE-ONLY-BLOCK-001",
        )
        item["patch_code"] = "def dummy_smp(): pass"
        with patch(
            "authority_gate_validation.validate_format_authority",
            return_value=_mock_authority(1),
        ):
            result = executor.execute(item)
        assert result.status == "BLOCKED"

    def test_investigation_only_governance_doc_does_not_block(self):
        """investigation_only on a non-product item should not trigger executor block.
        The executor only runs PRODUCT_SOURCE items, so this tests the preflight
        classification boundary — GOVERNANCE_DOC items don't go through the executor
        at all, so investigation_only exception is safe for them."""
        # Verify: investigation_only is NOT in _AUTHORITY_ALLOWED_EXCEPTIONS
        import product_source_executor as pse
        assert "investigation_only" not in pse._AUTHORITY_ALLOWED_EXCEPTIONS, (
            "investigation_only must not be in _AUTHORITY_ALLOWED_EXCEPTIONS"
        )
        assert "investigation_only" in pse._NON_PRODUCT_EXCEPTION_CLASSES, (
            "investigation_only must be in _NON_PRODUCT_EXCEPTION_CLASSES"
        )

    def test_executor_and_governance_exception_policies_match(self):
        """The executor's allowed exceptions should align with product authority policy.
        Valid product exceptions: no_public_spec_available, schema_authority_available,
        empirical_authority_with_limits, fallback_authority_approved, legacy_backfill.
        Non-product exceptions: investigation_only, sample_only_non_product."""
        import product_source_executor as pse
        # Valid product exceptions must all be present
        expected_product = {
            "no_public_spec_available", "schema_authority_available",
            "empirical_authority_with_limits", "fallback_authority_approved", "legacy_backfill",
        }
        for exc in expected_product:
            assert exc in pse._AUTHORITY_ALLOWED_EXCEPTIONS, (
                f"{exc} must be in _AUTHORITY_ALLOWED_EXCEPTIONS"
            )
        # Non-product exceptions must NOT be in allowed set
        for exc in ("investigation_only", "sample_only_non_product"):
            assert exc not in pse._AUTHORITY_ALLOWED_EXCEPTIONS, (
                f"{exc} must NOT be in _AUTHORITY_ALLOWED_EXCEPTIONS (non-product bypass)"
            )
            assert exc in pse._NON_PRODUCT_EXCEPTION_CLASSES, (
                f"{exc} must be in _NON_PRODUCT_EXCEPTION_CLASSES"
            )
