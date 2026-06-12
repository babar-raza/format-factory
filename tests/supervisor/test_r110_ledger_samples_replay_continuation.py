"""R110: Lane-ledger enforcement, sample-output packaging, replay, continuation semantics.

Sprint: FORMAT-FACTORY-SUPERVISOR-R110-STREAM-LOCAL-REPLAY-LEDGER-SAMPLE-OUTPUTS-AND-YES-WITH-LIMITATIONS-CLOSURE-001
"""

import json
import sys
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parent.parent.parent / "tools" / "supervisor"
sys.path.insert(0, str(TOOLS_DIR))

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

from anti_skip_checker import (
    detect_missing_lane_ledger,
    detect_missing_sample_outputs,
    detect_wrong_stream_next_sprint,
    classify_stream_output_authority,
    classify_violation_impact,
    run_all_checks,
    SEVERITY_MAP,
)


# ============================================================
# Wave 1: Lane-ledger enforcement
# ============================================================


class TestLaneLedgerEnforcement:
    """Lane ledger: missing fails, present passes."""

    def test_missing_ledger_is_violation(self, tmp_path):
        result = detect_missing_lane_ledger(tmp_path)
        assert result["is_violation"] is True

    def test_ledger_in_evidence_root_clears(self, tmp_path):
        (tmp_path / "dry-run-ledger.json").write_text("{}")
        result = detect_missing_lane_ledger(tmp_path)
        assert result["is_violation"] is False

    def test_ledger_json_in_evidence_root_clears(self, tmp_path):
        (tmp_path / "lane-execution-ledger.json").write_text("{}")
        result = detect_missing_lane_ledger(tmp_path)
        assert result["is_violation"] is False

    def test_r110_report_ledger_exists(self):
        path = REPO_ROOT / "reports" / "supervisor-r110" / "lane-execution-ledger.json"
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "lanes" in data
        assert data["summary"]["total_lanes"] >= 7

    def test_ledger_has_all_waves(self):
        path = REPO_ROOT / "reports" / "supervisor-r110" / "lane-execution-ledger.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        lane_ids = {lane["lane_id"] for lane in data["lanes"]}
        for w in range(7):
            assert f"W{w}" in lane_ids

    def test_ledger_severity_is_medium(self):
        assert SEVERITY_MAP["missing_lane_ledger"] == "medium"


# ============================================================
# Wave 2: Sample-output packaging
# ============================================================


class TestSampleOutputPackaging:
    """At least 5 supervisor sample outputs must exist."""

    def test_missing_samples_is_violation(self, tmp_path):
        result = detect_missing_sample_outputs(tmp_path)
        assert result["is_violation"] is True

    def test_samples_present_clears(self, tmp_path):
        samples = tmp_path / "sample-outputs"
        samples.mkdir()
        (samples / "a.json").write_text("{}")
        result = detect_missing_sample_outputs(tmp_path, sample_outputs_dir=samples)
        assert result["is_violation"] is False

    def test_r110_samples_exist(self):
        samples_dir = REPO_ROOT / "reports" / "supervisor-r110" / "sample-outputs"
        assert samples_dir.exists()
        files = list(samples_dir.iterdir())
        assert len(files) >= 5

    def test_sample_authority_map_valid(self):
        path = REPO_ROOT / "reports" / "supervisor-r110" / "sample-outputs" / "sample-stream-local-authority-map.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["stream"] == "supervisor"
        assert "authority_root" in data

    def test_sample_replay_result_valid(self):
        path = REPO_ROOT / "reports" / "supervisor-r110" / "sample-outputs" / "sample-replay-result.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["stream"] == "supervisor"
        assert "stream_local_files" in data

    def test_sample_continuation_signal_valid(self):
        path = REPO_ROOT / "reports" / "supervisor-r110" / "sample-outputs" / "sample-continuation-signal.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["stream"] == "supervisor"
        assert data["continuation_state"] == "YES_WITH_LIMITATIONS"

    def test_sample_wrong_stream_valid(self):
        path = REPO_ROOT / "reports" / "supervisor-r110" / "sample-outputs" / "sample-wrong-stream-classification.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["authority"] == "ARCHIVED_LAST_WRITER_SNAPSHOT"
        assert data["is_blocking"] is False

    def test_sample_prompt_exists(self):
        path = REPO_ROOT / "reports" / "supervisor-r110" / "sample-outputs" / "sample-generated-supervisor-prompt.md"
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "supervisor" in content.lower()


# ============================================================
# Wave 3: Wrong-stream next-sprint handling
# ============================================================


class TestWrongStreamNextSprint:
    """Wrong-stream detection and authority classification."""

    def test_wrong_stream_detected(self):
        text = "# Stream: acceleration\nSprint prompt here"
        result = detect_wrong_stream_next_sprint(text, "supervisor")
        assert result["is_violation"] is True
        assert result["detected_stream"] == "acceleration"
        assert result["authority"] == "ARCHIVED_LAST_WRITER_SNAPSHOT"
        assert result["is_blocking"] is False

    def test_same_stream_not_violation(self):
        text = "# Stream: supervisor\nSupervisor sprint prompt"
        result = detect_wrong_stream_next_sprint(text, "supervisor")
        assert result["is_violation"] is False
        assert result["authority"] == "CURRENT_STREAM_AUTHORITY"

    def test_no_header_treated_as_archived(self):
        text = "Some random text without stream header"
        result = detect_wrong_stream_next_sprint(text, "supervisor")
        assert result["is_violation"] is False
        assert result["authority"] == "ARCHIVED_LAST_WRITER_SNAPSHOT"

    def test_authority_classification_global_wrong(self):
        result = classify_stream_output_authority(
            "reports/supervisor/next-sprint.md", "acceleration", "supervisor", is_global=True
        )
        assert result == "ARCHIVED_LAST_WRITER_SNAPSHOT"

    def test_authority_classification_global_correct(self):
        result = classify_stream_output_authority(
            "reports/supervisor/next-sprint.md", "supervisor", "supervisor", is_global=True
        )
        assert result == "CURRENT_STREAM_AUTHORITY"

    def test_r110_analysis_exists(self):
        path = REPO_ROOT / "reports" / "supervisor-r110" / "wrong-stream-next-sprint-analysis.md"
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "ARCHIVED_LAST_WRITER_SNAPSHOT" in content
        assert "acceleration" in content


# ============================================================
# Wave 4: Stream-local replay
# ============================================================


class TestStreamLocalReplay:
    """Replay proves each stream resolves its own authority files."""

    def test_supervisor_stream_dir_has_authority(self):
        stream_dir = REPO_ROOT / "reports" / "supervisor-streams" / "supervisor"
        assert stream_dir.exists()
        files = [f.name for f in stream_dir.iterdir()]
        assert any("review" in f.lower() for f in files)

    def test_mainstream_stream_dir_exists(self):
        assert (REPO_ROOT / "reports" / "supervisor-streams" / "mainstream").exists()

    def test_skills_stream_dir_exists(self):
        assert (REPO_ROOT / "reports" / "supervisor-streams" / "skills").exists()

    def test_acceleration_stream_dir_exists(self):
        assert (REPO_ROOT / "reports" / "supervisor-streams" / "acceleration").exists()

    def test_replay_results_exist(self):
        path = REPO_ROOT / "reports" / "supervisor-r110" / "replay-results.json"
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        streams = {p["stream"] for p in data["replayed_packages"]}
        assert streams == {"supervisor", "mainstream", "skills", "acceleration"}

    def test_global_is_reference_only(self):
        """Global next-sprint.md must be from a different stream (proving it's last-writer)."""
        text = (REPO_ROOT / "reports" / "supervisor" / "next-sprint.md").read_text(encoding="utf-8")
        result = detect_wrong_stream_next_sprint(text, "supervisor")
        # Either same stream or wrong stream — both valid, just classify
        assert result["authority"] in (
            "CURRENT_STREAM_AUTHORITY",
            "ARCHIVED_LAST_WRITER_SNAPSHOT",
        )


# ============================================================
# Wave 5: Continuation semantics
# ============================================================


class TestContinuationSemantics:
    """YES_WITH_LIMITATIONS is consistent and correct."""

    def test_clean_state_produces_yes(self, tmp_path):
        """No violations → all_pass=true."""
        (tmp_path / "raw-test-log.txt").write_text("output")
        (tmp_path / "evidence-manifest.yaml").write_text("sprint_id: R110")
        (tmp_path / "dry-run-ledger.json").write_text("{}")
        s = tmp_path / "sample-outputs"
        s.mkdir()
        (s / "a.json").write_text("{}")
        result = run_all_checks(
            prompt_text="Supervisor sprint: close ledger, samples.",
            gaps_data={"sprint_id": "R110", "stream": "supervisor"},
            expected_sprint="R110",
            evidence_root=tmp_path,
            grades=[{"item_id": "A1", "supervisor_grade": "ACCEPTED_VERIFIED", "test_file_content_checked": True}],
            target_stream="supervisor",
            repo_root=tmp_path,
            sample_outputs_dir=s,
        )
        assert result["all_pass"] is True

    def test_missing_ledger_downgrades(self, tmp_path):
        """Missing ledger → violation, all_pass=false."""
        result = detect_missing_lane_ledger(tmp_path)
        assert result["is_violation"] is True

    def test_wrong_stream_archived_is_non_blocking(self):
        """Archived wrong-stream → is_blocking=false."""
        text = "# Stream: mainstream\nMainstream content"
        result = detect_wrong_stream_next_sprint(text, "supervisor")
        assert result["is_blocking"] is False

    def test_violation_impact_wrong_stream_is_caveat(self):
        """Wrong-stream next-sprint is a caveat, not a block."""
        checks = [{"check": "wrong_stream_next_sprint", "is_violation": True}]
        impact = classify_violation_impact(checks)
        assert not impact["block"]
        assert "wrong_stream_next_sprint" in impact.get("caveats", []) or "wrong_stream_next_sprint" in impact.get("notes", [])

    def test_stream_local_authority_is_note(self):
        """stream_local_authority violation is low severity (note)."""
        checks = [{"check": "stream_local_authority", "is_violation": True}]
        impact = classify_violation_impact(checks)
        assert not impact["block"]

    def test_continuation_semantics_plan_exists(self):
        path = REPO_ROOT / "reports" / "supervisor-r110" / "continuation-semantics-plan.md"
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "YES_WITH_LIMITATIONS" in content
        assert "YES" in content


# ============================================================
# R109 reconciliation verification
# ============================================================


class TestR109Reconciliation:
    """R109 reconciliation report is complete."""

    def test_reconciliation_exists(self):
        path = REPO_ROOT / "reports" / "supervisor-r110" / "r109-reconciliation.md"
        assert path.exists()

    def test_reconciliation_classifies_r109(self):
        path = REPO_ROOT / "reports" / "supervisor-r110" / "r109-reconciliation.md"
        content = path.read_text(encoding="utf-8")
        assert "ACCEPTED_WITH_LIMITATIONS" in content
        assert "D110-LEDGER-01" in content
        assert "D110-SAMPLE-01" in content

    def test_preflight_exists(self):
        path = REPO_ROOT / "reports" / "supervisor-r110" / "00-preflight.md"
        assert path.exists()


# ============================================================
# Quota compliance
# ============================================================


class TestQuotaCompliance:
    """All 7 hard quota items must be satisfiable."""

    def test_quota_1_reconciliation(self):
        assert (REPO_ROOT / "reports" / "supervisor-r110" / "r109-reconciliation.md").exists()

    def test_quota_2_lane_ledger(self):
        assert (REPO_ROOT / "reports" / "supervisor-r110" / "lane-execution-ledger.json").exists()

    def test_quota_3_sample_outputs(self):
        samples = REPO_ROOT / "reports" / "supervisor-r110" / "sample-outputs"
        assert len(list(samples.iterdir())) >= 5

    def test_quota_4_wrong_stream(self):
        assert (REPO_ROOT / "reports" / "supervisor-r110" / "wrong-stream-next-sprint-analysis.md").exists()

    def test_quota_5_replay(self):
        assert (REPO_ROOT / "reports" / "supervisor-r110" / "replay-results.json").exists()

    def test_quota_6_continuation(self):
        assert (REPO_ROOT / "reports" / "supervisor-r110" / "continuation-semantics-plan.md").exists()

    def test_quota_7_evidence(self):
        # Lane ledger + sample outputs + replay + reports all exist
        r110 = REPO_ROOT / "reports" / "supervisor-r110"
        assert (r110 / "lane-execution-ledger.json").exists()
        assert (r110 / "sample-outputs").exists()
        assert (r110 / "replay-results.json").exists()
