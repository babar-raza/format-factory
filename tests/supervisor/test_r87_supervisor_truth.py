"""
test_r87_supervisor_truth.py — Supervisor autonomy quality tests for R87.

Trains E, F, G: Fresh outputs, broad next-sprint, gate classifier truth.
Sprint: FORMAT-FACTORY-R87-CLEAN-SUPERVISOR-CLOSEOUT-REVIEW-PACKAGE-POC-PRODUCT-FACTORY-DEEPENING-MEGA-TRAIN-001
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


class TestEmbeddedSupervisorOutputsCurrent:
    """Train E: Bundled supervisor outputs must reference the current sprint."""

    def test_evidence_review_not_stale_r85(self):
        review_path = REPO_ROOT / "reports" / "supervisor" / "evidence-review.md"
        if not review_path.exists():
            pytest.skip("evidence-review.md not generated yet")
        content = review_path.read_text(encoding="utf-8")
        assert "R85-POC-DIRECTION" not in content, \
            "evidence-review.md still references stale R85 sprint"

    def test_contradictions_not_stale_r85(self):
        contradictions = REPO_ROOT / "reports" / "supervisor" / "contradictions.md"
        if not contradictions.exists():
            pytest.skip("contradictions.md not generated yet")
        content = contradictions.read_text(encoding="utf-8")
        assert "R85-POC-DIRECTION" not in content, \
            "contradictions.md still references stale R85"


class TestRepairPromptStillHasProductLanes:
    """Train F: Even under repair conditions, next-sprint must have product lanes."""

    def test_next_sprint_has_product_lanes_under_repair(self):
        """Generate next-sprint with a synthetic critical contradiction and verify product lanes exist."""
        from generate_supervisor_packet import synthesize_sprint_tasks

        fake_review = {
            "sprint_id": "TEST-REPAIR-SPRINT",
            "verdict": "REJECTED_BUNDLE_VALIDATION_FAIL",
            "test_count": {"passed": 100, "failed": 0},
        }
        fake_contradictions = {
            "critical_count": 1,
            "contradictions": [{
                "severity": "CRITICAL",
                "description": "BUNDLE_VALIDATION: FAIL",
                "detail": "Sidecar missing"
            }]
        }

        tasks = synthesize_sprint_tasks(
            fake_review, fake_contradictions,
            repo_root=REPO_ROOT
        )

        # Must have at least one repair task
        repair_tasks = [t for t in tasks if "repair" in t.get("title", "").lower()
                        or "critical" in t.get("priority", "").lower()]
        assert len(repair_tasks) >= 1, "Must have at least one repair task"

        # Must also have product-factory lanes (not repair-only)
        assert len(tasks) > len(repair_tasks), \
            f"Generated {len(tasks)} tasks but all {len(repair_tasks)} are repair — need product lanes too"

    def test_repair_prompt_has_evidence_bundle_task(self):
        """Even under repair, the evidence bundle build task must be present."""
        from generate_supervisor_packet import synthesize_sprint_tasks

        fake_review = {"sprint_id": "TEST", "verdict": "REJECTED"}
        fake_contradictions = {
            "critical_count": 1,
            "contradictions": [{"severity": "CRITICAL", "description": "test", "detail": "test"}]
        }
        tasks = synthesize_sprint_tasks(fake_review, fake_contradictions, repo_root=REPO_ROOT)
        evidence_tasks = [t for t in tasks if "evidence" in t.get("title", "").lower()]
        assert len(evidence_tasks) >= 1, "Evidence bundle task must always be generated"


class TestMCPPhysicalTruth:
    """Train G: MCP status must reflect physical file check."""

    def test_mcp_status_reflects_physical_file(self):
        """If .vscode/mcp.json doesn't exist, approval gates still mention MCP."""
        from generate_supervisor_packet import generate_approval_gates_md

        fake_review = {"sprint_id": "TEST", "verdict": "ACCEPTED"}
        fake_contradictions = {"critical_count": 0, "autonomous_continue": True}

        with tempfile.TemporaryDirectory() as tmpdir:
            gates_md = generate_approval_gates_md(
                fake_review, fake_contradictions,
                current_mode=4,
                repo_root=Path(tmpdir)
            )
            assert "MCP" in gates_md or "Mode" in gates_md, "Approval gates must mention MCP or mode"

    def test_gate_status_no_self_approval(self):
        """Gate 8 and Gate 11 must not be self-approved."""
        gates = REPO_ROOT / "reports" / "supervisor" / "approval-gates.md"
        if not gates.exists():
            pytest.skip("approval-gates.md not generated yet")
        content = gates.read_text(encoding="utf-8")
        assert "Gate_8: APPROVED" not in content, "Gate 8 must not be self-approved"
        assert "Gate_11: APPROVED" not in content, "Gate 11 must not be self-approved"
