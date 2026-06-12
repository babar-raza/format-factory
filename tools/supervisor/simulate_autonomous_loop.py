"""
simulate_autonomous_loop.py — End-to-End Autonomous Loop Simulation

Simulates the autonomous execution loop using synthetic fixtures (no product mutation).
Verifies that the loop does not stop early for invalid reasons and correctly
handles all scenarios from the autonomous execution contract.

Usage:
    python tools/supervisor/simulate_autonomous_loop.py

Exit codes:
    0 — all simulations passed
    1 — one or more simulations failed
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent

# ─────────────────────────────────────────────────────────────
# Valid terminal states (from autonomous-execution-contract.md)
# ─────────────────────────────────────────────────────────────

VALID_TERMINAL_STATES = frozenset({
    "POC_READY_CANDIDATE_AUTHORITY_VERIFIED_RELEASE_APPROVAL_PENDING",
    "POC_READY_CANDIDATE_AUTHORITY_VERIFIED",
    "MAINSTREAM_POC_READY_CANDIDATE_AUTHORITY_VERIFIED_RELEASE_APPROVAL_PENDING",
    "MAINSTREAM_POC_READY_CANDIDATE_AUTHORITY_VERIFIED",
    "TRUE_EXTERNAL_GATE",
    "UNSAFE_WORKSPACE",
    "RUNTIME_LIMIT_WITH_CONTINUATION_PACKET",
    "HOST_INVOCATION_LAYER_MISSING_WITH_WIRING_INSTRUCTIONS",
    "HOST_RUNNER_LIVE_INVOCATION_BLOCKED_BY_POLICY",
})

INVALID_TERMINAL_STATES = frozenset({
    "ACCEPTED",
    "ACCEPTED_WITH_REWORK",
    "ACCEPTED_WITH_LIMITATIONS",
    "EVIDENCE_PACKAGE_BUILT",
    "NEXT_SPRINT_GENERATED",
    "MAX_ITERATIONS_REACHED",
    "GATE_11_PREPARATION_NEEDED",
    "COMMIT_PREPARATION_NEEDED",
    "PROOF_MATERIALIZATION_WARNING",
    "ANTI_SKIP_FALSE_POSITIVE",
    "PROMPT_QUALITY_WARNING",
    "MISSING_OPTIONAL_ACCELERATION",
    "HOST_RUNNER_DRY_RUN_ONLY",
})


@dataclass
class SimState:
    """State machine state for the simulated loop."""
    cycle: int = 0
    max_cycles: int = 10
    poc_ready: bool = False
    commercial_all_pass: bool = False
    foss_pass_count: int = 0
    autonomous_continue: bool = True
    safe_lanes_available: bool = True
    host_available: bool = True
    has_product_gaps: bool = True
    adoption_compliant: bool = True
    anti_skip_all_pass: bool = True
    gate_11_approved: bool = False
    hard_stop_detected: bool = False
    terminal_state: str = ""
    actions_taken: list[str] = field(default_factory=list)
    stop_reasons_encountered: list[str] = field(default_factory=list)
    false_stops_encountered: list[str] = field(default_factory=list)


class AutonomousLoopSimulator:
    """Simulates the autonomous execution loop without real product mutation."""

    def __init__(self, scenario: dict):
        self.scenario = scenario
        self.state = SimState(**{k: v for k, v in scenario.get("initial_state", {}).items() if k != "description"})

    def _inspect_state(self) -> dict:
        """Inspect current state (simulated)."""
        return {
            "cycle": self.state.cycle,
            "poc_ready": self.state.poc_ready,
            "commercial_all_pass": self.state.commercial_all_pass,
            "foss_pass_count": self.state.foss_pass_count,
            "autonomous_continue": self.state.autonomous_continue,
            "safe_lanes_available": self.state.safe_lanes_available,
            "host_available": self.state.host_available,
            "has_product_gaps": self.state.has_product_gaps,
            "adoption_compliant": self.state.adoption_compliant,
            "anti_skip_all_pass": self.state.anti_skip_all_pass,
            "gate_11_approved": self.state.gate_11_approved,
            "hard_stop_detected": self.state.hard_stop_detected,
        }

    def _classify_terminal_state(self, state_dict: dict) -> str | None:
        """Classify if current state is terminal. Returns None if non-terminal."""
        # True external gate: only if hard stop detected
        if state_dict["hard_stop_detected"]:
            return "TRUE_EXTERNAL_GATE"

        # POC ready + release pending
        if (state_dict["poc_ready"]
                and state_dict["commercial_all_pass"]
                and state_dict["foss_pass_count"] >= 3
                and not state_dict["gate_11_approved"]):
            return "POC_READY_CANDIDATE_AUTHORITY_VERIFIED_RELEASE_APPROVAL_PENDING"

        # POC ready + gate approved
        if (state_dict["poc_ready"]
                and state_dict["commercial_all_pass"]
                and state_dict["foss_pass_count"] >= 3
                and state_dict["gate_11_approved"]):
            return "POC_READY_CANDIDATE_AUTHORITY_VERIFIED"

        # Host layer missing
        if not state_dict["host_available"] and not state_dict["poc_ready"]:
            return "HOST_INVOCATION_LAYER_MISSING_WITH_WIRING_INSTRUCTIONS"

        # Max cycles (checkpoint rollover, not hard stop)
        if self.state.cycle >= self.state.max_cycles:
            return "RUNTIME_LIMIT_WITH_CONTINUATION_PACKET"

        # NOT terminal — continue
        return None

    def _validate_terminal_state(self, terminal: str) -> tuple[bool, str]:
        """Validate that a terminal state is valid per contract. Returns (valid, reason)."""
        if terminal in VALID_TERMINAL_STATES:
            return True, "Valid terminal state"
        if terminal in INVALID_TERMINAL_STATES:
            return False, f"INVALID terminal state: {terminal} (causes false stop)"
        # Unknown state — warn but allow
        return True, f"Unknown terminal state (not explicitly invalid): {terminal}"

    def _execute_next_action(self, state_dict: dict) -> dict:
        """Execute the next action (simulated). Never modifies real files."""
        actions = []

        if not state_dict["adoption_compliant"]:
            # Fix adoption compliance first
            self.state.adoption_compliant = True
            actions.append("REPAIR_ADOPTION_COMPLIANCE")

        if not state_dict["anti_skip_all_pass"]:
            # Fix anti-skip
            self.state.anti_skip_all_pass = True
            actions.append("REPAIR_ANTI_SKIP_DISCOVERY")

        if state_dict["has_product_gaps"] and not state_dict["poc_ready"]:
            # Continue product work
            self.state.foss_pass_count = min(self.state.foss_pass_count + 1, 4)
            if self.state.foss_pass_count >= 3 and not self.state.commercial_all_pass:
                self.state.commercial_all_pass = True
            if self.state.commercial_all_pass and self.state.foss_pass_count >= 3:
                self.state.poc_ready = True
            actions.append("CONTINUE_PRODUCT_TRAIN")

        if not state_dict["host_available"] and not state_dict["poc_ready"]:
            actions.append("GENERATE_CONTINUATION_PACKET")

        self.state.actions_taken.extend(actions)
        return {"actions": actions, "cycle": self.state.cycle}

    def run(self) -> dict:
        """Run the simulation for max_cycles or until terminal."""
        result = {
            "scenario": self.scenario.get("name", "unnamed"),
            "cycles_run": 0,
            "terminal_state": None,
            "terminal_valid": None,
            "false_stops": [],
            "actions": [],
            "passed": False,
            "reason": "",
        }

        while self.state.cycle < self.state.max_cycles:
            self.state.cycle += 1
            state_dict = self._inspect_state()

            # Classify terminal state
            terminal = self._classify_terminal_state(state_dict)

            if terminal:
                valid, reason = self._validate_terminal_state(terminal)
                result["terminal_state"] = terminal
                result["terminal_valid"] = valid
                result["cycles_run"] = self.state.cycle
                result["actions"] = self.state.actions_taken

                if not valid:
                    result["false_stops"].append(terminal)
                    result["passed"] = False
                    result["reason"] = f"FALSE STOP: {reason}"
                    return result

                # Valid terminal — check expected outcome
                expected = self.scenario.get("expected_terminal", None)
                if expected and terminal != expected:
                    # Check if it's in a family of expected states
                    expected_family = self.scenario.get("expected_terminal_family", [])
                    if not any(terminal.startswith(e) for e in expected_family):
                        result["passed"] = False
                        result["reason"] = f"Expected terminal '{expected}' but got '{terminal}'"
                        return result

                result["passed"] = True
                result["reason"] = f"Valid terminal reached: {terminal}"
                return result

            # Non-terminal: execute next action
            action_result = self._execute_next_action(state_dict)
            result["actions"].extend(action_result["actions"])

        # Max cycles hit
        terminal = "RUNTIME_LIMIT_WITH_CONTINUATION_PACKET"
        valid, reason = self._validate_terminal_state(terminal)
        result["terminal_state"] = terminal
        result["terminal_valid"] = valid
        result["cycles_run"] = self.state.cycle
        result["actions"] = self.state.actions_taken
        result["passed"] = valid
        result["reason"] = f"Runtime limit reached: {terminal}"
        return result


# ─────────────────────────────────────────────────────────────
# Scenarios
# ─────────────────────────────────────────────────────────────

SCENARIOS = [
    {
        "name": "scenario_1_non_terminal_accepted_continues",
        "description": "Non-terminal accepted sprint automatically produces next action",
        "initial_state": {
            "autonomous_continue": True,
            "safe_lanes_available": True,
            "poc_ready": False,
            "commercial_all_pass": False,
            "foss_pass_count": 0,
            "has_product_gaps": True,
        },
        "expected_terminal_family": ["POC_READY"],
        "expected_behavior": "Loop continues until POC ready",
        "must_not_stop_at": ["ACCEPTED", "EVIDENCE_PACKAGE_BUILT", "NEXT_SPRINT_GENERATED"],
    },
    {
        "name": "scenario_2_false_human_gate_preparation",
        "description": "Gate 11 PREPARATION is agent-owned, never terminal",
        "initial_state": {
            "poc_ready": False,
            "commercial_all_pass": False,
            "foss_pass_count": 0,
            "hard_stop_detected": False,  # preparation != stop
            "has_product_gaps": True,
        },
        "expected_terminal_family": ["POC_READY"],
        "expected_behavior": "Gate 11 preparation does not stop the loop",
    },
    {
        "name": "scenario_3_release_approval_after_poc",
        "description": "After POC ready, gate 11 approval pending is valid terminal",
        "initial_state": {
            "poc_ready": True,
            "commercial_all_pass": True,
            "foss_pass_count": 3,
            "gate_11_approved": False,
        },
        "expected_terminal": "POC_READY_CANDIDATE_AUTHORITY_VERIFIED_RELEASE_APPROVAL_PENDING",
        "expected_behavior": "POC ready with release pending is valid terminal",
    },
    {
        "name": "scenario_4_host_missing",
        "description": "POC not ready, no host runner/CLI → HOST_INVOCATION_LAYER_MISSING",
        "initial_state": {
            "poc_ready": False,
            "commercial_all_pass": False,
            "foss_pass_count": 0,
            "host_available": False,
            "has_product_gaps": True,
        },
        "expected_terminal": "HOST_INVOCATION_LAYER_MISSING_WITH_WIRING_INSTRUCTIONS",
        "expected_behavior": "Honest classification with wiring instructions",
    },
    {
        "name": "scenario_5_anti_skip_false_positive_repaired",
        "description": "Anti-skip false positive causes repair/continue, not stop",
        "initial_state": {
            "anti_skip_all_pass": False,
            "poc_ready": False,
            "commercial_all_pass": False,
            "foss_pass_count": 0,
            "has_product_gaps": True,
        },
        "expected_terminal_family": ["POC_READY"],
        "expected_behavior": "Anti-skip false positive repaired, loop continues",
        "must_not_stop_at": ["ANTI_SKIP_FALSE_POSITIVE", "ACCEPTED_WITH_LIMITATIONS"],
    },
    {
        "name": "scenario_6_adoption_compliance_failure_repaired",
        "description": "Adoption compliance failure causes repair/continue, not invalid stop",
        "initial_state": {
            "adoption_compliant": False,
            "poc_ready": False,
            "commercial_all_pass": False,
            "foss_pass_count": 0,
            "has_product_gaps": True,
        },
        "expected_terminal_family": ["POC_READY"],
        "expected_behavior": "Adoption compliance repaired, loop continues",
    },
    {
        "name": "scenario_7_max_iterations_checkpoint",
        "description": "Max iterations hit → continuation packet, not hard stop",
        "initial_state": {
            "max_cycles": 3,
            "poc_ready": False,
            "commercial_all_pass": False,
            "foss_pass_count": 0,
            "has_product_gaps": True,
        },
        "expected_terminal": "RUNTIME_LIMIT_WITH_CONTINUATION_PACKET",
        "expected_behavior": "Max iterations produces checkpoint, not complete",
    },
    {
        "name": "scenario_8_three_cycle_poc",
        "description": "Three-cycle loop: accepted → repair → POC ready",
        "initial_state": {
            "poc_ready": False,
            "commercial_all_pass": False,
            "foss_pass_count": 0,
            "adoption_compliant": False,
            "anti_skip_all_pass": False,
            "has_product_gaps": True,
        },
        "expected_terminal_family": ["POC_READY"],
        "min_cycles": 3,
        "expected_behavior": "Three cycles: repair then POC",
    },
]


def run_all_simulations() -> dict:
    """Run all scenarios and return aggregate results."""
    results = []
    all_passed = True

    for scenario in SCENARIOS:
        sim = AutonomousLoopSimulator(scenario)
        result = sim.run()
        results.append(result)
        if not result["passed"]:
            all_passed = False

    return {
        "all_passed": all_passed,
        "total_scenarios": len(SCENARIOS),
        "passed_count": sum(1 for r in results if r["passed"]),
        "failed_count": sum(1 for r in results if not r["passed"]),
        "results": results,
    }


def main() -> int:
    report = run_all_simulations()
    print(json.dumps(report, indent=2))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
