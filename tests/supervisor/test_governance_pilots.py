"""Controlled governance pilot tests (Lane H, GRH-TC-010).

Exercises 6 pilot fixtures that cover: missing execution_method,
deprecated QUEUE_DECLARED_EXECUTION, REPLAYABLE overclaim without recipe,
forbidden state jump for PRODUCT_SOURCE, valid legacy backfill, and
GOVERNANCE_DOC short-circuit path.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES = REPO_ROOT / "tests/supervisor/fixtures/governance-pilots"
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


def _load_pilot(fixture_name: str) -> dict:
    path = FIXTURES / fixture_name
    if not path.exists():
        pytest.skip(f"Pilot fixture not found: {path}")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestPilot001ExecutionMethodMissing:
    """Pilot 001: PRODUCT_SOURCE missing execution_method → FAIL."""

    def test_pilot_fixture_loads(self):
        pilot = _load_pilot("pilot-001-execution-method-missing.yaml")
        assert pilot["pilot_id"] == "PILOT-001"

    def test_execution_method_required_fails(self):
        from governance_validators import validate_execution_method_required
        pilot = _load_pilot("pilot-001-execution-method-missing.yaml")
        result = validate_execution_method_required(pilot["declaration"])
        assert result["result"] == "FAIL", (
            f"Expected FAIL for missing execution_method, got {result['result']}"
        )
        assert result["blocks_sprint"] is True

    def test_fail_item_identifies_correct_item(self):
        from governance_validators import validate_execution_method_required
        pilot = _load_pilot("pilot-001-execution-method-missing.yaml")
        result = validate_execution_method_required(pilot["declaration"])
        assert any("PILOT-001-TC-001" in str(item) for item in result["items"])


class TestPilot002ManualUngoverned:
    """Pilot 002: MANUAL_UNGOVERNED without LEGACY_BACKFILLED claim → FAIL."""

    def test_pilot_fixture_loads(self):
        pilot = _load_pilot("pilot-002-queue-declared-deprecated.yaml")
        assert pilot["pilot_id"] == "PILOT-002"

    def test_manual_ungoverned_validator_rejects_without_backfill(self):
        from governance_validators import validate_manual_ungoverned_rejection
        pilot = _load_pilot("pilot-002-queue-declared-deprecated.yaml")
        result = validate_manual_ungoverned_rejection(pilot["declaration"])
        assert result["result"] == "FAIL", (
            f"MANUAL_UNGOVERNED without LEGACY_BACKFILLED should FAIL, got {result['result']}"
        )
        assert result["blocks_sprint"] is True

    def test_execution_method_field_present_passes_required_check(self):
        """MANUAL_UNGOVERNED is present so execution_method_required passes."""
        from governance_validators import validate_execution_method_required
        pilot = _load_pilot("pilot-002-queue-declared-deprecated.yaml")
        result = validate_execution_method_required(pilot["declaration"])
        # execution_method IS present (just wrong method), so required check passes
        assert result["result"] != "FAIL"


class TestPilot003ReplayableClaimWithoutRecipe:
    """Pilot 003: Claiming REPLAYABLE without replay_recipe_path → FAIL."""

    def test_pilot_fixture_loads(self):
        pilot = _load_pilot("pilot-003-replayable-claim-without-recipe.yaml")
        assert pilot["pilot_id"] == "PILOT-003"

    def test_replay_recipe_validator_fails(self):
        from governance_validators import validate_replay_recipe_required
        pilot = _load_pilot("pilot-003-replayable-claim-without-recipe.yaml")
        result = validate_replay_recipe_required(pilot["declaration"])
        assert result["result"] == "FAIL", (
            f"REPLAYABLE claim without recipe should FAIL, got {result['result']}"
        )
        assert result["blocks_sprint"] is True

    def test_fail_mentions_replayable_claim(self):
        from governance_validators import validate_replay_recipe_required
        pilot = _load_pilot("pilot-003-replayable-claim-without-recipe.yaml")
        result = validate_replay_recipe_required(pilot["declaration"])
        assert len(result["items"]) > 0
        item_text = str(result["items"])
        assert "REPLAYABLE" in item_text or "replay_recipe" in item_text.lower()


class TestPilot004ForbiddenStateJump:
    """Pilot 004: PRODUCT_SOURCE DISCOVERED→GOVERNANCE_ACCEPTED is forbidden."""

    def test_pilot_fixture_loads(self):
        pilot = _load_pilot("pilot-004-forbidden-state-jump.yaml")
        assert pilot["pilot_id"] == "PILOT-004"

    def test_state_machine_validator_fails(self):
        from governance_validators import validate_taskcard_state_transitions
        pilot = _load_pilot("pilot-004-forbidden-state-jump.yaml")
        result = validate_taskcard_state_transitions(pilot["declaration"])
        assert result["result"] == "FAIL", (
            f"Forbidden PRODUCT_SOURCE state jump should FAIL, got {result['result']}"
        )

    def test_fail_mentions_forbidden(self):
        from governance_validators import validate_taskcard_state_transitions
        pilot = _load_pilot("pilot-004-forbidden-state-jump.yaml")
        result = validate_taskcard_state_transitions(pilot["declaration"])
        issue_text = " ".join(str(item.get("issue", "")) for item in result.get("items", []))
        assert "FORBIDDEN" in issue_text or "forbidden" in issue_text.lower()


class TestPilot005LegacyBackfillAccepted:
    """Pilot 005: Properly formed legacy backfill passes all validators."""

    def test_pilot_fixture_loads(self):
        pilot = _load_pilot("pilot-005-legacy-backfill-accepted.yaml")
        assert pilot["pilot_id"] == "PILOT-005"

    def test_execution_method_passes(self):
        from governance_validators import validate_execution_method_required
        pilot = _load_pilot("pilot-005-legacy-backfill-accepted.yaml")
        result = validate_execution_method_required(pilot["declaration"])
        assert result["result"] != "FAIL"

    def test_claim_classification_passes(self):
        from governance_validators import validate_claim_classification
        pilot = _load_pilot("pilot-005-legacy-backfill-accepted.yaml")
        result = validate_claim_classification(pilot["declaration"])
        assert result["result"] != "FAIL"

    def test_state_transition_passes(self):
        from governance_validators import validate_taskcard_state_transitions
        pilot = _load_pilot("pilot-005-legacy-backfill-accepted.yaml")
        result = validate_taskcard_state_transitions(pilot["declaration"])
        assert result["result"] != "FAIL", f"Legacy backfill state transition failed: {result}"

    def test_replay_recipe_not_required_for_legacy_backfill(self):
        """Legacy backfill does not need replay_recipe_path."""
        from governance_validators import validate_replay_recipe_required
        pilot = _load_pilot("pilot-005-legacy-backfill-accepted.yaml")
        result = validate_replay_recipe_required(pilot["declaration"])
        assert result["result"] != "FAIL"

    def test_manual_ungoverned_validator_passes(self):
        from governance_validators import validate_manual_ungoverned_rejection
        pilot = _load_pilot("pilot-005-legacy-backfill-accepted.yaml")
        result = validate_manual_ungoverned_rejection(pilot["declaration"])
        assert result["result"] != "FAIL"


class TestPilot006GovernanceDocShortCircuit:
    """Pilot 006: GOVERNANCE_DOC DISCOVERED→GOVERNANCE_ACCEPTED is valid."""

    def test_pilot_fixture_loads(self):
        pilot = _load_pilot("pilot-006-governance-doc-short-circuit.yaml")
        assert pilot["pilot_id"] == "PILOT-006"

    def test_state_machine_allows_governance_doc_short_circuit(self):
        from governance_validators import validate_taskcard_state_transitions
        pilot = _load_pilot("pilot-006-governance-doc-short-circuit.yaml")
        result = validate_taskcard_state_transitions(pilot["declaration"])
        assert result["result"] != "FAIL", (
            f"GOVERNANCE_DOC DISCOVERED→GOVERNANCE_ACCEPTED should not FAIL: {result}"
        )

    def test_adoption_compliance_passes_for_investigation_only(self):
        """investigation_only exception_classification should exempt from transcript req."""
        import importlib
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "validate_adoption_compliance",
            str(REPO_ROOT / "tools/supervisor/validate_adoption_compliance.py"),
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        pilot = _load_pilot("pilot-006-governance-doc-short-circuit.yaml")
        item = pilot["declaration"]["planned_work_items"][0]
        assert mod._has_explicit_exemption(item) is True
