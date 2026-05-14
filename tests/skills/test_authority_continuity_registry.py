"""
test_authority_continuity_registry.py -- Lane R9-1 Tests (CONWAY-R9)

Tests for authority_continuity_registry.py.

COVERAGE:
  - _stable_hash determinism + cross-input isolation
  - build_authority_entry: structure, governance flags, format isolation marker
  - build_full_registry: determinism, cross-format isolation, all_authoritative, any_stale_blocked
  - add_simulation_entry: append-only, no mutation of original
  - build_live_registry: structural validity (smoke test)
  - Governance flags are always False/True (immutable)
  - simulation_log is append-only
  - format_isolation_marker is correct

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

from authority_continuity_registry import (
    _stable_hash,
    build_authority_entry,
    build_full_registry,
    add_simulation_entry,
    build_live_registry,
    _GOVERNANCE_FLAGS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def minimal_gate_state():
    return {
        "gates_passed": 10,
        "gate_11_status": "commercial_readiness_in_progress",
        "gate_11_approved": False,
    }


@pytest.fixture
def fods_entry(minimal_gate_state):
    return build_authority_entry(
        fmt="fods",
        requirements_state="REQUIREMENTS_AUTHORITATIVE",
        accepted_requirement_ids=["FODS-REQ-001", "FODS-REQ-002", "FODS-REQ-003"],
        stale_verdict="FRESH",
        planning_slice_ids=["FODS-I-LOAD", "FODS-I-OBJECT-MODEL"],
        gate_state=minimal_gate_state,
        replay_fingerprint="abc123",
        simulation_log=None,
    )


@pytest.fixture
def fodt_entry(minimal_gate_state):
    return build_authority_entry(
        fmt="fodt",
        requirements_state="REQUIREMENTS_AUTHORITATIVE",
        accepted_requirement_ids=["FODT-REQ-001", "FODT-REQ-002"],
        stale_verdict="REVIEW_REQUIRED",
        planning_slice_ids=["FODT-I-LOAD"],
        gate_state=minimal_gate_state,
        replay_fingerprint="def456",
        simulation_log=None,
    )


# ---------------------------------------------------------------------------
# _stable_hash
# ---------------------------------------------------------------------------

class TestStableHash:
    def test_deterministic_string(self):
        h1 = _stable_hash("hello")
        h2 = _stable_hash("hello")
        assert h1 == h2

    def test_deterministic_dict(self):
        data = {"b": 2, "a": 1}
        h1 = _stable_hash(data)
        h2 = _stable_hash(data)
        assert h1 == h2

    def test_sorted_keys_invariant(self):
        """Dict key order must not affect hash."""
        h1 = _stable_hash({"a": 1, "b": 2})
        h2 = _stable_hash({"b": 2, "a": 1})
        assert h1 == h2

    def test_different_inputs_different_hashes(self):
        assert _stable_hash("hello") != _stable_hash("world")
        assert _stable_hash([1, 2]) != _stable_hash([2, 1])
        assert _stable_hash({"a": 1}) != _stable_hash({"a": 2})

    def test_list_order_matters(self):
        """List ordering IS significant for hash."""
        h1 = _stable_hash(["a", "b"])
        h2 = _stable_hash(["b", "a"])
        assert h1 != h2

    def test_hash_length_16(self):
        h = _stable_hash("test")
        assert len(h) == 16

    def test_hash_is_hex(self):
        h = _stable_hash({"key": "value"})
        int(h, 16)  # raises ValueError if not hex


# ---------------------------------------------------------------------------
# _GOVERNANCE_FLAGS
# ---------------------------------------------------------------------------

class TestGovernanceFlags:
    def test_commercial_product_ready_false(self):
        assert _GOVERNANCE_FLAGS["commercial_product_ready"] is False

    def test_autonomous_execution_allowed_false(self):
        assert _GOVERNANCE_FLAGS["autonomous_execution_allowed"] is False

    def test_gate_self_approval_allowed_false(self):
        assert _GOVERNANCE_FLAGS["gate_self_approval_allowed"] is False

    def test_dry_run_only_true(self):
        assert _GOVERNANCE_FLAGS["dry_run_only"] is True

    def test_simulation_only_true(self):
        assert _GOVERNANCE_FLAGS["simulation_only"] is True

    def test_implementation_requires_human_authorization_true(self):
        assert _GOVERNANCE_FLAGS["implementation_requires_human_authorization"] is True


# ---------------------------------------------------------------------------
# build_authority_entry
# ---------------------------------------------------------------------------

class TestBuildAuthorityEntry:
    def test_required_keys_present(self, fods_entry):
        required = {
            "authority_id", "format_id", "requirements_state",
            "accepted_requirement_count", "accepted_requirement_ids",
            "stale_verdict", "planning_slice_count", "planning_slice_ids",
            "gate_state", "source_hashes", "replay_fingerprint",
            "simulation_log", "dependency_lineage", "format_isolation_marker",
            "governance", "created_date",
        }
        assert required.issubset(fods_entry.keys())

    def test_format_id_correct(self, fods_entry):
        assert fods_entry["format_id"] == "fods"

    def test_requirements_state_propagated(self, fods_entry):
        assert fods_entry["requirements_state"] == "REQUIREMENTS_AUTHORITATIVE"

    def test_stale_verdict_propagated(self, fods_entry):
        assert fods_entry["stale_verdict"] == "FRESH"

    def test_req_ids_sorted(self, minimal_gate_state):
        entry = build_authority_entry(
            fmt="fods",
            requirements_state="REQUIREMENTS_AUTHORITATIVE",
            accepted_requirement_ids=["FODS-REQ-003", "FODS-REQ-001", "FODS-REQ-002"],
            stale_verdict="FRESH",
            planning_slice_ids=[],
            gate_state=minimal_gate_state,
        )
        assert entry["accepted_requirement_ids"] == sorted(["FODS-REQ-001", "FODS-REQ-002", "FODS-REQ-003"])

    def test_slice_ids_sorted(self, minimal_gate_state):
        entry = build_authority_entry(
            fmt="fods",
            requirements_state="REQUIREMENTS_AUTHORITATIVE",
            accepted_requirement_ids=[],
            stale_verdict="FRESH",
            planning_slice_ids=["FODS-I-SAVE", "FODS-I-LOAD"],
            gate_state=minimal_gate_state,
        )
        assert entry["planning_slice_ids"] == ["FODS-I-LOAD", "FODS-I-SAVE"]

    def test_accepted_requirement_count_matches(self, fods_entry):
        assert fods_entry["accepted_requirement_count"] == len(fods_entry["accepted_requirement_ids"])

    def test_planning_slice_count_matches(self, fods_entry):
        assert fods_entry["planning_slice_count"] == len(fods_entry["planning_slice_ids"])

    def test_format_isolation_marker_correct_fods(self, fods_entry):
        assert fods_entry["format_isolation_marker"] == "FORMAT:FODS"

    def test_format_isolation_marker_correct_fodt(self, fodt_entry):
        assert fodt_entry["format_isolation_marker"] == "FORMAT:FODT"

    def test_governance_flags_immutable(self, fods_entry):
        gov = fods_entry["governance"]
        assert gov["commercial_product_ready"] is False
        assert gov["autonomous_execution_allowed"] is False
        assert gov["gate_self_approval_allowed"] is False
        assert gov["dry_run_only"] is True
        assert gov["simulation_only"] is True
        assert gov["implementation_requires_human_authorization"] is True

    def test_governance_is_copy_not_reference(self, fods_entry):
        """Mutating entry governance must not affect _GOVERNANCE_FLAGS."""
        fods_entry["governance"]["commercial_product_ready"] = True
        assert _GOVERNANCE_FLAGS["commercial_product_ready"] is False

    def test_simulation_log_empty_when_none(self, fods_entry):
        assert fods_entry["simulation_log"] == []

    def test_simulation_log_copied_not_reference(self, minimal_gate_state):
        original_log = [{"simulation_id": "SIM-001", "simulation_status": "SIMULATION_PASS",
                          "summary": "test", "simulation_date": "2026-05-14", "appended_at_index": 0}]
        entry = build_authority_entry(
            fmt="fods",
            requirements_state="REQUIREMENTS_AUTHORITATIVE",
            accepted_requirement_ids=[],
            stale_verdict="FRESH",
            planning_slice_ids=[],
            gate_state=minimal_gate_state,
            simulation_log=original_log,
        )
        entry["simulation_log"].append({"extra": "entry"})
        assert len(original_log) == 1  # original not mutated

    def test_source_hashes_present(self, fods_entry):
        hashes = fods_entry["source_hashes"]
        assert "requirements_hash" in hashes
        assert "slice_hash" in hashes
        assert "gate_hash" in hashes

    def test_source_hashes_are_hex_strings(self, fods_entry):
        for key, val in fods_entry["source_hashes"].items():
            assert isinstance(val, str), f"{key} is not a string"
            int(val, 16)  # validates hex

    def test_authority_id_is_hex(self, fods_entry):
        int(fods_entry["authority_id"], 16)

    def test_dependency_lineage_empty_list(self, fods_entry):
        assert fods_entry["dependency_lineage"] == []

    def test_determinism_same_inputs(self, minimal_gate_state):
        kwargs = dict(
            fmt="fods",
            requirements_state="REQUIREMENTS_AUTHORITATIVE",
            accepted_requirement_ids=["FODS-REQ-001", "FODS-REQ-002"],
            stale_verdict="FRESH",
            planning_slice_ids=["FODS-I-LOAD"],
            gate_state=minimal_gate_state,
            replay_fingerprint="fp1",
        )
        e1 = build_authority_entry(**kwargs)
        e2 = build_authority_entry(**kwargs)
        assert e1["authority_id"] == e2["authority_id"]
        assert e1["source_hashes"] == e2["source_hashes"]

    def test_cross_format_isolation_different_authority_ids(self, fods_entry, fodt_entry):
        """fods and fodt must have different authority IDs even if other fields match."""
        assert fods_entry["authority_id"] != fodt_entry["authority_id"]

    def test_created_date_is_date_string(self, fods_entry):
        import re
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", fods_entry["created_date"])


# ---------------------------------------------------------------------------
# build_full_registry
# ---------------------------------------------------------------------------

class TestBuildFullRegistry:
    def test_required_keys(self, fods_entry, fodt_entry):
        reg = build_full_registry([fods_entry, fodt_entry])
        for key in ["registry_id", "format_count", "formats", "format_ids",
                    "all_authoritative", "any_stale_blocked", "governance", "created_date"]:
            assert key in reg

    def test_format_count_correct(self, fods_entry, fodt_entry):
        reg = build_full_registry([fods_entry, fodt_entry])
        assert reg["format_count"] == 2

    def test_format_ids_sorted(self, fods_entry, fodt_entry):
        reg = build_full_registry([fodt_entry, fods_entry])  # reversed input
        assert reg["format_ids"] == sorted(["fods", "fodt"])

    def test_formats_dict_keyed_by_format_id(self, fods_entry, fodt_entry):
        reg = build_full_registry([fods_entry, fodt_entry])
        assert "fods" in reg["formats"]
        assert "fodt" in reg["formats"]

    def test_all_authoritative_true_when_all_authoritative(self, fods_entry, fodt_entry):
        # Both REQUIREMENTS_AUTHORITATIVE
        reg = build_full_registry([fods_entry, fodt_entry])
        assert reg["all_authoritative"] is True

    def test_all_authoritative_false_when_one_not(self, fods_entry, minimal_gate_state):
        non_auth = build_authority_entry(
            fmt="fodt",
            requirements_state="REQUIREMENTS_PENDING",
            accepted_requirement_ids=[],
            stale_verdict="FRESH",
            planning_slice_ids=[],
            gate_state=minimal_gate_state,
        )
        reg = build_full_registry([fods_entry, non_auth])
        assert reg["all_authoritative"] is False

    def test_any_stale_blocked_false_when_none_blocked(self, fods_entry, fodt_entry):
        reg = build_full_registry([fods_entry, fodt_entry])
        assert reg["any_stale_blocked"] is False

    def test_any_stale_blocked_true_when_one_blocked(self, fods_entry, minimal_gate_state):
        stale_entry = build_authority_entry(
            fmt="fodt",
            requirements_state="REQUIREMENTS_AUTHORITATIVE",
            accepted_requirement_ids=[],
            stale_verdict="STALE_BLOCKED",
            planning_slice_ids=[],
            gate_state=minimal_gate_state,
        )
        reg = build_full_registry([fods_entry, stale_entry])
        assert reg["any_stale_blocked"] is True

    def test_registry_id_is_hex(self, fods_entry, fodt_entry):
        reg = build_full_registry([fods_entry, fodt_entry])
        int(reg["registry_id"], 16)

    def test_registry_determinism(self, fods_entry, fodt_entry):
        """Same inputs in different order must produce same registry_id."""
        reg1 = build_full_registry([fods_entry, fodt_entry])
        reg2 = build_full_registry([fodt_entry, fods_entry])
        assert reg1["registry_id"] == reg2["registry_id"]

    def test_governance_flags_in_registry(self, fods_entry, fodt_entry):
        reg = build_full_registry([fods_entry, fodt_entry])
        gov = reg["governance"]
        assert gov["commercial_product_ready"] is False
        assert gov["autonomous_execution_allowed"] is False
        assert gov["dry_run_only"] is True

    def test_empty_registry_valid(self):
        reg = build_full_registry([])
        assert reg["format_count"] == 0
        assert reg["formats"] == {}
        assert reg["all_authoritative"] is True  # vacuously true
        assert reg["any_stale_blocked"] is False


# ---------------------------------------------------------------------------
# add_simulation_entry
# ---------------------------------------------------------------------------

class TestAddSimulationEntry:
    def test_returns_new_dict(self, fods_entry):
        updated = add_simulation_entry(fods_entry, "SIM-001", "SIMULATION_PASS", "All checks passed.")
        assert updated is not fods_entry

    def test_does_not_mutate_original(self, fods_entry):
        original_len = len(fods_entry["simulation_log"])
        add_simulation_entry(fods_entry, "SIM-001", "SIMULATION_PASS", "test")
        assert len(fods_entry["simulation_log"]) == original_len

    def test_appends_to_simulation_log(self, fods_entry):
        updated = add_simulation_entry(fods_entry, "SIM-001", "SIMULATION_PASS", "OK")
        assert len(updated["simulation_log"]) == 1

    def test_appended_at_index_correct(self, fods_entry):
        e1 = add_simulation_entry(fods_entry, "SIM-001", "SIMULATION_PASS", "OK")
        e2 = add_simulation_entry(e1, "SIM-002", "SIMULATION_PASS", "Also OK")
        assert e1["simulation_log"][0]["appended_at_index"] == 0
        assert e2["simulation_log"][1]["appended_at_index"] == 1

    def test_simulation_id_recorded(self, fods_entry):
        updated = add_simulation_entry(fods_entry, "SIM-XYZ", "SIMULATION_PASS", "test")
        assert updated["simulation_log"][0]["simulation_id"] == "SIM-XYZ"

    def test_simulation_status_recorded(self, fods_entry):
        updated = add_simulation_entry(fods_entry, "SIM-001", "SIMULATION_FAIL", "Failed check")
        assert updated["simulation_log"][0]["simulation_status"] == "SIMULATION_FAIL"

    def test_summary_recorded(self, fods_entry):
        updated = add_simulation_entry(fods_entry, "SIM-001", "SIMULATION_PASS", "My summary")
        assert updated["simulation_log"][0]["summary"] == "My summary"

    def test_all_simulation_statuses_accepted(self, fods_entry):
        statuses = [
            "SIMULATION_PASS", "SIMULATION_FAIL", "BLOCKED_STALE",
            "BLOCKED_AUTHORITY", "BLOCKED_DEPENDENCY", "BLOCKED_GOVERNANCE",
            "REPLAY_MISMATCH",
        ]
        entry = fods_entry
        for i, status in enumerate(statuses):
            entry = add_simulation_entry(entry, f"SIM-{i:03d}", status, f"summary {i}")
        assert len(entry["simulation_log"]) == len(statuses)

    def test_simulation_log_is_append_only(self, fods_entry):
        """Earlier entries must not be modified when a new entry is appended."""
        e1 = add_simulation_entry(fods_entry, "SIM-001", "SIMULATION_PASS", "first")
        e2 = add_simulation_entry(e1, "SIM-002", "SIMULATION_FAIL", "second")
        # First entry is unchanged
        assert e2["simulation_log"][0]["simulation_id"] == "SIM-001"
        assert e2["simulation_log"][0]["simulation_status"] == "SIMULATION_PASS"

    def test_simulation_date_is_date_string(self, fods_entry):
        import re
        updated = add_simulation_entry(fods_entry, "SIM-001", "SIMULATION_PASS", "test")
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", updated["simulation_log"][0]["simulation_date"])


# ---------------------------------------------------------------------------
# build_live_registry (smoke test)
# ---------------------------------------------------------------------------

class TestBuildLiveRegistry:
    def test_returns_dict(self):
        reg = build_live_registry()
        assert isinstance(reg, dict)

    def test_has_registry_id(self):
        reg = build_live_registry()
        assert "registry_id" in reg

    def test_has_governance(self):
        reg = build_live_registry()
        assert "governance" in reg
        gov = reg["governance"]
        assert gov["commercial_product_ready"] is False
        assert gov["autonomous_execution_allowed"] is False

    def test_has_formats_key(self):
        reg = build_live_registry()
        assert "formats" in reg

    def test_format_count_matches_format_ids(self):
        reg = build_live_registry()
        if "error" not in reg:
            assert reg["format_count"] == len(reg["format_ids"])

    def test_formats_have_governance(self):
        reg = build_live_registry()
        for fmt_id, entry in reg.get("formats", {}).items():
            gov = entry.get("governance", {})
            assert gov.get("commercial_product_ready") is False, f"{fmt_id} commercial_product_ready not False"
            assert gov.get("autonomous_execution_allowed") is False, f"{fmt_id} autonomous_execution_allowed not False"

    def test_formats_have_format_isolation_markers(self):
        reg = build_live_registry()
        for fmt_id, entry in reg.get("formats", {}).items():
            marker = entry.get("format_isolation_marker", "")
            assert marker.startswith("FORMAT:"), f"{fmt_id} missing isolation marker"

    def test_formats_cross_isolated(self):
        """fods and fodt entries must have different authority IDs."""
        reg = build_live_registry()
        formats = reg.get("formats", {})
        if "fods" in formats and "fodt" in formats:
            assert formats["fods"]["authority_id"] != formats["fodt"]["authority_id"]

    def test_serializable_to_json(self):
        reg = build_live_registry()
        json.dumps(reg)  # must not raise


# ---------------------------------------------------------------------------
# Governance invariant (entries from live registry must respect all flags)
# ---------------------------------------------------------------------------

class TestGovernanceInvariants:
    def test_no_entry_can_have_commercial_product_ready_true(self, fods_entry, fodt_entry):
        for entry in [fods_entry, fodt_entry]:
            assert entry["governance"]["commercial_product_ready"] is False

    def test_no_entry_can_have_autonomous_execution_allowed_true(self, fods_entry, fodt_entry):
        for entry in [fods_entry, fodt_entry]:
            assert entry["governance"]["autonomous_execution_allowed"] is False

    def test_no_entry_can_have_gate_self_approval_true(self, fods_entry, fodt_entry):
        for entry in [fods_entry, fodt_entry]:
            assert entry["governance"]["gate_self_approval_allowed"] is False

    def test_cross_format_isolation_markers_differ(self, fods_entry, fodt_entry):
        assert fods_entry["format_isolation_marker"] != fodt_entry["format_isolation_marker"]

    def test_registry_governance_never_mutable(self, fods_entry, fodt_entry):
        reg = build_full_registry([fods_entry, fodt_entry])
        reg["governance"]["commercial_product_ready"] = True
        # Original _GOVERNANCE_FLAGS must not be affected
        assert _GOVERNANCE_FLAGS["commercial_product_ready"] is False
