"""
test_r200_gate11_criteria_validator.py — Tests for Gate 11 spec-literal validators.

REQ-GOV-001: gate11-criteria.yaml has 7 required fields
REQ-GOV-002: 5 new depth validators are callable and work correctly
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from governance_validators import (
    validate_spec_fact_count,
    validate_qname_coverage,
    validate_parity_matrix_present,
    validate_no_placeholder_metadata,
    validate_gate11_criteria,
)


def _make_decl(items=None):
    """Build a minimal declaration dict."""
    return {
        "run_id": "test-run",
        "sprint_id": "TEST-SPRINT-001",
        "planned_work_items": items or [],
    }


# ── validate_spec_fact_count ──────────────────────────────────────────────────

class TestValidateSpecFactCount:
    def test_empty_items_pass(self):
        result = validate_spec_fact_count(_make_decl())
        assert result["result"] == "PASS"

    def test_governance_doc_items_exempt(self):
        decl = _make_decl([{
            "item_id": "T1",
            "item_type": "GOVERNANCE_DOC",
            "spec_fact_refs": [],
        }])
        result = validate_spec_fact_count(decl)
        assert result["result"] == "PASS"

    def test_product_source_with_refs_passes(self):
        decl = _make_decl([{
            "item_id": "T2",
            "item_type": "PRODUCT_SOURCE",
            "spec_fact_refs": ["FODS-FACT-001", "FODS-FACT-002", "FODS-FACT-003"],
        }])
        result = validate_spec_fact_count(decl)
        assert result["result"] == "PASS"

    def test_never_blocks_sprint(self):
        decl = _make_decl([{
            "item_id": "T3",
            "item_type": "PRODUCT_SOURCE",
            "spec_fact_refs": [],
        }])
        result = validate_spec_fact_count(decl)
        assert result["blocks_sprint"] is False

    def test_returns_required_keys(self):
        result = validate_spec_fact_count(_make_decl())
        assert "validator" in result
        assert "result" in result
        assert "summary" in result
        assert "blocks_sprint" in result


# ── validate_qname_coverage ───────────────────────────────────────────────────

class TestValidateQnameCoverage:
    def test_empty_declaration_pass(self):
        result = validate_qname_coverage(_make_decl())
        assert result["result"] == "PASS"

    def test_file_with_qname_detected(self, tmp_path):
        # Create a file containing a QName pattern
        proof = tmp_path / "proof.md"
        proof.write_text("Test references FODS-FACT-001 spec.", encoding="utf-8")
        decl = _make_decl([{
            "item_id": "T1",
            "item_type": "PRODUCT_SOURCE",
            "evidence_paths": [str(proof)],
        }])
        result = validate_qname_coverage(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"
        assert "1 files with QName" in result["summary"]

    def test_never_blocks_sprint(self):
        result = validate_qname_coverage(_make_decl())
        assert result["blocks_sprint"] is False


# ── validate_parity_matrix_present ───────────────────────────────────────────

class TestValidateParityMatrixPresent:
    def test_non_release_gate_items_exempt(self):
        decl = _make_decl([{
            "item_id": "T1",
            "item_type": "PRODUCT_SOURCE",
            "evidence_paths": [],
        }])
        result = validate_parity_matrix_present(decl)
        assert result["result"] == "PASS"

    def test_release_gate_without_parity_fails(self):
        decl = _make_decl([{
            "item_id": "T2",
            "item_type": "RELEASE_GATE",
            "evidence_paths": ["some-other-file.md"],
        }])
        result = validate_parity_matrix_present(decl)
        assert result["result"] == "FAIL"
        assert len(result["items"]) == 1

    def test_release_gate_with_parity_passes(self):
        decl = _make_decl([{
            "item_id": "T3",
            "item_type": "RELEASE_GATE",
            "evidence_paths": ["reports/fods-parity-matrix.md"],
        }])
        result = validate_parity_matrix_present(decl)
        assert result["result"] == "PASS"

    def test_never_blocks_sprint(self):
        decl = _make_decl([{
            "item_id": "T4",
            "item_type": "RELEASE_GATE",
            "evidence_paths": [],
        }])
        result = validate_parity_matrix_present(decl)
        assert result["blocks_sprint"] is False


# ── validate_no_placeholder_metadata ─────────────────────────────────────────

class TestValidateNoPlaceholderMetadata:
    def test_product_source_items_exempt(self):
        decl = _make_decl([{
            "item_id": "T1",
            "item_type": "PRODUCT_SOURCE",
            "evidence_paths": [],
        }])
        result = validate_no_placeholder_metadata(decl)
        assert result["result"] == "PASS"

    def test_release_gate_with_placeholder_fails(self, tmp_path):
        evidence = tmp_path / "evidence.md"
        evidence.write_text("Status: TBD — to be completed later.", encoding="utf-8")
        decl = _make_decl([{
            "item_id": "T2",
            "item_type": "RELEASE_GATE",
            "evidence_paths": [str(evidence)],
        }])
        result = validate_no_placeholder_metadata(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"

    def test_release_gate_clean_evidence_passes(self, tmp_path):
        evidence = tmp_path / "evidence.md"
        evidence.write_text("All tests pass. Gate 11 readiness confirmed.", encoding="utf-8")
        decl = _make_decl([{
            "item_id": "T3",
            "item_type": "RELEASE_GATE",
            "evidence_paths": [str(evidence)],
        }])
        result = validate_no_placeholder_metadata(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_never_blocks_sprint(self, tmp_path):
        evidence = tmp_path / "evidence.md"
        evidence.write_text("TBD", encoding="utf-8")
        decl = _make_decl([{
            "item_id": "T4",
            "item_type": "RELEASE_GATE",
            "evidence_paths": [str(evidence)],
        }])
        result = validate_no_placeholder_metadata(decl, repo_root=tmp_path)
        assert result["blocks_sprint"] is False


# ── validate_gate11_criteria ──────────────────────────────────────────────────

class TestValidateGate11Criteria:
    def test_no_release_gate_items_pass(self):
        result = validate_gate11_criteria(_make_decl())
        assert result["result"] == "PASS"

    def test_release_gate_with_enough_refs_passes(self):
        decl = _make_decl([{
            "item_id": "T1",
            "item_type": "RELEASE_GATE",
            "spec_fact_refs": ["FODS-FACT-001", "FODS-FACT-002", "FODS-FACT-003"],
        }])
        result = validate_gate11_criteria(decl, repo_root=_REPO)
        assert result["result"] == "PASS"

    def test_release_gate_without_refs_fails(self):
        decl = _make_decl([{
            "item_id": "T2",
            "item_type": "RELEASE_GATE",
            "spec_fact_refs": [],
        }])
        result = validate_gate11_criteria(decl, repo_root=_REPO)
        assert result["result"] == "FAIL"
        assert len(result["items"]) >= 1

    def test_gate11_criteria_file_loaded(self):
        import yaml
        criteria_path = _REPO / "registry" / "gate11-criteria.yaml"
        assert criteria_path.exists(), "gate11-criteria.yaml must exist"
        data = yaml.safe_load(criteria_path.read_text(encoding="utf-8"))
        assert "criteria" in data
        c = data["criteria"]
        assert "min_spec_facts_cited" in c
        assert "min_api_coverage" in c
        assert "foss_test_count_min" in c
        assert "commercial_test_count_min" in c
        assert "parity_matrix_required" in c
        assert "dogfood_proof_required" in c
        assert "no_placeholder_metadata" in c

    def test_never_blocks_sprint(self):
        decl = _make_decl([{
            "item_id": "T3",
            "item_type": "RELEASE_GATE",
            "spec_fact_refs": [],
        }])
        result = validate_gate11_criteria(decl, repo_root=_REPO)
        assert result["blocks_sprint"] is False
