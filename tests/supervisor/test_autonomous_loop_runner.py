"""Tests for autonomous_loop_runner.py

Verifies:
- Stops are forbidden when continuation is YES and queue has executable items
- At least two items are consumed in one invocation
- Gate 11 approval items are skipped
- External gate items are skipped
- Queue state is updated after each item
- Continuation signal is updated (not treated as terminal)
- Package/checkpoint creation is not treated as a stop condition
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure tools/supervisor is on path
_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from autonomous_loop_runner import (
    WorkItem,
    LoopRunnerResult,
    check_continuation_allowed,
    _classify_item_executability,
    _is_gate11_item,
    _is_true_external_gate,
    _is_package_terminal,
    load_continuation_signal,
    parse_next_sprint_items,
    run_loop,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_signal(
    auto_continue="true_with_rework",
    cont_state="YES_WITH_REWORK",
    iteration=8,
    max_iterations=12,
    hard_stops=None,
) -> dict:
    return {
        "autonomous_continue": auto_continue,
        "continuation_state": cont_state,
        "iteration": iteration,
        "max_iterations": max_iterations,
        "hard_stops_detected": hard_stops or [],
    }


def _make_item(
    item_id: str = "TASK-001",
    label: str = "pending",
    description: str = "Do something agent-owned",
    action_type: str = "AGENT_TASK",
    external_gate: bool = False,
) -> WorkItem:
    return WorkItem(
        item_id=item_id,
        label=label,
        description=description,
        action_type=action_type,
        external_gate=external_gate,
    )


def _make_next_sprint_md(items: list[tuple[str, str, str]]) -> str:
    """items = list of (label, task_id, description)"""
    lines = ["# Next Sprint\n", "## Section 1: New Product Work\n"]
    for label, task_id, desc in items:
        lines.append(f"- [{label}] {task_id}: {desc}\n")
    return "".join(lines)


# ---------------------------------------------------------------------------
# Unit: continuation check
# ---------------------------------------------------------------------------

class TestContinuationCheck:
    def test_yes_with_rework_allows_continuation(self):
        signal = _make_signal(auto_continue="true_with_rework", cont_state="YES_WITH_REWORK")
        allowed, reason = check_continuation_allowed(signal)
        assert allowed, f"Should allow: {reason}"

    def test_yes_state_allows_continuation(self):
        signal = _make_signal(auto_continue=True, cont_state="YES")
        allowed, reason = check_continuation_allowed(signal)
        assert allowed

    def test_no_broken_baseline_blocks(self):
        signal = _make_signal(cont_state="NO_BROKEN_BASELINE")
        allowed, reason = check_continuation_allowed(signal)
        assert not allowed

    def test_max_iterations_blocks(self):
        signal = _make_signal(iteration=12, max_iterations=12)
        allowed, reason = check_continuation_allowed(signal)
        assert not allowed
        assert "Max iterations" in reason

    def test_hard_stops_block(self):
        signal = _make_signal(hard_stops=["EXTERNAL_BLOCKER: git_push_credentials"])
        allowed, reason = check_continuation_allowed(signal)
        assert not allowed
        assert "Hard stops" in reason

    def test_no_signal_blocks(self):
        allowed, reason = check_continuation_allowed(None)
        assert not allowed


# ---------------------------------------------------------------------------
# Unit: item classification
# ---------------------------------------------------------------------------

class TestItemClassification:
    def test_agent_owned_item_is_executable(self):
        item = _make_item(label="agent-owned", action_type="AGENT_TASK")
        executable, reason = _classify_item_executability(item)
        assert executable

    def test_pending_item_is_executable(self):
        item = _make_item(label="pending", action_type="PRODUCT_GAP_CLOSURE")
        executable, reason = _classify_item_executability(item)
        assert executable

    def test_external_gate_item_is_skipped(self):
        item = _make_item(
            label="external-gate",
            description="Execute git commit",
            action_type="GIT_COMMIT",
            external_gate=True,
        )
        executable, reason = _classify_item_executability(item)
        assert not executable
        assert "SKIP" in reason

    def test_gate11_item_is_skipped(self):
        item = _make_item(
            label="external-gate",
            description="Submit FODS Gate 11 for Babar Raza approval",
            action_type="GATE_11_APPROVAL",
        )
        executable, reason = _classify_item_executability(item)
        assert not executable
        assert "Gate 11" in reason

    def test_git_commit_action_type_is_skipped(self):
        item = _make_item(action_type="GIT_COMMIT", description="Prepare commit candidate")
        executable, reason = _classify_item_executability(item)
        assert not executable

    def test_git_push_action_type_is_skipped(self):
        item = _make_item(action_type="GIT_PUSH", description="Push to remote")
        executable, reason = _classify_item_executability(item)
        assert not executable


class TestGate11Detection:
    def test_gate11_in_description(self):
        item = _make_item(description="Submit Gate 11 approval for commercial release")
        assert _is_gate11_item(item)

    def test_babar_raza_in_description(self):
        item = _make_item(description="Send to Babar Raza for review")
        assert _is_gate11_item(item)

    def test_normal_item_not_gate11(self):
        item = _make_item(description="Close product gap for NDJSON format")
        assert not _is_gate11_item(item)


class TestPackageTerminalCheck:
    def test_package_creation_not_terminal(self):
        item = _make_item(description="Build package artifacts and run installed-workflow proof")
        # Package items are still executable (not terminal)
        executable, reason = _classify_item_executability(item)
        assert executable, "Package creation should NOT be treated as terminal"

    def test_evidence_task_not_terminal(self):
        item = _make_item(description="Write evidence declaration and run supervisor autonomous-cycle")
        executable, reason = _classify_item_executability(item)
        assert executable


# ---------------------------------------------------------------------------
# Unit: next-sprint.md parsing
# ---------------------------------------------------------------------------

class TestNextSprintParsing:
    def test_parses_items_correctly(self, tmp_path):
        content = _make_next_sprint_md([
            ("pending", "TASK-001", "Select governed product gaps"),
            ("agent-owned", "TASK-002", "Prepare commit candidate summary"),
            ("external-gate", "TASK-003", "Execute git commit"),
            ("agent-owned", "TASK-004", "Prepare FODS Gate 11 readiness"),
        ])
        sprint_file = tmp_path / "next-sprint.md"
        sprint_file.write_text(content)
        items = parse_next_sprint_items(sprint_file)
        assert len(items) == 4
        assert items[0].item_id == "TASK-001"
        assert items[2].external_gate is True

    def test_returns_empty_for_missing_file(self, tmp_path):
        items = parse_next_sprint_items(tmp_path / "nonexistent.md")
        assert items == []


# ---------------------------------------------------------------------------
# Integration: loop runner
# ---------------------------------------------------------------------------

class TestLoopRunnerConsumesTwoItems:
    """Core acceptance test: loop must consume >= 2 items when queue has them."""

    def test_consumes_two_items_in_one_invocation(self, tmp_path):
        # Write signal
        signal = _make_signal()
        signal_path = tmp_path / "continuation-signal.json"
        signal_path.write_text(json.dumps(signal))

        # Write next-sprint with multiple executable items
        content = _make_next_sprint_md([
            ("pending", "TASK-001", "Select governed product gaps and validate ledger"),
            ("agent-owned", "TASK-002", "Prepare commit candidate summary and manifest"),
            ("external-gate", "TASK-003", "Execute git commit requires user authorization"),
            ("pending", "TASK-008", "Continue ZST implementation toward Gate 11 readiness"),
            ("pending", "TASK-012", "Product deepening GAP-ABW-FOSS-LOAD-001"),
        ])
        sprint_path = tmp_path / "next-sprint.md"
        sprint_path.write_text(content)

        result = run_loop(
            signal_path=signal_path,
            evidence_root=tmp_path / "evidence",
            next_sprint_path=sprint_path,
            max_items=2,
        )

        assert len(result.items_consumed) >= 2, (
            f"Expected >= 2 consumed, got {len(result.items_consumed)}. "
            f"Verdict: {result.autonomy_verdict}"
        )

    def test_verdict_autonomy_fixed_when_two_consumed(self, tmp_path):
        signal = _make_signal()
        signal_path = tmp_path / "continuation-signal.json"
        signal_path.write_text(json.dumps(signal))

        content = _make_next_sprint_md([
            ("pending", "TASK-001", "Work item one agent owned"),
            ("pending", "TASK-002", "Work item two agent owned"),
            ("pending", "TASK-003", "Work item three agent owned"),
        ])
        sprint_path = tmp_path / "next-sprint.md"
        sprint_path.write_text(content)

        result = run_loop(
            signal_path=signal_path,
            evidence_root=tmp_path / "evidence",
            next_sprint_path=sprint_path,
            max_items=2,
        )

        assert result.autonomy_verdict == "AUTONOMY_FIXED", (
            f"Expected AUTONOMY_FIXED, got {result.autonomy_verdict}"
        )


class TestLoopRunnerSkipsGate11:
    def test_gate11_items_are_always_skipped(self, tmp_path):
        signal = _make_signal()
        signal_path = tmp_path / "continuation-signal.json"
        signal_path.write_text(json.dumps(signal))

        content = _make_next_sprint_md([
            ("external-gate", "TASK-005", "Submit FODS Gate 11 for Babar Raza approval"),
            ("external-gate", "TASK-007", "Submit FODT Gate 11 Babar Raza approval"),
            ("pending", "TASK-008", "Continue ZST product implementation"),
        ])
        sprint_path = tmp_path / "next-sprint.md"
        sprint_path.write_text(content)

        result = run_loop(
            signal_path=signal_path,
            evidence_root=tmp_path / "evidence",
            next_sprint_path=sprint_path,
            max_items=3,
        )

        # Gate 11 items should be skipped
        skipped_ids = [i.item_id for i in result.items_skipped]
        assert "TASK-005" in skipped_ids, "FODS Gate 11 item must be skipped"
        assert "TASK-007" in skipped_ids, "FODT Gate 11 item must be skipped"

        # TASK-008 should be consumed
        consumed_ids = [i.item_id for i in result.items_consumed]
        assert "TASK-008" in consumed_ids, "ZST implementation item should be consumed"


class TestLoopRunnerQueueState:
    def test_queue_state_written_after_each_item(self, tmp_path):
        signal = _make_signal()
        signal_path = tmp_path / "continuation-signal.json"
        signal_path.write_text(json.dumps(signal))

        content = _make_next_sprint_md([
            ("pending", "TASK-001", "First agent item"),
            ("pending", "TASK-002", "Second agent item"),
        ])
        sprint_path = tmp_path / "next-sprint.md"
        sprint_path.write_text(content)

        evidence_root = tmp_path / "evidence"
        result = run_loop(
            signal_path=signal_path,
            evidence_root=evidence_root,
            next_sprint_path=sprint_path,
            max_items=2,
        )

        queue_state_path = evidence_root / "loop-queue-state.json"
        assert queue_state_path.exists(), "Queue state must be written"
        state = json.loads(queue_state_path.read_text())
        assert state["consumed"] >= 2

    def test_continuation_signal_updated_not_deleted(self, tmp_path):
        signal = _make_signal()
        signal_path = tmp_path / "continuation-signal.json"
        signal_path.write_text(json.dumps(signal))

        content = _make_next_sprint_md([
            ("pending", "TASK-001", "Agent owned item"),
        ])
        sprint_path = tmp_path / "next-sprint.md"
        sprint_path.write_text(content)

        run_loop(
            signal_path=signal_path,
            evidence_root=tmp_path / "evidence",
            next_sprint_path=sprint_path,
            max_items=1,
        )

        # Signal must still exist and have the original fields
        assert signal_path.exists(), "Continuation signal must not be deleted"
        updated = json.loads(signal_path.read_text())
        assert "autonomous_continue" in updated, "autonomous_continue must be preserved"
        assert "last_loop_runner_at" in updated, "Runner must add timestamp"
        assert updated["last_loop_items_consumed"] >= 1


class TestLoopRunnerNoFalseStops:
    def test_does_not_stop_when_continuation_yes_and_queue_nonempty(self, tmp_path):
        signal = _make_signal(auto_continue=True, cont_state="YES")
        signal_path = tmp_path / "continuation-signal.json"
        signal_path.write_text(json.dumps(signal))

        content = _make_next_sprint_md([
            ("pending", "TASK-001", "First executable item"),
            ("pending", "TASK-002", "Second executable item"),
            ("pending", "TASK-003", "Third executable item"),
        ])
        sprint_path = tmp_path / "next-sprint.md"
        sprint_path.write_text(content)

        result = run_loop(
            signal_path=signal_path,
            evidence_root=tmp_path / "evidence",
            next_sprint_path=sprint_path,
            max_items=10,  # High limit — should consume all 3
        )

        # Must not stop after just 1 item
        assert len(result.items_consumed) >= 2, (
            f"Must not stop after one item when continuation=YES. "
            f"Got {len(result.items_consumed)} consumed."
        )

    def test_dry_run_consumes_items_without_side_effects(self, tmp_path):
        signal = _make_signal()
        signal_path = tmp_path / "continuation-signal.json"
        signal_path.write_text(json.dumps(signal))

        content = _make_next_sprint_md([
            ("pending", "TASK-001", "Item one"),
            ("pending", "TASK-002", "Item two"),
        ])
        sprint_path = tmp_path / "next-sprint.md"
        sprint_path.write_text(content)

        result = run_loop(
            signal_path=signal_path,
            evidence_root=tmp_path / "evidence",
            next_sprint_path=sprint_path,
            max_items=2,
            dry_run=True,
        )

        assert len(result.items_consumed) == 2
        # In dry_run, signal is not updated
        updated = json.loads(signal_path.read_text())
        assert "last_loop_runner_at" not in updated, "Dry run must not modify signal"
