"""
TC-SAL-AITEST-001: Prove AI output cannot contaminate SAL fact registry.

Plan: shiny-kindling-cocoa v2.0 / Lane C
"""
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_SUP = str(_REPO / "tools" / "supervisor")
if _SUP not in sys.path:
    sys.path.insert(0, _SUP)

from validate_spec_fact_refs import validate_ai_fact_guard, validate_spec_cache_ai_guard


class TestAiNonAuthority:

    def test_ai_extraction_cannot_self_certify(self):
        """AI-sourced fact with verified status must be flagged."""
        facts = [{
            "claim_id": "FACT-TEST-001",
            "provenance": {
                "extraction_method": "llm_extraction",
                "verification_status": "verified",
                "validated_by": "none",
            }
        }]
        result = validate_ai_fact_guard(facts)
        assert not result["compliant"], "AI guard must flag AI-sourced verified fact"
        assert len(result["violations"]) == 1

    def test_deterministic_extraction_passes(self):
        """Deterministically-extracted fact must pass."""
        facts = [{
            "claim_id": "FACT-TEST-002",
            "provenance": {
                "extraction_method": "tier1_direct_citation",
                "verification_status": "verified",
                "validated_by": "deterministic_spec_text_search",
            }
        }]
        result = validate_ai_fact_guard(facts)
        assert result["compliant"], "Deterministic fact should pass"
        assert len(result["violations"]) == 0

    def test_sal_output_contains_no_ai_sourced_facts(self):
        """sal-facts-latest.json must not contain AI-sourced self-certified facts."""
        sal_path = _REPO / ".local" / "sal-output" / "sal-facts-latest.json"
        if not sal_path.exists():
            return  # Skip if file missing
        data = json.loads(sal_path.read_text(encoding="utf-8"))
        all_facts = []
        for r in data.get("results", []):
            all_facts.extend(r.get("spec_facts", []))
        result = validate_ai_fact_guard(all_facts)
        assert result["compliant"], f"Found AI-sourced verified facts: {result['violations'][:3]}"
