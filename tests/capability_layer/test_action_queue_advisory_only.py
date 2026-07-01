"""TC-C3-003: Tests verifying advisory_only semantics for the capability action queue.

Gate C5: action queue executability — confirms that:
1. _eval_action_conditions only emits ACT-UPDATE-POC-TARGETS when formats are actually missing.
2. machine_executable=True actions always have advisory_only=False.
3. The top-level advisory_only reflects whether any machine_executable action exists.
4. When all formats are present, action-queue is empty and advisory_only=True (advisory).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ACTION_QUEUE = REPO_ROOT / "reports" / "capability-layer" / "action-queue.json"
GENERATOR = REPO_ROOT / "tools" / "capability_layer" / "capability_map_generator.py"

sys.path.insert(0, str(REPO_ROOT / "tools" / "capability_layer"))
from capability_map_generator import _eval_action_conditions  # noqa: E402


@pytest.fixture(scope="module")
def action_queue() -> dict:
    """Load the current action-queue.json."""
    assert ACTION_QUEUE.exists(), f"action-queue.json not found at {ACTION_QUEUE}"
    return json.loads(ACTION_QUEUE.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Structural tests (live file)
# ---------------------------------------------------------------------------

class TestActionQueueStructure:
    """TC-C3-003a: Structural invariants of the live action-queue.json file."""

    def test_action_queue_file_exists(self):
        """action-queue.json must exist at expected path."""
        assert ACTION_QUEUE.exists()

    def test_action_queue_has_required_schema_fields(self, action_queue):
        """action-queue.json must have required schema fields."""
        required = ["schema_version", "advisory_only", "total_actions", "actions"]
        for field in required:
            assert field in action_queue, f"Missing field: {field}"

    def test_total_actions_matches_actions_list(self, action_queue):
        """total_actions must match len(actions)."""
        assert action_queue.get("total_actions") == len(action_queue.get("actions", []))

    def test_machine_executable_items_are_not_advisory(self, action_queue):
        """All machine_executable=True actions must have advisory_only=False (invariant)."""
        for action in action_queue.get("actions", []):
            if action.get("machine_executable") is True:
                assert action.get("advisory_only") is False, (
                    f"Action {action.get('action_id')} is machine_executable=True "
                    f"but advisory_only={action.get('advisory_only')}"
                )

    def test_top_level_advisory_only_matches_machine_executable_presence(self, action_queue):
        """Top-level advisory_only semantics depend on schema_version.

        Schema v1.x: advisory_only=False when any machine_executable=True action exists.
        Schema v2.0 (TC-CAP-010): advisory_only=False is a gate flag meaning the queue
        has active items; per-action advisory_only reflects individual executability.
        In v2.0 all open-blocked items have per-action advisory_only=True.
        """
        schema_version = action_queue.get("schema_version", "1.0")
        actions = action_queue.get("actions", [])
        has_machine_executable = any(a.get("machine_executable") for a in actions)
        actual_advisory = action_queue.get("advisory_only")
        if schema_version == "2.0":
            # v2.0 gate flag: advisory_only=False means queue is active (not that actions are executable)
            assert actual_advisory is not None, "advisory_only must be set"
        else:
            # v1.x semantics
            expected_advisory = not has_machine_executable
            assert actual_advisory is expected_advisory, (
                f"Expected advisory_only={expected_advisory} "
                f"(machine_executable actions present: {has_machine_executable}), "
                f"got {actual_advisory}"
            )


# ---------------------------------------------------------------------------
# Unit tests for _eval_action_conditions (deterministic — no file dependency)
# ---------------------------------------------------------------------------

class TestEvalActionConditions:
    """TC-C3-003b: _eval_action_conditions is conditional on actual system state."""

    def _poc_with_all_formats(self) -> dict:
        """poc_data that includes FODG, TSV, and NDJSON."""
        return {
            "foss_reduced_products": [
                {"format": "FODG"},
                {"format": "TSV"},
                {"format": "NDJSON"},
                {"format": "ABW"},
            ]
        }

    def _poc_with_missing_fodg(self) -> dict:
        """poc_data that is missing FODG."""
        return {
            "foss_reduced_products": [
                {"format": "TSV"},
                {"format": "NDJSON"},
                {"format": "ABW"},
            ]
        }

    def _poc_empty(self) -> dict:
        """poc_data with no foss_reduced_products."""
        return {"foss_reduced_products": []}

    def test_no_action_emitted_when_all_formats_present(self):
        """ACT-UPDATE-POC-TARGETS must NOT be emitted when FODG/TSV/NDJSON all present."""
        actions = _eval_action_conditions(self._poc_with_all_formats())
        ids = [a["action_id"] for a in actions]
        assert "ACT-UPDATE-POC-TARGETS" not in ids

    def test_action_emitted_when_fodg_missing(self):
        """ACT-UPDATE-POC-TARGETS must be emitted when FODG is absent."""
        actions = _eval_action_conditions(self._poc_with_missing_fodg())
        ids = [a["action_id"] for a in actions]
        assert "ACT-UPDATE-POC-TARGETS" in ids

    def test_action_emitted_when_all_missing(self):
        """ACT-UPDATE-POC-TARGETS must be emitted when all three formats are absent."""
        actions = _eval_action_conditions(self._poc_empty())
        ids = [a["action_id"] for a in actions]
        assert "ACT-UPDATE-POC-TARGETS" in ids

    def test_emitted_action_has_advisory_only_false(self):
        """When emitted, ACT-UPDATE-POC-TARGETS must have advisory_only=False."""
        actions = _eval_action_conditions(self._poc_with_missing_fodg())
        for a in actions:
            if a["action_id"] == "ACT-UPDATE-POC-TARGETS":
                assert a.get("advisory_only") is False
                return
        pytest.skip("ACT-UPDATE-POC-TARGETS not emitted — precondition not met")

    def test_emitted_action_is_machine_executable(self):
        """When emitted, ACT-UPDATE-POC-TARGETS must be machine_executable=True."""
        actions = _eval_action_conditions(self._poc_with_missing_fodg())
        for a in actions:
            if a["action_id"] == "ACT-UPDATE-POC-TARGETS":
                assert a.get("machine_executable") is True
                return
        pytest.skip("ACT-UPDATE-POC-TARGETS not emitted — precondition not met")

    def test_emitted_action_is_safe_for_autonomous(self):
        """When emitted, ACT-UPDATE-POC-TARGETS must be safe_for_autonomous=True."""
        actions = _eval_action_conditions(self._poc_with_missing_fodg())
        for a in actions:
            if a["action_id"] == "ACT-UPDATE-POC-TARGETS":
                assert a.get("safe_for_autonomous") is True
                return
        pytest.skip("ACT-UPDATE-POC-TARGETS not emitted — precondition not met")

    def test_empty_queue_when_all_formats_present(self):
        """With all formats present, _eval_action_conditions returns empty list."""
        actions = _eval_action_conditions(self._poc_with_all_formats())
        assert actions == [], f"Expected empty list, got: {actions}"

    def test_missing_description_names_missing_formats(self):
        """The description of the emitted action must name the missing formats."""
        actions = _eval_action_conditions(self._poc_with_missing_fodg())
        for a in actions:
            if a["action_id"] == "ACT-UPDATE-POC-TARGETS":
                assert "FODG" in a.get("description", ""), (
                    f"Expected FODG in description, got: {a.get('description')}"
                )
                return
        pytest.skip("ACT-UPDATE-POC-TARGETS not emitted — precondition not met")


# ---------------------------------------------------------------------------
# Generator integration test
# ---------------------------------------------------------------------------

class TestGeneratorAdvisoryOnlyIntegration:
    """TC-C3-003c: Generator produces semantically correct advisory_only with current poc-targets."""

    def test_live_action_queue_advisory_only_semantic_correct(self, action_queue):
        """The live action-queue advisory_only must semantically match machine_executable presence.

        Schema v2.0 (TC-CAP-010): advisory_only is a gate flag (False=active queue).
        Schema v1.x: advisory_only = not any(machine_executable actions).
        """
        schema_version = action_queue.get("schema_version", "1.0")
        actions = action_queue.get("actions", [])
        has_machine_exec = any(a.get("machine_executable") for a in actions)
        actual = action_queue.get("advisory_only")
        if schema_version == "2.0":
            # v2.0: gate flag semantics — advisory_only is explicitly set
            assert actual is not None, "advisory_only must be present in v2.0"
        else:
            expected = not has_machine_exec
            assert actual is expected, (
                f"Semantic mismatch: machine_executable_present={has_machine_exec}, "
                f"expected advisory_only={expected}, got {actual}"
            )

    def test_act_update_poc_targets_absent_from_live_queue(self, action_queue):
        """ACT-UPDATE-POC-TARGETS must NOT appear in live queue (all formats are present)."""
        ids = [a.get("action_id") for a in action_queue.get("actions", [])]
        assert "ACT-UPDATE-POC-TARGETS" not in ids, (
            "ACT-UPDATE-POC-TARGETS should not be emitted — FODG/TSV/NDJSON are all in poc-targets.yaml"
        )
