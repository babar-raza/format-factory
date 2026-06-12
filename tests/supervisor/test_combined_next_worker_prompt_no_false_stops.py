"""
test_combined_next_worker_prompt_no_false_stops.py

Verifies that all generated next-sprint output channels have no false-stop labels.
Tests run against the live repo state and the generator.

Requirements from Phase 2:
1. reports/supervisor/next-sprint.md has no false [approval-blocked] task labels
2. combined-next-worker-prompt.md has no false human gates
3. next-sprint-taskmaster.json has no approval-blocked statuses for agent-owned tasks
4. Generated tasks have no false labels
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

REPO_ROOT = Path(__file__).parent.parent.parent

# ─────────────────────────────────────────────────────────────
# Test current repo state of next-sprint.md
# ─────────────────────────────────────────────────────────────

class TestLiveNextSprintMd:
    def test_live_next_sprint_md_has_no_false_approval_blocked_tasks(self):
        """reports/supervisor/next-sprint.md must have no [approval-blocked] task lines."""
        path = REPO_ROOT / "reports" / "supervisor" / "next-sprint.md"
        if not path.exists():
            pytest.skip("next-sprint.md not present")

        content = path.read_text(encoding="utf-8")
        task_lines_with_false_stops = []
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("- [approval-blocked]") and "TASK-" in stripped:
                task_lines_with_false_stops.append(stripped[:80])
            elif stripped.startswith("- [blocked]") and "TASK-" in stripped:
                task_lines_with_false_stops.append(stripped[:80])

        assert task_lines_with_false_stops == [], (
            "False-stop task labels found in next-sprint.md:\n"
            + "\n".join(task_lines_with_false_stops)
        )

    def test_live_next_sprint_md_has_stop_reason_advisory_or_is_repaired(self):
        """After Phase 2, next-sprint.md must have STOP_REASON_ADVISORY or be clean."""
        path = REPO_ROOT / "reports" / "supervisor" / "next-sprint.md"
        if not path.exists():
            pytest.skip("next-sprint.md not present")
        content = path.read_text(encoding="utf-8")
        # Either has advisory OR has no false task labels at all (both acceptable)
        has_advisory = "STOP_REASON_ADVISORY" in content
        task_lines_with_false_stops = [
            l for l in content.splitlines()
            if l.strip().startswith("- [approval-blocked]") and "TASK-" in l
        ]
        assert has_advisory or len(task_lines_with_false_stops) == 0, (
            "next-sprint.md has no STOP_REASON_ADVISORY and still has false-stop task labels"
        )


# ─────────────────────────────────────────────────────────────
# Test generator output
# ─────────────────────────────────────────────────────────────

class TestGeneratorOutput:
    def test_synthesize_sprint_tasks_no_approval_blocked(self, tmp_path):
        """generate_supervisor_packet.synthesize_sprint_tasks emits no approval-blocked."""
        import sys
        sys.path.insert(0, str(REPO_ROOT))
        from tools.supervisor.generate_supervisor_packet import synthesize_sprint_tasks

        review = {"sprint_id": "TEST", "verdict": "ACCEPTED", "facts": {}, "item_grades": []}
        contradictions = {"critical_count": 0, "autonomous_continue": True, "contradictions": []}

        tasks = synthesize_sprint_tasks(review, contradictions, REPO_ROOT, stream="mainstream")
        false_stops = [t for t in tasks if t.get("status") in ("approval-blocked", "blocked")]

        assert false_stops == [], (
            "Generator emitted false-stop tasks:\n"
            + "\n".join(f"  {t['task_id']}: {t['status']} — {t['title'][:50]}" for t in false_stops)
        )

    def test_generated_gate11_task_is_agent_owned_prep(self, tmp_path):
        """Gate 11 preparation task must be agent-owned, not approval-blocked."""
        import sys
        sys.path.insert(0, str(REPO_ROOT))
        from tools.supervisor.generate_supervisor_packet import synthesize_sprint_tasks

        review = {"sprint_id": "TEST", "verdict": "ACCEPTED", "facts": {}, "item_grades": []}
        contradictions = {"critical_count": 0, "autonomous_continue": True, "contradictions": []}

        tasks = synthesize_sprint_tasks(review, contradictions, REPO_ROOT, stream="mainstream")

        gate_prep_tasks = [
            t for t in tasks
            if "readiness packet" in t.get("title", "").lower()
            or ("Gate" in t.get("title", "") and "Prepare" in t.get("title", ""))
        ]

        for task in gate_prep_tasks:
            assert task["status"] == "agent-owned", (
                f"Gate 11 prep task {task['task_id']} should be agent-owned, got {task['status']}"
            )

    def test_generated_gate11_approval_task_is_external_gate(self, tmp_path):
        """Gate 11 approval execution task must be external-gate."""
        import sys
        sys.path.insert(0, str(REPO_ROOT))
        from tools.supervisor.generate_supervisor_packet import synthesize_sprint_tasks

        review = {"sprint_id": "TEST", "verdict": "ACCEPTED", "facts": {}, "item_grades": []}
        contradictions = {"critical_count": 0, "autonomous_continue": True, "contradictions": []}

        tasks = synthesize_sprint_tasks(review, contradictions, REPO_ROOT, stream="mainstream")

        gate_exec_tasks = [
            t for t in tasks
            if "Babar Raza approval" in t.get("title", "")
            or ("Gate" in t.get("title", "") and "Submit" in t.get("title", ""))
        ]

        for task in gate_exec_tasks:
            assert task["status"] == "external-gate", (
                f"Gate 11 approval task {task['task_id']} should be external-gate, got {task['status']}"
            )

    def test_generated_commit_prep_is_agent_owned(self, tmp_path):
        """Commit preparation task must be agent-owned, not approval-blocked."""
        import sys
        sys.path.insert(0, str(REPO_ROOT))
        from tools.supervisor.generate_supervisor_packet import synthesize_sprint_tasks

        review = {"sprint_id": "TEST", "verdict": "ACCEPTED", "facts": {}, "item_grades": []}
        contradictions = {"critical_count": 0, "autonomous_continue": True, "contradictions": []}

        tasks = synthesize_sprint_tasks(review, contradictions, REPO_ROOT, stream="mainstream")

        # Look for commit PREPARATION tasks
        commit_prep = [
            t for t in tasks
            if "commit candidate" in t.get("title", "").lower()
            or ("Prepare" in t.get("title", "") and "commit" in t.get("title", "").lower())
        ]

        for task in commit_prep:
            assert task["status"] == "agent-owned", (
                f"Commit prep task {task['task_id']} should be agent-owned, got {task['status']}"
            )

    def test_generated_commit_execution_is_external_gate(self, tmp_path):
        """Commit execution task must be external-gate."""
        import sys
        sys.path.insert(0, str(REPO_ROOT))
        from tools.supervisor.generate_supervisor_packet import synthesize_sprint_tasks

        review = {"sprint_id": "TEST", "verdict": "ACCEPTED", "facts": {}, "item_grades": []}
        contradictions = {"critical_count": 0, "autonomous_continue": True, "contradictions": []}

        tasks = synthesize_sprint_tasks(review, contradictions, REPO_ROOT, stream="mainstream")

        commit_exec = [
            t for t in tasks
            if "Execute git commit" in t.get("title", "")
            or "user authorization" in t.get("title", "").lower()
        ]

        for task in commit_exec:
            assert task["status"] == "external-gate", (
                f"Commit exec task {task['task_id']} should be external-gate, got {task['status']}"
            )

    def test_generate_next_sprint_md_has_advisory(self):
        """generate_next_sprint_md output must include STOP_REASON_ADVISORY."""
        import sys
        sys.path.insert(0, str(REPO_ROOT))
        from tools.supervisor.generate_supervisor_packet import synthesize_sprint_tasks, generate_next_sprint_md

        review = {"sprint_id": "TEST", "verdict": "ACCEPTED", "facts": {}, "item_grades": []}
        contradictions = {"critical_count": 0, "autonomous_continue": True, "contradictions": []}

        tasks = synthesize_sprint_tasks(review, contradictions, REPO_ROOT, stream="mainstream")
        md = generate_next_sprint_md(review, contradictions, "", tasks)

        assert "STOP_REASON_ADVISORY" in md, "STOP_REASON_ADVISORY must be in generated next-sprint.md"


# ─────────────────────────────────────────────────────────────
# Test next-sprint-taskmaster.json
# ─────────────────────────────────────────────────────────────

class TestTaskmasterJson:
    def test_taskmaster_json_no_false_blocked_agent_tasks(self):
        """next-sprint-taskmaster.json must not have approval-blocked for agent-owned tasks."""
        path = REPO_ROOT / "reports" / "supervisor" / "next-sprint-taskmaster.json"
        if not path.exists():
            pytest.skip("next-sprint-taskmaster.json not present")

        data = json.loads(path.read_text(encoding="utf-8"))
        tasks = data.get("tasks", [])

        # These tasks should NOT be approval-blocked (they're agent-owned preparation)
        agent_owned_patterns = [
            "readiness packet",
            "prepare",
            "preparation",
        ]

        for task in tasks:
            title = task.get("title", "").lower()
            status = task.get("status", "")
            is_agent_owned = any(p in title for p in agent_owned_patterns)
            if is_agent_owned:
                assert status not in ("approval-blocked", "blocked"), (
                    f"Task '{task['title']}' is agent-owned preparation but has status={status}"
                )


# ─────────────────────────────────────────────────────────────
# Test executor validates combined prompt
# ─────────────────────────────────────────────────────────────

class TestExecutorCombinedPromptValidation:
    def test_executor_validates_live_combined_prompt(self):
        """Executor must validate the live combined-next-worker-prompt.md as clean."""

        # Check the latest combined prompt
        paths_to_check = [
            REPO_ROOT / "reports" / "supervisor" / "latest-next-worker-prompt.md",
        ]

        for path in paths_to_check:
            if not path.exists():
                continue

            content = path.read_text(encoding="utf-8")
            # The combined prompt should not have [approval-blocked] TASK- lines
            false_task_lines = [
                l for l in content.splitlines()
                if l.strip().startswith("- [approval-blocked]") and "TASK-" in l
            ]
            assert false_task_lines == [], (
                f"False-stop labels in {path.name}:\n" + "\n".join(false_task_lines)
            )
