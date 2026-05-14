"""
test_validate_generated_requirements.py

Tests for the AI-generated requirements validator.

Run: python -m pytest tests/requirements -q -vv
"""

import pytest
import sys
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "requirements"))

from validate_generated_requirements import manual_validate, validate_format


# ============================================================
# Helpers
# ============================================================

def make_requirement(overrides: dict = None) -> dict:
    """Return a minimal valid commercial requirement."""
    req = {
        "requirement_id": "FODS-REQ-001",
        "format": "fods",
        "capability_level": "C4",
        "requirement_type": "object_model",
        "title": "FodsDocument class",
        "description": "FodsDocument loads an FODS file into a typed object model.",
        "product_goal_mapping": ["PG-001"],
        "source_evidence": [
            {"source_type": "EXISTING_SOURCE", "reference": "src/net/fods/FodsDocument.cs"}
        ],
        "source_type": "EXISTING_SOURCE",
        "confidence": "HIGH",
        "status": "ACCEPTED_FOR_VERTICAL_SLICE",
        "test_requirements": ["Load valid FODS; verify sheet count"],
        "validation_notes": None,
        "implementation_target": "src/net/fods/FodsDocument.cs",
        "known_limitations": None,
    }
    if overrides:
        req.update(overrides)
    return req


def make_document(reqs: list = None, overrides: dict = None) -> dict:
    """Return a minimal valid commercial-requirements.yaml structure."""
    doc = {
        "format": "fods",
        "spec_version": "ODF 1.3",
        "generator_version": "1.0",
        "generation_timestamp": "2026-05-13T00:00:00Z",
        "model_tool": "test",
        "ai_available": False,
        "product_goals_ref": "docs/commercial-product-capability-model.md",
        "input_source_hashes": {},
        "requirements": reqs if reqs is not None else [make_requirement()],
    }
    if overrides:
        doc.update(overrides)
    return doc


MINIMAL_SCHEMA = {
    "required": ["format", "spec_version", "generator_version", "generation_timestamp", "product_goals_ref", "requirements"],
    "definitions": {
        "Requirement": {
            "required": [
                "requirement_id", "format", "capability_level", "requirement_type",
                "title", "description", "product_goal_mapping", "source_evidence",
                "source_type", "confidence", "status"
            ]
        }
    }
}


# ============================================================
# Schema validation tests
# ============================================================

class TestManualValidate:
    def test_valid_document_passes(self, tmp_path):
        doc = make_document()
        errors = manual_validate(doc, MINIMAL_SCHEMA, tmp_path / "test.yaml")
        assert errors == [], f"Unexpected errors: {errors}"

    def test_missing_required_top_level_field(self, tmp_path):
        doc = make_document()
        del doc["format"]
        errors = manual_validate(doc, MINIMAL_SCHEMA, tmp_path / "test.yaml")
        assert any("format" in e for e in errors)

    def test_empty_requirements_array(self, tmp_path):
        doc = make_document(reqs=[])
        errors = manual_validate(doc, MINIMAL_SCHEMA, tmp_path / "test.yaml")
        assert len(errors) > 0

    def test_duplicate_requirement_ids(self, tmp_path):
        req1 = make_requirement({"requirement_id": "FODS-REQ-001"})
        req2 = make_requirement({"requirement_id": "FODS-REQ-001"})
        doc = make_document(reqs=[req1, req2])
        errors = manual_validate(doc, MINIMAL_SCHEMA, tmp_path / "test.yaml")
        assert any("Duplicate" in e for e in errors)

    def test_ai_proposal_cannot_be_accepted(self, tmp_path):
        req = make_requirement({
            "source_type": "AI_PROPOSAL",
            "status": "ACCEPTED",
            "source_evidence": [{"source_type": "AI_PROPOSAL", "reference": "generated"}]
        })
        doc = make_document(reqs=[req])
        errors = manual_validate(doc, MINIMAL_SCHEMA, tmp_path / "test.yaml")
        assert any("AI_PROPOSAL" in e for e in errors)

    def test_accepted_for_vertical_slice_requires_tests(self, tmp_path):
        req = make_requirement({
            "status": "ACCEPTED_FOR_VERTICAL_SLICE",
            "test_requirements": None
        })
        doc = make_document(reqs=[req])
        errors = manual_validate(doc, MINIMAL_SCHEMA, tmp_path / "test.yaml")
        assert any("test_requirements" in e for e in errors)

    def test_non_product_decision_requires_source_evidence(self, tmp_path):
        req = make_requirement({
            "source_type": "SPEC",
            "source_evidence": []
        })
        doc = make_document(reqs=[req])
        errors = manual_validate(doc, MINIMAL_SCHEMA, tmp_path / "test.yaml")
        assert any("source_evidence" in e for e in errors)

    def test_product_decision_does_not_require_source_evidence(self, tmp_path):
        req = make_requirement({
            "source_type": "PRODUCT_DECISION",
            "source_evidence": [],
            "product_goal_mapping": ["PG-001"]
        })
        doc = make_document(reqs=[req])
        errors = manual_validate(doc, MINIMAL_SCHEMA, tmp_path / "test.yaml")
        assert errors == [], f"Unexpected errors for PRODUCT_DECISION: {errors}"

    def test_conversion_requirement_future_scope(self, tmp_path):
        """Conversion requirements marked current + ACCEPTED_FOR_VERTICAL_SLICE should fail."""
        doc = {
            "scope_note": "Future requirements",
            "requirements": [
                {
                    "requirement_id": "FODS-CONV-001",
                    "target_format": "html",
                    "title": "Export to HTML",
                    "description": "Export FODS to HTML",
                    "source_type": "PRODUCT_DECISION",
                    "confidence": "HIGH",
                    "status": "ACCEPTED_FOR_VERTICAL_SLICE",
                    "sprint_scope": "current"
                }
            ]
        }
        schema = {"required": ["scope_note", "requirements"], "definitions": {}}
        errors = manual_validate(doc, schema, tmp_path / "conv.yaml")
        assert any("cannot be ACCEPTED_FOR_VERTICAL_SLICE" in e for e in errors)


# ============================================================
# Integration tests (validate actual generated requirement files)
# ============================================================

class TestValidateFormatIntegration:
    def test_fods_requirements_exist(self):
        """FODS generated requirements directory must exist."""
        fods_dir = REPO_ROOT / "generated-requirements" / "fods"
        assert fods_dir.exists(), f"Missing: {fods_dir}"

    def test_fodt_requirements_exist(self):
        """FODT generated requirements directory must exist."""
        fodt_dir = REPO_ROOT / "generated-requirements" / "fodt"
        assert fodt_dir.exists(), f"Missing: {fodt_dir}"

    def test_fods_commercial_requirements_file_exists(self):
        path = REPO_ROOT / "generated-requirements" / "fods" / "commercial-requirements.yaml"
        assert path.exists(), f"Missing: {path}"

    def test_fodt_commercial_requirements_file_exists(self):
        path = REPO_ROOT / "generated-requirements" / "fodt" / "commercial-requirements.yaml"
        assert path.exists(), f"Missing: {path}"

    def test_fods_requirements_validate(self):
        results = validate_format("fods", verbose=False)
        for name, result in results.items():
            status = result["status"]
            assert status in ("PASS",), f"FODS {name}: {status} — {result['errors']}"

    def test_fodt_requirements_validate(self):
        results = validate_format("fodt", verbose=False)
        for name, result in results.items():
            status = result["status"]
            assert status in ("PASS",), f"FODT {name}: {status} — {result['errors']}"

    def test_fods_has_accepted_for_vertical_slice(self):
        """At least one FODS requirement must be ACCEPTED_FOR_VERTICAL_SLICE."""
        import yaml
        path = REPO_ROOT / "generated-requirements" / "fods" / "commercial-requirements.yaml"
        if not path.exists():
            pytest.skip("FODS requirements not yet generated")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        statuses = [r.get("status") for r in data.get("requirements", [])]
        assert "ACCEPTED_FOR_VERTICAL_SLICE" in statuses, "No ACCEPTED_FOR_VERTICAL_SLICE requirements found"

    def test_fodt_has_accepted_for_vertical_slice(self):
        """At least one FODT requirement must be ACCEPTED_FOR_VERTICAL_SLICE."""
        import yaml
        path = REPO_ROOT / "generated-requirements" / "fodt" / "commercial-requirements.yaml"
        if not path.exists():
            pytest.skip("FODT requirements not yet generated")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        statuses = [r.get("status") for r in data.get("requirements", [])]
        assert "ACCEPTED_FOR_VERTICAL_SLICE" in statuses, "No ACCEPTED_FOR_VERTICAL_SLICE requirements found"

    def test_conversion_requirements_are_future_scoped(self):
        """All conversion requirements must be future sprint_scope."""
        import yaml
        for fmt in ["fods", "fodt"]:
            path = REPO_ROOT / "generated-requirements" / fmt / "conversion-requirements.yaml"
            if not path.exists():
                continue
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            for req in data.get("requirements", []):
                scope = req.get("sprint_scope", "future")
                assert scope == "future", f"{fmt} conversion req {req.get('requirement_id')} has sprint_scope={scope}"

    def test_fods_traceability_map_exists(self):
        """FODS traceability-map.yaml must exist."""
        path = REPO_ROOT / "generated-requirements" / "fods" / "traceability-map.yaml"
        assert path.exists(), f"Missing: {path}"

    def test_fodt_traceability_map_exists(self):
        """FODT traceability-map.yaml must exist."""
        path = REPO_ROOT / "generated-requirements" / "fodt" / "traceability-map.yaml"
        assert path.exists(), f"Missing: {path}"

    def test_fods_verifier_review_exists(self):
        """FODS verifier-review.yaml must exist (DEC-034 IV requirement)."""
        path = REPO_ROOT / "generated-requirements" / "fods" / "verifier-review.yaml"
        assert path.exists(), f"Missing: {path}"

    def test_fodt_verifier_review_exists(self):
        """FODT verifier-review.yaml must exist (DEC-034 IV requirement)."""
        path = REPO_ROOT / "generated-requirements" / "fodt" / "verifier-review.yaml"
        assert path.exists(), f"Missing: {path}"

    def test_fods_verifier_review_is_lane_r5_pass(self):
        """FODS verifier verdict must be LANE_R5_PASS."""
        import yaml
        path = REPO_ROOT / "generated-requirements" / "fods" / "verifier-review.yaml"
        if not path.exists():
            pytest.skip("FODS verifier-review not yet generated")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        result = data.get("verifier_verdict", {}).get("result")
        assert result == "LANE_R5_PASS", f"FODS verifier verdict is {result!r} — must be LANE_R5_PASS"

    def test_fodt_verifier_review_is_lane_r5_pass(self):
        """FODT verifier verdict must be LANE_R5_PASS."""
        import yaml
        path = REPO_ROOT / "generated-requirements" / "fodt" / "verifier-review.yaml"
        if not path.exists():
            pytest.skip("FODT verifier-review not yet generated")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        result = data.get("verifier_verdict", {}).get("result")
        assert result == "LANE_R5_PASS", f"FODT verifier verdict is {result!r} — must be LANE_R5_PASS"

    def test_fods_cross_file_consistency(self):
        """FODS traceability-map accepted IDs must match requirement files."""
        from validate_generated_requirements import validate_cross_file_consistency
        result = validate_cross_file_consistency("fods", verbose=False)
        assert result["status"] == "PASS", f"FODS cross-file consistency FAIL: {result['errors']}"

    def test_fodt_cross_file_consistency(self):
        """FODT traceability-map accepted IDs must match requirement files."""
        from validate_generated_requirements import validate_cross_file_consistency
        result = validate_cross_file_consistency("fodt", verbose=False)
        assert result["status"] == "PASS", f"FODT cross-file consistency FAIL: {result['errors']}"

    def test_fods_ai_proposal_count_is_zero(self):
        """FODS traceability-map AI_PROPOSAL count must be 0 (AUTHORITATIVE requirement)."""
        import yaml
        path = REPO_ROOT / "generated-requirements" / "fods" / "traceability-map.yaml"
        if not path.exists():
            pytest.skip("FODS traceability-map not yet generated")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        ai_count = data.get("source_evidence_summary", {}).get("AI_PROPOSAL", -1)
        assert ai_count == 0, f"FODS AI_PROPOSAL count={ai_count}, must be 0 (GOVERNANCE.md 26.11)"

    def test_fodt_ai_proposal_count_is_zero(self):
        """FODT traceability-map AI_PROPOSAL count must be 0 (AUTHORITATIVE requirement)."""
        import yaml
        path = REPO_ROOT / "generated-requirements" / "fodt" / "traceability-map.yaml"
        if not path.exists():
            pytest.skip("FODT traceability-map not yet generated")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        ai_count = data.get("source_evidence_summary", {}).get("AI_PROPOSAL", -1)
        assert ai_count == 0, f"FODT AI_PROPOSAL count={ai_count}, must be 0 (GOVERNANCE.md 26.11)"


# ============================================================
# Fixture-based tests (Lane C hardening)
# ============================================================

FIXTURES_DIR = REPO_ROOT / "tests" / "requirements" / "fixtures"


class TestFixtures:
    """Fixture-based validation tests — confirm validator catches known-bad inputs."""

    def test_valid_fixture_passes(self):
        """valid-commercial-requirements.yaml must pass schema validation."""
        import yaml
        fixture = FIXTURES_DIR / "valid-commercial-requirements.yaml"
        assert fixture.exists(), f"Fixture missing: {fixture}"
        data = yaml.safe_load(fixture.read_text(encoding="utf-8"))
        schema_path = REPO_ROOT / "schemas" / "generated-requirements" / "commercial-format-requirements.schema.json"
        import json
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        errors = manual_validate(data, schema, fixture)
        assert errors == [], f"Valid fixture produced errors: {errors}"

    def test_duplicate_ids_fixture_fails(self):
        """invalid-duplicate-ids.yaml must fail with duplicate ID error."""
        import yaml, json
        fixture = FIXTURES_DIR / "invalid-duplicate-ids.yaml"
        assert fixture.exists(), f"Fixture missing: {fixture}"
        data = yaml.safe_load(fixture.read_text(encoding="utf-8"))
        schema_path = REPO_ROOT / "schemas" / "generated-requirements" / "commercial-format-requirements.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        errors = manual_validate(data, schema, fixture)
        assert any("Duplicate" in e for e in errors), f"Expected duplicate ID error, got: {errors}"

    def test_ai_only_accepted_fixture_fails(self):
        """invalid-ai-only-accepted.yaml must fail: AI_PROPOSAL cannot be ACCEPTED."""
        import yaml, json
        fixture = FIXTURES_DIR / "invalid-ai-only-accepted.yaml"
        assert fixture.exists(), f"Fixture missing: {fixture}"
        data = yaml.safe_load(fixture.read_text(encoding="utf-8"))
        schema_path = REPO_ROOT / "schemas" / "generated-requirements" / "commercial-format-requirements.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        errors = manual_validate(data, schema, fixture)
        assert any("AI_PROPOSAL" in e for e in errors), f"Expected AI_PROPOSAL error, got: {errors}"

    def test_conversion_not_scoped_fixture_fails(self):
        """invalid-conversion-not-scoped.yaml must fail: current scope not allowed."""
        import yaml, json
        fixture = FIXTURES_DIR / "invalid-conversion-not-scoped.yaml"
        assert fixture.exists(), f"Fixture missing: {fixture}"
        data = yaml.safe_load(fixture.read_text(encoding="utf-8"))
        schema_path = REPO_ROOT / "schemas" / "generated-requirements" / "conversion-requirements.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        errors = manual_validate(data, schema, fixture)
        assert any("cannot be ACCEPTED_FOR_VERTICAL_SLICE" in e for e in errors), \
            f"Expected conversion scope error, got: {errors}"
