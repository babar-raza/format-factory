"""Tests for Gate 11 state contract implementation (TC-GFB-022, FF-MR-2026-001).

Tests:
1. evaluate_gate11_readiness: format meeting all P1-P10 → GATE_11_READY
2. evaluate_gate11_readiness: format missing one criterion → not GATE_11_READY
3. Check 11 in check_continuation.py: STOP when product is GATE_11_READY
4. Check 11: other products with NOT_READY may continue
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


class TestGateStatesRegistry:
    """Tests for registry/gate-states.yaml."""

    def test_gate_states_yaml_exists(self):
        """registry/gate-states.yaml must exist after TC-GFB-022."""
        path = REPO_ROOT / "registry" / "gate-states.yaml"
        assert path.exists(), "registry/gate-states.yaml not found"

    def test_gate_11_ready_state_defined(self):
        """GATE_11_READY must be defined in gate_states list."""
        path = REPO_ROOT / "registry" / "gate-states.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        state_ids = [s["state_id"] for s in data.get("gate_states", [])]
        assert "GATE_11_READY" in state_ids, f"GATE_11_READY not found in {state_ids}"

    def test_gate_11_ready_has_per_product_scope(self):
        """GATE_11_READY must be per_product=true."""
        path = REPO_ROOT / "registry" / "gate-states.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        g11 = next((s for s in data["gate_states"] if s["state_id"] == "GATE_11_READY"), None)
        assert g11 is not None
        assert g11.get("per_product") is True

    def test_format_gate_states_exist(self):
        """format_gate_states section must exist with at least one format."""
        path = REPO_ROOT / "registry" / "gate-states.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data.get("format_gate_states"), "format_gate_states is empty"


class TestEvaluateGate11Readiness:
    """Tests for autonomous_cycle.evaluate_gate11_readiness()."""

    def test_product_meeting_all_criteria_is_gate11_ready(self, tmp_path: Path):
        """A product with all P1-P10 true must get gate_11_ready=True."""
        gate_yaml = {
            "gate_states": [{"state_id": "GATE_11_READY", "per_product": True, "per_language": True}],
            "format_gate_states": {
                "csv": {
                    "python": {
                        "p1_oracle_verified": True,
                        "p2_validators_pass": True,
                        "p3_pyproject_present": True,
                        "p4_package_installs": True,
                        "p5_consumer_roundtrip": True,
                        "p6_spec_qname_classvar": True,
                        "p7_py_typed_present": True,
                        "p8_dogfood_exports": True,
                        "p9_analytics_loc_compliant": True,
                        "p10_no_known_violations_at_cap": True,
                        "p11_babar_raza_authorized": "pending",
                        "state": "NOT_READY",
                    }
                }
            }
        }
        (tmp_path / "registry").mkdir()
        (tmp_path / "registry" / "gate-states.yaml").write_text(
            yaml.dump(gate_yaml), encoding="utf-8"
        )
        from autonomous_cycle import evaluate_gate11_readiness
        result = evaluate_gate11_readiness("csv", {}, repo_root=tmp_path)
        assert result["gate_11_ready"] is True, f"Expected True, got: {result}"
        assert result["criteria_missing"] == [], f"Expected no missing criteria, got: {result['criteria_missing']}"

    def test_product_missing_criterion_is_not_gate11_ready(self, tmp_path: Path):
        """A product missing P7 (py.typed) must NOT be gate_11_ready."""
        gate_yaml = {
            "gate_states": [{"state_id": "GATE_11_READY", "per_product": True, "per_language": True}],
            "format_gate_states": {
                "fods": {
                    "python": {
                        "p1_oracle_verified": True,
                        "p2_validators_pass": True,
                        "p3_pyproject_present": True,
                        "p4_package_installs": True,
                        "p5_consumer_roundtrip": True,
                        "p6_spec_qname_classvar": True,
                        "p7_py_typed_present": False,  # MISSING
                        "p8_dogfood_exports": True,
                        "p9_analytics_loc_compliant": True,
                        "p10_no_known_violations_at_cap": True,
                        "state": "NOT_READY",
                    }
                }
            }
        }
        (tmp_path / "registry").mkdir()
        (tmp_path / "registry" / "gate-states.yaml").write_text(
            yaml.dump(gate_yaml), encoding="utf-8"
        )
        from autonomous_cycle import evaluate_gate11_readiness
        result = evaluate_gate11_readiness("fods", {}, repo_root=tmp_path)
        assert result["gate_11_ready"] is False
        assert "p7_py_typed_present" in result["criteria_missing"]


class TestCheck11GateEnforcement:
    """Tests for Check 11 in check_continuation.py."""

    def test_check11_stops_when_product_is_gate11_ready(self, tmp_path: Path):
        """Check 11 must return STOP when a product has state=GATE_11_READY."""
        # Set up minimal repo structure with a GATE_11_READY product
        (tmp_path / "registry").mkdir()
        gate_yaml = {
            "gate_states": [{"state_id": "GATE_11_READY", "per_product": True}],
            "format_gate_states": {
                "csv": {
                    "python": {
                        "state": "GATE_11_READY",
                        "p1_oracle_verified": True,
                    }
                }
            }
        }
        (tmp_path / "registry" / "gate-states.yaml").write_text(
            yaml.dump(gate_yaml), encoding="utf-8"
        )
        # Set up minimal continuation signal
        sig_dir = tmp_path / ".local" / "supervisor"
        sig_dir.mkdir(parents=True)
        signal = {
            "autonomous_continue": True,
            "continuation_state": "YES",
            "iteration": 1,
            "max_iterations": 12,
            "rework_items": [],
            "stop_reason": None,
            "session_id": None,
            "hard_stops_detected": [],
        }
        (sig_dir / "continuation-signal.json").write_text(json.dumps(signal))
        # gates.md
        (tmp_path / "reports").mkdir()
        (tmp_path / "reports" / "supervisor").mkdir()
        (tmp_path / "reports" / "supervisor" / "approval-gates.md").write_text(
            "AUTONOMOUS_CONTINUE: YES\n"
        )
        # next-work-items.json
        (tmp_path / ".local" / "supervisor" / "next-work-items.json").write_text(
            json.dumps({"work_items": [{"id": "W1", "format": "csv"}]})
        )

        from check_continuation import check
        result = check(tmp_path)
        assert result["verdict"] == "STOP", f"Expected STOP, got: {result['verdict']}"
        assert result.get("reason") == "gate_11_ready_pending_authorization"

    def test_check11_continues_when_no_product_is_gate11_ready(self, tmp_path: Path):
        """Check 11 must not block when all products have state=NOT_READY."""
        (tmp_path / "registry").mkdir()
        gate_yaml = {
            "gate_states": [{"state_id": "NOT_READY", "per_product": True}],
            "format_gate_states": {
                "fods": {"python": {"state": "NOT_READY"}}
            }
        }
        (tmp_path / "registry" / "gate-states.yaml").write_text(
            yaml.dump(gate_yaml), encoding="utf-8"
        )
        # Minimal valid continuation environment
        sig_dir = tmp_path / ".local" / "supervisor"
        sig_dir.mkdir(parents=True)
        signal = {
            "autonomous_continue": True,
            "continuation_state": "YES",
            "iteration": 1,
            "max_iterations": 12,
            "rework_items": [],
            "stop_reason": None,
            "session_id": None,
            "hard_stops_detected": [],
        }
        (sig_dir / "continuation-signal.json").write_text(json.dumps(signal))
        (tmp_path / "reports").mkdir()
        (tmp_path / "reports" / "supervisor").mkdir()
        (tmp_path / "reports" / "supervisor" / "approval-gates.md").write_text(
            "AUTONOMOUS_CONTINUE: YES\n"
        )
        (tmp_path / ".local" / "supervisor" / "next-work-items.json").write_text(
            json.dumps({"work_items": [{"id": "W1", "format": "fods"}]})
        )

        from check_continuation import check
        result = check(tmp_path)
        # Should CONTINUE (gate11 not blocking)
        # NOTE: may still STOP for other reasons (e.g., missing plan lock, etc.)
        # but NOT for gate_11_ready_pending_authorization
        assert result.get("reason") != "gate_11_ready_pending_authorization", (
            f"Check 11 should not block when no product is GATE_11_READY: {result}"
        )


class TestTcMach003UnconditionalGatesBeforePlanLockContinue:
    """TC-MACH-003 regression: the plan-lock block's COMPLETION_CANDIDATE branch
    used to `return` a CONTINUE verdict directly, before Check 11 (Gate 11
    TRUE_EXTERNAL_GATE authorization) ever ran. A plan reaching
    COMPLETION_CANDIDATE could therefore CONTINUE even while an unrelated
    product was simultaneously GATE_11_READY and awaiting Babar Raza's
    authorization — a check CLAUDE.md documents as unconditional. This must
    now STOP with gate_11_ready_pending_authorization instead.
    """

    def test_completion_candidate_does_not_bypass_gate11_ready(self, tmp_path: Path):
        (tmp_path / "registry").mkdir()
        gate_yaml = {
            "gate_states": [{"state_id": "GATE_11_READY", "per_product": True}],
            "format_gate_states": {
                "csv": {"python": {"state": "GATE_11_READY", "p1_oracle_verified": True}}
            },
        }
        (tmp_path / "registry" / "gate-states.yaml").write_text(
            yaml.dump(gate_yaml), encoding="utf-8"
        )

        sig_dir = tmp_path / ".local" / "supervisor"
        sig_dir.mkdir(parents=True)
        signal = {
            "autonomous_continue": True,
            "continuation_state": "YES",
            "iteration": 1,
            "max_iterations": 12,
            "rework_items": [],
            "stop_reason": None,
            "session_id": None,
            "hard_stops_detected": [],
        }
        (sig_dir / "continuation-signal.json").write_text(json.dumps(signal))
        gates = tmp_path / "reports" / "supervisor"
        gates.mkdir(parents=True)
        (gates / "approval-gates.md").write_text("AUTONOMOUS_CONTINUE: YES\n")
        (sig_dir / "next-work-items.json").write_text(
            json.dumps({"work_items": [{"id": "W1", "format": "csv"}]})
        )

        # A per-chat plan lock marked COMPLETION_CANDIDATE — the CONTINUE-producing
        # branch this taskcard targets. Deliberately no session_id/track_type so
        # the lock passes Check 1b's session/track filters unconditionally.
        locks_dir = sig_dir / "plan-locks"
        locks_dir.mkdir()
        (locks_dir / "test-completion-candidate.json").write_text(
            json.dumps({
                "plan_path": "plans/.claude/some-plan.md",
                "status": "COMPLETION_CANDIDATE",
                "updated_at": "2026-07-16T12:00:00+00:00",
            }),
            encoding="utf-8",
        )

        from check_continuation import check
        result = check(tmp_path)
        assert result["verdict"] == "STOP", (
            f"TC-MACH-003 regression: COMPLETION_CANDIDATE bypassed the Gate 11 "
            f"TRUE_EXTERNAL_GATE instead of stopping. Got: {result}"
        )
        assert result.get("reason") == "gate_11_ready_pending_authorization", (
            f"Expected gate_11_ready_pending_authorization, got: {result.get('reason')}"
        )

    def test_completion_candidate_continues_when_no_gate_pending(self, tmp_path: Path):
        """Sibling control case: with no GATE_11_READY product, COMPLETION_CANDIDATE
        must still produce its normal CONTINUE/completion_candidate_detected verdict
        — TC-MACH-003 must not turn every COMPLETION_CANDIDATE into a STOP."""
        (tmp_path / "registry").mkdir()
        gate_yaml = {
            "gate_states": [{"state_id": "NOT_READY", "per_product": True}],
            "format_gate_states": {"fods": {"python": {"state": "NOT_READY"}}},
        }
        (tmp_path / "registry" / "gate-states.yaml").write_text(
            yaml.dump(gate_yaml), encoding="utf-8"
        )

        sig_dir = tmp_path / ".local" / "supervisor"
        sig_dir.mkdir(parents=True)
        signal = {
            "autonomous_continue": True,
            "continuation_state": "YES",
            "iteration": 1,
            "max_iterations": 12,
            "rework_items": [],
            "stop_reason": None,
            "session_id": None,
            "hard_stops_detected": [],
        }
        (sig_dir / "continuation-signal.json").write_text(json.dumps(signal))
        gates = tmp_path / "reports" / "supervisor"
        gates.mkdir(parents=True)
        (gates / "approval-gates.md").write_text("AUTONOMOUS_CONTINUE: YES\n")
        (sig_dir / "next-work-items.json").write_text(
            json.dumps({"work_items": [{"id": "W1", "format": "fods"}]})
        )

        locks_dir = sig_dir / "plan-locks"
        locks_dir.mkdir()
        (locks_dir / "test-completion-candidate.json").write_text(
            json.dumps({
                "plan_path": "plans/.claude/some-plan.md",
                "status": "COMPLETION_CANDIDATE",
                "updated_at": "2026-07-16T12:00:00+00:00",
            }),
            encoding="utf-8",
        )

        from check_continuation import check
        result = check(tmp_path)
        assert result["verdict"] == "CONTINUE", f"Expected CONTINUE, got: {result}"
        assert result.get("reason") != "gate_11_ready_pending_authorization"
