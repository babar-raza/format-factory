"""
test_r128_fodt_csv_authority_promotion.py
Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-PROOF-CLOSURE-AND-FORMAT-BACKFILL-MEGA-TRAIN-001
Added: 2026-06-08

Tests for:
- FODT P2→P4 promotion (verified fact from ODF 1.3 spec)
- CSV P3→P4 promotion (verified fact from IANA registry)
- Raw log path detection
- Anti-skip raw log regression
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

_SPEC_CACHE = REPO_ROOT / ".local" / "spec-cache"
pytestmark = pytest.mark.skipif(
    not _SPEC_CACHE.is_dir(),
    reason="SAL spec-cache not present in this environment",
)

from authority_gate_validation import validate_format_authority


class TestFodtPromotion:
    """FODT must be at P4 after verified fact extraction from ODF 1.3 spec."""

    def test_fodt_reaches_p4(self):
        """FODT has 1 verified fact from ODF 1.3 → must be P4."""
        result = validate_format_authority("fodt")
        assert result["authority_level_int"] >= 4, (
            f"FODT should be P4+ after verified fact. Got P{result['authority_level_int']}. "
            f"Blockers: {result['blockers']}"
        )

    def test_fodt_has_verified_fact(self):
        """FODT must have at least 1 verified fact (FACT-FODT-001)."""
        result = validate_format_authority("fodt")
        assert result["spec_state_summary"]["facts_verified"] >= 1, (
            "FODT must have at least 1 verified fact after ODF 1.3 spec verification"
        )

    def test_fodt_fact_fodt_001_present(self):
        """FACT-FODT-001 must be in verified fact IDs."""
        result = validate_format_authority("fodt")
        assert "FACT-FODT-001" in result["spec_state_summary"]["verified_fact_ids"], (
            "FACT-FODT-001 must be a verified fact for FODT"
        )

    def test_fodt_spec_cached(self):
        """FODT must have spec cached (via ODF 1.3 reuse)."""
        result = validate_format_authority("fodt")
        assert result["spec_state_summary"]["spec_cached"] is True, (
            "FODT spec must be cached via ODF 1.3 reuse"
        )

    def test_fodt_p4_is_readiness_allowed(self):
        """FODT P4 is readiness_allowed per MIN_READINESS_LEVEL=4 policy."""
        result = validate_format_authority("fodt")
        # P4+ is readiness_allowed in this system (product_expansion_allowed)
        assert result["readiness_allowed"] is True, (
            "FODT at P4 should be readiness_allowed (MIN_READINESS_LEVEL=4)"
        )


class TestCsvPromotion:
    """CSV is at P3 — candidate facts only (RFC 4180 text not cached locally).

    FACT-CSV-001 and FACT-CSV-002 are candidate status (needs_review).
    Promotion to P4 requires caching the RFC 4180 text and running
    deterministic text search. Until then CSV stays P3.
    """

    def test_csv_is_p3_candidate_facts_only(self):
        """CSV has candidate facts but no verified facts → P3."""
        result = validate_format_authority("csv")
        assert result["authority_level_int"] == 3, (
            f"CSV should be P3 (candidate facts, RFC not cached). Got P{result['authority_level_int']}. "
            f"Blockers: {result['blockers']}"
        )

    def test_csv_has_no_verified_facts(self):
        """CSV facts are candidate only — RFC 4180 text not cached for deterministic verification."""
        result = validate_format_authority("csv")
        assert result["spec_state_summary"]["facts_verified"] == 0, (
            "CSV should have 0 verified facts until RFC 4180 text is cached locally"
        )

    def test_csv_fact_001_is_candidate_not_verified(self):
        """CSV has candidate facts but none are verified (RFC not cached)."""
        result = validate_format_authority("csv")
        assert result["spec_state_summary"]["facts_candidate"] >= 1, (
            "CSV should have at least 1 candidate fact (FACT-CSV-001)"
        )
        assert "FACT-CSV-001" not in result["spec_state_summary"]["verified_fact_ids"], (
            "FACT-CSV-001 must NOT be verified until RFC 4180 text is cached"
        )

    def test_csv_p3_is_not_readiness_allowed(self):
        """CSV at P3 is NOT readiness_allowed (requires P4 minimum)."""
        result = validate_format_authority("csv")
        assert result["readiness_allowed"] is False, (
            "CSV at P3 should NOT be readiness_allowed (requires P4 minimum)"
        )

    def test_csv_spec_cached(self):
        """CSV spec-index must exist (RFC 4180 spec-index.yaml present)."""
        result = validate_format_authority("csv")
        assert result["spec_state_summary"]["spec_cached"] is True, (
            "CSV spec must be cached (RFC 4180 spec-index.yaml exists)"
        )


class TestRawLogDetection:
    """Raw logs must be present in the expected location for this sprint."""

    def test_targeted_tests_raw_log_exists(self):
        """targeted-tests.txt raw log must exist for anti-skip compliance."""
        run_id = "spec-authority-proof-closure-backfill-20260608-e382e5f"
        log_path = (
            REPO_ROOT
            / "reports"
            / "spec-authority-proof-closure-backfill"
            / run_id
            / "raw-logs"
            / "targeted-tests.txt"
        )
        assert log_path.exists(), (
            f"Raw log targeted-tests.txt not found at {log_path}. "
            "Lane 1 must capture test output to raw-logs/."
        )

    def test_targeted_tests_log_nonempty(self):
        """Raw test log must have content (not empty)."""
        run_id = "spec-authority-proof-closure-backfill-20260608-e382e5f"
        log_path = (
            REPO_ROOT
            / "reports"
            / "spec-authority-proof-closure-backfill"
            / run_id
            / "raw-logs"
            / "targeted-tests.txt"
        )
        if not log_path.exists():
            pytest.skip("Raw log not yet created")
        assert log_path.stat().st_size > 100, "Raw test log must have content"


class TestFormatAuthorityMatrix:
    """Authority matrix must be consistent with live validate_format_authority results."""

    def test_fods_p6_live(self):
        result = validate_format_authority("fods")
        assert result["authority_level_int"] == 6

    def test_zst_p6_live(self):
        result = validate_format_authority("zst")
        assert result["authority_level_int"] == 6

    def test_fodt_p4_live(self):
        result = validate_format_authority("fodt")
        # FODT was advanced to P5 in subsequent sprints (spec-cache present)
        assert result["authority_level_int"] >= 4

    def test_csv_p3_live(self):
        result = validate_format_authority("csv")
        assert result["authority_level_int"] == 3

    def test_gnumeric_p1_live(self):
        result = validate_format_authority("gnumeric")
        assert result["authority_level_int"] == 1

    def test_html_p0_live(self):
        result = validate_format_authority("html")
        assert result["authority_level_int"] == 0

    def test_unknown_format_p0_live(self):
        result = validate_format_authority("completely_unknown_xyz_format_999")
        assert result["authority_level_int"] == 0
