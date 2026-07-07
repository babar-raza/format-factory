"""
test_ai_acceleration_guard.py
Sprint: SPEC-AUTHORITY-LAYER-FAST-OPS-INTEGRATION-AND-AUTHORITY-CONVEYOR-001
Added: 2026-06-08

Tests for AI acceleration guard in validate_spec_fact_refs.py (Lane 6).

Stop gate: AI output cannot mark itself verified.
"""
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))
_SPEC_CACHE = _REPO_ROOT / ".local" / "spec-cache"

from validate_spec_fact_refs import (
    validate_ai_fact_guard,
    validate_spec_cache_ai_guard,
    _AI_EXTRACTION_METHODS,
    _INDEPENDENT_VERIFICATION_METHODS,
)


def _make_fact(
    claim_id: str = "FACT-TEST-001",
    extraction_method: str = "tier1_direct_citation",
    verification_status: str = "verified",
    validated_by: str = "independent_agent_verifier",
) -> dict:
    return {
        "claim_id": claim_id,
        "claim": "test claim",
        "provenance": {
            "extraction_method": extraction_method,
            "verification_status": verification_status,
            "validated_by": validated_by,
        },
    }


# ============================================================
# Core guard logic tests
# ============================================================


class TestAiFactGuardCore:
    """Core tests for validate_ai_fact_guard()."""

    def test_empty_facts_list_is_compliant(self):
        """Empty fact list has no violations."""
        result = validate_ai_fact_guard([])
        assert result["compliant"]
        assert result["violations"] == []
        assert result["total_facts"] == 0

    def test_deterministic_extraction_verified_is_compliant(self):
        """Fact with deterministic extraction + independent verification is compliant."""
        facts = [_make_fact(
            extraction_method="tier1_direct_citation",
            verification_status="verified",
            validated_by="independent_agent_verifier",
        )]
        result = validate_ai_fact_guard(facts)
        assert result["compliant"]
        assert result["violations"] == []

    def test_ai_suggested_candidate_is_compliant(self):
        """AI-suggested fact with needs_review status is compliant (correct behavior)."""
        facts = [_make_fact(
            extraction_method="ai_suggested",
            verification_status="needs_review",
            validated_by="",
        )]
        result = validate_ai_fact_guard(facts)
        assert result["compliant"]
        assert result["ai_suggested_count"] == 1
        assert result["ai_self_verified_count"] == 0

    def test_ai_suggested_self_verified_is_violation(self):
        """AI-suggested fact claiming 'verified' without independent check → violation."""
        facts = [_make_fact(
            extraction_method="ai_suggested",
            verification_status="verified",
            validated_by="",  # no independent validator
        )]
        result = validate_ai_fact_guard(facts)
        assert not result["compliant"]
        assert len(result["violations"]) == 1
        assert result["ai_self_verified_count"] == 1
        v = result["violations"][0]
        assert "cannot self-certify" in v["issue"]
        assert v["extraction_method"] == "ai_suggested"

    def test_llm_extraction_self_verified_is_violation(self):
        """LLM extraction method + verified status → violation."""
        facts = [_make_fact(
            extraction_method="llm_extraction",
            verification_status="verified",
            validated_by="",
        )]
        result = validate_ai_fact_guard(facts)
        assert not result["compliant"]
        assert len(result["violations"]) == 1

    def test_ai_suggested_with_independent_verifier_is_compliant(self):
        """AI-suggested fact that was then independently verified → compliant."""
        facts = [_make_fact(
            extraction_method="ai_suggested",
            verification_status="verified",
            validated_by="independent_agent_verifier",
        )]
        result = validate_ai_fact_guard(facts)
        assert result["compliant"]
        assert result["violations"] == []

    def test_ai_suggested_with_deterministic_search_is_compliant(self):
        """AI-suggested fact verified by deterministic spec text search → compliant."""
        facts = [_make_fact(
            extraction_method="ai_suggested",
            verification_status="verified",
            validated_by="deterministic_spec_text_search",
        )]
        result = validate_ai_fact_guard(facts)
        assert result["compliant"]

    def test_multiple_facts_mixed_violations(self):
        """Mix of compliant and violating facts."""
        facts = [
            _make_fact("FACT-001", "tier1_direct_citation", "verified", "independent_agent_verifier"),
            _make_fact("FACT-002", "ai_suggested", "needs_review", ""),
            _make_fact("FACT-003", "ai_suggested", "verified", ""),  # VIOLATION
            _make_fact("FACT-004", "llm_suggested", "verified", ""),  # VIOLATION
        ]
        result = validate_ai_fact_guard(facts)
        assert not result["compliant"]
        assert len(result["violations"]) == 2
        violation_ids = {v["fact_id"] for v in result["violations"]}
        assert "FACT-003" in violation_ids
        assert "FACT-004" in violation_ids
        assert "FACT-001" not in violation_ids
        assert "FACT-002" not in violation_ids

    def test_ai_suggested_count_correct(self):
        """ai_suggested_count counts all AI-extracted facts."""
        facts = [
            _make_fact("FACT-001", "ai_suggested", "needs_review", ""),
            _make_fact("FACT-002", "llm_extraction", "needs_review", ""),
            _make_fact("FACT-003", "tier1_direct_citation", "verified", "independent_agent_verifier"),
        ]
        result = validate_ai_fact_guard(facts)
        assert result["ai_suggested_count"] == 2
        assert result["compliant"]

    def test_all_ai_extraction_method_variants_detected(self):
        """All _AI_EXTRACTION_METHODS variants trigger the guard when verified."""
        for method in _AI_EXTRACTION_METHODS:
            facts = [_make_fact(
                extraction_method=method,
                verification_status="verified",
                validated_by="",
            )]
            result = validate_ai_fact_guard(facts)
            assert not result["compliant"], (
                f"AI method {method!r} + verified + no independent check should be a violation"
            )


# ============================================================
# Real spec-cache scan test
# ============================================================


class TestSpecCacheAiGuard:
    """Tests for validate_spec_cache_ai_guard() against real spec cache."""

    pytestmark = pytest.mark.skipif(
        not _SPEC_CACHE.is_dir(),
        reason="SAL spec-cache not present in this environment",
    )

    def test_real_spec_cache_has_no_ai_self_verification(self):
        """Real spec cache must not contain any AI self-verification violations."""
        result = validate_spec_cache_ai_guard()
        if result["violations"]:
            violation_summary = "\n".join(
                f"  {v['source_file']}: {v['fact_id']} - {v['issue']}"
                for v in result["violations"]
            )
            pytest.fail(
                f"AI self-verification violations found in spec cache:\n{violation_summary}"
            )
        assert result["compliant"]

    def test_spec_cache_scan_checks_files(self):
        """Spec cache scan reports files checked (non-zero if cache populated)."""
        result = validate_spec_cache_ai_guard()
        # If .local/spec-cache exists with workbench files, files_checked > 0
        from pathlib import Path
        cache_dir = Path(__file__).parent.parent.parent / ".local" / "spec-cache"
        has_workbench_files = bool(list(cache_dir.rglob("verified-facts-review.yaml"))) if cache_dir.exists() else False
        if has_workbench_files:
            assert result["files_checked"] > 0


# ============================================================
# Constants validation
# ============================================================


class TestAiGuardConstants:
    """Tests for AI guard constant definitions."""

    def test_ai_extraction_methods_includes_ai_suggested(self):
        """ai_suggested must be in AI extraction methods."""
        assert "ai_suggested" in _AI_EXTRACTION_METHODS

    def test_ai_extraction_methods_includes_llm_variants(self):
        """LLM variants must be in AI extraction methods."""
        assert "llm_extraction" in _AI_EXTRACTION_METHODS
        assert "llm_suggested" in _AI_EXTRACTION_METHODS

    def test_independent_verification_includes_deterministic(self):
        """Deterministic spec text search is an independent verification method."""
        assert "deterministic_spec_text_search" in _INDEPENDENT_VERIFICATION_METHODS

    def test_independent_verification_includes_human_reviewed(self):
        """Human reviewed is an independent verification method."""
        assert "human_reviewed" in _INDEPENDENT_VERIFICATION_METHODS

    def test_tier1_direct_citation_is_independent(self):
        """tier1_direct_citation extraction is not AI — it's deterministic."""
        assert "tier1_direct_citation" in _INDEPENDENT_VERIFICATION_METHODS
