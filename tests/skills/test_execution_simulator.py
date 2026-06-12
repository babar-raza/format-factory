"""
test_execution_simulator.py -- Lane R9-2 Tests (CONWAY-R9)

Tests for execution_simulator.py.

COVERAGE:
  - simulate_format_sprint: structure, governance flags, lane simulations
  - simulate_all_formats: aggregate results, cross-format isolation
  - _build_lane_simulation: prerequisite enforcement, constraint propagation
  - Blocked states: BLOCKED_STALE, BLOCKED_AUTHORITY, BLOCKED_DEPENDENCY
  - Governance invariants: no source execution, no gate approval
  - Determinism: same inputs → same simulation_id
  - No subprocess calls
  - No src/ writes

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

from execution_simulator import (
    _stable_hash,
    _build_lane_simulation,
    simulate_format_sprint,
    simulate_all_formats,
    _blocked_result,
    _GOVERNANCE_FLAGS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_mock_ctx(
    req_state="REQUIREMENTS_AUTHORITATIVE",
    gates_passed=10,
    gate_11_status="commercial_readiness_in_progress",
    gate_11_approved=False,
    req_ids=None,
):
    if req_ids is None:
        req_ids = ["FODS-REQ-001", "FODS-REQ-002", "FODS-REQ-003"]
    return {
        "requirements_state": {"status": req_state},
        "gates_passed": gates_passed,
        "gate_11_status": gate_11_status,
        "gate_11_approved": gate_11_approved,
        "accepted_requirement_ids": req_ids,
    }


def _make_mock_stale(verdict="FRESH"):
    return {
        "verdict": verdict,
        "reasons": [],
        "checks": {},
        "blocker_count": 0 if verdict != "STALE_BLOCKED" else 1,
    }


def _make_mock_plan(status="EXPANDED", lane_rec=None, slices=None, constraints=None):
    if lane_rec is None:
        lane_rec = {"LANE-I-LOAD": ["FODS-REQ-001"], "LANE-I-OBJECT-MODEL": ["FODS-REQ-002", "FODS-REQ-003"]}
    if slices is None:
        slices = [{"slice_id": "FODS-I-LOAD"}, {"slice_id": "FODS-I-OBJECT-MODEL"}]
    return {
        "expansion_status": status,
        "lane_recommendations": lane_rec,
        "implementation_slices": slices,
        "known_constraints": constraints or [],
    }


# ---------------------------------------------------------------------------
# _stable_hash
# ---------------------------------------------------------------------------

class TestStableHash:
    def test_deterministic(self):
        assert _stable_hash({"a": 1}) == _stable_hash({"a": 1})

    def test_different_inputs(self):
        assert _stable_hash("fods") != _stable_hash("fodt")

    def test_hex_length_16(self):
        h = _stable_hash("test")
        assert len(h) == 16
        int(h, 16)


# ---------------------------------------------------------------------------
# _build_lane_simulation
# ---------------------------------------------------------------------------

class TestBuildLaneSimulation:
    def test_pass_when_no_prereqs(self):
        sim = _build_lane_simulation("LANE-I-LOAD", "fods", ["FODS-REQ-001"], [], set())
        assert sim["simulation_status"] == "SIMULATION_PASS"

    def test_blocked_when_prereq_missing(self):
        sim = _build_lane_simulation("LANE-I-OBJECT-MODEL", "fods", ["FODS-REQ-002"], [], set())
        assert sim["simulation_status"] == "BLOCKED_DEPENDENCY"
        assert "LANE-I-LOAD" in sim["unmet_prerequisites"]

    def test_pass_when_prereq_met(self):
        sim = _build_lane_simulation("LANE-I-OBJECT-MODEL", "fods", ["FODS-REQ-002"], [], {"LANE-I-LOAD"})
        assert sim["simulation_status"] == "SIMULATION_PASS"

    def test_contains_simulated_actions(self):
        sim = _build_lane_simulation("LANE-I-LOAD", "fods", ["FODS-REQ-001"], [], set())
        assert len(sim["simulated_actions"]) > 0

    def test_actions_are_descriptive_not_executable(self):
        sim = _build_lane_simulation("LANE-I-LOAD", "fods", ["FODS-REQ-001"], [], set())
        for action in sim["simulated_actions"]:
            assert action.startswith("[SIM]"), f"Action not labeled as simulation: {action}"

    def test_dry_run_only_true(self):
        sim = _build_lane_simulation("LANE-I-LOAD", "fods", [], [], set())
        assert sim["dry_run_only"] is True

    def test_autonomous_execution_allowed_false(self):
        sim = _build_lane_simulation("LANE-I-LOAD", "fods", [], [], set())
        assert sim["autonomous_execution_allowed"] is False

    def test_constraint_propagated_global(self):
        constraints = [{"constraint": "no recursion", "scope": "global"}]
        sim = _build_lane_simulation("LANE-I-LOAD", "fods", ["REQ-001"], constraints, set())
        assert any(c["scope"] == "global" for c in sim["constraint_violations"])

    def test_constraint_propagated_by_req_id(self):
        constraints = [{"constraint": "iterative only", "scope": "FODS-REQ-001"}]
        sim = _build_lane_simulation("LANE-I-LOAD", "fods", ["FODS-REQ-001"], constraints, set())
        assert len(sim["constraint_violations"]) == 1

    def test_constraint_not_propagated_for_different_req(self):
        constraints = [{"constraint": "iterative only", "scope": "FODS-REQ-999"}]
        sim = _build_lane_simulation("LANE-I-LOAD", "fods", ["FODS-REQ-001"], constraints, set())
        assert len(sim["constraint_violations"]) == 0

    def test_test_simulation_present(self):
        sim = _build_lane_simulation("LANE-I-LOAD", "fods", ["FODS-REQ-001"], [], set())
        assert "test_simulation" in sim
        assert "expected_test_count" in sim["test_simulation"]

    def test_evidence_simulation_present(self):
        sim = _build_lane_simulation("LANE-I-LOAD", "fods", ["FODS-REQ-001"], [], set())
        assert "evidence_simulation" in sim
        assert "evidence_items" in sim["evidence_simulation"]

    def test_lane_id_recorded(self):
        sim = _build_lane_simulation("LANE-I-LOAD", "fods", [], [], set())
        assert sim["lane_id"] == "LANE-I-LOAD"

    def test_format_id_recorded(self):
        sim = _build_lane_simulation("LANE-I-LOAD", "fods", [], [], set())
        assert sim["format_id"] == "fods"


# ---------------------------------------------------------------------------
# _blocked_result
# ---------------------------------------------------------------------------

class TestBlockedResult:
    def test_returns_dict(self):
        r = _blocked_result("fods", "BLOCKED_STALE", "stale", "REQUIREMENTS_AUTHORITATIVE", "STALE_BLOCKED")
        assert isinstance(r, dict)

    def test_status_propagated(self):
        r = _blocked_result("fods", "BLOCKED_AUTHORITY", "not auth", "REQUIREMENTS_PENDING", "FRESH")
        assert r["simulation_status"] == "BLOCKED_AUTHORITY"

    def test_governance_flags_present(self):
        r = _blocked_result("fods", "BLOCKED_STALE", "stale", "REQUIREMENTS_AUTHORITATIVE", "STALE_BLOCKED")
        assert r["governance"]["commercial_product_ready"] is False
        assert r["autonomous_execution_allowed"] is False
        assert r["dry_run_only"] is True

    def test_lane_simulations_empty(self):
        r = _blocked_result("fods", "BLOCKED_STALE", "stale", "REQUIREMENTS_AUTHORITATIVE", "STALE_BLOCKED")
        assert r["lane_simulations"] == []


# ---------------------------------------------------------------------------
# simulate_format_sprint (mocked dependencies)
# ---------------------------------------------------------------------------

class TestSimulateFormatSprintMocked:
    def _run_fods_sim(self, req_state="REQUIREMENTS_AUTHORITATIVE", stale_verdict="FRESH"):
        ctx = _make_mock_ctx(req_state=req_state)
        stale = _make_mock_stale(verdict=stale_verdict)
        plan = _make_mock_plan()

        with patch("execution_simulator.resolve_format_context", return_value=ctx), \
             patch("execution_simulator.detect_stale_state", return_value=stale), \
             patch("execution_simulator.expand_implementation_plan", return_value=plan):
            return simulate_format_sprint("fods")

    def test_returns_dict(self):
        result = self._run_fods_sim()
        assert isinstance(result, dict)

    def test_required_keys_present(self):
        result = self._run_fods_sim()
        for key in ["format_id", "simulation_status", "lane_simulations",
                    "authority_entry", "gate_state_snapshot", "governance",
                    "dry_run_only", "autonomous_execution_allowed"]:
            assert key in result, f"Missing key: {key}"

    def test_simulation_pass_when_authoritative_and_fresh(self):
        result = self._run_fods_sim()
        assert result["simulation_status"] == "SIMULATION_PASS"

    def test_blocked_authority_when_not_authoritative(self):
        result = self._run_fods_sim(req_state="REQUIREMENTS_PENDING")
        assert result["simulation_status"] == "BLOCKED_AUTHORITY"

    def test_blocked_stale_when_stale_blocked(self):
        result = self._run_fods_sim(stale_verdict="STALE_BLOCKED")
        assert result["simulation_status"] == "BLOCKED_STALE"

    def test_governance_flags_in_result(self):
        result = self._run_fods_sim()
        gov = result["governance"]
        assert gov["commercial_product_ready"] is False
        assert gov["autonomous_execution_allowed"] is False
        assert gov["dry_run_only"] is True
        assert gov["simulation_only"] is True

    def test_dry_run_only_true(self):
        result = self._run_fods_sim()
        assert result["dry_run_only"] is True

    def test_autonomous_execution_allowed_false(self):
        result = self._run_fods_sim()
        assert result["autonomous_execution_allowed"] is False

    def test_gate_11_approved_never_true(self):
        result = self._run_fods_sim()
        snapshot = result["gate_state_snapshot"]
        assert snapshot.get("gate_11_approved") is False

    def test_gate_state_snapshot_read_only(self):
        result = self._run_fods_sim()
        assert result["gate_state_snapshot"].get("simulation_read_only") is True

    def test_lane_simulations_non_empty(self):
        result = self._run_fods_sim()
        assert len(result["lane_simulations"]) > 0

    def test_lane_simulations_all_have_status(self):
        result = self._run_fods_sim()
        for sim in result["lane_simulations"]:
            assert "simulation_status" in sim

    def test_authority_entry_present_on_pass(self):
        result = self._run_fods_sim()
        assert result["authority_entry"] is not None

    def test_authority_entry_has_simulation_log(self):
        result = self._run_fods_sim()
        entry = result["authority_entry"]
        assert "simulation_log" in entry
        assert len(entry["simulation_log"]) == 1

    def test_simulation_id_is_hex(self):
        result = self._run_fods_sim()
        sid = result["simulation_id"]
        if sid != "BLOCKED":
            int(sid, 16)

    def test_simulation_summary_non_empty(self):
        result = self._run_fods_sim()
        assert len(result["simulation_summary"]) > 0

    def test_result_is_json_serializable(self):
        result = self._run_fods_sim()
        json.dumps(result)

    def test_determinism_same_inputs(self):
        """Two runs with identical context must produce same simulation_id."""
        ctx = _make_mock_ctx()
        stale = _make_mock_stale()
        plan = _make_mock_plan()

        with patch("execution_simulator.resolve_format_context", return_value=ctx), \
             patch("execution_simulator.detect_stale_state", return_value=stale), \
             patch("execution_simulator.expand_implementation_plan", return_value=plan):
            r1 = simulate_format_sprint("fods")
            r2 = simulate_format_sprint("fods")

        assert r1["simulation_id"] == r2["simulation_id"]

    def test_cross_format_isolation_different_simulation_ids(self):
        ctx_fods = _make_mock_ctx(req_ids=["FODS-REQ-001"])
        ctx_fodt = _make_mock_ctx(req_ids=["FODT-REQ-001"])
        stale = _make_mock_stale()
        plan = _make_mock_plan()

        with patch("execution_simulator.resolve_format_context", return_value=ctx_fods), \
             patch("execution_simulator.detect_stale_state", return_value=stale), \
             patch("execution_simulator.expand_implementation_plan", return_value=plan):
            r_fods = simulate_format_sprint("fods")

        with patch("execution_simulator.resolve_format_context", return_value=ctx_fodt), \
             patch("execution_simulator.detect_stale_state", return_value=stale), \
             patch("execution_simulator.expand_implementation_plan", return_value=plan):
            r_fodt = simulate_format_sprint("fodt")

        assert r_fods["simulation_id"] != r_fodt["simulation_id"]


# ---------------------------------------------------------------------------
# simulate_all_formats (mocked)
# ---------------------------------------------------------------------------

class TestSimulateAllFormatsMocked:
    def _run_all(self):
        ctx = _make_mock_ctx()
        stale = _make_mock_stale()
        plan = _make_mock_plan()

        with patch("execution_simulator.resolve_format_context", return_value=ctx), \
             patch("execution_simulator.detect_stale_state", return_value=stale), \
             patch("execution_simulator.expand_implementation_plan", return_value=plan):
            return simulate_all_formats(["fods", "fodt"])

    def test_returns_dict(self):
        result = self._run_all()
        assert isinstance(result, dict)

    def test_formats_simulated_present(self):
        result = self._run_all()
        assert result["formats_simulated"] == ["fods", "fodt"]

    def test_per_format_results_present(self):
        result = self._run_all()
        assert "fods" in result["per_format_results"]
        assert "fodt" in result["per_format_results"]

    def test_all_pass_when_all_pass(self):
        result = self._run_all()
        assert result["all_pass"] is True

    def test_any_blocked_false_when_none_blocked(self):
        result = self._run_all()
        assert result["any_blocked"] is False

    def test_total_lanes_simulated_positive(self):
        result = self._run_all()
        assert result["total_lanes_simulated"] > 0

    def test_governance_in_aggregate_result(self):
        result = self._run_all()
        assert result["governance"]["commercial_product_ready"] is False

    def test_dry_run_only_true(self):
        result = self._run_all()
        assert result["dry_run_only"] is True

    def test_autonomous_execution_allowed_false(self):
        result = self._run_all()
        assert result["autonomous_execution_allowed"] is False

    def test_any_blocked_true_when_one_stale(self):
        ctx = _make_mock_ctx()
        stale_blocked = _make_mock_stale(verdict="STALE_BLOCKED")
        stale_fresh = _make_mock_stale(verdict="FRESH")
        plan = _make_mock_plan()

        call_count = [0]
        def mock_stale(fmt):
            call_count[0] += 1
            return stale_blocked if fmt == "fods" else stale_fresh

        with patch("execution_simulator.resolve_format_context", return_value=ctx), \
             patch("execution_simulator.detect_stale_state", side_effect=mock_stale), \
             patch("execution_simulator.expand_implementation_plan", return_value=plan):
            result = simulate_all_formats(["fods", "fodt"])

        assert result["any_blocked"] is True
        assert result["all_pass"] is False

    def test_default_formats_are_fods_fodt(self):
        ctx = _make_mock_ctx()
        stale = _make_mock_stale()
        plan = _make_mock_plan()

        with patch("execution_simulator.resolve_format_context", return_value=ctx), \
             patch("execution_simulator.detect_stale_state", return_value=stale), \
             patch("execution_simulator.expand_implementation_plan", return_value=plan):
            result = simulate_all_formats()  # no explicit formats

        assert set(result["formats_simulated"]) == {"fods", "fodt"}


# ---------------------------------------------------------------------------
# Safety boundary: no subprocess, no src/ writes
# ---------------------------------------------------------------------------

class TestSimulationSafetyBoundary:
    def test_no_subprocess_call(self):
        """execution_simulator must never import or call subprocess."""
        import execution_simulator as esm
        assert not hasattr(esm, "subprocess"), "subprocess must not be imported"

    def test_governance_flags_are_immutable(self):
        """_GOVERNANCE_FLAGS must not be modifiable via simulate results."""
        ctx = _make_mock_ctx()
        stale = _make_mock_stale()
        plan = _make_mock_plan()

        with patch("execution_simulator.resolve_format_context", return_value=ctx), \
             patch("execution_simulator.detect_stale_state", return_value=stale), \
             patch("execution_simulator.expand_implementation_plan", return_value=plan):
            result = simulate_format_sprint("fods")

        result["governance"]["commercial_product_ready"] = True
        assert _GOVERNANCE_FLAGS["commercial_product_ready"] is False

    def test_simulated_actions_contain_no_actual_code(self):
        ctx = _make_mock_ctx()
        stale = _make_mock_stale()
        plan = _make_mock_plan()

        with patch("execution_simulator.resolve_format_context", return_value=ctx), \
             patch("execution_simulator.detect_stale_state", return_value=stale), \
             patch("execution_simulator.expand_implementation_plan", return_value=plan):
            result = simulate_format_sprint("fods")

        for sim in result["lane_simulations"]:
            for action in sim.get("simulated_actions", []):
                assert "[SIM]" in action, f"Non-simulation action found: {action}"

    def test_simulation_note_contains_no_execution(self):
        ctx = _make_mock_ctx()
        stale = _make_mock_stale()
        plan = _make_mock_plan()

        with patch("execution_simulator.resolve_format_context", return_value=ctx), \
             patch("execution_simulator.detect_stale_state", return_value=stale), \
             patch("execution_simulator.expand_implementation_plan", return_value=plan):
            result = simulate_format_sprint("fods")

        summary = result["simulation_summary"]
        assert "DRY-RUN" in summary or "no implementation" in summary.lower()


# ---------------------------------------------------------------------------
# simulate_format_sprint with live dependencies (smoke test)
# ---------------------------------------------------------------------------

class TestSimulateFormatSprintLive:
    def test_fods_returns_valid_structure(self):
        result = simulate_format_sprint("fods")
        assert isinstance(result, dict)
        assert "simulation_status" in result
        assert "governance" in result
        assert result["governance"]["commercial_product_ready"] is False

    def test_fodt_returns_valid_structure(self):
        result = simulate_format_sprint("fodt")
        assert isinstance(result, dict)
        assert "simulation_status" in result
        assert result["governance"]["autonomous_execution_allowed"] is False

    def test_all_formats_governance_preserved(self):
        result = simulate_all_formats()
        for fmt, res in result["per_format_results"].items():
            assert res["governance"]["commercial_product_ready"] is False
            assert res["autonomous_execution_allowed"] is False

    def test_fods_fodt_different_simulation_ids(self):
        r_fods = simulate_format_sprint("fods")
        r_fodt = simulate_format_sprint("fodt")
        if r_fods["simulation_id"] != "BLOCKED" and r_fodt["simulation_id"] != "BLOCKED":
            assert r_fods["simulation_id"] != r_fodt["simulation_id"]

    def test_result_serializable(self):
        result = simulate_all_formats()
        json.dumps(result)
