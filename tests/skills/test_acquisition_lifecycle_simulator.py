"""
test_acquisition_lifecycle_simulator.py -- Lane B Tests (FORMAT-FACTORY-R10)

Tests for acquisition_lifecycle_simulator.py.

COVERAGE:
  - simulate_lifecycle_state: all states, blockers, next_state, governance
  - simulate_format_acquisition: profile-based simulation
  - simulate_multi_format_acquisition: aggregate results, cross-format
  - simulate_standard_formats: known format profiles
  - Governance invariants: no source execution, no gate approval
  - Blocker detection: stale, missing audit, requirements not authoritative
  - State ordering: STATE_ORDER is correct
  - Determinism: same inputs → same simulation_id

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

from acquisition_lifecycle_simulator import (
    simulate_lifecycle_state,
    simulate_format_acquisition,
    simulate_multi_format_acquisition,
    simulate_standard_formats,
    KNOWN_FORMAT_PROFILES,
    STATE_ORDER,
    STATE_CANDIDATE,
    STATE_SUPPORT_MATRIX_AUDIT,
    STATE_SPEC_DISCOVERY,
    STATE_SPEC_NORMALIZATION,
    STATE_REQUIREMENTS_GENERATION,
    STATE_VERIFIER_REVIEW,
    STATE_DEC034_IV,
    STATE_PLANNING_READY,
    STATE_IMPLEMENTATION_SIMULATION,
    STATE_EVIDENCE_READY,
    STATE_BLOCKED,
    STATE_DEFERRED,
    _GOVERNANCE_FLAGS,
    _stable_hash,
)


# ---------------------------------------------------------------------------
# STATE_ORDER
# ---------------------------------------------------------------------------

class TestStateOrder:
    def test_candidate_is_lowest_non_terminal(self):
        assert STATE_ORDER[STATE_CANDIDATE] == 0

    def test_evidence_ready_is_highest_positive(self):
        positive_states = {k: v for k, v in STATE_ORDER.items() if v >= 0}
        assert max(positive_states.values()) == STATE_ORDER[STATE_EVIDENCE_READY]

    def test_blocked_is_negative(self):
        assert STATE_ORDER[STATE_BLOCKED] < 0

    def test_deferred_is_negative(self):
        assert STATE_ORDER[STATE_DEFERRED] < 0

    def test_progression_order_correct(self):
        ordered = [
            STATE_CANDIDATE, STATE_SUPPORT_MATRIX_AUDIT, STATE_SPEC_DISCOVERY,
            STATE_SPEC_NORMALIZATION, STATE_REQUIREMENTS_GENERATION, STATE_VERIFIER_REVIEW,
            STATE_DEC034_IV, STATE_PLANNING_READY, STATE_IMPLEMENTATION_SIMULATION, STATE_EVIDENCE_READY,
        ]
        for i in range(len(ordered) - 1):
            assert STATE_ORDER[ordered[i]] < STATE_ORDER[ordered[i + 1]]


# ---------------------------------------------------------------------------
# _stable_hash
# ---------------------------------------------------------------------------

class TestStableHash:
    def test_deterministic(self):
        assert _stable_hash({"a": 1}) == _stable_hash({"a": 1})

    def test_length_16(self):
        h = _stable_hash("test")
        assert len(h) == 16
        int(h, 16)


# ---------------------------------------------------------------------------
# simulate_lifecycle_state
# ---------------------------------------------------------------------------

class TestSimulateLifecycleState:
    def _minimal(self, state=STATE_CANDIDATE, fmt="hwpx", **kwargs):
        return simulate_lifecycle_state(fmt=fmt, current_state=state, **kwargs)

    def test_required_keys_present(self):
        result = self._minimal()
        for key in ["format_id", "current_state", "state_order", "next_state",
                    "is_terminal", "is_blocked", "spec_available", "spec_type",
                    "support_matrix_audited", "requirements_state", "stale_verdict",
                    "gates_passed", "active_blockers", "next_actions",
                    "evidence_requirements", "required_gates", "simulation_id",
                    "governance", "dry_run_only", "autonomous_execution_allowed"]:
            assert key in result, f"Missing: {key}"

    def test_candidate_state_order(self):
        r = self._minimal(STATE_CANDIDATE)
        assert r["state_order"] == 0

    def test_candidate_next_state_is_audit(self):
        r = self._minimal(STATE_CANDIDATE)
        assert r["next_state"] == STATE_SUPPORT_MATRIX_AUDIT

    def test_evidence_ready_is_terminal(self):
        r = self._minimal(STATE_EVIDENCE_READY)
        assert r["is_terminal"] is True
        assert r["next_state"] is None

    def test_blocked_is_terminal(self):
        r = self._minimal(STATE_BLOCKED)
        assert r["is_terminal"] is True

    def test_deferred_is_terminal(self):
        r = self._minimal(STATE_DEFERRED)
        assert r["is_terminal"] is True

    def test_stale_blocked_adds_blocker(self):
        r = simulate_lifecycle_state("hwpx", STATE_PLANNING_READY, stale_verdict="STALE_BLOCKED")
        assert "stale_blocked" in r["active_blockers"]
        assert r["is_blocked"] is True

    def test_unaudited_in_non_candidate_adds_blocker(self):
        r = simulate_lifecycle_state("hwpx", STATE_SPEC_DISCOVERY, support_matrix_audited=False)
        assert "support_matrix_audit_required" in r["active_blockers"]

    def test_unaudited_in_candidate_no_blocker(self):
        r = simulate_lifecycle_state("hwpx", STATE_CANDIDATE, support_matrix_audited=False)
        assert "support_matrix_audit_required" not in r["active_blockers"]

    def test_requirements_not_authoritative_in_planning_adds_blocker(self):
        r = simulate_lifecycle_state(
            "hwpx", STATE_PLANNING_READY,
            support_matrix_audited=True,
            requirements_state="REQUIREMENTS_PENDING",
        )
        assert "requirements_not_authoritative" in r["active_blockers"]

    def test_governance_flags_correct(self):
        r = self._minimal()
        gov = r["governance"]
        assert gov["commercial_product_ready"] is False
        assert gov["autonomous_execution_allowed"] is False
        assert gov["gate_self_approval_allowed"] is False
        assert gov["dry_run_only"] is True
        assert gov["simulation_only"] is True
        assert gov["unsupported_by_aspose_requires_audit"] is True

    def test_dry_run_only_true(self):
        assert self._minimal()["dry_run_only"] is True

    def test_autonomous_execution_allowed_false(self):
        assert self._minimal()["autonomous_execution_allowed"] is False

    def test_simulation_id_is_hex(self):
        r = self._minimal()
        int(r["simulation_id"], 16)

    def test_determinism(self):
        r1 = self._minimal()
        r2 = self._minimal()
        assert r1["simulation_id"] == r2["simulation_id"]

    def test_cross_format_different_simulation_ids(self):
        r_fods = simulate_lifecycle_state("fods", STATE_EVIDENCE_READY, requirements_state="REQUIREMENTS_AUTHORITATIVE", gates_passed=10)
        r_hwpx = simulate_lifecycle_state("hwpx", STATE_EVIDENCE_READY, requirements_state="REQUIREMENTS_AUTHORITATIVE", gates_passed=10)
        assert r_fods["simulation_id"] != r_hwpx["simulation_id"]

    def test_next_actions_non_empty(self):
        for state in [STATE_CANDIDATE, STATE_SPEC_DISCOVERY, STATE_PLANNING_READY]:
            r = simulate_lifecycle_state("hwpx", state, support_matrix_audited=True)
            assert len(r["next_actions"]) > 0

    def test_next_actions_are_sim_prefixed(self):
        r = self._minimal()
        for action in r["next_actions"]:
            assert action.startswith("[SIM]"), f"Non-SIM action: {action}"

    def test_format_id_in_result(self):
        r = simulate_lifecycle_state("hwpx", STATE_CANDIDATE)
        assert r["format_id"] == "hwpx"

    def test_explicit_blockers_included(self):
        r = simulate_lifecycle_state("hwpx", STATE_BLOCKED, blockers=["legal_clearance_required"])
        assert "legal_clearance_required" in r["active_blockers"]

    def test_deferred_reason_propagated(self):
        r = simulate_lifecycle_state("hwpx", STATE_DEFERRED, deferred_reason="awaiting patent review")
        assert r["deferred_reason"] == "awaiting patent review"

    def test_result_json_serializable(self):
        r = self._minimal()
        json.dumps(r)

    def test_all_states_return_valid_result(self):
        all_states = [
            STATE_CANDIDATE, STATE_SUPPORT_MATRIX_AUDIT, STATE_SPEC_DISCOVERY,
            STATE_SPEC_NORMALIZATION, STATE_REQUIREMENTS_GENERATION, STATE_VERIFIER_REVIEW,
            STATE_DEC034_IV, STATE_PLANNING_READY, STATE_IMPLEMENTATION_SIMULATION,
            STATE_EVIDENCE_READY, STATE_BLOCKED, STATE_DEFERRED,
        ]
        for state in all_states:
            r = simulate_lifecycle_state("hwpx", state, support_matrix_audited=True)
            assert r["current_state"] == state


# ---------------------------------------------------------------------------
# simulate_format_acquisition
# ---------------------------------------------------------------------------

class TestSimulateFormatAcquisition:
    def test_default_profile_is_candidate(self):
        r = simulate_format_acquisition("newformat")
        assert r["current_state"] == STATE_CANDIDATE

    def test_known_profile_used(self):
        r = simulate_format_acquisition("fods", KNOWN_FORMAT_PROFILES["fods"])
        assert r["current_state"] == STATE_EVIDENCE_READY

    def test_hwpx_is_candidate(self):
        r = simulate_format_acquisition("hwpx", KNOWN_FORMAT_PROFILES["hwpx"])
        assert r["current_state"] == STATE_CANDIDATE

    def test_governance_flags_in_result(self):
        r = simulate_format_acquisition("hwpx")
        assert r["governance"]["commercial_product_ready"] is False

    def test_json_serializable(self):
        r = simulate_format_acquisition("hwpx")
        json.dumps(r)


# ---------------------------------------------------------------------------
# simulate_multi_format_acquisition
# ---------------------------------------------------------------------------

class TestSimulateMultiFormatAcquisition:
    def _run(self):
        profiles = {
            "fods": KNOWN_FORMAT_PROFILES["fods"],
            "fodt": KNOWN_FORMAT_PROFILES["fodt"],
            "hwpx": KNOWN_FORMAT_PROFILES["hwpx"],
            "alz": KNOWN_FORMAT_PROFILES["alz"],
        }
        return simulate_multi_format_acquisition(profiles)

    def test_required_keys_present(self):
        r = self._run()
        for key in ["formats_simulated", "per_format", "all_planning_ready",
                    "any_blocked", "any_deferred", "state_distribution", "governance"]:
            assert key in r

    def test_formats_simulated_sorted(self):
        r = self._run()
        assert r["formats_simulated"] == sorted(r["formats_simulated"])

    def test_per_format_contains_all(self):
        r = self._run()
        assert "fods" in r["per_format"]
        assert "fodt" in r["per_format"]
        assert "hwpx" in r["per_format"]

    def test_state_distribution_sums_to_format_count(self):
        r = self._run()
        total = sum(r["state_distribution"].values())
        assert total == len(r["formats_simulated"])

    def test_fods_fodt_not_blocking_aggregate(self):
        """FODS/FODT are EVIDENCE_READY — should not add blockers."""
        profiles = {
            "fods": KNOWN_FORMAT_PROFILES["fods"],
            "fodt": KNOWN_FORMAT_PROFILES["fodt"],
        }
        r = simulate_multi_format_acquisition(profiles)
        assert r["all_planning_ready"] is True

    def test_candidate_formats_not_planning_ready(self):
        profiles = {"hwpx": KNOWN_FORMAT_PROFILES["hwpx"]}
        r = simulate_multi_format_acquisition(profiles)
        assert r["all_planning_ready"] is False

    def test_governance_in_aggregate(self):
        r = self._run()
        assert r["governance"]["commercial_product_ready"] is False

    def test_dry_run_only_true(self):
        r = self._run()
        assert r["dry_run_only"] is True

    def test_json_serializable(self):
        r = self._run()
        json.dumps(r)


# ---------------------------------------------------------------------------
# simulate_standard_formats
# ---------------------------------------------------------------------------

class TestSimulateStandardFormats:
    def test_returns_dict(self):
        r = simulate_standard_formats()
        assert isinstance(r, dict)

    def test_contains_fods_and_fodt(self):
        r = simulate_standard_formats()
        assert "fods" in r["per_format"]
        assert "fodt" in r["per_format"]

    def test_contains_candidate_formats(self):
        r = simulate_standard_formats()
        for fmt in ["hwpx", "hwp", "alz", "egg"]:
            assert fmt in r["per_format"]

    def test_fods_is_evidence_ready(self):
        r = simulate_standard_formats()
        assert r["per_format"]["fods"]["current_state"] == STATE_EVIDENCE_READY

    def test_hwpx_is_candidate(self):
        r = simulate_standard_formats()
        assert r["per_format"]["hwpx"]["current_state"] == STATE_CANDIDATE

    def test_governance_preserved(self):
        r = simulate_standard_formats()
        assert r["governance"]["commercial_product_ready"] is False
        assert r["autonomous_execution_allowed"] is False


# ---------------------------------------------------------------------------
# KNOWN_FORMAT_PROFILES
# ---------------------------------------------------------------------------

class TestKnownFormatProfiles:
    def test_fods_fodt_have_10_gates(self):
        assert KNOWN_FORMAT_PROFILES["fods"]["gates_passed"] == 10
        assert KNOWN_FORMAT_PROFILES["fodt"]["gates_passed"] == 10

    def test_fods_fodt_requirements_authoritative(self):
        assert KNOWN_FORMAT_PROFILES["fods"]["requirements_state"] == "REQUIREMENTS_AUTHORITATIVE"
        assert KNOWN_FORMAT_PROFILES["fodt"]["requirements_state"] == "REQUIREMENTS_AUTHORITATIVE"

    def test_candidate_formats_have_zero_gates(self):
        for fmt in ["hwpx", "hwp", "alz", "egg", "hwt"]:
            assert KNOWN_FORMAT_PROFILES[fmt]["gates_passed"] == 0

    def test_candidate_formats_not_audited(self):
        for fmt in ["hwpx", "hwp", "alz", "egg", "hwt"]:
            assert KNOWN_FORMAT_PROFILES[fmt]["support_matrix_audited"] is False
            assert KNOWN_FORMAT_PROFILES[fmt]["aspose_supported"] is None

    def test_aspose_supported_requires_audit(self):
        """No format should claim aspose_supported=True or False without audit."""
        for fmt, profile in KNOWN_FORMAT_PROFILES.items():
            if not profile.get("support_matrix_audited", False):
                assert profile.get("aspose_supported") is None, \
                    f"{fmt} claims aspose_supported without audit"

    def test_governance_flags_immutable(self):
        """Mutating a returned governance dict must not affect _GOVERNANCE_FLAGS."""
        r = simulate_format_acquisition("hwpx", KNOWN_FORMAT_PROFILES["hwpx"])
        r["governance"]["commercial_product_ready"] = True
        assert _GOVERNANCE_FLAGS["commercial_product_ready"] is False
