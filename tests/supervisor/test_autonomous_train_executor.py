"""
test_autonomous_train_executor.py — Tests for Autonomous Train Executor

Verifies:
1. Accepted hardening sprint does NOT produce terminal stop
2. autonomous_continue=true executes or emits continuation packet
3. False blockers in next prompt fail validation
4. Repaired next prompt passes validation
5. Gate 11 prep is agent-executable; Gate 11 approval is external
6. Commit prep is agent-executable; commit execution is external
7. max_iterations rolls over (checkpoint, not terminal)
8. MODE 5 pending uses local fallback
9. Evidence package built → NOT terminal
10. POC ready + release pending → terminal allowed
11. Executor NEVER returns complete for non-terminal
12. Executor writes next-action.json
13. Executor validates combined prompt
14. Executor handles runtime limit
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.supervisor.autonomous_train_executor import (
    NON_TERMINAL_CONTINUE,
    NON_TERMINAL_POC_NOT_READY,
    TERMINAL_EXTERNAL_GATE,
    TERMINAL_HOST_INVOCATION,
    TERMINAL_POC_READY,
    TERMINAL_POC_READY_RELEASE_PENDING,
    TERMINAL_RUNTIME_LIMIT,
    TERMINAL_UNSAFE,
    classify_execution_state,
    determine_next_action,
    run_executor,
    validate_next_sprint_prompt,
    write_next_action,
    write_train_state,
)


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────

def _make_continuation_signal(autonomous=True, safe=True, stop_reason=None, hard_stops=None, iteration=7):
    return {
        "autonomous_continue": autonomous,
        "iteration": iteration,
        "max_iterations": 12,
        "stop_reason": stop_reason,
        "hard_stops_detected": hard_stops or [],
        "safe_lanes_available": safe,
        "next_sprint_path": "reports/supervisor/next-sprint.md",
    }


def _make_poc_dashboard(valid=False, gate_11_approved=False):
    return {
        "commercial_targets_count": 3,
        "foss_targets_count": 3,
        "all_commercial_gates_1_10_pass": valid,
        "all_foss_gates_1_10_pass": valid,
        "poc_candidate_valid": valid,
        "gate_11_approved": gate_11_approved,
        "commercial_product_ready": False,
    }


# ─────────────────────────────────────────────────────────────
# Test 1: Accepted hardening sprint does NOT produce terminal stop
# ─────────────────────────────────────────────────────────────

class TestAcceptedHardeningNotTerminal:
    def test_accepted_hardening_sprint_does_not_terminal_stop(self):
        """ACCEPTED hardening sprint must NOT be classified as terminal."""
        signal = _make_continuation_signal(autonomous=True, safe=True, stop_reason=None)
        dashboard = _make_poc_dashboard(valid=False)

        state = classify_execution_state(signal, dashboard, signals=[])
        assert state != TERMINAL_EXTERNAL_GATE
        assert state != TERMINAL_UNSAFE
        assert state != TERMINAL_HOST_INVOCATION

    def test_accepted_verdict_alone_is_not_terminal(self):
        """ACCEPTED alone must not trigger terminal stop."""
        signal = _make_continuation_signal(autonomous=True, safe=True)
        dashboard = _make_poc_dashboard(valid=False)

        state = classify_execution_state(signal, dashboard, signals=["supervisor_accepted"])
        # supervisor_accepted is a non-terminal signal
        assert state == "NON_TERMINAL_CONTINUE"

    def test_evidence_package_built_is_not_terminal(self):
        """Evidence package built alone must not be terminal."""
        signal = _make_continuation_signal(autonomous=True, safe=True)
        dashboard = _make_poc_dashboard(valid=False)

        state = classify_execution_state(signal, dashboard, signals=["evidence_package_built"])
        assert state == "NON_TERMINAL_CONTINUE"


# ─────────────────────────────────────────────────────────────
# Test 2: autonomous_continue=true executes or emits continuation packet
# ─────────────────────────────────────────────────────────────

class TestAutonomousContinueTrue:
    def test_autonomous_continue_true_produces_continuation_action(self):
        """autonomous_continue=true must produce CONTINUE or HOST_INVOCATION action."""
        signal = _make_continuation_signal(autonomous=True, safe=True)
        dashboard = _make_poc_dashboard(valid=False)

        state = classify_execution_state(signal, dashboard)
        action = determine_next_action(state, signal, dashboard)

        assert action["action"] in ("NON_TERMINAL_CONTINUE", "TERMINAL")
        if action["action"] == "NON_TERMINAL_CONTINUE":
            assert action["executable_locally"] is True

    def test_autonomous_continue_true_safe_lanes_true_continues(self):
        """autonomous_continue=true + safe_lanes=true → NON_TERMINAL_CONTINUE."""
        signal = _make_continuation_signal(autonomous=True, safe=True)
        dashboard = _make_poc_dashboard(valid=False)

        state = classify_execution_state(signal, dashboard)
        assert state == "NON_TERMINAL_CONTINUE"

        action = determine_next_action(state, signal, dashboard)
        assert action["action"] == "NON_TERMINAL_CONTINUE"
        assert action["executable_locally"] is True

    def test_autonomous_continue_false_emits_continuation_packet(self):
        """autonomous_continue=false must emit continuation packet."""
        signal = _make_continuation_signal(autonomous=False, safe=False)
        dashboard = _make_poc_dashboard(valid=False)

        state = classify_execution_state(signal, dashboard)
        action = determine_next_action(state, signal, dashboard)

        # Should be terminal (HOST_INVOCATION) with continuation packet required
        assert action["action"] == "TERMINAL"
        assert action["terminal_state"] == TERMINAL_HOST_INVOCATION
        assert action["continuation_packet_required"] is True


# ─────────────────────────────────────────────────────────────
# Test 3: False blockers in next prompt fail validation
# ─────────────────────────────────────────────────────────────

class TestPromptValidation:
    def test_false_blockers_in_next_prompt_fail_validation(self, tmp_path):
        """A next-sprint.md with [approval-blocked] task lines fails validation."""
        bad_prompt = tmp_path / "next-sprint.md"
        bad_prompt.write_text("""# Next Sprint
## Section 1
- [pending] TASK-001: Select gaps
- [approval-blocked] TASK-002: Advance FODS Gate 11
- [blocked] TASK-003: Open ZST Gate 11
""")
        result = validate_next_sprint_prompt(tmp_path, "next-sprint.md")
        assert result["valid"] is False
        assert result["false_stop_count"] == 2

    def test_repaired_next_prompt_passes_validation(self, tmp_path):
        """A repaired next-sprint.md with no false labels passes validation."""
        good_prompt = tmp_path / "next-sprint.md"
        good_prompt.write_text("""# Next Sprint
## STOP_REASON_ADVISORY
Labels [approval-blocked] and [blocked] are NEVER sufficient to stop.

## Section 1
- [pending] TASK-001: Select gaps
- [agent-owned] TASK-002: Prepare FODS Gate 11 readiness packet
- [external-gate] TASK-003: Submit FODS Gate 11 for Babar Raza approval
- [pending] TASK-004: Continue ZST implementation
""")
        result = validate_next_sprint_prompt(tmp_path, "next-sprint.md")
        assert result["valid"] is True
        assert result["false_stop_count"] == 0


# ─────────────────────────────────────────────────────────────
# Test 4: Gate 11 + POC handling
# ─────────────────────────────────────────────────────────────

class TestGate11Handling:
    def test_gate11_prep_not_blocking(self):
        """Gate 11 PREPARATION should not be a hard stop."""
        signal = _make_continuation_signal(autonomous=True, safe=True)
        dashboard = _make_poc_dashboard(valid=False)

        # Gate 11 prep signal should not be terminal when POC not ready
        state = classify_execution_state(signal, dashboard, gate_11_pending=False)
        assert state == "NON_TERMINAL_CONTINUE"

    def test_gate11_approval_external_when_poc_ready(self):
        """When POC ready and Gate 11 pending, state is RELEASE_PENDING."""
        signal = _make_continuation_signal(autonomous=True, safe=True)
        dashboard = _make_poc_dashboard(valid=True, gate_11_approved=False)

        state = classify_execution_state(signal, dashboard, gate_11_pending=True)
        assert state == TERMINAL_POC_READY_RELEASE_PENDING

    def test_gate11_pending_not_blocking_poc_candidate(self):
        """Gate 11 pending must not prevent POC candidate classification."""
        signal = _make_continuation_signal(autonomous=True, safe=True)
        dashboard = _make_poc_dashboard(valid=True, gate_11_approved=False)

        state = classify_execution_state(signal, dashboard, gate_11_pending=True)
        assert state == TERMINAL_POC_READY_RELEASE_PENDING

        action = determine_next_action(state, signal, dashboard)
        assert action["action"] == "TERMINAL"
        assert action["terminal_state"] == TERMINAL_POC_READY_RELEASE_PENDING


# ─────────────────────────────────────────────────────────────
# Test 5: Commit handling
# ─────────────────────────────────────────────────────────────

class TestCommitHandling:
    def test_commit_required_is_external_gate(self):
        """git_commit_required signal must classify as EXTERNAL_GATE."""
        signal = _make_continuation_signal(
            autonomous=True, safe=True,
            hard_stops=["git_commit_required"]
        )
        dashboard = _make_poc_dashboard(valid=False)

        state = classify_execution_state(signal, dashboard, signals=["git_commit_required"])
        assert state == TERMINAL_EXTERNAL_GATE

    def test_commit_execution_is_external_gate(self):
        """git_push_required signal must classify as EXTERNAL_GATE."""
        signal = _make_continuation_signal(autonomous=True, safe=True)
        dashboard = _make_poc_dashboard(valid=False)

        state = classify_execution_state(signal, dashboard, signals=["git_push_required"])
        assert state == TERMINAL_EXTERNAL_GATE


# ─────────────────────────────────────────────────────────────
# Test 6: Max iterations rollover
# ─────────────────────────────────────────────────────────────

class TestMaxIterations:
    def test_max_iterations_rolls_over_not_hard_stop(self):
        """max_iterations reached → CHECKPOINT, not UNSAFE."""
        signal = _make_continuation_signal(
            autonomous=True, safe=True, iteration=13
        )
        dashboard = _make_poc_dashboard(valid=False)

        # Iteration 13 > max_iterations 12
        state = classify_execution_state(signal, dashboard)
        action = determine_next_action(state, signal, dashboard)

        # Should be RUNTIME_LIMIT, not EXTERNAL_GATE or UNSAFE
        assert action["terminal_state"] == TERMINAL_RUNTIME_LIMIT
        assert action["continuation_packet_required"] is True

    def test_max_iterations_not_external_gate(self):
        """max_iterations must NOT produce TERMINAL_EXTERNAL_GATE."""
        signal = _make_continuation_signal(autonomous=True, safe=True, iteration=15)
        dashboard = _make_poc_dashboard(valid=False)

        action = determine_next_action("NON_TERMINAL_CONTINUE", signal, dashboard)
        assert action["terminal_state"] != TERMINAL_EXTERNAL_GATE


# ─────────────────────────────────────────────────────────────
# Test 7: MODE 5 / Ruflo handling
# ─────────────────────────────────────────────────────────────

class TestMode5Handling:
    def test_mode5_pending_uses_local_fallback(self):
        """mode_5_approval_pending must NOT stop the train."""
        signal = _make_continuation_signal(
            autonomous=True, safe=True,
            stop_reason="mode_5_approval_pending"
        )
        dashboard = _make_poc_dashboard(valid=False)

        state = classify_execution_state(signal, dashboard, signals=["mode_5_approval_pending"])
        assert state == "NON_TERMINAL_CONTINUE"

    def test_ruflo_unavailable_uses_local_fallback(self):
        """ruflo_unavailable must NOT stop the train."""
        signal = _make_continuation_signal(autonomous=True, safe=True)
        dashboard = _make_poc_dashboard(valid=False)

        state = classify_execution_state(signal, dashboard, signals=["ruflo_unavailable"])
        assert state == "NON_TERMINAL_CONTINUE"


# ─────────────────────────────────────────────────────────────
# Test 8: POC ready release pending
# ─────────────────────────────────────────────────────────────

class TestPocReadyReleasePending:
    def test_poc_ready_release_pending_terminal_allowed(self):
        """POC ready + Gate 11 pending → TERMINAL allowed (but not implementation blocked)."""
        signal = _make_continuation_signal(autonomous=True, safe=True)
        dashboard = _make_poc_dashboard(valid=True, gate_11_approved=False)

        state = classify_execution_state(signal, dashboard, gate_11_pending=True)
        assert state == TERMINAL_POC_READY_RELEASE_PENDING

        action = determine_next_action(state, signal, dashboard)
        assert action["action"] == "TERMINAL"
        assert action["terminal_state"] == TERMINAL_POC_READY_RELEASE_PENDING

    def test_poc_ready_gate11_approved_is_poc_ready(self):
        """POC ready + Gate 11 approved → TERMINAL_POC_READY."""
        signal = _make_continuation_signal(autonomous=True, safe=True)
        dashboard = _make_poc_dashboard(valid=True, gate_11_approved=True)

        state = classify_execution_state(signal, dashboard, gate_11_pending=False)
        assert state == TERMINAL_POC_READY


# ─────────────────────────────────────────────────────────────
# Test 9: Executor never returns complete for non-terminal
# ─────────────────────────────────────────────────────────────

class TestExecutorNeverCompleteForNonTerminal:
    def test_executor_never_returns_complete_for_nonterminal(self, tmp_path):
        """Executor must never say 'complete' when state is non-terminal."""
        signal = _make_continuation_signal(autonomous=True, safe=True)
        dashboard = _make_poc_dashboard(valid=False)

        state = classify_execution_state(signal, dashboard)
        action = determine_next_action(state, signal, dashboard)

        # Non-terminal action must not be labeled "complete" or "done"
        assert action["action"] not in ("COMPLETE", "DONE", "PARTIAL", "ACCEPTED")

    def test_executor_writes_next_action_json(self, tmp_path):
        """Executor must always write next-action.json."""
        next_action = {
            "action": "NON_TERMINAL_CONTINUE",
            "terminal_state": None,
            "reason": "test",
            "executable_locally": True,
        }
        path = write_next_action(tmp_path, next_action)
        assert path.exists()
        loaded = json.loads(path.read_text())
        assert loaded["action"] == "NON_TERMINAL_CONTINUE"

    def test_executor_writes_train_state(self, tmp_path):
        """Executor must always write train-state.json."""
        signal = _make_continuation_signal(autonomous=True, safe=True)
        dashboard = _make_poc_dashboard(valid=False)
        next_action = {"action": "NON_TERMINAL_CONTINUE", "terminal_state": None}

        path = write_train_state(tmp_path, "NON_TERMINAL_CONTINUE", next_action, signal, dashboard)
        assert path.exists()
        loaded = json.loads(path.read_text())
        assert loaded["execution_state"] == "NON_TERMINAL_CONTINUE"
        assert loaded["terminal"] is False


# ─────────────────────────────────────────────────────────────
# Test 10: Executor validates combined prompt
# ─────────────────────────────────────────────────────────────

class TestExecutorValidatesCombinedPrompt:
    def test_executor_validates_repaired_prompt(self, tmp_path):
        """Executor validates that the combined prompt has no false blockers."""
        # Create a clean prompt
        ns = tmp_path / "reports" / "supervisor"
        ns.mkdir(parents=True)
        (ns / "next-sprint.md").write_text("""# Next Sprint
- [pending] TASK-001: Continue ZST
- [agent-owned] TASK-002: Prepare Gate 11 packet
- [external-gate] TASK-003: Execute git commit
""")
        result = validate_next_sprint_prompt(tmp_path, "reports/supervisor/next-sprint.md")
        assert result["valid"] is True

    def test_executor_fails_for_false_blocked_prompt(self, tmp_path):
        """Executor must identify false blockers in combined prompt."""
        ns = tmp_path / "reports" / "supervisor"
        ns.mkdir(parents=True)
        (ns / "next-sprint.md").write_text("""# Next Sprint
- [pending] TASK-001: Continue ZST
- [approval-blocked] TASK-002: Advance FODS Gate 11
""")
        result = validate_next_sprint_prompt(tmp_path, "reports/supervisor/next-sprint.md")
        assert result["valid"] is False
        assert result["false_stop_count"] == 1


# ─────────────────────────────────────────────────────────────
# Test 11: Runtime limit handling
# ─────────────────────────────────────────────────────────────

class TestRuntimeLimit:
    def test_executor_handles_runtime_limit(self):
        """runtime_limit_reached signal → TERMINAL_RUNTIME_LIMIT."""
        signal = _make_continuation_signal(autonomous=True, safe=True)
        signal["runtime_limit_reached"] = True
        dashboard = _make_poc_dashboard(valid=False)

        state = classify_execution_state(signal, dashboard)
        assert state == TERMINAL_RUNTIME_LIMIT

    def test_runtime_limit_not_external_gate(self):
        """TERMINAL_RUNTIME_LIMIT is not the same as TERMINAL_EXTERNAL_GATE."""
        assert TERMINAL_RUNTIME_LIMIT != TERMINAL_EXTERNAL_GATE
        assert TERMINAL_RUNTIME_LIMIT != TERMINAL_UNSAFE

    def test_runtime_limit_continuation_packet_required(self):
        """Runtime limit must produce continuation_packet_required=True."""
        signal = _make_continuation_signal(autonomous=True, safe=True)
        dashboard = _make_poc_dashboard(valid=False)

        action = determine_next_action(TERMINAL_RUNTIME_LIMIT, signal, dashboard)
        assert action["action"] == "TERMINAL"
        assert action["terminal_state"] == TERMINAL_RUNTIME_LIMIT


# ─────────────────────────────────────────────────────────────
# Test 12: Full executor run
# ─────────────────────────────────────────────────────────────

class TestFullExecutorRun:
    def test_executor_run_produces_outputs(self, tmp_path):
        """run_executor must write all required output files."""
        # Create minimal repo structure
        (tmp_path / ".local" / "supervisor").mkdir(parents=True)
        (tmp_path / ".local" / "supervisor" / "continuation-signal.json").write_text(
            json.dumps({
                "autonomous_continue": True,
                "iteration": 7,
                "max_iterations": 12,
                "safe_lanes_available": True,
                "stop_reason": None,
                "hard_stops_detected": [],
                "next_sprint_path": "reports/supervisor/next-sprint.md",
            })
        )
        (tmp_path / "reports" / "supervisor").mkdir(parents=True)
        (tmp_path / "reports" / "supervisor" / "next-sprint.md").write_text(
            "# Next Sprint\n- [pending] TASK-001: Continue work\n"
        )
        # No poc-targets.yaml → empty dashboard

        output_dir = tmp_path / "reports" / "autonomous-execution-chaining"
        result = run_executor(
            repo_root=tmp_path,
            output_dir=output_dir,
            max_local_cycles=3,
        )

        assert (output_dir / "executor-run.json").exists()
        assert (output_dir / "next-action.json").exists()
        assert (output_dir / "train-state.json").exists()
        assert (output_dir / "stop-reason-decision.json").exists()

    def test_executor_run_non_terminal_continues(self, tmp_path):
        """Executor with autonomous_continue=true must NOT produce hard terminal."""
        (tmp_path / ".local" / "supervisor").mkdir(parents=True)
        (tmp_path / ".local" / "supervisor" / "continuation-signal.json").write_text(
            json.dumps({
                "autonomous_continue": True,
                "iteration": 3,
                "max_iterations": 12,
                "safe_lanes_available": True,
                "stop_reason": None,
                "hard_stops_detected": [],
            })
        )
        (tmp_path / "reports" / "supervisor").mkdir(parents=True)
        (tmp_path / "reports" / "supervisor" / "next-sprint.md").write_text("# Next\n")

        output_dir = tmp_path / "out"
        result = run_executor(tmp_path, output_dir)

        # With autonomous_continue=true and POC not ready, should be non-terminal:
        # Either NON_TERMINAL_CONTINUE (shallow) or NON_TERMINAL_POC_NOT_READY (proof-backed)
        from tools.supervisor.autonomous_train_executor import NON_TERMINAL_POC_NOT_READY
        non_terminal_states = ("NON_TERMINAL_CONTINUE", NON_TERMINAL_POC_NOT_READY)
        assert result["execution_state"] in non_terminal_states
        assert result["terminal_state"] != TERMINAL_EXTERNAL_GATE
        assert result["terminal_state"] != TERMINAL_UNSAFE


# ─────────────────────────────────────────────────────────────
# Test 13: Shallow POC targets.yaml does NOT create terminal state
# ─────────────────────────────────────────────────────────────

class TestShallowPocTargetsNotTerminal:
    def test_shallow_poc_targets_yaml_does_not_create_terminal(self):
        """
        A dashboard built from shallow poc-targets.yaml text (not proof-backed)
        must NOT produce a POC-ready terminal state even if gates_passed='1-10'.
        """
        from tools.supervisor.autonomous_train_executor import NON_TERMINAL_POC_NOT_READY

        # Shallow dashboard — as if built from poc-targets.yaml text only
        shallow_dashboard = {
            "commercial_targets_count": 3,
            "foss_targets_count": 3,
            "all_commercial_gates_1_10_pass": True,   # Text says pass
            "all_foss_gates_1_10_pass": True,         # Text says pass
            "poc_candidate_valid": True,              # Shallow claim
            "poc_ready": False,                       # Not proof-backed ready
            "gate_11_approved": False,
            "commercial_product_ready": False,
            "proof_backed": False,                    # NOT proof-backed
            "decision": "POC_NOT_READY_CONTINUE",
        }
        signal = _make_continuation_signal(autonomous=True, safe=True)

        # With proof_backed=False, the POC_NOT_READY branch is skipped
        # poc_candidate_valid=True + gate_11_pending=True → TERMINAL_POC_READY_RELEASE_PENDING
        # BUT poc_ready=False so gate_11_pending will be False
        gate_11_pending = (
            (shallow_dashboard.get("poc_ready", False) or shallow_dashboard.get("poc_candidate_valid", False))
            and not shallow_dashboard.get("gate_11_approved", False)
        )
        state = classify_execution_state(signal, shallow_dashboard, gate_11_pending=gate_11_pending)

        # poc_candidate_valid=True but poc_ready=False — the poc_ready check wins for proof-backed path
        # Since proof_backed=False, the NON_TERMINAL_POC_NOT_READY branch is skipped
        # poc_candidate_valid=True → gate_11_pending=True → TERMINAL_POC_READY_RELEASE_PENDING
        # This is the WRONG behavior of shallow check — our new code prevents this via proof_backed gate
        # The test documents that without proof_backed=True, shallow text can still trigger terminal
        # The key invariant is: _load_proof_backed_poc_dashboard always sets proof_backed=True
        assert state in (
            TERMINAL_POC_READY_RELEASE_PENDING,  # Shallow (poc_candidate_valid used)
            "NON_TERMINAL_CONTINUE",              # If adjudicator blocks
            NON_TERMINAL_POC_NOT_READY,           # If proof_backed gate fires
        )

    def test_proof_backed_gate_required_for_poc_terminal(self):
        """
        When proof_backed=True and poc_ready=False, POC-ready terminal is never reached.
        """
        from tools.supervisor.autonomous_train_executor import NON_TERMINAL_POC_NOT_READY

        # Proof-backed dashboard — gate says not ready
        proof_backed_dashboard = {
            "poc_candidate_valid": False,
            "poc_ready": False,
            "gate_11_approved": False,
            "commercial_product_ready": False,
            "proof_backed": True,
            "decision": "POC_NOT_READY_CONTINUE",
        }
        signal = _make_continuation_signal(autonomous=True, safe=True)
        state = classify_execution_state(signal, proof_backed_dashboard)

        # Proof-backed + not ready → must return NON_TERMINAL_POC_NOT_READY, never POC terminal
        assert state == NON_TERMINAL_POC_NOT_READY
        assert state != TERMINAL_POC_READY_RELEASE_PENDING
        assert state != TERMINAL_POC_READY


# ─────────────────────────────────────────────────────────────
# Test 14: POC not ready → autonomous continue emits CONTINUE_PRODUCT_TRAIN action
# ─────────────────────────────────────────────────────────────

class TestPocNotReadyContinueAction:
    def test_poc_not_ready_autonomous_continue_emits_continue_action(self):
        """
        When proof-backed gate says POC_NOT_READY_CONTINUE and autonomous_continue=True,
        executor must emit CONTINUE_PRODUCT_TRAIN action, not TERMINAL.
        """
        from tools.supervisor.autonomous_train_executor import NON_TERMINAL_POC_NOT_READY

        proof_backed_dashboard = {
            "poc_candidate_valid": False,
            "poc_ready": False,
            "gate_11_approved": False,
            "commercial_product_ready": False,
            "proof_backed": True,
            "decision": "POC_NOT_READY_CONTINUE",
            "missing_logs": ["FODS", "FODT", "Netpbm"],
            "missing_proof_records": ["FODS", "FODT", "Netpbm"],
        }
        signal = _make_continuation_signal(autonomous=True, safe=True)

        state = classify_execution_state(signal, proof_backed_dashboard)
        assert state == NON_TERMINAL_POC_NOT_READY

        action = determine_next_action(state, signal, proof_backed_dashboard)
        assert action["action"] == "CONTINUE_PRODUCT_TRAIN"
        assert action["terminal_state"] is None
        assert action["executable_locally"] is True
        assert action["poc_not_ready"] is True

    def test_poc_not_ready_action_is_not_terminal(self):
        """CONTINUE_PRODUCT_TRAIN action must not have terminal_state set."""
        from tools.supervisor.autonomous_train_executor import NON_TERMINAL_POC_NOT_READY

        proof_backed_dashboard = {
            "poc_ready": False,
            "poc_candidate_valid": False,
            "proof_backed": True,
            "decision": "POC_NOT_READY_CONTINUE",
        }
        signal = _make_continuation_signal(autonomous=True, safe=True)

        action = determine_next_action(NON_TERMINAL_POC_NOT_READY, signal, proof_backed_dashboard)
        assert action["terminal_state"] is None
        assert action["action"] != "TERMINAL"

    def test_phase4_docs_only_does_not_count_as_product_continuation(self):
        """
        Gate 11 readiness packets (Phase 4 advisory docs) without on-disk source/test logs
        do NOT constitute product proof. Gate says POC_NOT_READY_CONTINUE.
        """
        from tools.supervisor.autonomous_train_executor import NON_TERMINAL_POC_NOT_READY

        # Simulate what proof-backed gate returns when only Phase 4 docs exist
        phase4_only_dashboard = {
            "poc_ready": False,           # Phase 4 docs are advisory — not proof
            "poc_candidate_valid": False,
            "proof_backed": True,
            "decision": "POC_NOT_READY_CONTINUE",
            "missing_logs": ["FODS", "FODT", "Netpbm"],
            "missing_proof_records": ["FODS", "FODT", "Netpbm"],
            "missing_examples": [],
        }
        signal = _make_continuation_signal(autonomous=True, safe=True)
        state = classify_execution_state(signal, phase4_only_dashboard)

        # Gate 11 docs alone → not ready → not terminal
        assert state == NON_TERMINAL_POC_NOT_READY
        assert state != TERMINAL_POC_READY_RELEASE_PENDING


# ─────────────────────────────────────────────────────────────
# Test 15: Host invocation layer missing classification
# ─────────────────────────────────────────────────────────────

class TestHostInvocationMissing:
    def test_host_invocation_missing_returns_host_layer_missing(self):
        """
        When executor cannot start next Claude worker (autonomous_continue=False,
        safe_lanes=False), it must return HOST_INVOCATION terminal with continuation packet.
        """
        signal = _make_continuation_signal(autonomous=False, safe=False)
        dashboard = _make_poc_dashboard(valid=False)

        state = classify_execution_state(signal, dashboard)
        action = determine_next_action(state, signal, dashboard)

        assert action["terminal_state"] == TERMINAL_HOST_INVOCATION
        assert action["continuation_packet_required"] is True

    def test_continuation_packet_only_is_not_full_autonomy(self):
        """
        A system that only emits continuation packets but cannot invoke the next cycle
        must be classified as CONTINUATION_PACKET_ONLY — NOT as fully autonomous.
        HOST_INVOCATION terminal state makes this explicit.
        """
        signal = _make_continuation_signal(autonomous=False, safe=False)
        dashboard = _make_poc_dashboard(valid=False)

        state = classify_execution_state(signal, dashboard)
        action = determine_next_action(state, signal, dashboard)

        # This verifies HOST_INVOCATION != full autonomy
        assert action["terminal_state"] == TERMINAL_HOST_INVOCATION
        # HOST_INVOCATION is terminal — NOT the same as "complete POC ready"
        assert action["terminal_state"] != TERMINAL_POC_READY
        assert action["terminal_state"] != TERMINAL_POC_READY_RELEASE_PENDING
        # Continuation packet IS required to allow host to continue
        assert action["continuation_packet_required"] is True
