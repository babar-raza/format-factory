"""Tests for anti_skip_checker.py — R102 Wave 1 + R103/R104/R105 hardening."""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"))

from anti_skip_checker import (
    detect_generic_prompt,
    detect_stale_gaps,
    detect_missing_raw_logs,
    detect_path_only_acceptance,
    detect_missing_evidence_manifest,
    detect_missing_report_files,
    detect_missing_lane_ledger,
    detect_cross_stream_prompt_contamination,
    detect_missing_sample_outputs,
    detect_dirty_git_state,
    detect_wrong_stream_gaps,
    run_all_checks,
)


# --- Generic prompt detection ---

def test_generic_prompt_detected():
    """Positive: generic prompt with no stream markers."""
    result = detect_generic_prompt("Continue with next sprint tasks. Proceed with remaining work.")
    assert result["is_violation"] is True


def test_generic_prompt_not_detected():
    """Negative: prompt with stream-specific content."""
    result = detect_generic_prompt(
        "Mainstream product sprint: implement FODS save capability. "
        "Acceleration tooling: add tests for router. "
        "Skills registry: add new governed skill. "
        "Supervisor pipeline: fix grading."
    )
    assert result["is_violation"] is False


def test_generic_prompt_edge_case():
    """Negative: empty prompt is not generic (no generic markers)."""
    result = detect_generic_prompt("")
    assert result["is_violation"] is False


# --- Stale gap detection ---

def test_stale_gaps_detected():
    """Positive: sprint mismatch is violation."""
    result = detect_stale_gaps({"sprint_id": "R98"}, "R102")
    assert result["is_violation"] is True


def test_stale_gaps_not_detected():
    """Negative: matching sprint is not violation."""
    result = detect_stale_gaps({"sprint_id": "R102"}, "R102")
    assert result["is_violation"] is False


def test_stale_gaps_empty():
    """Negative: no sprint_id means no violation."""
    result = detect_stale_gaps({}, "R102")
    assert result["is_violation"] is False


# --- Missing raw logs detection ---

def test_missing_raw_logs_detected(tmp_path):
    """Positive: no log files is violation."""
    result = detect_missing_raw_logs(tmp_path)
    assert result["is_violation"] is True


def test_missing_raw_logs_found(tmp_path):
    """Negative: log file exists is not violation."""
    (tmp_path / "raw-test-log.txt").write_text("test output")
    result = detect_missing_raw_logs(tmp_path)
    assert result["is_violation"] is False


def test_missing_raw_logs_nonexistent_root(tmp_path):
    """Negative: nonexistent root is violation."""
    result = detect_missing_raw_logs(tmp_path / "nonexistent")
    assert result["is_violation"] is True


# --- Path-only acceptance detection ---

def test_path_only_acceptance_detected():
    """Positive: ACCEPTED without test evidence is violation."""
    grades = [{"item_id": "A1", "supervisor_grade": "ACCEPTED"}]
    result = detect_path_only_acceptance(grades)
    assert result["is_violation"] is True
    assert "A1" in result["path_only_items"]


def test_path_only_acceptance_with_evidence():
    """Negative: ACCEPTED with test evidence is not violation."""
    grades = [{"item_id": "A1", "supervisor_grade": "ACCEPTED", "test_file_content_checked": True}]
    result = detect_path_only_acceptance(grades)
    assert result["is_violation"] is False


def test_path_only_acceptance_with_criteria():
    """Negative: ACCEPTED with acceptance criteria is not violation."""
    grades = [{"item_id": "A1", "supervisor_grade": "ACCEPTED", "acceptance_criteria_met": True}]
    result = detect_path_only_acceptance(grades)
    assert result["is_violation"] is False


def test_path_only_acceptance_non_accepted():
    """Negative: non-ACCEPTED grades don't trigger."""
    grades = [{"item_id": "A1", "supervisor_grade": "REJECTED"}]
    result = detect_path_only_acceptance(grades)
    assert result["is_violation"] is False


# --- Consolidated checks ---

def test_run_all_checks_all_pass(tmp_path):
    (tmp_path / "raw-test-log.txt").write_text("output")
    (tmp_path / "evidence-manifest.yaml").write_text("sprint_id: R102")
    (tmp_path / "dry-run-ledger.json").write_text("{}")
    samples = tmp_path / "sample-outputs"
    samples.mkdir()
    (samples / "data.json").write_text("{}")
    result = run_all_checks(
        prompt_text="Mainstream sprint: implement FODS. Acceleration: tools. Skills: registry. Supervisor: pipeline.",
        gaps_data={"sprint_id": "R102"},
        expected_sprint="R102",
        evidence_root=tmp_path,
        grades=[{"item_id": "A1", "supervisor_grade": "ACCEPTED_VERIFIED", "test_file_content_checked": True}],
    )
    assert result["all_pass"] is True
    assert result["violations"] == 0


def test_run_all_checks_with_violations(tmp_path):
    result = run_all_checks(
        prompt_text="Continue with next sprint tasks.",
        gaps_data={"sprint_id": "R98"},
        expected_sprint="R102",
        evidence_root=tmp_path,
        grades=[{"item_id": "A1", "supervisor_grade": "ACCEPTED"}],
    )
    assert result["all_pass"] is False
    assert result["violations"] >= 2


# --- Missing evidence-manifest detection (R103) ---

def test_missing_evidence_manifest_detected(tmp_path):
    """Positive: no evidence-manifest.yaml is violation."""
    result = detect_missing_evidence_manifest(tmp_path)
    assert result["is_violation"] is True
    assert result["check"] == "missing_evidence_manifest"


def test_missing_evidence_manifest_found(tmp_path):
    """Negative: evidence-manifest.yaml exists is not violation."""
    (tmp_path / "evidence-manifest.yaml").write_text("sprint_id: R103")
    result = detect_missing_evidence_manifest(tmp_path)
    assert result["is_violation"] is False


def test_missing_evidence_manifest_from_declaration(tmp_path):
    """Negative: manifest found via declaration evidence_root."""
    decl_root = tmp_path / "reports" / "r103"
    decl_root.mkdir(parents=True)
    (decl_root / "evidence-manifest.yaml").write_text("sprint_id: R103")
    result = detect_missing_evidence_manifest(tmp_path, declaration={"evidence_root": str(decl_root)})
    assert result["is_violation"] is False


# --- Missing report files detection (R103) ---

def test_missing_report_files_detected(tmp_path):
    """Positive: declared reports that don't exist."""
    declaration = {
        "reports_created": ["reports/r103/preflight.md", "reports/r103/iv.md"],
    }
    result = detect_missing_report_files(declaration, repo_root=tmp_path)
    assert result["is_violation"] is True
    assert len(result["missing_reports"]) == 2


def test_missing_report_files_all_exist(tmp_path):
    """Negative: all declared reports exist."""
    (tmp_path / "reports" / "r103").mkdir(parents=True)
    (tmp_path / "reports" / "r103" / "preflight.md").write_text("ok")
    declaration = {"reports_created": ["reports/r103/preflight.md"]}
    result = detect_missing_report_files(declaration, repo_root=tmp_path)
    assert result["is_violation"] is False


def test_missing_report_files_checks_evidence_paths(tmp_path):
    """Positive: evidence_paths in work items also checked."""
    declaration = {
        "reports_created": [],
        "planned_work_items": [
            {"evidence_paths": ["reports/r103/missing.md"]},
        ],
    }
    result = detect_missing_report_files(declaration, repo_root=tmp_path)
    assert result["is_violation"] is True


def test_missing_report_files_empty_declaration():
    """Negative: empty declaration has no violations."""
    result = detect_missing_report_files({})
    assert result["is_violation"] is False


# --- Missing lane ledger detection (R103) ---

def test_missing_lane_ledger_detected(tmp_path):
    """Positive: no ledger files is violation."""
    result = detect_missing_lane_ledger(tmp_path)
    assert result["is_violation"] is True
    assert result["check"] == "missing_lane_ledger"


def test_missing_lane_ledger_found(tmp_path):
    """Negative: ledger file exists is not violation."""
    (tmp_path / "dry-run-ledger.json").write_text("{}")
    result = detect_missing_lane_ledger(tmp_path)
    assert result["is_violation"] is False


def test_missing_lane_ledger_in_sample_outputs(tmp_path):
    """Negative: ledger in sample-outputs subdir found."""
    samples = tmp_path / "sample-outputs"
    samples.mkdir()
    (samples / "dry-run-ledger.json").write_text("{}")
    result = detect_missing_lane_ledger(tmp_path, sample_outputs_dir=samples)
    assert result["is_violation"] is False


# --- Cross-stream prompt contamination detection (R103) ---

def test_cross_stream_contamination_detected():
    """Positive: acceleration prompt with product content is contaminated."""
    prompt = (
        "Next sprint: implement FODS export_csv. "
        "Add FODT save_same_format. "
        "Netpbm dotnet_status improvements. "
        "SYLK commercial readiness. "
        "Gate 11 approval needed."
    )
    result = detect_cross_stream_prompt_contamination(prompt, "acceleration")
    assert result["is_violation"] is True
    assert len(result["product_markers_found"]) > 3


def test_cross_stream_contamination_clean_acceleration():
    """Negative: acceleration prompt with only tooling content."""
    prompt = (
        "Acceleration sprint: improve gap selector. "
        "Add anti-skip checker tests. "
        "Harden stream prompt generator."
    )
    result = detect_cross_stream_prompt_contamination(prompt, "acceleration")
    assert result["is_violation"] is False


def test_cross_stream_contamination_mainstream_with_src():
    """Negative: mainstream prompt referencing src/ is expected."""
    prompt = "Mainstream sprint: edit src/net/fods/FodsDocument.cs and src/python/fods/parser.py"
    result = detect_cross_stream_prompt_contamination(prompt, "mainstream")
    assert result["is_violation"] is False


def test_cross_stream_contamination_mainstream_with_tools():
    """Positive: mainstream prompt referencing tools/supervisor/ is contaminated."""
    prompt = "Mainstream sprint: edit tools/supervisor/anti_skip_checker.py"
    result = detect_cross_stream_prompt_contamination(prompt, "mainstream")
    assert result["is_violation"] is True
    assert "tools/supervisor/" in result["forbidden_refs_found"]


def test_cross_stream_exemption_with_supervisor_scope():
    """Stream-aware: supervisor item types exempt supervisor paths in mainstream."""
    prompt = "Sprint: fix tools/supervisor/closeout_gate.py and tests/supervisor/test_gate.py"
    result = detect_cross_stream_prompt_contamination(
        prompt, "mainstream",
        declared_scope=["SUPERVISOR_REPAIR", "SUPERVISOR_TEST"],
    )
    assert result["is_violation"] is False
    assert "exempt_paths" in result
    assert len(result["exempt_paths"]) == 2


def test_cross_stream_no_exemption_without_supervisor_scope():
    """Stream-aware: no exemption when scope is only product work."""
    prompt = "Sprint: fix tools/supervisor/closeout_gate.py"
    result = detect_cross_stream_prompt_contamination(
        prompt, "mainstream",
        declared_scope=["PRODUCT_SOURCE", "TEST"],
    )
    assert result["is_violation"] is True


def test_cross_stream_mixed_scope_exempts_only_supervisor():
    """Stream-aware: mixed scope with GOVERNANCE_DOC exempts supervisor paths."""
    prompt = "Sprint: fix tools/supervisor/anti_skip_checker.py and update src/python/csv/csv_parser.py"
    result = detect_cross_stream_prompt_contamination(
        prompt, "mainstream",
        declared_scope=["PRODUCT_SOURCE", "GOVERNANCE_HARDENING"],
    )
    assert result["is_violation"] is False


def test_cross_stream_exemption_does_not_apply_to_acceleration():
    """Stream-aware: exemption only applies to mainstream, not acceleration."""
    prompt = "Sprint: fix src/python/csv/csv_parser.py"
    result = detect_cross_stream_prompt_contamination(
        prompt, "acceleration",
        declared_scope=["SUPERVISOR_REPAIR"],
    )
    # src/python/ is forbidden for acceleration and supervisor scope shouldn't exempt it
    assert result["is_violation"] is True


# --- Missing sample outputs detection (R104) ---

def test_missing_sample_outputs_detected(tmp_path):
    """Positive: no sample outputs directory is violation."""
    result = detect_missing_sample_outputs(tmp_path)
    assert result["is_violation"] is True
    assert result["check"] == "missing_sample_outputs"


def test_missing_sample_outputs_found(tmp_path):
    """Negative: sample outputs exist is not violation."""
    samples = tmp_path / "sample-outputs"
    samples.mkdir()
    (samples / "gaps.json").write_text("{}")
    result = detect_missing_sample_outputs(tmp_path)
    assert result["is_violation"] is False


def test_missing_sample_outputs_explicit_dir(tmp_path):
    """Negative: explicit sample_outputs_dir with files."""
    samples = tmp_path / "outputs"
    samples.mkdir()
    (samples / "data.json").write_text("{}")
    result = detect_missing_sample_outputs(tmp_path, sample_outputs_dir=samples)
    assert result["is_violation"] is False


def test_missing_sample_outputs_min_threshold(tmp_path):
    """Positive: below min_outputs threshold."""
    samples = tmp_path / "sample-outputs"
    samples.mkdir()
    (samples / "one.json").write_text("{}")
    result = detect_missing_sample_outputs(tmp_path, min_outputs=3)
    assert result["is_violation"] is True
    assert result["outputs_found"] == 1


# --- Dirty git state detection (R105) ---

def test_dirty_git_state_detected():
    """Positive: uncommitted changes without classification."""
    decl = {"git_status_final": "uncommitted acceleration-r104 changes"}
    result = detect_dirty_git_state(decl)
    assert result["is_violation"] is True
    assert result["is_dirty"] is True
    assert result["has_classification"] is False


def test_dirty_git_state_classified():
    """Negative: dirty but classified."""
    decl = {
        "git_status_final": "uncommitted acceleration-r105 changes",
        "dirty_state_classification": "DIRTY_MULTI_STREAM_ACCUMULATED",
    }
    result = detect_dirty_git_state(decl)
    assert result["is_violation"] is False
    assert result["is_dirty"] is True
    assert result["has_classification"] is True


def test_dirty_git_state_clean():
    """Negative: clean git state."""
    decl = {"git_status_final": "clean"}
    result = detect_dirty_git_state(decl)
    assert result["is_violation"] is False
    assert result["is_dirty"] is False


def test_dirty_git_state_empty():
    """Negative: no git_status_final field."""
    result = detect_dirty_git_state({})
    assert result["is_violation"] is False


# --- Wrong-stream gaps detection (R105) ---

def test_wrong_stream_gaps_detected():
    """Positive: mainstream gaps used for acceleration stream."""
    gaps = {"stream": "mainstream", "gaps": []}
    result = detect_wrong_stream_gaps(gaps, "acceleration")
    assert result["is_violation"] is True
    assert result["actual_stream"] == "mainstream"


def test_wrong_stream_gaps_correct():
    """Negative: acceleration gaps for acceleration stream."""
    gaps = {"stream": "acceleration", "gaps": []}
    result = detect_wrong_stream_gaps(gaps, "acceleration")
    assert result["is_violation"] is False


def test_wrong_stream_gaps_inferred_from_items():
    """Positive: stream inferred from gap items."""
    gaps = {"gaps": [{"stream": "skills"}, {"stream": "skills"}]}
    result = detect_wrong_stream_gaps(gaps, "acceleration")
    assert result["is_violation"] is True
    assert result["actual_stream"] == "skills"


def test_wrong_stream_gaps_empty():
    """Negative: no stream info means no violation."""
    gaps = {"gaps": []}
    result = detect_wrong_stream_gaps(gaps, "acceleration")
    assert result["is_violation"] is False


# --- Consolidated 11-check run (R105) ---

def test_run_all_16_checks_legacy(tmp_path):
    """All 16 checks run when all inputs provided (updated from 14 in R107)."""
    (tmp_path / "raw-test-log.txt").write_text("output")
    (tmp_path / "evidence-manifest.yaml").write_text("sprint_id: R105")
    (tmp_path / "dry-run-ledger.json").write_text("{}")
    samples = tmp_path / "sample-outputs"
    samples.mkdir()
    (samples / "gaps.json").write_text("{}")
    (tmp_path / "reports" / "r105").mkdir(parents=True)
    (tmp_path / "reports" / "r105" / "preflight.md").write_text("ok")
    declaration = {
        "run_id": "r105",
        "sprint_id": "R105",
        "evidence_root": "reports/r105",
        "planned_work_items": [],
        "test_results": {"passed": 50, "failed": 0},
        "worker_self_verdict": "PASS",
        "reports_created": ["reports/r105/preflight.md"],
        "git_status_final": "clean",
        "changed_files": [],
    }
    result = run_all_checks(
        prompt_text="Acceleration sprint: improve tools. Add skills registry entries.",
        gaps_data={"sprint_id": "R105", "stream": "acceleration"},
        expected_sprint="R105",
        evidence_root=tmp_path,
        declaration=declaration,
        grades=[{"item_id": "A1", "supervisor_grade": "ACCEPTED_VERIFIED", "test_file_content_checked": True}],
        target_stream="acceleration",
        repo_root=tmp_path,
        sample_outputs_dir=samples,
    )
    assert result["total_checks"] == 18
    assert result["all_pass"] is True
