"""
Tests for tools/supervisor/lifecycle_audit.py

Task: TC-UNIFIED-010 (agile-munching-quasar TC-LIF-002)
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure tools/ is importable
_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO))

from tools.supervisor.lifecycle_audit import (
    check_mission_complete,
    generate_audit_taskcard,
    main,
    run_lifecycle_audit,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_repo(tmp_path: Path, signal: dict | None = None, has_rework_review: bool = False) -> Path:
    """Create a minimal fake repo structure for testing."""
    # Continuation signal
    sig_dir = tmp_path / ".local" / "supervisor"
    sig_dir.mkdir(parents=True, exist_ok=True)
    default_signal = {
        "autonomous_continue": True,
        "stop_reason": "",
        "rework_items": [],
        "govblock_resolved_by": None,
        "iteration": 0,
    }
    if signal is not None:
        default_signal.update(signal)
    (sig_dir / "continuation-signal.json").write_text(json.dumps(default_signal))

    # Optional evidence review
    if has_rework_review:
        reviews_dir = tmp_path / "reports" / "supervisor"
        reviews_dir.mkdir(parents=True, exist_ok=True)
        (reviews_dir / "evidence-review.md").write_text("Status: ACCEPTED_WITH_REWORK\n")

    return tmp_path


# ---------------------------------------------------------------------------
# TC-LIF-002 Tests (9 tests per plan spec)
# ---------------------------------------------------------------------------


class TestLifecycleAuditPass:
    def test_audit_pass_when_signal_clean(self, tmp_path):
        repo = _make_repo(tmp_path, signal={"autonomous_continue": True, "rework_items": []})
        result = run_lifecycle_audit(repo_root=repo, mission_id="TEST-MISSION", sprint_id="TC-TEST-001")
        assert result["verdict"] == "AUDIT_PASS"
        assert result["next_iteration_required"] is False
        assert result["mission_complete"] is True

    def test_output_file_written(self, tmp_path):
        repo = _make_repo(tmp_path)
        run_lifecycle_audit(repo_root=repo)
        output = repo / ".local/supervisor/lifecycle-audit-results.json"
        assert output.exists()
        data = json.loads(output.read_text())
        assert "verdict" in data
        assert "findings" in data
        assert "audited_at" in data

    def test_mission_complete_true_when_all_clean(self, tmp_path):
        repo = _make_repo(tmp_path, signal={"autonomous_continue": True, "rework_items": []})
        result = run_lifecycle_audit(repo_root=repo, mission_id="TEST")
        assert check_mission_complete(repo_root=repo, mission_id="TEST") is True


class TestLifecycleAuditGovBlock:
    def test_audit_requires_iteration_when_govblock(self, tmp_path):
        repo = _make_repo(
            tmp_path,
            signal={
                "autonomous_continue": False,
                "stop_reason": "critical_rework_blocks_continuation",
                "rework_items": ["GOV_BLOCK:monolith_detection_validator"],
                "govblock_resolved_by": None,
            },
        )
        result = run_lifecycle_audit(repo_root=repo)
        assert result["verdict"] == "AUDIT_REQUIRES_ITERATION"
        assert any(f["type"] == "GOVBLOCK_PRESENT" for f in result["findings"])
        assert result["next_iteration_required"] is True

    def test_mission_complete_false_when_rework_present(self, tmp_path):
        repo = _make_repo(
            tmp_path,
            signal={
                "autonomous_continue": False,
                "rework_items": ["GOV_BLOCK:monolith_detection_validator"],
                "govblock_resolved_by": None,
            },
        )
        assert check_mission_complete(repo_root=repo) is False

    def test_govblock_clears_when_resolved_by_set(self, tmp_path):
        repo = _make_repo(
            tmp_path,
            signal={
                "autonomous_continue": True,
                "rework_items": ["GOV_BLOCK:monolith_detection_validator"],
                "govblock_resolved_by": "TC-UNIFIED-001-xcf-parser-loc-reduction",
            },
        )
        result = run_lifecycle_audit(repo_root=repo)
        # govblock_resolved_by is truthy, so GOVBLOCK_PRESENT should NOT fire
        assert not any(f["type"] == "GOVBLOCK_PRESENT" for f in result["findings"])


class TestLifecycleAuditContinuationBlocked:
    def test_audit_requires_iteration_when_continuation_false(self, tmp_path):
        repo = _make_repo(
            tmp_path,
            signal={
                "autonomous_continue": False,
                "stop_reason": "some_internal_reason",
                "rework_items": [],
            },
        )
        result = run_lifecycle_audit(repo_root=repo)
        assert result["verdict"] == "AUDIT_REQUIRES_ITERATION"
        assert any(f["type"] == "CONTINUATION_BLOCKED" for f in result["findings"])


class TestLifecycleAuditRework:
    def test_rework_pending_from_evidence_review(self, tmp_path):
        repo = _make_repo(tmp_path, has_rework_review=True)
        result = run_lifecycle_audit(repo_root=repo)
        assert result["verdict"] == "AUDIT_REQUIRES_ITERATION"
        assert any(f["type"] == "REWORK_PENDING" for f in result["findings"])


class TestGenerateAuditTaskcard:
    def test_generate_taskcard_has_required_fields(self):
        finding = {
            "finding_id": "FIND-GOV-001",
            "type": "GOVBLOCK_PRESENT",
            "severity": "CRITICAL",
            "description": "GOV_BLOCK item present",
            "source_file": "continuation-signal.json",
            "recommended_action": "Fix monolith",
        }
        tc = generate_audit_taskcard(finding, mission_id="TEST-MISSION")
        assert "task_id" in tc
        assert "status" in tc
        assert tc["status"] == "READY"
        assert "objective" in tc
        assert "finding_ref" in tc
        assert tc["finding_ref"] == "FIND-GOV-001"
        assert tc["mission_id"] == "TEST-MISSION"


class TestAdversarialLifecycleControls:
    """
    Adversarial controls: prove these specific failure modes are blocked.
    These tests address TC-LIF-006 adversarial requirements from agile-munching-quasar.
    """

    def test_iteration_limit_does_not_produce_mission_complete(self, tmp_path):
        """iteration == max_iterations with blocked continuation must NOT produce mission_complete=True."""
        _make_repo(tmp_path, signal={
            "autonomous_continue": False,
            "stop_reason": "max_iterations_reached",
            "rework_items": [],
            "iteration": 12,
            "max_iterations": 12,
        })
        result = run_lifecycle_audit(repo_root=tmp_path, mission_id="TEST-MISSION")
        # CONTINUATION_BLOCKED fires (autonomous_continue=False) → AUDIT_REQUIRES_ITERATION
        assert result["mission_complete"] is False
        assert result["next_iteration_required"] is True

    def test_closeout_artifact_does_not_terminate_with_open_gaps(self, tmp_path):
        """If mission ledger has open gaps, mission is not complete even with clean signal."""
        _make_repo(tmp_path, signal={"autonomous_continue": True, "rework_items": []})
        # lifecycle_audit.py reads ledger["gaps"][i]["gap_id"] for status != closed/resolved
        ledger_dir = tmp_path / ".local" / "supervisor"
        ledger_dir.mkdir(parents=True, exist_ok=True)
        (ledger_dir / "product-mission-ledger.json").write_text(
            json.dumps({
                "mission_id": "TEST-MISSION",
                "gaps": [{"gap_id": "gap-001", "status": "open"}],
            })
        )
        assert check_mission_complete(repo_root=tmp_path, mission_id="TEST-MISSION") is False

    def test_single_execution_cannot_claim_mission_complete_with_rework(self, tmp_path):
        """After single execution leaving ACCEPTED_WITH_REWORK in evidence, mission is not complete."""
        _make_repo(tmp_path, signal={"autonomous_continue": True, "rework_items": []}, has_rework_review=True)
        result = run_lifecycle_audit(repo_root=tmp_path, mission_id="TEST-MISSION", sprint_id="TC-TEST")
        # REWORK_PENDING fires from evidence-review.md → AUDIT_REQUIRES_ITERATION
        assert result["verdict"] != "AUDIT_PASS"
        assert result["next_iteration_required"] is True

    def test_audit_output_file_is_required_artifact(self, tmp_path):
        """lifecycle_audit must produce lifecycle-audit-results.json before verdict is trusted."""
        _make_repo(tmp_path, signal={"autonomous_continue": True, "rework_items": []})
        run_lifecycle_audit(repo_root=tmp_path, mission_id="TEST-MISSION", sprint_id="TC-TEST")
        output = tmp_path / ".local" / "supervisor" / "lifecycle-audit-results.json"
        assert output.exists(), "audit output file must be written"
        data = json.loads(output.read_text())
        assert "verdict" in data
        assert "mission_complete" in data
        assert "next_iteration_required" in data


class TestAdvisoryReworkPending:
    def test_advisory_rework_does_not_block_mission_complete(self, tmp_path):
        """Non-GOV_BLOCK rework items with truthy autonomous_continue must NOT block AUDIT_PASS."""
        repo = _make_repo(
            tmp_path,
            signal={
                "autonomous_continue": "true_with_rework",
                "rework_items": ["LANE_ENFORCEMENT:1_violations"],
            },
        )
        result = run_lifecycle_audit(repo_root=repo, mission_id="TEST")
        assert result["verdict"] == "AUDIT_PASS"
        assert result["mission_complete"] is True
        assert result["next_iteration_required"] is False

    def test_advisory_rework_appears_in_findings(self, tmp_path):
        """ADVISORY_REWORK_PENDING finding must be present when non-GOV_BLOCK rework items exist."""
        repo = _make_repo(
            tmp_path,
            signal={
                "autonomous_continue": "true_with_rework",
                "rework_items": ["LANE_ENFORCEMENT:1_violations"],
            },
        )
        result = run_lifecycle_audit(repo_root=repo, mission_id="TEST")
        assert any(f["type"] == "ADVISORY_REWORK_PENDING" for f in result["findings"])


class TestLifecycleAuditCLI:
    def test_cli_exit_code_0_on_pass(self, tmp_path):
        repo = _make_repo(tmp_path, signal={"autonomous_continue": True, "rework_items": []})
        exit_code = main([
            "--mission-id", "TEST",
            "--sprint-id", "TC-TEST",
            "--repo-root", str(repo),
            "--json",
        ])
        assert exit_code == 0

    def test_cli_exit_code_1_on_iteration_required(self, tmp_path):
        repo = _make_repo(
            tmp_path,
            signal={
                "autonomous_continue": False,
                "stop_reason": "blocked",
                "rework_items": ["GOV_BLOCK:monolith_detection_validator"],
                "govblock_resolved_by": None,
            },
        )
        exit_code = main([
            "--mission-id", "TEST",
            "--repo-root", str(repo),
            "--json",
        ])
        assert exit_code == 1


class TestVacuousCallGuard:
    """TC-RJO-004: Vacuous-call guard — no plan_path and no mission_id."""

    def test_vacuous_call_returns_audit_pass_vacuous(self, tmp_path):
        """Without plan_path or mission_id, verdict must be AUDIT_PASS_VACUOUS, not AUDIT_PASS."""
        from tools.supervisor.lifecycle_audit import run_lifecycle_audit

        result = run_lifecycle_audit(repo_root=tmp_path)
        assert result["verdict"] == "AUDIT_PASS_VACUOUS", (
            f"Expected AUDIT_PASS_VACUOUS but got {result['verdict']!r}"
        )
        assert result["mission_complete"] is False, (
            "mission_complete must be False for vacuous call"
        )
        finding_types = [f["type"] for f in result.get("findings", [])]
        assert "VACUOUS_CALL" in finding_types, (
            f"Expected VACUOUS_CALL finding, got: {finding_types}"
        )

    def test_vacuous_call_writes_output_file(self, tmp_path):
        """Vacuous-call guard must still write lifecycle-audit-results.json."""
        import json
        from tools.supervisor.lifecycle_audit import run_lifecycle_audit

        # Create expected output directory
        out_dir = tmp_path / ".local" / "supervisor"
        out_dir.mkdir(parents=True)

        run_lifecycle_audit(repo_root=tmp_path)

        out_path = tmp_path / ".local" / "supervisor" / "lifecycle-audit-results.json"
        assert out_path.exists(), "lifecycle-audit-results.json must be written even for vacuous calls"
        data = json.loads(out_path.read_text(encoding="utf-8"))
        assert data["verdict"] == "AUDIT_PASS_VACUOUS"


# ---------------------------------------------------------------------------
# TC-RJO-NEW-001: READY status must be parsed as open (non-terminal)
# ---------------------------------------------------------------------------


class TestReadyStatusParsing:
    """TC-RJO-NEW-001: READY tasks must be detected as open, not missed."""

    def test_plan_with_ready_tasks_reports_open_taskcards(self, tmp_path):
        """A plan using READY status must not produce all_taskcards_closed=True."""
        from tools.supervisor.lifecycle_audit import _TERMINAL_STATUSES, parse_plan_taskcards

        plan = tmp_path / "test-plan.md"
        plan.write_text(
            "### TC-TEST-001: Some Task\n"
            "**Status:** READY\n"
            "\n"
            "### TC-TEST-002: Another Task\n"
            "**Status:** CLOSED\n"
        )
        tcs = parse_plan_taskcards(plan)
        tc_ids = {tc["tc_id"] for tc in tcs}
        assert "TC-TEST-001" in tc_ids, "READY taskcard must be parsed"
        assert "TC-TEST-002" in tc_ids, "CLOSED taskcard must be parsed"
        ready_tc = next(tc for tc in tcs if tc["tc_id"] == "TC-TEST-001")
        assert ready_tc["status"] == "READY"
        assert ready_tc["status"].upper() not in _TERMINAL_STATUSES, (
            "READY is not terminal — it must appear as open"
        )


# ---------------------------------------------------------------------------
# TC-RJO-NEW-002: --track parameter selects correct signal path
# ---------------------------------------------------------------------------


class TestTrackParameter:
    """TC-RJO-NEW-002: --track selects correct continuation signal path."""

    def test_machinery_track_reads_machinery_signal(self, tmp_path):
        """--track machinery must read from .local/supervisor/machinery/continuation-signal.json."""
        from tools.supervisor.lifecycle_audit import run_lifecycle_audit

        # Create a blocked legacy signal
        legacy_dir = tmp_path / ".local" / "supervisor"
        legacy_dir.mkdir(parents=True)
        (legacy_dir / "continuation-signal.json").write_text(
            json.dumps({"autonomous_continue": False, "stop_reason": "blocked", "rework_items": []})
        )

        # Create a clean machinery signal
        mach_dir = legacy_dir / "machinery"
        mach_dir.mkdir(parents=True)
        (mach_dir / "continuation-signal.json").write_text(
            json.dumps({"autonomous_continue": True, "rework_items": []})
        )

        result = run_lifecycle_audit(repo_root=tmp_path, track="machinery")
        assert not any(f["type"] == "CONTINUATION_BLOCKED" for f in result["findings"]), (
            "CONTINUATION_BLOCKED must not fire when machinery track signal is clean"
        )
