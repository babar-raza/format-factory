"""State machine enforcement tests against real taskcards (Lane G, GRE-TC-007).

Validates all GRH-TC and GR-REPLAY taskcards against the 15-state machine.
Tests:
- All real taskcards have valid start state
- All real taskcards have valid target state
- All real taskcards use allowed transitions
- GR-REPLAY taskcards use BACKFILLED_LEGACY_ACCEPTED → target path
- BACKFILLED_LEGACY_ACCEPTED does not count as repeatability proof
- Negative fixture for forbidden jump (PRODUCT_SOURCE DISCOVERED→GOVERNANCE_ACCEPTED)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

GRH_TC_DIR = REPO_ROOT / "taskcards/governance-repeatability-hardening"
GR_REPLAY_DIR = REPO_ROOT / "taskcards/governance-repeatability"
GRE_TC_DIR = REPO_ROOT / "taskcards/governance-repeatability-enforcement"

GRH_TC_IDS = [f"GRH-TC-{i:03d}" for i in range(1, 16)]
GR_REPLAY_IDS = ["GR-REPLAY-001", "GR-REPLAY-002", "GR-REPLAY-003", "GR-REPLAY-004"]


def _load_taskcard(path: Path) -> dict:
    if not path.exists():
        pytest.skip(f"Taskcard not found: {path}")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestGRHTCTaskcardsStateMachine:
    """Validate GRH-TC-001..015 against 15-state machine."""

    @pytest.mark.parametrize("tc_id", GRH_TC_IDS)
    def test_taskcard_exists(self, tc_id):
        path = GRH_TC_DIR / f"{tc_id}.yaml"
        assert path.exists(), f"Missing taskcard: {path}"

    @pytest.mark.parametrize("tc_id", GRH_TC_IDS)
    def test_taskcard_yaml_valid(self, tc_id):
        tc = _load_taskcard(GRH_TC_DIR / f"{tc_id}.yaml")
        assert isinstance(tc, dict)

    @pytest.mark.parametrize("tc_id", GRH_TC_IDS)
    def test_taskcard_id_matches_filename(self, tc_id):
        tc = _load_taskcard(GRH_TC_DIR / f"{tc_id}.yaml")
        assert tc.get("id") == tc_id, (
            f"Taskcard id {tc.get('id')!r} != filename {tc_id!r}"
        )

    @pytest.mark.parametrize("tc_id", GRH_TC_IDS)
    def test_start_state_is_valid(self, tc_id):
        from governance_validators import ALLOWED_TRANSITIONS
        tc = _load_taskcard(GRH_TC_DIR / f"{tc_id}.yaml")
        start = tc.get("state_machine_start")
        assert start in ALLOWED_TRANSITIONS, (
            f"{tc_id}: start state {start!r} not in 15-state machine"
        )

    @pytest.mark.parametrize("tc_id", GRH_TC_IDS)
    def test_target_state_is_valid(self, tc_id):
        from governance_validators import ALLOWED_TRANSITIONS
        tc = _load_taskcard(GRH_TC_DIR / f"{tc_id}.yaml")
        target = tc.get("state_machine_target")
        assert target in ALLOWED_TRANSITIONS, (
            f"{tc_id}: target state {target!r} not in 15-state machine"
        )

    @pytest.mark.parametrize("tc_id", GRH_TC_IDS)
    def test_governance_doc_state_transition_passes_validator(self, tc_id):
        from governance_validators import validate_taskcard_state_transitions
        tc = _load_taskcard(GRH_TC_DIR / f"{tc_id}.yaml")
        decl = {"planned_work_items": [{
            "item_id": tc_id,
            "item_type": tc.get("item_type", "GOVERNANCE_DOC"),
            "state_machine_start": tc.get("state_machine_start"),
            "state_machine_target": tc.get("state_machine_target"),
            "status": "completed",
        }]}
        result = validate_taskcard_state_transitions(decl)
        assert result["result"] != "FAIL", (
            f"{tc_id}: state transition validation FAILED: {result}"
        )

    @pytest.mark.parametrize("tc_id", GRH_TC_IDS)
    def test_taskcard_has_required_fields(self, tc_id):
        tc = _load_taskcard(GRH_TC_DIR / f"{tc_id}.yaml")
        for field in ("id", "status", "item_type", "state_machine_start", "state_machine_target"):
            assert field in tc, f"{tc_id}: missing required field {field!r}"


class TestGRReplayTaskcardsStateMachine:
    """Validate GR-REPLAY-001..004 against 15-state machine."""

    @pytest.mark.parametrize("tc_id", GR_REPLAY_IDS)
    def test_taskcard_exists(self, tc_id):
        path = GR_REPLAY_DIR / f"{tc_id}.yaml"
        assert path.exists(), f"Missing replay taskcard: {path}"

    @pytest.mark.parametrize("tc_id", GR_REPLAY_IDS)
    def test_current_state_is_backfilled_legacy_accepted(self, tc_id):
        tc = _load_taskcard(GR_REPLAY_DIR / f"{tc_id}.yaml")
        assert tc.get("current_state") == "BACKFILLED_LEGACY_ACCEPTED", (
            f"{tc_id}: expected current_state=BACKFILLED_LEGACY_ACCEPTED, "
            f"got {tc.get('current_state')!r}"
        )

    @pytest.mark.parametrize("tc_id", GR_REPLAY_IDS)
    def test_target_state_is_replay_recipe_recorded(self, tc_id):
        tc = _load_taskcard(GR_REPLAY_DIR / f"{tc_id}.yaml")
        assert tc.get("target_state") == "REPLAY_RECIPE_RECORDED", (
            f"{tc_id}: target_state should be REPLAY_RECIPE_RECORDED"
        )

    @pytest.mark.parametrize("tc_id", GR_REPLAY_IDS)
    def test_backfilled_does_not_count_as_repeatability_proof(self, tc_id):
        tc = _load_taskcard(GR_REPLAY_DIR / f"{tc_id}.yaml")
        # current_claim must be LEGACY_BACKFILLED, not any REPLAYABLE claim
        current_claim = tc.get("current_claim", "")
        assert "REPLAYABLE" not in current_claim, (
            f"{tc_id}: current_claim {current_claim!r} should not be REPLAYABLE"
        )
        assert current_claim == "LEGACY_BACKFILLED", (
            f"{tc_id}: current_claim should be LEGACY_BACKFILLED, got {current_claim!r}"
        )

    @pytest.mark.parametrize("tc_id", GR_REPLAY_IDS)
    def test_target_claim_is_replayable_not_yet(self, tc_id):
        tc = _load_taskcard(GR_REPLAY_DIR / f"{tc_id}.yaml")
        assert tc.get("target_claim") == "REPLAYABLE_NOT_YET_REPLAYED"


class TestNegativeForbiddenJump:
    """Negative tests: forbidden state jumps must be caught."""

    def test_product_source_discovered_to_governance_accepted_forbidden(self):
        from governance_validators import validate_taskcard_state_transitions
        decl = {"planned_work_items": [{
            "item_id": "TC-FORBIDDEN-001",
            "item_type": "PRODUCT_SOURCE",
            "product_track": "foss_python",
            "state_machine_start": "DISCOVERED",
            "state_machine_target": "GOVERNANCE_ACCEPTED",
            "status": "completed",
        }]}
        result = validate_taskcard_state_transitions(decl)
        assert result["result"] == "FAIL"
        issue_text = " ".join(str(i.get("issue", "")) for i in result.get("items", []))
        assert "FORBIDDEN" in issue_text

    def test_product_source_not_close_eligible_in_mutation_executed(self):
        from governance_validators import validate_taskcard_state_transitions
        decl = {"planned_work_items": [{
            "item_id": "TC-NOT-ELIGIBLE",
            "item_type": "PRODUCT_SOURCE",
            "state_machine_start": "MUTATION_BOUNDED",
            "state_machine_target": "MUTATION_EXECUTED",
            "status": "completed",
            "execution_method": "MANUAL_GOVERNED_BY_SKILL",
        }]}
        result = validate_taskcard_state_transitions(decl)
        assert result["result"] == "FAIL"
        issue_text = " ".join(str(i.get("issue", "")) for i in result.get("items", []))
        assert "close-eligible" in issue_text.lower()

    def test_governance_doc_not_forbidden_for_discovered_to_accepted(self):
        from governance_validators import validate_taskcard_state_transitions
        decl = {"planned_work_items": [{
            "item_id": "GR-TC-VALID",
            "item_type": "GOVERNANCE_DOC",
            "exception_classification": "investigation_only",
            "state_machine_start": "DISCOVERED",
            "state_machine_target": "GOVERNANCE_ACCEPTED",
            "status": "completed",
        }]}
        result = validate_taskcard_state_transitions(decl)
        assert result["result"] != "FAIL"


class TestClosedTaskcardsHaveCloseEligibleTargets:
    """All completed GRH-TC taskcards must target close-eligible states."""

    @pytest.mark.parametrize("tc_id", GRH_TC_IDS)
    def test_completed_taskcard_targets_close_eligible_state(self, tc_id):
        from governance_validators import CLOSE_ELIGIBLE_STATES
        tc = _load_taskcard(GRH_TC_DIR / f"{tc_id}.yaml")
        if tc.get("status") == "completed":
            target = tc.get("state_machine_target")
            assert target in CLOSE_ELIGIBLE_STATES, (
                f"{tc_id}: completed but target {target!r} not in CLOSE_ELIGIBLE_STATES"
            )
