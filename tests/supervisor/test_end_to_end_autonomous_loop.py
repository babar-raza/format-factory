"""Tests for end-to-end autonomous loop simulation.

Uses synthetic fixtures — no product source mutation.
Verifies that the autonomous loop does not stop early for invalid reasons.

Phase 8 of autonomous-system-audit sprint.
"""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "supervisor"))
from simulate_autonomous_loop import (
    AutonomousLoopSimulator,
    run_all_simulations,
    VALID_TERMINAL_STATES,
    INVALID_TERMINAL_STATES,
    SCENARIOS,
)


class TestValidInvalidTerminalStateConstants:
    """Test that the terminal state constants are correctly defined."""

    def test_valid_terminal_states_not_empty(self):
        assert len(VALID_TERMINAL_STATES) >= 6

    def test_invalid_terminal_states_not_empty(self):
        assert len(INVALID_TERMINAL_STATES) >= 10

    def test_no_overlap_valid_invalid(self):
        """Valid and invalid sets must not overlap."""
        overlap = VALID_TERMINAL_STATES & INVALID_TERMINAL_STATES
        assert overlap == frozenset(), f"Overlap detected: {overlap}"

    def test_accepted_is_invalid(self):
        assert "ACCEPTED" in INVALID_TERMINAL_STATES

    def test_accepted_with_limitations_is_invalid(self):
        assert "ACCEPTED_WITH_LIMITATIONS" in INVALID_TERMINAL_STATES

    def test_evidence_package_built_is_invalid(self):
        assert "EVIDENCE_PACKAGE_BUILT" in INVALID_TERMINAL_STATES

    def test_poc_ready_release_pending_is_valid(self):
        assert "POC_READY_CANDIDATE_AUTHORITY_VERIFIED_RELEASE_APPROVAL_PENDING" in VALID_TERMINAL_STATES

    def test_true_external_gate_is_valid(self):
        assert "TRUE_EXTERNAL_GATE" in VALID_TERMINAL_STATES

    def test_host_layer_missing_is_valid(self):
        assert "HOST_INVOCATION_LAYER_MISSING_WITH_WIRING_INSTRUCTIONS" in VALID_TERMINAL_STATES


class TestScenario1NonTerminalContinues:
    """Scenario 1: Non-terminal accepted sprint continues to POC."""

    def test_non_terminal_continues_to_poc(self):
        sim = AutonomousLoopSimulator({
            "name": "test_scenario_1",
            "initial_state": {
                "autonomous_continue": True,
                "safe_lanes_available": True,
                "poc_ready": False,
                "commercial_all_pass": False,
                "foss_pass_count": 0,
                "has_product_gaps": True,
            },
        })
        result = sim.run()
        assert result["passed"] is True
        assert result["terminal_state"] != "ACCEPTED"
        assert result["terminal_state"] != "ACCEPTED_WITH_LIMITATIONS"
        assert result["terminal_state"] != "NEXT_SPRINT_GENERATED"

    def test_accepted_verdict_does_not_stop_loop(self):
        """ACCEPTED supervisor verdict alone must not be a terminal state."""
        sim = AutonomousLoopSimulator({
            "name": "test_accepted_not_terminal",
            "initial_state": {
                "poc_ready": False,
                "commercial_all_pass": False,
                "foss_pass_count": 0,
                "has_product_gaps": True,
            },
        })
        result = sim.run()
        assert "ACCEPTED" not in VALID_TERMINAL_STATES, "ACCEPTED must not be valid terminal"
        assert result["terminal_state"] != "ACCEPTED"


class TestScenario2FalseHumanGate:
    """Scenario 2: Gate 11 preparation is agent-owned, never terminal."""

    def test_gate11_preparation_not_terminal(self):
        """Gate 11 PREPARATION does not stop the loop."""
        sim = AutonomousLoopSimulator({
            "name": "test_gate11_prep",
            "initial_state": {
                "poc_ready": False,
                "commercial_all_pass": False,
                "foss_pass_count": 0,
                "hard_stop_detected": False,  # preparation != hard stop
                "has_product_gaps": True,
            },
        })
        result = sim.run()
        assert result["passed"] is True
        assert result["terminal_state"] != "GATE_11_PREPARATION_NEEDED"
        assert "GATE_11_PREPARATION_NEEDED" in INVALID_TERMINAL_STATES


class TestScenario3ReleaseApprovalPending:
    """Scenario 3: POC ready + Gate 11 pending = valid terminal."""

    def test_poc_ready_release_pending_is_valid_terminal(self):
        sim = AutonomousLoopSimulator({
            "name": "test_poc_release_pending",
            "initial_state": {
                "poc_ready": True,
                "commercial_all_pass": True,
                "foss_pass_count": 3,
                "gate_11_approved": False,
            },
        })
        result = sim.run()
        assert result["passed"] is True
        assert "POC_READY" in result["terminal_state"]
        assert "RELEASE_APPROVAL_PENDING" in result["terminal_state"]
        assert result["cycles_run"] == 1  # Immediate terminal


class TestScenario4HostMissing:
    """Scenario 4: No host runner/CLI → HOST_INVOCATION_LAYER_MISSING."""

    def test_host_missing_classified_honestly(self):
        sim = AutonomousLoopSimulator({
            "name": "test_host_missing",
            "initial_state": {
                "poc_ready": False,
                "commercial_all_pass": False,
                "foss_pass_count": 0,
                "host_available": False,
                "has_product_gaps": True,
            },
        })
        result = sim.run()
        assert result["passed"] is True
        assert result["terminal_state"] == "HOST_INVOCATION_LAYER_MISSING_WITH_WIRING_INSTRUCTIONS"

    def test_host_missing_classification_is_valid_terminal(self):
        """HOST_INVOCATION_LAYER_MISSING_WITH_WIRING_INSTRUCTIONS is a valid terminal."""
        assert "HOST_INVOCATION_LAYER_MISSING_WITH_WIRING_INSTRUCTIONS" in VALID_TERMINAL_STATES


class TestScenario5AntiSkipFalsePositive:
    """Scenario 5: Anti-skip false positive causes repair/continue, not stop."""

    def test_anti_skip_false_positive_repaired_not_stopped(self):
        sim = AutonomousLoopSimulator({
            "name": "test_anti_skip_repair",
            "initial_state": {
                "anti_skip_all_pass": False,
                "poc_ready": False,
                "commercial_all_pass": False,
                "foss_pass_count": 0,
                "has_product_gaps": True,
            },
        })
        result = sim.run()
        assert result["passed"] is True
        assert "REPAIR_ANTI_SKIP_DISCOVERY" in result["actions"]
        assert result["terminal_state"] != "ANTI_SKIP_FALSE_POSITIVE"


class TestScenario6AdoptionComplianceRepaired:
    """Scenario 6: Adoption compliance failure → repair/continue."""

    def test_adoption_compliance_repaired(self):
        sim = AutonomousLoopSimulator({
            "name": "test_adoption_repair",
            "initial_state": {
                "adoption_compliant": False,
                "poc_ready": False,
                "commercial_all_pass": False,
                "foss_pass_count": 0,
                "has_product_gaps": True,
            },
        })
        result = sim.run()
        assert result["passed"] is True
        assert "REPAIR_ADOPTION_COMPLIANCE" in result["actions"]
        assert "ACCEPTED_WITH_LIMITATIONS" not in result["terminal_state"]


class TestScenario7MaxIterations:
    """Scenario 7: Max iterations → RUNTIME_LIMIT_WITH_CONTINUATION_PACKET."""

    def test_max_iterations_produces_checkpoint(self):
        sim = AutonomousLoopSimulator({
            "name": "test_max_iter",
            "initial_state": {
                "max_cycles": 2,
                "poc_ready": False,
                "commercial_all_pass": False,
                "foss_pass_count": 0,
                "has_product_gaps": True,
            },
        })
        result = sim.run()
        assert result["passed"] is True
        # Should reach runtime limit, not a hard stop
        assert result["terminal_state"] in (
            "RUNTIME_LIMIT_WITH_CONTINUATION_PACKET",
            "POC_READY_CANDIDATE_AUTHORITY_VERIFIED_RELEASE_APPROVAL_PENDING",
        )

    def test_runtime_limit_is_valid_terminal(self):
        assert "RUNTIME_LIMIT_WITH_CONTINUATION_PACKET" in VALID_TERMINAL_STATES


class TestScenario8ThreeCyclePoc:
    """Scenario 8: Three-cycle loop: cycle1 repair, cycle2 repair, cycle3 POC ready."""

    def test_three_cycle_loop(self):
        sim = AutonomousLoopSimulator({
            "name": "test_3_cycle",
            "initial_state": {
                "poc_ready": False,
                "commercial_all_pass": False,
                "foss_pass_count": 0,
                "adoption_compliant": False,
                "anti_skip_all_pass": False,
                "has_product_gaps": True,
            },
        })
        result = sim.run()
        assert result["passed"] is True
        assert result["cycles_run"] >= 3
        assert "REPAIR_ADOPTION_COMPLIANCE" in result["actions"]
        assert "REPAIR_ANTI_SKIP_DISCOVERY" in result["actions"]
        assert "CONTINUE_PRODUCT_TRAIN" in result["actions"]


class TestRunAllSimulations:
    """Test that all predefined scenarios pass."""

    def test_all_scenarios_pass(self):
        """All 8 predefined scenarios must pass."""
        report = run_all_simulations()
        assert report["all_passed"] is True, (
            f"Failed scenarios: {[r['scenario'] for r in report['results'] if not r['passed']]}\n"
            f"Details: {[r for r in report['results'] if not r['passed']]}"
        )

    def test_all_scenarios_have_valid_terminal(self):
        """Every scenario must end with a valid terminal state."""
        report = run_all_simulations()
        for result in report["results"]:
            ts = result["terminal_state"]
            assert ts not in INVALID_TERMINAL_STATES, (
                f"Scenario {result['scenario']} ended with INVALID terminal: {ts}"
            )
            assert ts in VALID_TERMINAL_STATES, (
                f"Scenario {result['scenario']} terminal {ts} not in VALID_TERMINAL_STATES"
            )

    def test_no_false_stops_in_any_scenario(self):
        """No scenario should have false stops."""
        report = run_all_simulations()
        for result in report["results"]:
            assert result["false_stops"] == [], (
                f"Scenario {result['scenario']} had false stops: {result['false_stops']}"
            )

    def test_scenario_count_matches(self):
        """All defined scenarios are tested."""
        report = run_all_simulations()
        assert report["total_scenarios"] == len(SCENARIOS)
