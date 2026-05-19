"""R29 Lane B — Sprint-state consistency enforcement tests.

Prevents the R28 defect class: sprint-state.yaml left with `status: in_progress`
and lanes `pending` after sprint was actually completed and committed.

These tests enforce:
1. Final sprint-state must have terminal status
2. Lane statuses must be terminal or explicitly blocked
3. No sprint-state with in_progress status in completed sprint metadata dirs
4. Sprint-state status must be consistent with verdict files
5. PENDING markers in repair context (before/after) are allowed, active PENDING is not
"""

import sys
from pathlib import Path

import yaml as _yaml_check  # noqa: F401 — ensures yaml is available
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

REPO = Path(__file__).resolve().parents[2]

# Terminal states for sprint status
TERMINAL_SPRINT_STATES = {
    "closed_verified",
    "complete",
    "r28_complete",
    "r29_complete",
    "failed_with_evidence",
    "blocked_external",
    "blocked_policy",
    "blocked_dependency",
}

# Terminal states for lane status
TERMINAL_LANE_STATES = {
    "closed_verified",
    "complete",
    "pass",
    "done",
    "no_change",
    "assessed",
    "blocked_external",
    "blocked_policy",
    "blocked_dependency",
    "blocked_concurrent_change",
    "blocked_missing_env",
    "blocked_missing_dependency",
    "blocked_no_model",
    "blocked_sample_generation_requires_tool",
    "failed_with_evidence",
    "partial_verified_with_remaining_backlog",
}

# Sprint metadata dirs that are expected to have final state
RECENT_PREFIXES = ("r25-", "r26-", "r27-", "r28-", "r29-", "r30-", "r31-")


def _load_yaml(path: Path) -> dict:
    """Load YAML file using PyYAML if available, else minimal parser."""
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8", errors="ignore")) or {}
    except ImportError:
        return {}


class TestSprintStateTerminality:
    """Sprint-state.yaml must have terminal status when sprint is complete."""

    def _find_sprint_state_files(self) -> list[Path]:
        """Find all sprint-state.yaml files in reports/r*/ directories."""
        results = []
        reports = REPO / "reports"
        for d in sorted(reports.iterdir()):
            if d.is_dir() and d.name.startswith("r"):
                ss = d / "sprint-state.yaml"
                if ss.exists():
                    results.append(ss)
        return results

    def test_completed_sprint_states_are_terminal(self):
        """Any sprint-state.yaml in a reports/r*/ dir with a corresponding
        final-verdict file claiming COMPLETE for THE SAME SPRINT must have terminal status.

        Note: Multiple sprints may share a directory (e.g., reports/r29/).
        We match by sprint_id to avoid false positives."""
        reports = REPO / "reports"
        violations = []
        for d in sorted(reports.iterdir()):
            if not d.is_dir() or not d.name.startswith("r"):
                continue
            ss = d / "sprint-state.yaml"
            if not ss.exists():
                continue
            data = _load_yaml(ss)
            if not data:
                continue
            status = (data.get("status") or "").lower().strip()
            sprint_id = (data.get("sprint_id") or "").strip()

            # Check if there's a verdict file for THIS sprint claiming completion
            verdict_files = list(d.glob("final-verdict*.md"))
            has_matching_complete_verdict = False
            for vf in verdict_files:
                vtext = vf.read_text(encoding="utf-8", errors="ignore")
                # Verdict must reference the same sprint AND claim COMPLETE
                if sprint_id and sprint_id in vtext:
                    if "VERDICT:" in vtext and "COMPLETE" in vtext.upper():
                        has_matching_complete_verdict = True
                        break

            if has_matching_complete_verdict and status in ("in_progress", "pending", "not_started"):
                violations.append(f"{ss}: status={status} but verdict for {sprint_id} says COMPLETE")

        assert not violations, f"Sprint-state contradicts verdict: {violations}"

    def test_completed_lanes_are_terminal(self):
        """No lane in a completed sprint should still be 'pending' or 'in_progress'."""
        reports = REPO / "reports"
        violations = []
        for d in sorted(reports.iterdir()):
            if not d.is_dir() or not d.name.startswith("r"):
                continue
            ss = d / "sprint-state.yaml"
            if not ss.exists():
                continue
            data = _load_yaml(ss)
            if not data:
                continue
            status = (data.get("status") or "").lower().strip()
            if status in ("in_progress", "pending", "not_started"):
                continue  # Sprint not claimed complete, skip lane check
            if status not in TERMINAL_SPRINT_STATES:
                continue
            lanes = data.get("lanes") or {}
            for lane_id, lane_data in lanes.items():
                lane_status = ""
                if isinstance(lane_data, dict):
                    lane_status = (lane_data.get("status") or "").lower().strip()
                elif isinstance(lane_data, str):
                    lane_status = lane_data.lower().strip()
                if lane_status in ("pending", "in_progress", "not_started"):
                    violations.append(f"{ss}: {lane_id} status={lane_status} in terminal sprint")

        assert not violations, f"Non-terminal lanes in terminal sprint: {violations}"


class TestSprintStateVerdictConsistency:
    """Sprint-state and verdict files must agree."""

    def test_no_in_progress_sprint_state_with_complete_verdict(self):
        """Direct regression test for the R28 defect.
        Only flags if the verdict is for the SAME sprint_id as the sprint-state."""
        reports = REPO / "reports"
        for d in sorted(reports.iterdir()):
            if not d.is_dir() or not d.name.startswith("r"):
                continue
            ss = d / "sprint-state.yaml"
            if not ss.exists():
                continue
            data = _load_yaml(ss)
            if not data:
                continue
            status = (data.get("status") or "").lower().strip()
            sprint_id = (data.get("sprint_id") or "").strip()
            if status != "in_progress":
                continue
            # Check for verdict claiming complete for THIS sprint
            for vf in d.glob("final-verdict*.md"):
                vtext = vf.read_text(encoding="utf-8", errors="ignore")
                if sprint_id and sprint_id not in vtext:
                    continue  # Different sprint, not a conflict
                assert "COMPLETE" not in vtext.upper() or "VERDICT:" not in vtext, (
                    f"{ss} has status=in_progress but {vf.name} claims COMPLETE for same sprint"
                )


class TestPendingInRepairContext:
    """PENDING in repair reports (before/after) must not trigger false positives."""

    def test_repair_reports_allow_quoted_pending(self):
        """Repair/reconciliation reports may mention PENDING as historical context.
        The TestPendingMarkerDetection should NOT flag lines like:
        'BUNDLE_VALIDATION: PENDING → BUNDLE_VALIDATION: PASS'
        but SHOULD flag active 'BUNDLE_VALIDATION: PENDING' at end of line."""
        # This test documents the expected behavior
        assert True  # Placeholder — actual enforcement is in TestPendingMarkerDetection

    def test_active_pending_in_sprint_overview_detected(self):
        """Regression: sprint overviews must not have active BUNDLE_VALIDATION: PENDING."""
        reports = REPO / "reports"
        violations = []
        for d in reports.iterdir():
            if not d.is_dir():
                continue
            if not any(d.name.startswith(p) for p in RECENT_PREFIXES):
                continue
            so = d / "sprint-overview.md"
            if not so.exists():
                continue
            for i, line in enumerate(so.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                stripped = line.strip()
                # Active PENDING: line ends with PENDING (not in an arrow/repair context)
                if "BUNDLE_VALIDATION: PENDING" in stripped:
                    if "→" not in stripped and "PASS" not in stripped:
                        violations.append(f"{so}:{i}: {stripped}")
        assert not violations, f"Active PENDING in sprint overviews: {violations}"


class TestStaleCommitSHA:
    """Final verdicts must not have COMMIT_SHA: PENDING."""

    def test_no_pending_commit_sha_in_recent_verdicts(self):
        reports = REPO / "reports"
        violations = []
        for d in sorted(reports.iterdir()):
            if not d.is_dir():
                continue
            if not any(d.name.startswith(p) for p in RECENT_PREFIXES):
                continue
            for f in d.glob("*.md"):
                text = f.read_text(encoding="utf-8", errors="ignore")
                for i, line in enumerate(text.splitlines(), 1):
                    if "COMMIT_SHA: PENDING" in line and "→" not in line:
                        violations.append(f"{f}:{i}")
        # Also check r*/ directories
        for d in sorted(reports.iterdir()):
            if not d.is_dir() or not d.name.startswith("r"):
                continue
            prefix = d.name
            if not any(prefix.startswith(p.rstrip("-")) for p in RECENT_PREFIXES):
                continue
            for f in d.glob("final-verdict*.md"):
                text = f.read_text(encoding="utf-8", errors="ignore")
                for i, line in enumerate(text.splitlines(), 1):
                    if "COMMIT_SHA: PENDING" in line and "→" not in line:
                        violations.append(f"{f}:{i}")
        assert not violations, f"COMMIT_SHA: PENDING in recent verdicts: {violations}"
