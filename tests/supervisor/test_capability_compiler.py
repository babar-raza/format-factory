"""Tests for the capability-to-feature compiler."""

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from capability_compiler import (
    compile_gap_to_feature_ir,
    compile_feature_ir_to_taskcard,
    compile_gap,
    compile_gap_to_feature_graph,
    compile_test_obligation_matrix,
    compile_evidence_obligation_matrix,
    compile_gate_readiness_projection,
    attach_qname_ontology,
    validate_sal_input,
    verify_idempotency,
    write_outputs,
    reset_sal_cache,
)


SAMPLE_GAP = {
    "format_id": "FODP",
    "function_name": "fodp_slide_notes",
    "expected_signature": "fodp_slide_notes(source: str | bytes | Path) -> list[str | None]",
    "gap_type": "missing_function",
}


class TestCompileGapToFeatureIR:
    def test_produces_feature_id(self):
        ir = compile_gap_to_feature_ir(SAMPLE_GAP)
        assert ir["feature_id"].startswith("FEAT-")

    def test_correct_format(self):
        ir = compile_gap_to_feature_ir(SAMPLE_GAP)
        assert ir["format_id"] == "FODP"

    def test_correct_function_name(self):
        ir = compile_gap_to_feature_ir(SAMPLE_GAP)
        assert ir["function_name"] == "fodp_slide_notes"

    def test_correct_module_path(self):
        ir = compile_gap_to_feature_ir(SAMPLE_GAP)
        assert ir["expected_module"] == "src/python/fodp/fodp_codec.py"

    def test_test_file_path(self):
        ir = compile_gap_to_feature_ir(SAMPLE_GAP)
        assert "tests/python/fodp/" in ir["expected_test_file"]

    def test_has_evidence_obligations(self):
        ir = compile_gap_to_feature_ir(SAMPLE_GAP)
        assert "source_diff" in ir["evidence_obligations"]
        assert "test_log" in ir["evidence_obligations"]

    def test_test_obligation_count(self):
        ir = compile_gap_to_feature_ir(SAMPLE_GAP)
        assert ir["test_obligation_count"] == 10


class TestCompileFeatureIRToTaskcard:
    def test_produces_taskcard_id(self):
        ir = compile_gap_to_feature_ir(SAMPLE_GAP)
        tc = compile_feature_ir_to_taskcard(ir)
        assert tc["taskcard_id"].startswith("TC-")

    def test_has_governance_requirements(self):
        ir = compile_gap_to_feature_ir(SAMPLE_GAP)
        tc = compile_feature_ir_to_taskcard(ir)
        gov = tc["governance_requirements"]
        assert gov["execution_method"] == "DIRECT_IMPLEMENTATION"
        assert "idempotency_key" in gov
        assert "route_decision_id" in gov
        assert "source_diff_paths" in gov

    def test_has_test_obligations(self):
        ir = compile_gap_to_feature_ir(SAMPLE_GAP)
        tc = compile_feature_ir_to_taskcard(ir)
        assert tc["test_obligations"]["min_test_count"] == 10

    def test_status_is_ready(self):
        ir = compile_gap_to_feature_ir(SAMPLE_GAP)
        tc = compile_feature_ir_to_taskcard(ir)
        assert tc["status"] == "READY_TO_EXECUTE"

    def test_acceptance_criteria_string(self):
        ir = compile_gap_to_feature_ir(SAMPLE_GAP)
        tc = compile_feature_ir_to_taskcard(ir)
        assert isinstance(tc["acceptance_criteria"], str)
        assert "fodp_slide_notes" in tc["acceptance_criteria"]


class TestFullCompilation:
    def test_compile_gap(self):
        result = compile_gap(SAMPLE_GAP)
        assert "gap" in result
        assert "feature_ir" in result
        assert "taskcard" in result

    def test_qoi_gap(self):
        gap = {
            "format_id": "QOI",
            "function_name": "qoi_colorspace_name",
            "expected_signature": "qoi_colorspace_name(path) -> str",
        }
        result = compile_gap(gap)
        assert result["feature_ir"]["format_id"] == "QOI"
        assert result["taskcard"]["format_id"] == "QOI"


class TestIdempotency:
    def test_is_idempotent(self):
        result = verify_idempotency(SAMPLE_GAP)
        assert result["idempotent"] is True
        assert result["feature_ir_match"] is True
        assert result["taskcard_match"] is True

    def test_different_input_different_output(self):
        gap2 = {**SAMPLE_GAP, "function_name": "different_func"}
        r1 = compile_gap(SAMPLE_GAP)
        r2 = compile_gap(gap2)
        assert r1["feature_ir"]["feature_id"] != r2["feature_ir"]["feature_id"]


class TestWriteOutputs:
    def test_writes_files(self, tmp_path):
        compilation = compile_gap(SAMPLE_GAP)
        paths = write_outputs(compilation, tmp_path / "out")
        assert Path(paths["feature_ir_path"]).is_file()
        assert Path(paths["taskcard_path"]).is_file()

    def test_output_is_valid_json(self, tmp_path):
        compilation = compile_gap(SAMPLE_GAP)
        paths = write_outputs(compilation, tmp_path / "out")
        ir = json.loads(Path(paths["feature_ir_path"]).read_text())
        assert ir["function_name"] == "fodp_slide_notes"

    def test_writes_all_phase_outputs(self, tmp_path):
        compilation = compile_gap(SAMPLE_GAP)
        paths = write_outputs(compilation, tmp_path / "out")
        assert Path(paths["sal_validation_path"]).is_file()
        assert Path(paths["feature_graph_path"]).is_file()
        assert Path(paths["test_obligation_matrix_path"]).is_file()
        assert Path(paths["evidence_obligation_matrix_path"]).is_file()
        assert Path(paths["gate_readiness_projection_path"]).is_file()


# ── Phase 0: SAL Input Validation ──────────────────────────────────────────

class TestPhase0SALValidation:
    def test_valid_sal(self, tmp_path):
        reset_sal_cache()
        sal = tmp_path / "sal-facts.json"
        sal.write_text(json.dumps({
            "results": [{"format_id": "FODP", "spec_facts": [
                {"qname": "FODP-FACT-001", "section": "ODF 1.3", "description": "test"}
            ]}]
        }))
        result = validate_sal_input(SAMPLE_GAP, sal)
        assert result["valid"] is True
        assert result["sal_exists"] is True
        assert result["sal_parseable"] is True
        assert result["facts_count"] == 1
        reset_sal_cache()

    def test_missing_sal(self, tmp_path):
        reset_sal_cache()
        result = validate_sal_input(SAMPLE_GAP, tmp_path / "nonexistent.json")
        assert result["valid"] is True  # Degraded mode
        assert result["sal_exists"] is False
        assert len(result["warnings"]) >= 1
        reset_sal_cache()

    def test_malformed_sal(self, tmp_path):
        reset_sal_cache()
        sal = tmp_path / "bad.json"
        sal.write_text("not valid json {{{")
        result = validate_sal_input(SAMPLE_GAP, sal)
        assert result["valid"] is True  # Degraded mode
        assert result["sal_parseable"] is False
        reset_sal_cache()


# ── Phase 3: Feature Graph ─────────────────────────────────────────────────

class TestPhase3FeatureGraph:
    def test_produces_graph_node(self):
        ir = compile_gap_to_feature_ir(SAMPLE_GAP)
        graph = compile_gap_to_feature_graph(ir)
        assert graph["node_id"] == ir["feature_id"]
        assert graph["node_type"] == "feature"
        assert graph["format_id"] == "FODP"

    def test_spec_connections(self):
        ir = compile_gap_to_feature_ir(SAMPLE_GAP)
        graph = compile_gap_to_feature_graph(ir)
        assert isinstance(graph["spec_connections"], list)


# ── Phase 3.5: QName Ontology ──────────────────────────────────────────────

class TestPhase35QNameOntology:
    def test_attaches_ontology_ref(self):
        ir = compile_gap_to_feature_ir(SAMPLE_GAP)
        enriched = attach_qname_ontology(ir)
        assert "qname_ontology" in enriched
        assert isinstance(enriched["qname_ontology"]["qname_map_exists"], bool)

    def test_with_mock_qname_map(self, tmp_path):
        import capability_compiler as cc
        original_dir = cc.QNAME_OUTPUT_DIR
        cc.QNAME_OUTPUT_DIR = tmp_path
        try:
            fmt_dir = tmp_path / "FODP"
            fmt_dir.mkdir()
            (fmt_dir / "qname-to-code-map-fodp.json").write_text(json.dumps({
                "coverage_summary": {"coverage_percent": 83.3},
                "mappings": [{"qname": "office:document"}],
            }))
            ir = compile_gap_to_feature_ir(SAMPLE_GAP)
            enriched = attach_qname_ontology(ir)
            assert enriched["qname_ontology"]["qname_map_exists"] is True
            assert enriched["qname_ontology"]["coverage_percent"] == 83.3
            assert "office:document" in enriched["qname_ontology"]["mapped_qnames"]
        finally:
            cc.QNAME_OUTPUT_DIR = original_dir


# ── Phase 6: Test Obligation Matrix ────────────────────────────────────────

class TestPhase6TestObligations:
    def test_produces_obligations(self):
        ir = compile_gap_to_feature_ir(SAMPLE_GAP)
        tom = compile_test_obligation_matrix(ir)
        assert tom["min_tests_required"] == 10
        assert len(tom["test_types"]) == 5
        assert all(t["required"] for t in tom["test_types"])

    def test_test_types_are_named(self):
        ir = compile_gap_to_feature_ir(SAMPLE_GAP)
        tom = compile_test_obligation_matrix(ir)
        type_names = [t["type"] for t in tom["test_types"]]
        assert "file_based_input" in type_names
        assert "error_handling" in type_names


# ── Phase 7: Evidence Obligation Matrix ────────────────────────────────────

class TestPhase7EvidenceObligations:
    def test_produces_obligations(self):
        ir = compile_gap_to_feature_ir(SAMPLE_GAP)
        eom = compile_evidence_obligation_matrix(ir)
        assert len(eom["evidence_obligations"]) == 4
        types = [o["type"] for o in eom["evidence_obligations"]]
        assert "source_diff" in types
        assert "ledger_entry" in types


# ── Phase 8: Gate Readiness Projection ─────────────────────────────────────

class TestPhase8GateProjection:
    def test_produces_projection(self):
        ir = compile_gap_to_feature_ir(SAMPLE_GAP)
        tc = compile_feature_ir_to_taskcard(ir)
        proj = compile_gate_readiness_projection(ir, tc)
        assert proj["format_id"] == "FODP"
        assert "gate_impact" in proj
        assert proj["blocks_gate_11"] is False

    def test_gate11_not_advanced_by_foss(self):
        ir = compile_gap_to_feature_ir(SAMPLE_GAP)
        tc = compile_feature_ir_to_taskcard(ir)
        proj = compile_gate_readiness_projection(ir, tc)
        assert proj["gate_impact"]["gate_11_commercial"] == "no_direct_impact"


# ── Full Compilation With All Phases ───────────────────────────────────────

class TestFullCompilationAllPhases:
    def test_all_phases_executed(self):
        result = compile_gap(SAMPLE_GAP)
        assert 0 in result["phases_executed"]
        assert 1 in result["phases_executed"]
        assert 2 in result["phases_executed"]
        assert 3 in result["phases_executed"]
        assert 3.5 in result["phases_executed"]
        assert 6 in result["phases_executed"]
        assert 7 in result["phases_executed"]
        assert 8 in result["phases_executed"]

    def test_all_outputs_present(self):
        result = compile_gap(SAMPLE_GAP)
        assert "sal_validation" in result
        assert "feature_ir" in result
        assert "taskcard" in result
        assert "feature_graph" in result
        assert "test_obligation_matrix" in result
        assert "evidence_obligation_matrix" in result
        assert "gate_readiness_projection" in result

    def test_idempotency_across_all_phases(self):
        r1 = compile_gap(SAMPLE_GAP)
        r2 = compile_gap(SAMPLE_GAP)
        assert json.dumps(r1["feature_ir"], sort_keys=True) == json.dumps(r2["feature_ir"], sort_keys=True)
        assert json.dumps(r1["taskcard"], sort_keys=True) == json.dumps(r2["taskcard"], sort_keys=True)
        assert json.dumps(r1["feature_graph"], sort_keys=True) == json.dumps(r2["feature_graph"], sort_keys=True)
