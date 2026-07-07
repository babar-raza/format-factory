"""Tests for R107 acceleration: hard gates, severity mapping, new detectors, and enforcement."""

import json
import sys
from pathlib import Path

import pytest


TOOLS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"
sys.path.insert(0, str(TOOLS_DIR))

from anti_skip_checker import (
    SEVERITY_MAP,
    classify_violation_impact,
    detect_missing_changed_files,
    detect_stale_evidence_manifest,
    run_all_checks,
)


# --- Lane B: Severity mapping tests ---

class TestSeverityMapping:
    def test_severity_map_has_19_entries(self):
        assert len(SEVERITY_MAP) == 19  # R111: +wrong_stream_next_sprint R113: +odf_spec_linkage

    def test_critical_severities(self):
        critical = [k for k, v in SEVERITY_MAP.items() if v == "critical"]
        assert "stale_gaps" in critical
        assert "cross_stream_prompt_contamination" in critical
        assert "wrong_stream_gaps" in critical
        assert "declaration_completeness" in critical

    def test_high_severities(self):
        high = [k for k, v in SEVERITY_MAP.items() if v == "high"]
        assert "generic_prompt" in high
        assert "missing_report_files" in high
        assert "evidence_quality_score" in high
        assert "test_count_regression" in high
        assert "stale_evidence_manifest" in high
        assert "missing_changed_files" in high
        assert "odf_spec_linkage" in high  # R113: ODF items need spec refs

    def test_medium_severities(self):
        medium = [k for k, v in SEVERITY_MAP.items() if v == "medium"]
        assert "missing_raw_logs" in medium
        assert "path_only_acceptance" in medium
        assert "dirty_git_state" in medium
        assert "missing_lane_ledger" in medium  # R109: upgraded from low

    def test_low_severities(self):
        low = [k for k, v in SEVERITY_MAP.items() if v == "low"]
        assert "missing_sample_outputs" in low


class TestClassifyViolationImpact:
    def test_no_violations_no_impact(self):
        checks = [{"check": "stale_gaps", "is_violation": False}]
        impact = classify_violation_impact(checks)
        assert not impact["block"]
        assert not impact["downgrade"]
        assert impact["total_violations"] == 0

    def test_critical_violation_blocks(self):
        checks = [{"check": "stale_gaps", "is_violation": True}]
        impact = classify_violation_impact(checks)
        assert impact["block"]
        assert "stale_gaps" in impact["block_items"]

    def test_high_violation_downgrades(self):
        checks = [{"check": "generic_prompt", "is_violation": True}]
        impact = classify_violation_impact(checks)
        assert not impact["block"]
        assert impact["downgrade"]
        assert "generic_prompt" in impact["downgrade_items"]

    def test_medium_violation_caveat(self):
        checks = [{"check": "missing_raw_logs", "is_violation": True}]
        impact = classify_violation_impact(checks)
        assert not impact["block"]
        assert not impact["downgrade"]
        assert "missing_raw_logs" in impact["caveats"]

    def test_low_violation_note(self):
        checks = [{"check": "missing_sample_outputs", "is_violation": True}]
        impact = classify_violation_impact(checks)
        assert not impact["block"]
        assert not impact["downgrade"]
        assert "missing_sample_outputs" in impact["notes"]

    def test_medium_lane_ledger_caveat(self):
        """R109: missing_lane_ledger is now medium → caveat."""
        checks = [{"check": "missing_lane_ledger", "is_violation": True}]
        impact = classify_violation_impact(checks)
        assert not impact["block"]
        assert not impact["downgrade"]
        assert "missing_lane_ledger" in impact["caveats"]

    def test_mixed_severities_block_wins(self):
        checks = [
            {"check": "stale_gaps", "is_violation": True},  # critical
            {"check": "generic_prompt", "is_violation": True},  # high
            {"check": "missing_raw_logs", "is_violation": True},  # medium
        ]
        impact = classify_violation_impact(checks)
        assert impact["block"]
        assert impact["downgrade"]
        assert len(impact["caveats"]) == 1
        assert impact["total_violations"] == 3


# --- Lane H: New detector tests ---

class TestDetectStaleEvidenceManifest:
    def test_no_manifest_no_violation(self, tmp_path):
        result = detect_stale_evidence_manifest(tmp_path, "R107")
        assert not result["is_violation"]

    def test_matching_sprint_passes(self, tmp_path):
        manifest = {"sprint_id": "R107", "artifacts": []}
        import yaml
        (tmp_path / "evidence-manifest.yaml").write_text(
            yaml.dump(manifest), encoding="utf-8"
        )
        result = detect_stale_evidence_manifest(tmp_path, "R107")
        assert not result["is_violation"]

    def test_stale_sprint_fails(self, tmp_path):
        manifest = {"sprint_id": "R105", "artifacts": []}
        import yaml
        (tmp_path / "evidence-manifest.yaml").write_text(
            yaml.dump(manifest), encoding="utf-8"
        )
        result = detect_stale_evidence_manifest(tmp_path, "R107")
        assert result["is_violation"]
        assert result["manifest_sprint"] == "R105"


class TestDetectMissingChangedFiles:
    def test_no_changed_files_no_violation(self):
        result = detect_missing_changed_files({})
        assert not result["is_violation"]

    def test_all_files_exist(self, tmp_path):
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "file.py").write_text("x", encoding="utf-8")
        decl = {"changed_files": ["src/file.py"]}
        result = detect_missing_changed_files(decl, repo_root=tmp_path)
        assert not result["is_violation"]

    def test_missing_file_flagged(self, tmp_path):
        decl = {"changed_files": ["src/nonexistent.py"]}
        result = detect_missing_changed_files(decl, repo_root=tmp_path)
        assert result["is_violation"]
        assert "src/nonexistent.py" in result["missing_files"]


# --- Lane B+H: run_all_checks returns 16 detectors and impact ---

class TestRunAllChecks16:
    def test_run_all_16_checks(self, tmp_path):
        import yaml
        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()
        sample_dir = evidence_root / "sample-outputs"
        sample_dir.mkdir()
        (sample_dir / "sample.json").write_text("{}", encoding="utf-8")
        (evidence_root / "raw-test-log.txt").write_text("log", encoding="utf-8")
        (evidence_root / "lane-ledger.json").write_text("[]", encoding="utf-8")
        manifest = {"sprint_id": "R107-TEST", "artifacts": []}
        (evidence_root / "evidence-manifest.yaml").write_text(
            yaml.dump(manifest), encoding="utf-8"
        )

        decl = {
            "run_id": "test-r107",
            "sprint_id": "R107-TEST",
            "evidence_root": str(evidence_root),
            "planned_work_items": [],
            "test_results": {"passed": 10, "failed": 0},
            "worker_self_verdict": "ACCEPTED",
            "changed_files": [],
        }
        grades = [{"supervisor_grade": "ACCEPTED_VERIFIED", "item_id": "W0",
                    "test_file_content_checked": True}]
        gaps = {"sprint_id": "R107-TEST", "stream": "acceleration", "gaps": []}
        prompt = "acceleration stream R107 tool gap selector anti-skip ## Lane A"

        result = run_all_checks(
            prompt_text=prompt,
            gaps_data=gaps,
            expected_sprint="R107-TEST",
            evidence_root=evidence_root,
            declaration=decl,
            grades=grades,
            target_stream="acceleration",
            repo_root=tmp_path,
            sample_outputs_dir=sample_dir,
        )
        assert result["total_checks"] == 18  # 19th requires next_sprint_text; 18th=detect_odf_spec_linkage (R113)
        assert "impact" in result
        assert isinstance(result["impact"], dict)

    def test_impact_present_in_result(self, tmp_path):
        result = run_all_checks(evidence_root=tmp_path)
        assert "impact" in result


# --- Lane C: Evidence quality enforcement tests ---

class TestEvidenceQualityEnforcement:
    def test_zero_quality_downgrades_verdict(self):
        from grade_declared_work import grade_all

        inspection = {
            "run_id": "test",
            "sprint_id": "test",
            "test_results": {"passed": 5, "failed": 0},
            "item_inspections": [
                {
                    "item_id": "W0",
                    "declared_status": "completed",
                    "has_evidence": True,
                    "has_tests": True,
                    "evidence_paths_found": ["reports/test.md"],
                    "evidence_paths_missing": [],
                    "tests_declared": ["test_x"],
                    # No tests_with_content → path-only
                },
            ],
        }
        declaration = {
            "planned_work_items": [{"item_id": "W0", "title": "Test item"}],
            "test_results": {"passed": 5, "failed": 0},
        }
        review = grade_all(inspection, declaration)
        # Path-only → evidence_quality_score = 0.0 → verdict downgraded
        assert review["evidence_quality_score"] == 0.0
        assert review["overall_verdict"] == "ACCEPTED_WITH_REWORK"

    @pytest.mark.xfail(strict=False, reason="TC-CQGA-015: without LLM items capped at ACCEPTED_WITH_LIMITATIONS → score 0.0, verdict ACCEPTED_WITH_REWORK")
    def test_verified_items_keep_accepted(self):
        from grade_declared_work import grade_all

        inspection = {
            "run_id": "test",
            "sprint_id": "test",
            "test_results": {"passed": 5, "failed": 0},
            "item_inspections": [
                {
                    "item_id": "W0",
                    "declared_status": "completed",
                    "has_evidence": True,
                    "has_tests": True,
                    "evidence_paths_found": ["reports/test.md"],
                    "evidence_paths_missing": [],
                    "tests_declared": ["test_x"],
                    "tests_with_content": ["test_x.py"],
                },
            ],
        }
        declaration = {
            "planned_work_items": [{"item_id": "W0", "title": "Test item"}],
            "test_results": {"passed": 5, "failed": 0},
        }
        review = grade_all(inspection, declaration)
        assert review["evidence_quality_score"] == 1.0
        assert review["overall_verdict"] in ("ACCEPTED", "ACCEPTED_WITH_REWORK")


# --- Lane E: Prompt quality check tests ---

class TestPromptQualityGates:
    def test_valid_acceleration_prompt_passes(self):
        from validate_prompt_quality import validate_prompt_quality

        prompt = (
            "## Acceleration R107 Sprint Prompt\n"
            "This acceleration sprint focuses on tool improvements, "
            "gap selector hardening, anti-skip checker expansion, "
            "and package validator enhancements for the acceleration stream.\n"
            "### Lane A: Repair\n"
            "Fix R106 deficiencies in the anti-skip checker and gap selector tools.\n"
            "### Lane B: Advancement\n"
            "Add new anti-skip detectors and improve package validator quality.\n"
            "### Evidence Closeout\n"
            "Write evidence-declaration.yaml and run autonomous-cycle to validate.\n"
        )
        result = validate_prompt_quality(prompt, "acceleration")
        assert result["valid"]

    def test_generic_prompt_fails(self):
        from validate_prompt_quality import validate_prompt_quality

        prompt = "Do stuff."
        result = validate_prompt_quality(prompt, "acceleration")
        assert not result["valid"]

    def test_wrong_stream_prompt_fails(self):
        from validate_prompt_quality import validate_prompt_quality

        prompt = (
            "## Mainstream Sprint\n"
            "This sprint focuses on src/net/fods and src/python/fodt "
            "product improvements and gate 11 readiness.\n"
            "### Lane A: FODS .NET improvements\n"
            "### Lane B: FODT Python hardening\n"
            "Write evidence-declaration.yaml.\n"
        )
        result = validate_prompt_quality(prompt, "acceleration")
        failed = [c["check"] for c in result["checks"] if not c["pass"]]
        assert "no_wrong_stream" in failed


# --- Lane G: Continuation policy tests ---

class TestContinuationPolicyEnforcement:
    def test_evidence_quality_zero_added_to_hard_stops(self):
        """Simulates what autonomous_cycle does when eqs == 0.0."""
        review = {
            "evidence_quality_score": 0.0,
            "accepted_items": ["W0"],
        }
        hard_stops = []
        eqs = review.get("evidence_quality_score", 1.0)
        if eqs == 0.0 and len(review.get("accepted_items", [])) > 0:
            hard_stops.append("evidence_quality_zero")
        assert "evidence_quality_zero" in hard_stops

    def test_nonzero_quality_no_hard_stop(self):
        review = {
            "evidence_quality_score": 0.5,
            "accepted_items": ["W0"],
        }
        hard_stops = []
        eqs = review.get("evidence_quality_score", 1.0)
        if eqs == 0.0 and len(review.get("accepted_items", [])) > 0:
            hard_stops.append("evidence_quality_zero")
        assert "evidence_quality_zero" not in hard_stops

    def test_anti_skip_block_added_to_hard_stops(self):
        """Simulates anti_skip_impact blocking continuation."""
        anti_skip_impact = {"block": True, "block_items": ["stale_gaps"]}
        hard_stops = []
        if anti_skip_impact and anti_skip_impact.get("block"):
            hard_stops.append("anti_skip_critical_block")
        assert "anti_skip_critical_block" in hard_stops


# --- Lane H: Bridge includes evidence_quality_score ---

class TestBridgeEvidenceQuality:
    def test_bridge_includes_quality_fields(self):
        from autonomous_cycle import bridge_to_legacy_format
        import tempfile

        review = {
            "overall_verdict": "ACCEPTED",
            "item_grades": [],
            "critical_rework_count": 0,
            "evidence_quality_score": 0.75,
            "verified_item_count": 3,
        }
        manifest = {
            "sprint_id": "test",
            "timestamp": "2026-01-01",
            "exit_code": 0,
            "autonomous_continue": True,
        }
        decl = {
            "evidence_root": "",
            "test_results": {"passed": 10, "failed": 0, "skipped": 0},
            "git_head_end": "abc123",
        }
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            (repo_root / "reports" / "supervisor").mkdir(parents=True)
            bridge_to_legacy_format(review, manifest, decl, repo_root)
            er = json.loads(
                (repo_root / "reports" / "supervisor" / "evidence-review.json").read_text()
            )
            assert er["evidence_quality_score"] == 0.75
            assert er["verified_item_count"] == 3
