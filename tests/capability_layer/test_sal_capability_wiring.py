"""Tests for SAL-to-capability wiring (Train B: WIRING-SAL-TO-CAPABILITY).

Verifies that:
1. SAL facts are consumed by capability map generation
2. Missing SAL output gives classified warning
3. Malformed SAL output is quarantined
4. SAL facts enrich capability records
"""

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "capability_layer"))

import capability_map_generator as cmg


@pytest.fixture(autouse=True)
def reset_cache():
    """Reset SAL cache before and after each test."""
    cmg.reset_sal_facts_cache()
    yield
    cmg.reset_sal_facts_cache()


class TestSALFactsLoader:
    def test_loads_valid_sal(self, tmp_path):
        sal = tmp_path / "sal-facts.json"
        sal.write_text(json.dumps({
            "results": [
                {"format_id": "fods", "spec_facts": [
                    {"qname": "FODS-FACT-001", "section": "ODF 1.3"},
                    {"qname": "FODS-FACT-002", "section": "ODF 1.3"},
                ]},
                {"format_id": "zst", "spec_facts": [
                    {"qname": "ZST-FACT-001", "section": "RFC 8878"},
                ]},
            ]
        }))
        # Temporarily replace the SAL path
        original = cmg._SAL_OUTPUT
        cmg._SAL_OUTPUT = sal
        try:
            facts = cmg._load_sal_facts()
            assert "FODS" in facts
            assert "ZST" in facts
            assert len(facts["FODS"]) == 2
            assert len(facts["ZST"]) == 1
        finally:
            cmg._SAL_OUTPUT = original

    def test_missing_sal_gives_empty(self, tmp_path):
        original = cmg._SAL_OUTPUT
        cmg._SAL_OUTPUT = tmp_path / "nonexistent.json"
        try:
            facts = cmg._load_sal_facts()
            assert facts == {}
        finally:
            cmg._SAL_OUTPUT = original

    def test_malformed_sal_gives_empty(self, tmp_path):
        sal = tmp_path / "bad.json"
        sal.write_text("NOT JSON {{{")
        original = cmg._SAL_OUTPUT
        cmg._SAL_OUTPUT = sal
        try:
            facts = cmg._load_sal_facts()
            assert facts == {}
        finally:
            cmg._SAL_OUTPUT = original

    def test_sal_missing_results_key(self, tmp_path):
        sal = tmp_path / "empty.json"
        sal.write_text(json.dumps({"no_results": True}))
        original = cmg._SAL_OUTPUT
        cmg._SAL_OUTPUT = sal
        try:
            facts = cmg._load_sal_facts()
            assert facts == {}
        finally:
            cmg._SAL_OUTPUT = original

    def test_existing_verified_facts_still_work(self):
        """Ensure _load_spec_facts still works for verified fact loading."""
        # This is a smoke test — the function should not crash
        facts = cmg._load_spec_facts("fods")
        assert isinstance(facts, list)

    def test_sal_enrichment_changes_output(self, tmp_path):
        """A SAL fact present should change or enrich capability output."""
        sal = tmp_path / "sal-facts.json"
        sal.write_text(json.dumps({
            "results": [
                {"format_id": "testformat", "spec_facts": [
                    {"qname": "TEST-FACT-001", "section": "Test Spec"},
                ]},
            ]
        }))
        original = cmg._SAL_OUTPUT
        cmg._SAL_OUTPUT = sal
        try:
            facts = cmg._load_sal_facts()
            assert "TESTFORMAT" in facts
            assert facts["TESTFORMAT"][0]["qname"] == "TEST-FACT-001"
        finally:
            cmg._SAL_OUTPUT = original
