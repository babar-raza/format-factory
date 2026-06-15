"""Tests for spec-parity enforcement (Train E).

Validates that:
1. Positive taskcard with valid spec_qname passes
2. Negative product model taskcard missing spec_qname fails
3. Negative arbitrary flat class name fails
4. Reduced-scope exception is honored
5. FODS/FODT 0% coverage is treated as migration debt, not readiness failure
"""

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from capability_compiler import (
    compile_gap,
    compile_gap_to_feature_ir,
    compile_feature_ir_to_taskcard,
    attach_qname_ontology,
    reset_sal_cache,
)


@pytest.fixture(autouse=True)
def clean_sal():
    reset_sal_cache()
    yield
    reset_sal_cache()


class TestPositiveSpecQName:
    """Positive fixture: taskcard with valid spec_qname passes."""

    def test_taskcard_with_spec_qnames(self, tmp_path):
        """When SAL has spec facts, taskcard gets spec_qnames."""
        sal = tmp_path / "sal.json"
        sal.write_text(json.dumps({
            "results": [{"format_id": "FODP", "spec_facts": [
                {"qname": "FODP-FACT-001", "section": "ODF 1.3"},
            ]}]
        }))
        gap = {
            "format_id": "FODP",
            "function_name": "fodp_slide_notes",
            "expected_signature": "fodp_slide_notes(source) -> list[str]",
        }
        result = compile_gap(gap, sal_path=sal)
        tc = result["taskcard"]
        assert tc["governance_requirements"]["spec_qnames"] == ["FODP-FACT-001"]
        assert tc["governance_requirements"]["exception_classification"] == "spec_authority_available"

    def test_taskcard_has_spec_facts_count(self, tmp_path):
        sal = tmp_path / "sal.json"
        sal.write_text(json.dumps({
            "results": [{"format_id": "CSV", "spec_facts": [
                {"qname": "CSV-FACT-001", "section": "RFC 4180"},
                {"qname": "CSV-FACT-002", "section": "RFC 4180"},
            ]}]
        }))
        gap = {"format_id": "CSV", "function_name": "csv_count_rows"}
        result = compile_gap(gap, sal_path=sal)
        assert result["feature_ir"]["spec_facts_count"] == 2


class TestNegativeNoSpecQName:
    """Negative fixture: product model taskcard missing spec_qname."""

    def test_missing_spec_qname_classified(self):
        """No SAL facts -> exception_classification = no_public_spec_available."""
        gap = {
            "format_id": "UNKNOWN_FORMAT",
            "function_name": "unknown_func",
        }
        result = compile_gap(gap)
        tc = result["taskcard"]
        assert tc["governance_requirements"]["spec_qnames"] == []
        assert tc["governance_requirements"]["exception_classification"] == "no_public_spec_available"


class TestNegativeFlatClassName:
    """Negative fixture: arbitrary flat class names are not spec-aligned."""

    def test_flat_function_gets_no_qname_ontology(self):
        gap = {
            "format_id": "XYZ",
            "function_name": "MyArbitraryClass_doThing",
        }
        ir = compile_gap_to_feature_ir(gap)
        enriched = attach_qname_ontology(ir)
        # No QName map for unknown format
        assert enriched["qname_ontology"]["qname_map_exists"] is False


class TestReducedScopeException:
    """Reduced-scope exception should be honored."""

    def test_no_sal_facts_still_compiles(self):
        """Compilation should succeed even without SAL facts (degraded mode)."""
        gap = {
            "format_id": "TOML",
            "function_name": "toml_load",
        }
        result = compile_gap(gap)
        assert result["taskcard"]["status"] == "READY_TO_EXECUTE"
        assert result["sal_validation"]["valid"] is True


class TestFODSFODTMigrationDebt:
    """FODS/FODT 0% QName coverage = migration debt, not readiness failure."""

    def test_fods_zero_coverage_is_debt(self, tmp_path):
        """FODS with 0% coverage should still compile (treated as debt)."""
        import capability_compiler as cc
        original = cc.QNAME_OUTPUT_DIR
        cc.QNAME_OUTPUT_DIR = tmp_path
        try:
            fods_dir = tmp_path / "FODS"
            fods_dir.mkdir()
            (fods_dir / "qname-to-code-map-fods.json").write_text(json.dumps({
                "coverage_summary": {"coverage_percent": 0.0, "total_expected": 10, "mapped": 0},
                "mappings": [],
            }))
            gap = {"format_id": "FODS", "function_name": "fods_load"}
            ir = compile_gap_to_feature_ir(gap)
            enriched = attach_qname_ontology(ir)
            assert enriched["qname_ontology"]["qname_map_exists"] is True
            assert enriched["qname_ontology"]["coverage_percent"] == 0.0
            # Zero coverage doesn't block compilation
            result = compile_gap(gap)
            assert result["taskcard"]["status"] == "READY_TO_EXECUTE"
        finally:
            cc.QNAME_OUTPUT_DIR = original

    def test_fodt_zero_coverage_is_debt(self, tmp_path):
        import capability_compiler as cc
        original = cc.QNAME_OUTPUT_DIR
        cc.QNAME_OUTPUT_DIR = tmp_path
        try:
            fodt_dir = tmp_path / "FODT"
            fodt_dir.mkdir()
            (fodt_dir / "qname-to-code-map-fodt.json").write_text(json.dumps({
                "coverage_summary": {"coverage_percent": 0.0, "total_expected": 11, "mapped": 0},
                "mappings": [],
            }))
            gap = {"format_id": "FODT", "function_name": "fodt_load"}
            result = compile_gap(gap)
            assert result["taskcard"]["status"] == "READY_TO_EXECUTE"
        finally:
            cc.QNAME_OUTPUT_DIR = original
