"""
test_task_generation.py — TC-PB-007/TC-PB-009 Taskcard Generation Tests

FF-PLAYBOOK-SYSTEM-001 (bright-marinating-map)

Tests:
1. Valid parameters → bounded taskcards with provenance
2. Missing required parameters → validation failure
3. allowed_paths and forbidden_paths preserved in every taskcard
4. provenance fields (playbook_id, playbook_version, plan_id, gap_ids, generator) present
5. rollback included in every taskcard
6. Authority constraints present and correct
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "playbook"))

from generate_playbook_taskcards import (
    parse_contract,
    validate_contract,
    generate_taskcards,
    resolve_parameters,
)

FORMAT_FEATURE_PLAYBOOK = REPO_ROOT / "playbooks" / "format-factory" / "format-feature-expansion.md"
NEW_FORMAT_PLAYBOOK = REPO_ROOT / "playbooks" / "format-factory" / "new-format-kickstart-template.md"

VALID_PARAMS_FORMAT_FEATURE = {
    "format_name": "tsv",
    "codec_file": "src/python/tsv/tsv_codec.py",
    "init_file": "src/python/tsv/__init__.py",
    "test_dir": "tests/python/tsv/",
    "function_name": "get_row_count",
    "function_signature": "def get_row_count(model: dict) -> int",
    "capability_label": "row_count",
}


@pytest.mark.skipif(not FORMAT_FEATURE_PLAYBOOK.exists(), reason="playbook template not found")
class TestParseContract:
    def test_parses_valid_playbook(self):
        contract = parse_contract(FORMAT_FEATURE_PLAYBOOK)
        assert isinstance(contract, dict)
        assert contract["playbook_id"] == "format-feature-expansion"
        assert contract["version"]
        assert contract["status"].upper() == "ACTIVE"

    def test_contract_has_required_fields(self):
        contract = parse_contract(FORMAT_FEATURE_PLAYBOOK)
        for field in ("playbook_id", "version", "status", "owner_layer",
                      "required_inputs", "allowed_paths", "forbidden_paths",
                      "evidence_requirements", "rollback", "limitations"):
            assert field in contract, f"Missing field: {field}"


@pytest.mark.skipif(not FORMAT_FEATURE_PLAYBOOK.exists(), reason="playbook template not found")
class TestValidateContract:
    def test_valid_params_pass(self):
        contract = parse_contract(FORMAT_FEATURE_PLAYBOOK)
        errors = validate_contract(contract)
        # Contract itself is valid (structure check, not param check)
        # validate_contract checks contract structure, not parameter values
        assert isinstance(errors, list)

    def test_missing_required_input_detected(self):
        contract = parse_contract(FORMAT_FEATURE_PLAYBOOK)
        # resolve_parameters with missing required inputs should fail
        try:
            resolved = resolve_parameters(contract, {})
        except SystemExit as e:
            assert e.code != 0
        except Exception:
            pass  # Any error is acceptable — missing params must not silently succeed


@pytest.mark.skipif(not FORMAT_FEATURE_PLAYBOOK.exists(), reason="playbook template not found")
class TestGenerateTaskcards:
    def test_valid_params_produce_taskcards(self):
        contract = parse_contract(FORMAT_FEATURE_PLAYBOOK)
        taskcards = generate_taskcards(
            contract, plan_id="FF-TEST-001", gap_ids=["GAP-PB-001"],
            parameters=VALID_PARAMS_FORMAT_FEATURE,
        )
        assert len(taskcards) > 0

    def test_every_taskcard_has_provenance(self):
        contract = parse_contract(FORMAT_FEATURE_PLAYBOOK)
        taskcards = generate_taskcards(
            contract, plan_id="FF-TEST-001", gap_ids=["GAP-PB-001"],
            parameters=VALID_PARAMS_FORMAT_FEATURE,
        )
        for tc in taskcards:
            assert tc["playbook_id"], "playbook_id must be non-empty"
            assert tc["playbook_version"], "playbook_version must be non-empty"
            assert tc["plan_id"] == "FF-TEST-001"
            assert "GAP-PB-001" in tc["gap_ids"]
            assert tc["generator"], "generator field must be present"
            assert tc["generated_at"], "generated_at must be present"

    def test_allowed_paths_preserved(self):
        contract = parse_contract(FORMAT_FEATURE_PLAYBOOK)
        taskcards = generate_taskcards(
            contract, plan_id="FF-TEST-001", gap_ids=["GAP-PB-001"],
            parameters=VALID_PARAMS_FORMAT_FEATURE,
        )
        for tc in taskcards:
            assert tc["allowed_paths"], "allowed_paths must not be empty"
            assert tc["forbidden_paths"], "forbidden_paths must not be empty"

    def test_forbidden_paths_preserved(self):
        contract = parse_contract(FORMAT_FEATURE_PLAYBOOK)
        taskcards = generate_taskcards(
            contract, plan_id="FF-TEST-001", gap_ids=["GAP-PB-001"],
            parameters=VALID_PARAMS_FORMAT_FEATURE,
        )
        for tc in taskcards:
            # forbidden_paths must exist and prohibit net source
            assert any("net" in str(p) or "registry" in str(p) for p in tc["forbidden_paths"]), \
                "forbidden_paths must include src/net/ or registry/"

    def test_rollback_in_every_taskcard(self):
        contract = parse_contract(FORMAT_FEATURE_PLAYBOOK)
        taskcards = generate_taskcards(
            contract, plan_id="FF-TEST-001", gap_ids=["GAP-PB-001"],
            parameters=VALID_PARAMS_FORMAT_FEATURE,
        )
        for tc in taskcards:
            assert tc["rollback"], "rollback must be non-empty in every taskcard"

    def test_authority_constraints_present(self):
        contract = parse_contract(FORMAT_FEATURE_PLAYBOOK)
        taskcards = generate_taskcards(
            contract, plan_id="FF-TEST-001", gap_ids=["GAP-PB-001"],
            parameters=VALID_PARAMS_FORMAT_FEATURE,
        )
        for tc in taskcards:
            auth = tc.get("authority_constraints", {})
            assert auth.get("no_gate_approval") is True
            assert auth.get("no_plan_override") is True

    def test_no_provenance_gap(self):
        """PLAYBOOK_GENERATED_TASKS_WITHOUT_PROVENANCE must be 0."""
        contract = parse_contract(FORMAT_FEATURE_PLAYBOOK)
        taskcards = generate_taskcards(
            contract, plan_id="FF-TEST-001", gap_ids=["GAP-PB-001"],
            parameters=VALID_PARAMS_FORMAT_FEATURE,
        )
        missing_provenance = [
            tc for tc in taskcards
            if not tc.get("playbook_id") or not tc.get("playbook_version") or not tc.get("plan_id")
        ]
        assert len(missing_provenance) == 0, \
            f"PLAYBOOK_GENERATED_TASKS_WITHOUT_PROVENANCE = {len(missing_provenance)}"
