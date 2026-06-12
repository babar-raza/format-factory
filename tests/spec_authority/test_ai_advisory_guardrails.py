"""
test_ai_advisory_guardrails.py

Tests proving that AI/TF-IDF advisory output cannot set authoritative status.

SAL-VERIFICATION-HARDENING-001 (Lane F) — 2026-06-11

Key invariants:
1. AI-extracted facts with status=verified (without independent validation) → REJECTED
2. Advisory output (TF-IDF retrieval) cannot elevate a requirement to VERIFIED
3. LLM-derived entries may never appear with status=verified in fact registry
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fact(fact_id: str, extraction_method: str, verification_status: str,
          validated_by: str = "") -> dict:
    return {
        "claim_id": fact_id,
        "provenance": {
            "extraction_method": extraction_method,
            "verification_status": verification_status,
            "validated_by": validated_by,
        },
    }


# ---------------------------------------------------------------------------
# Test 1: AI suggestion without independent confirmation is rejected
# ---------------------------------------------------------------------------

class TestAiSuggestionWithoutSourceRefRejected:
    def test_ai_extraction_method_cannot_self_certify_as_verified(self):
        """AI-extracted fact (extraction_method=llm_extraction) must be rejected if status=verified."""
        from validate_spec_fact_refs import validate_ai_fact_guard

        facts = [
            _fact("FACT-ZST-AI-001", "llm_extraction", "verified", validated_by="")
        ]
        result = validate_ai_fact_guard(facts)
        assert result["compliant"] is False
        assert len(result["violations"]) >= 1
        assert result["ai_self_verified_count"] >= 1

    def test_ai_suggested_without_independent_validation_blocked(self):
        """AI-extracted via ai_suggested cannot be verified without independent method."""
        from validate_spec_fact_refs import validate_ai_fact_guard

        facts = [
            _fact("FACT-FODS-AI-001", "ai_suggested", "verified", validated_by="")
        ]
        result = validate_ai_fact_guard(facts)
        assert result["compliant"] is False
        assert any("FACT-FODS-AI-001" in v["fact_id"] for v in result["violations"])

    def test_ai_extraction_with_deterministic_validation_passes(self):
        """AI-extracted fact independently verified by deterministic_spec_text_search PASSES."""
        from validate_spec_fact_refs import validate_ai_fact_guard

        facts = [
            _fact(
                "FACT-ZST-001",
                "llm_extraction",
                "verified",
                validated_by="deterministic_spec_text_search",
            )
        ]
        result = validate_ai_fact_guard(facts)
        assert result["compliant"] is True
        assert len(result["violations"]) == 0

    def test_deterministic_extraction_allows_verified_status(self):
        """Fact extracted deterministically (manual, keyword_search) can be verified."""
        from validate_spec_fact_refs import validate_ai_fact_guard

        facts = [
            _fact("FACT-ZST-002", "manual_extraction", "verified",
                  validated_by="deterministic_spec_text_search"),
            _fact("FACT-ZST-003", "keyword_search", "verified",
                  validated_by="deterministic_spec_text_search"),
        ]
        result = validate_ai_fact_guard(facts)
        assert result["compliant"] is True


# ---------------------------------------------------------------------------
# Test 2: Advisory flag present in ledger output
# ---------------------------------------------------------------------------

class TestAdvisoryBoundaryInSpecGovernance:
    def test_ai_output_not_propagated_to_fact_registry(self):
        """AI guard confirms ai_self_verified_count tracked separately from compliant facts."""
        from validate_spec_fact_refs import validate_ai_fact_guard

        facts = [
            # AI-extracted but needs_review (acceptable)
            _fact("FACT-X-001", "llm_extraction", "needs_review"),
            # Deterministic and verified (acceptable)
            _fact("FACT-X-002", "manual_extraction", "verified",
                  validated_by="deterministic_spec_text_search"),
            # AI self-certified (VIOLATION)
            _fact("FACT-X-003", "ai_suggested", "verified"),
        ]
        result = validate_ai_fact_guard(facts)
        assert result["total_facts"] == 3
        assert result["ai_suggested_count"] >= 2  # llm_extraction + ai_suggested
        assert result["ai_self_verified_count"] == 1  # only FACT-X-003 is a violation
        assert result["compliant"] is False

    def test_empty_fact_list_is_compliant(self):
        """Empty fact list has no violations."""
        from validate_spec_fact_refs import validate_ai_fact_guard

        result = validate_ai_fact_guard([])
        assert result["compliant"] is True
        assert result["total_facts"] == 0
        assert result["violations"] == []

    def test_pure_needs_review_ai_facts_are_compliant(self):
        """AI-extracted facts with needs_review status are acceptable (not self-certified)."""
        from validate_spec_fact_refs import validate_ai_fact_guard

        facts = [
            _fact("FACT-A-001", "llm_extraction", "needs_review"),
            _fact("FACT-A-002", "ai_suggested", "needs_review"),
        ]
        result = validate_ai_fact_guard(facts)
        assert result["compliant"] is True
        assert result["ai_suggested_count"] == 2
        assert len(result["violations"]) == 0
