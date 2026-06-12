"""
test_queue_dispatch_authority_pilot.py

Lane L: Real queue dispatch pilot — proves ProductSourceExecutor.execute() respects
authority preflight when called via the standard dispatch path.

Sprint: FORMAT-FACTORY-SAL-INTEGRATION-HARDENING-SPRINT-2
Added: 2026-06-11

Gap closed: GAP-02 (integration proof — beyond unit tests of run_authority_preflight alone)
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch, MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from product_source_executor import ProductSourceExecutor, run_authority_preflight


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _queue_item(
    format_id: str,
    exception_classification: str = "",
    spec_fact_refs=None,
    target_path: str = "src/python/zst/zst_codec.py",
    action_id: str = "PILOT-001",
) -> Dict[str, Any]:
    item: Dict[str, Any] = {
        "action_id": action_id,
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "format_id": format_id,
        "target_path": target_path,
        "spec_fact_refs": spec_fact_refs or [],
    }
    if exception_classification:
        item["exception_classification"] = exception_classification
    return item


def _mock_auth(level_int: int, exception_allowed=None) -> Dict[str, Any]:
    return {
        "authority_level": f"P{level_int}",
        "authority_level_int": level_int,
        "product_expansion_allowed": level_int >= 4,
        "exception_allowed": exception_allowed,
        "readiness_allowed": level_int >= 4,
    }


# ---------------------------------------------------------------------------
# Test 1: High-authority format proceeds past preflight
# ---------------------------------------------------------------------------

class TestDispatchHighAuthorityFormatProceeds:
    """ZST (P4+) passes authority preflight and execution continues to later steps."""

    def test_dispatch_high_authority_format_proceeds(self):
        """ZST at P4 with valid spec_fact_refs passes preflight; executor continues to later steps.
        Sprint 3 (Hard Rule 10): spec_fact_refs required even for P4+ formats."""
        executor = ProductSourceExecutor()
        # Hard Rule 10: must include spec_fact_refs for P4+ dispatch to pass preflight
        item = _queue_item(
            format_id="zst",
            target_path="src/python/zst/zst_codec.py",
            spec_fact_refs=["FACT-ZST-001"],
        )

        with patch("authority_gate_validation.validate_format_authority",
                   return_value=_mock_auth(4)):
            result = executor.execute(item)

        # May be BLOCKED for other reasons (no patch_code), but NOT by authority preflight
        assert "Authority preflight BLOCKED" not in (result.error or ""), (
            f"ZST P4 with spec_fact_refs should not be blocked by authority preflight. "
            f"Got: {result.error}"
        )

    def test_dispatch_p6_format_never_blocked_by_preflight(self):
        """FODS at P6 with valid spec_fact_refs is never blocked by preflight.
        Sprint 3 (Hard Rule 10): spec_fact_refs required even for P6 formats."""
        executor = ProductSourceExecutor()
        # Hard Rule 10: spec_fact_refs required for P4+ — no silent authority bypass
        item = _queue_item(
            format_id="fods",
            target_path="src/python/fods/writer.py",
            spec_fact_refs=["FACT-FODS-001"],
        )

        with patch("authority_gate_validation.validate_format_authority",
                   return_value=_mock_auth(6)):
            result = executor.execute(item)

        assert "Authority preflight BLOCKED" not in (result.error or ""), (
            f"FODS P6 with spec_fact_refs should not be blocked by authority preflight. "
            f"Got: {result.error}"
        )


# ---------------------------------------------------------------------------
# Test 2: Low-authority format blocked without exception
# ---------------------------------------------------------------------------

class TestDispatchLowAuthorityFormatBlockedWithoutException:
    """ABW (P1) is blocked unless a valid exception_classification is provided."""

    def test_dispatch_low_authority_format_blocked_without_exception(self):
        """ABW at P1 without exception_classification → ExecutionResult BLOCKED."""
        executor = ProductSourceExecutor()
        item = _queue_item(format_id="abw", target_path="src/python/abw/abw_codec.py")

        with patch("authority_gate_validation.validate_format_authority",
                   return_value=_mock_auth(1)):
            result = executor.execute(item)

        assert result.status == "BLOCKED", (
            f"ABW P1 without exception should be BLOCKED. Got status={result.status}"
        )
        assert "Authority preflight BLOCKED" in (result.error or ""), (
            f"BLOCKED error should mention authority preflight. Got: {result.error}"
        )

    def test_dispatch_p0_format_always_blocked(self):
        """P0 format without exception is always blocked by preflight."""
        executor = ProductSourceExecutor()
        item = _queue_item(format_id="unknown_format", target_path="src/python/html/html_codec.py")

        with patch("authority_gate_validation.validate_format_authority",
                   return_value=_mock_auth(0)):
            result = executor.execute(item)

        assert result.status == "BLOCKED", (
            f"P0 format should be BLOCKED by authority preflight. Got: {result.status}"
        )
        assert "Authority preflight BLOCKED" in (result.error or ""), (
            f"BLOCKED error should cite authority preflight. Got: {result.error}"
        )


# ---------------------------------------------------------------------------
# Test 3: Low-authority format allowed with valid exception
# ---------------------------------------------------------------------------

class TestDispatchLowAuthorityFormatAllowedWithException:
    """ABW with no_public_spec_available passes preflight (WARN_ALLOW) and continues."""

    def test_dispatch_low_authority_format_allowed_with_exception(self):
        """ABW P1 + no_public_spec_available → not blocked by preflight."""
        executor = ProductSourceExecutor()
        item = _queue_item(
            format_id="abw",
            exception_classification="no_public_spec_available",
            target_path="src/python/abw/abw_codec.py",
        )

        with patch("authority_gate_validation.validate_format_authority",
                   return_value=_mock_auth(1)):
            result = executor.execute(item)

        assert "Authority preflight BLOCKED" not in (result.error or ""), (
            f"ABW with no_public_spec_available should not be blocked by authority preflight. "
            f"Got: {result.error}"
        )

    def test_dispatch_legacy_backfill_exception_allows_preflight(self):
        """legacy_backfill exception on P2 format passes authority preflight."""
        executor = ProductSourceExecutor()
        item = _queue_item(
            format_id="gnumeric",
            exception_classification="legacy_backfill",
            target_path="src/python/gnumeric/gnumeric_codec.py",
        )

        with patch("authority_gate_validation.validate_format_authority",
                   return_value=_mock_auth(2)):
            result = executor.execute(item)

        assert "Authority preflight BLOCKED" not in (result.error or ""), (
            f"legacy_backfill exception should pass preflight. Got: {result.error}"
        )


# ---------------------------------------------------------------------------
# Test 4: ExecutionResult.error contains format_id and authority_level
# ---------------------------------------------------------------------------

class TestPreflightResultInExecutionResult:
    """BLOCKED ExecutionResult.error must include format_id and authority level."""

    def test_preflight_result_in_execution_result_error(self):
        """Blocked result error must contain format_id and authority level."""
        executor = ProductSourceExecutor()
        item = _queue_item(format_id="sylk", target_path="src/python/sylk/sylk_parser.py")

        with patch("authority_gate_validation.validate_format_authority",
                   return_value=_mock_auth(1)):
            result = executor.execute(item)

        assert result.status == "BLOCKED"
        assert "sylk" in (result.error or "").lower(), (
            f"Error should mention format_id 'sylk'. Got: {result.error}"
        )
        assert "P1" in (result.error or ""), (
            f"Error should mention authority level P1. Got: {result.error}"
        )


# ---------------------------------------------------------------------------
# Sprint 3 Lane G: Extended positive/negative/exception dispatch pilots
# ---------------------------------------------------------------------------

class TestDispatchPositivePilots:
    """Sprint 3: positive pilots with spec_fact_refs for ZST, FODS, PBM."""

    def test_zst_with_spec_refs_dispatches(self):
        """ZST P4 + FACT-ZST-001 → ALLOW, not blocked by authority preflight."""
        executor = ProductSourceExecutor()
        item = _queue_item("zst", target_path="src/python/zst/zst_codec.py",
                           spec_fact_refs=["FACT-ZST-001"])
        with patch("authority_gate_validation.validate_format_authority",
                   return_value=_mock_auth(4)):
            result = executor.execute(item)
        assert "Authority preflight BLOCKED" not in (result.error or "")

    def test_fods_with_spec_refs_dispatches(self):
        """FODS P6 + FACT-FODS-001 → ALLOW."""
        executor = ProductSourceExecutor()
        item = _queue_item("fods", target_path="src/python/fods/writer.py",
                           spec_fact_refs=["FACT-FODS-001"])
        with patch("authority_gate_validation.validate_format_authority",
                   return_value=_mock_auth(6)):
            result = executor.execute(item)
        assert "Authority preflight BLOCKED" not in (result.error or "")

    def test_pbm_with_spec_refs_dispatches(self):
        """PBM P4 + FACT-PBM-001 → ALLOW."""
        executor = ProductSourceExecutor()
        item = _queue_item("pbm", target_path="src/python/pbm/pbm_parser.py",
                           spec_fact_refs=["FACT-PBM-001"])
        with patch("authority_gate_validation.validate_format_authority",
                   return_value=_mock_auth(4)):
            result = executor.execute(item)
        assert "Authority preflight BLOCKED" not in (result.error or "")


class TestDispatchNegativePilots:
    """Sprint 3: negative pilots that must BLOCK."""

    def test_abw_without_refs_or_exception_blocked(self):
        """ABW P1 + no spec_fact_refs + no exception → BLOCK."""
        executor = ProductSourceExecutor()
        item = _queue_item("abw", target_path="src/python/abw/abw_codec.py")
        with patch("authority_gate_validation.validate_format_authority",
                   return_value=_mock_auth(1)):
            result = executor.execute(item)
        assert result.status == "BLOCKED"

    def test_fods_without_refs_or_exception_blocked(self):
        """FODS P6 + no spec_fact_refs + no exception → BLOCK (Hard Rule 10)."""
        executor = ProductSourceExecutor()
        item = _queue_item("fods", target_path="src/python/fods/writer.py")
        with patch("authority_gate_validation.validate_format_authority",
                   return_value=_mock_auth(6)):
            result = executor.execute(item)
        assert result.status == "BLOCKED"
        assert "Authority preflight BLOCKED" in (result.error or "")

    def test_ai_only_authority_blocked(self):
        """Item with ai_generated_authority exception_classification → BLOCK."""
        executor = ProductSourceExecutor()
        item = _queue_item("abw", target_path="src/python/abw/abw_codec.py",
                           exception_classification="ai_generated_authority")
        with patch("authority_gate_validation.validate_format_authority",
                   return_value=_mock_auth(1)):
            result = executor.execute(item)
        assert result.status == "BLOCKED"

    def test_fallback_authority_without_rationale_blocked(self):
        """fallback_authority_approved without exception_rationale → BLOCK."""
        executor = ProductSourceExecutor()
        item = _queue_item("abw", target_path="src/python/abw/abw_codec.py",
                           exception_classification="fallback_authority_approved")
        item["exception_rationale"] = ""
        with patch("authority_gate_validation.validate_format_authority",
                   return_value=_mock_auth(1)):
            result = executor.execute(item)
        assert result.status == "BLOCKED"


class TestDispatchExceptionPositivePilots:
    """Sprint 3: exception positive cases — ABW and DIF with valid exceptions."""

    def test_abw_with_no_public_spec_exception_allowed(self):
        """ABW P1 + no_public_spec_available → ALLOW (exception positive)."""
        executor = ProductSourceExecutor()
        item = _queue_item("abw", target_path="src/python/abw/abw_codec.py",
                           exception_classification="no_public_spec_available")
        with patch("authority_gate_validation.validate_format_authority",
                   return_value=_mock_auth(1)):
            result = executor.execute(item)
        assert "Authority preflight BLOCKED" not in (result.error or "")

    def test_dif_with_empirical_authority_exception_allowed(self):
        """DIF + empirical_authority_with_limits → ALLOW (exception positive)."""
        executor = ProductSourceExecutor()
        item = _queue_item("dif", target_path="src/python/dif/dif_parser.py",
                           exception_classification="empirical_authority_with_limits")
        with patch("authority_gate_validation.validate_format_authority",
                   return_value=_mock_auth(1)):
            result = executor.execute(item)
        assert "Authority preflight BLOCKED" not in (result.error or "")
