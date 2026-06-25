"""TC-FL-010: Tests for V72 validate_artifact_identity.

The plan called this 'V57' but V57 was already used; the validator is V72.
This test file is named test_v57 per plan requirement for traceability.

Tests assert:
1. V72 FAILs (blocks_sprint=True) for RELEASE_GATE items lacking artifact_id+authority
2. V72 WARNs (blocks_sprint=False) for PRODUCT_SOURCE items lacking identity fields
3. V72 PASSes when all artifacts have artifact_id and valid authority
4. V72 PASSes for items with no evidence_artifacts
5. V72 is registered in run_all_governance_validators
6. The artifact-identity.yaml contract file exists
"""

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))
sys.path.insert(0, str(_REPO))

import pytest
import yaml


def _make_item(item_type: str, artifacts: list) -> dict:
    return {
        "item_id": "TEST-001",
        "item_type": item_type,
        "title": "Test item",
        "evidence_artifacts": artifacts,
    }


class TestArtifactIdentityContract:
    def test_contract_file_exists(self):
        contract = _REPO / ".supervisor" / "knowledge" / "contracts" / "artifact-identity.yaml"
        assert contract.exists(), "artifact-identity.yaml contract must exist"

    def test_contract_has_required_fields_section(self):
        contract = _REPO / ".supervisor" / "knowledge" / "contracts" / "artifact-identity.yaml"
        data = yaml.safe_load(contract.read_text(encoding="utf-8"))
        assert "required_fields" in data
        assert "artifact_id" in data["required_fields"]
        assert "authority" in data["required_fields"]

    def test_contract_lists_valid_authority_values(self):
        contract = _REPO / ".supervisor" / "knowledge" / "contracts" / "artifact-identity.yaml"
        data = yaml.safe_load(contract.read_text(encoding="utf-8"))
        auth_field = data["required_fields"]["authority"]
        assert "values" in auth_field
        assert "AUTHORITATIVE" in auth_field["values"]
        assert "AI_DRAFT" in auth_field["values"]


class TestV72ArtifactIdentityValidator:
    def test_passes_when_no_evidence_artifacts(self):
        from governance_validators_ext import validate_artifact_identity
        decl = {"planned_work_items": [_make_item("RELEASE_GATE", [])]}
        result = validate_artifact_identity(decl, _REPO)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_passes_when_all_fields_present(self):
        from governance_validators_ext import validate_artifact_identity
        artifacts = [{
            "path": "reports/test.yaml",
            "artifact_id": "FF-TEST/run-001/test.yaml",
            "authority": "AUTHORITATIVE",
        }]
        decl = {"planned_work_items": [_make_item("RELEASE_GATE", artifacts)]}
        result = validate_artifact_identity(decl, _REPO)
        assert result["result"] == "PASS"

    def test_fails_for_release_gate_missing_artifact_id(self):
        from governance_validators_ext import validate_artifact_identity
        artifacts = [{"path": "reports/test.yaml", "authority": "AUTHORITATIVE"}]
        decl = {"planned_work_items": [_make_item("RELEASE_GATE", artifacts)]}
        result = validate_artifact_identity(decl, _REPO)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_fails_for_release_gate_missing_authority(self):
        from governance_validators_ext import validate_artifact_identity
        artifacts = [{"path": "reports/test.yaml", "artifact_id": "FF-TEST/run-001/test.yaml"}]
        decl = {"planned_work_items": [_make_item("RELEASE_GATE", artifacts)]}
        result = validate_artifact_identity(decl, _REPO)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_warns_for_product_source_missing_fields(self):
        from governance_validators_ext import validate_artifact_identity
        artifacts = [{"path": "src/python/csv/models.py"}]  # no artifact_id, no authority
        decl = {"planned_work_items": [_make_item("PRODUCT_SOURCE", artifacts)]}
        result = validate_artifact_identity(decl, _REPO)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False

    def test_fails_for_invalid_authority_value_in_release_gate(self):
        from governance_validators_ext import validate_artifact_identity
        artifacts = [{
            "path": "reports/test.yaml",
            "artifact_id": "FF-TEST/run-001/test.yaml",
            "authority": "INVALID_VALUE",
        }]
        decl = {"planned_work_items": [_make_item("RELEASE_GATE", artifacts)]}
        result = validate_artifact_identity(decl, _REPO)
        assert result["result"] == "FAIL"

    def test_empty_declaration_passes(self):
        from governance_validators_ext import validate_artifact_identity
        result = validate_artifact_identity({}, _REPO)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_v72_registered_in_runner(self):
        from governance_validator_runner import run_all_governance_validators
        decl = {"planned_work_items": []}
        output = run_all_governance_validators(decl, _REPO)
        validator_names = [r["validator"] for r in output.get("validators", [])]
        assert "validate_artifact_identity" in validator_names
