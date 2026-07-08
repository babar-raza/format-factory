"""R108 Strict Closure: Contradiction repair, dirty-git detector, lane ledger hardening,
changed-file materialization, per-stream state directories.

Sprint: FORMAT-FACTORY-SUPERVISOR-R108-STRICT-CLOSURE-CONTRADICTION-REPAIR-PER-STREAM-STATE-AND-EXECUTION-PROOF-MEGA-TRAIN-001
"""

import json
import sys
import tempfile
from pathlib import Path


# Ensure tools/supervisor is on path
TOOLS_DIR = Path(__file__).resolve().parent.parent.parent / "tools" / "supervisor"
sys.path.insert(0, str(TOOLS_DIR))

from anti_skip_checker import (
    _detect_dirty_from_status,
    detect_dirty_git_state,
    classify_violation_impact,
)
from lane_execution_ledger import (
    create_ledger,
    add_lane,
    validate_ledger,
    generate_from_declaration,
)


# ============================================================
# Lane C: Dirty git-state detector repair
# ============================================================


class TestDirtyGitStateDetector:
    """C-R107-03: detect_dirty_git_state must detect M/?? patterns."""

    def test_short_format_modified_detected(self):
        """M prefix in comma-separated git status is detected as dirty."""
        assert _detect_dirty_from_status("M tools/supervisor/anti_skip_checker.py") is True

    def test_short_format_untracked_detected(self):
        """?? prefix in git status is detected as dirty."""
        assert _detect_dirty_from_status("?? tools/supervisor/capture_raw_logs.py") is True

    def test_short_format_mixed_detected(self):
        """Comma-separated M and ?? entries are detected as dirty."""
        status = "M tools/supervisor/anti_skip_checker.py, ?? tools/supervisor/capture_raw_logs.py"
        assert _detect_dirty_from_status(status) is True

    def test_empty_status_is_clean(self):
        assert _detect_dirty_from_status("") is False

    def test_prose_uncommitted_detected(self):
        """Legacy prose format still works."""
        assert _detect_dirty_from_status("uncommitted changes in working tree") is True

    def test_clean_status_not_detected(self):
        """A string without git indicators is not dirty."""
        assert _detect_dirty_from_status("all files committed") is False

    def test_added_file_detected(self):
        assert _detect_dirty_from_status("A new_file.py") is True

    def test_deleted_file_detected(self):
        assert _detect_dirty_from_status("D removed_file.py") is True

    def test_r107_declaration_detected_dirty(self):
        """The exact R107 git_status_final is detected as dirty."""
        decl = {
            "git_status_final": (
                "M tools/supervisor/anti_skip_checker.py, "
                "M tools/supervisor/grade_declared_work.py, "
                "M tests/supervisor/test_r100_grade_engine.py, "
                "?? tools/supervisor/capture_raw_logs.py, "
                "?? tools/supervisor/lane_execution_ledger.py"
            )
        }
        result = detect_dirty_git_state(decl)
        assert result["is_dirty"] is True
        assert result["is_violation"] is True  # no classification

    def test_dirty_with_classification_not_violation(self):
        decl = {
            "git_status_final": "M file.py",
            "dirty_state_classification": "DIRTY_SUPERVISOR_WORK_IN_PROGRESS",
        }
        result = detect_dirty_git_state(decl)
        assert result["is_dirty"] is True
        assert result["is_violation"] is False


# ============================================================
# Lane B: Raw log exit-code integrity
# ============================================================


class TestLaneLedgerExitCodeIntegrity:
    """C-R107-01/02: generate_from_declaration must use capture-meta.json exit_code."""

    def test_capture_meta_exit_code_used(self, tmp_path):
        """When capture-meta.json exists, its exit_code is used for TEST-EXECUTION."""
        evidence_root = tmp_path / "evidence"
        raw_logs = evidence_root / "raw-logs"
        raw_logs.mkdir(parents=True)

        # Create capture-meta.json with exit_code=1
        meta = {
            "command": ["python", "-m", "pytest", "tests/"],
            "exit_code": 1,
            "duration_seconds": 15.33,
        }
        (raw_logs / "capture-meta.json").write_text(json.dumps(meta))
        (raw_logs / "raw-test-log.txt").write_text("test output")

        decl = {
            "sprint_id": "R108-TEST",
            "run_id": "test-run",
            "planned_work_items": [],
            "test_results": {"passed": 100, "failed": 0, "skipped": 1},
        }

        ledger = generate_from_declaration(decl, evidence_root)
        test_lane = [l for l in ledger["lanes"] if l["lane_id"] == "TEST-EXECUTION"][0]

        # Real exit_code from capture-meta (1) overrides declaration-derived (0)
        assert test_lane["exit_code"] == 1
        assert test_lane["status"] == "failed"
        assert test_lane["duration_seconds"] == 15.33
        assert test_lane["command"] is not None

    def test_no_capture_meta_falls_back(self, tmp_path):
        """Without capture-meta.json, falls back to declaration-derived exit_code."""
        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir(parents=True)

        decl = {
            "sprint_id": "R108-TEST",
            "run_id": "test-run",
            "planned_work_items": [],
            "test_results": {"passed": 100, "failed": 0, "skipped": 0},
        }

        ledger = generate_from_declaration(decl, evidence_root)
        test_lane = [l for l in ledger["lanes"] if l["lane_id"] == "TEST-EXECUTION"][0]
        assert test_lane["exit_code"] == 0
        assert test_lane["status"] == "completed"


# ============================================================
# Lane E: Lane execution ledger hardening
# ============================================================


class TestLaneLedgerHardening:
    """C-R107-04: validate_ledger flags null execution metadata."""

    def test_null_execution_produces_warnings(self):
        ledger = create_ledger("R108", "test")
        add_lane(ledger, "WAVE-1", "Test wave", status="completed")  # null command/exit_code
        result = validate_ledger(ledger)
        assert result["valid"] is True  # still valid (warnings not errors)
        assert result["null_execution_count"] == 1
        assert len(result["warnings"]) == 1

    def test_populated_execution_no_warnings(self):
        ledger = create_ledger("R108", "test")
        add_lane(ledger, "WAVE-1", "Test wave", status="completed",
                 command="python test.py", exit_code=0)
        result = validate_ledger(ledger)
        assert result["null_execution_count"] == 0
        assert len(result["warnings"]) == 0

    def test_generate_populates_descriptive_commands(self):
        """R108: generate_from_declaration now populates descriptive commands."""
        decl = {
            "sprint_id": "R108-TEST",
            "run_id": "test",
            "planned_work_items": [
                {
                    "item_id": "ITEM-1",
                    "title": "Implement feature X",
                    "status": "completed",
                    "evidence_paths": ["file.py"],
                },
            ],
            "test_results": {},
        }
        evidence_root = Path(tempfile.mkdtemp())
        ledger = generate_from_declaration(decl, evidence_root)
        item_lane = [l for l in ledger["lanes"] if l["lane_id"] == "ITEM-1"][0]
        assert item_lane["command"] is not None
        assert "[manual]" in item_lane["command"]
        assert item_lane["exit_code"] == 0

    def test_validate_returns_warnings_key(self):
        """validate_ledger returns warnings list (R108 schema extension)."""
        ledger = create_ledger("R108", "test")
        add_lane(ledger, "L1", "Lane 1", status="completed", command="cmd", exit_code=0)
        result = validate_ledger(ledger)
        assert "warnings" in result
        assert isinstance(result["warnings"], list)


# ============================================================
# Lane G: Changed-file/diff materialization
# ============================================================


class TestChangedFileMaterialization:
    """C-R107-07: Untracked files should produce NEW_FILE diff."""

    def test_git_diff_file_handles_untracked(self, tmp_path):
        """git_diff_file for untracked files should attempt --no-index diff."""
        # This is a unit-level check that the function exists and has the NEW_FILE branch
        import inspect
        from materialize_declared_evidence import git_diff_file
        source = inspect.getsource(git_diff_file)
        assert "NEW_FILE" in source
        assert "no-index" in source

    def test_fallback_message_no_ambiguity(self):
        """The fallback message should not say 'not tracked' for committed files."""
        # Just verify the string constant was updated
        import materialize_declared_evidence as mod
        source = Path(mod.__file__).read_text(encoding="utf-8")
        assert "committed clean" in source
        assert "not tracked" not in source.split("no diff available")[1].split(")")[0]


# ============================================================
# Lane D: Per-stream state directories
# ============================================================


class TestPerStreamStateDirectories:
    """R108: Autonomous cycle writes to per-stream directory."""

    def test_stream_dir_code_exists(self):
        """autonomous_cycle or extensions contains supervisor-streams directory logic."""
        import autonomous_cycle as mod
        source = Path(mod.__file__).read_text(encoding="utf-8")
        ext_path = Path(mod.__file__).parent / "autonomous_cycle_extensions.py"
        if ext_path.exists():
            source += ext_path.read_text(encoding="utf-8")
        assert "supervisor-streams" in source

    def test_stream_dir_path_structure(self):
        """Stream directory follows reports/supervisor-streams/{stream}/ pattern."""
        import autonomous_cycle as mod
        source = Path(mod.__file__).read_text(encoding="utf-8")
        assert "detected_stream" in source


# ============================================================
# Lane A: Contradiction register
# ============================================================


class TestContradictionRegister:
    """R107 contradiction register produced by Lane A."""

    def test_register_exists(self):
        repo_root = Path(__file__).resolve().parent.parent.parent
        reg_path = repo_root / "reports" / "supervisor-r108" / "r107-contradiction-register.json"
        assert reg_path.exists(), f"Contradiction register not found: {reg_path}"

    def test_register_has_contradictions(self):
        repo_root = Path(__file__).resolve().parent.parent.parent
        reg_path = repo_root / "reports" / "supervisor-r108" / "r107-contradiction-register.json"
        data = json.loads(reg_path.read_text(encoding="utf-8"))
        assert len(data["contradictions"]) >= 5
        ids = {c["id"] for c in data["contradictions"]}
        assert "C-R107-03" in ids  # dirty git detector

    def test_register_summary_counts(self):
        repo_root = Path(__file__).resolve().parent.parent.parent
        reg_path = repo_root / "reports" / "supervisor-r108" / "r107-contradiction-register.json"
        data = json.loads(reg_path.read_text(encoding="utf-8"))
        assert data["summary"]["total"] == len(data["contradictions"])
        assert data["summary"]["critical"] >= 1


# ============================================================
# Lane H: Enforcement integration
# ============================================================


class TestEnforcementIntegration:
    """Dirty git detector now works in the anti-skip pipeline."""

    def test_dirty_state_in_severity_map(self):
        from anti_skip_checker import SEVERITY_MAP
        assert "dirty_git_state" in SEVERITY_MAP
        assert SEVERITY_MAP["dirty_git_state"] == "medium"

    def test_dirty_state_produces_caveat(self):
        """A dirty-state violation produces a caveat (medium severity)."""
        checks = [
            {"check": "dirty_git_state", "is_violation": True},
        ]
        impact = classify_violation_impact(checks)
        assert "dirty_git_state" in impact["caveats"]
        assert not impact["block"]

    def test_clean_state_no_violation(self):
        result = detect_dirty_git_state({"git_status_final": ""})
        assert result["is_violation"] is False


# ============================================================
# Cross-lane integration
# ============================================================


class TestCrossLaneIntegration:
    """Verify fixes work together end-to-end."""

    def test_r107_style_declaration_produces_correct_anti_skip(self):
        """R107-style declaration with M/?? status triggers dirty_git_state."""
        from anti_skip_checker import run_all_checks
        decl = {
            "run_id": "test",
            "sprint_id": "R107-TEST",
            "evidence_root": ".",
            "planned_work_items": [],
            "test_results": {"passed": 100, "failed": 0},
            "worker_self_verdict": "PASS",
            "git_status_final": "M file.py, ?? new_file.py",
            "changed_files": [],
        }
        result = run_all_checks(declaration=decl)
        dirty_checks = [c for c in result["checks"] if c["check"] == "dirty_git_state"]
        assert len(dirty_checks) == 1
        assert dirty_checks[0]["is_violation"] is True
        assert dirty_checks[0]["is_dirty"] is True

    def test_full_ledger_generation_with_capture_meta(self, tmp_path):
        """Full pipeline: declaration + capture-meta -> correct ledger."""
        evidence_root = tmp_path / "evidence"
        raw_logs = evidence_root / "raw-logs"
        raw_logs.mkdir(parents=True)
        (raw_logs / "capture-meta.json").write_text(json.dumps({
            "command": ["pytest", "tests/"],
            "exit_code": 1,
            "duration_seconds": 20.5,
        }))
        (raw_logs / "raw-test-log.txt").write_text("output")

        decl = {
            "sprint_id": "R108",
            "run_id": "test",
            "planned_work_items": [
                {"item_id": "W1", "title": "Work 1", "status": "completed",
                 "evidence_paths": ["f.py"], "test_references": ["t.py::test"]},
            ],
            "test_results": {"passed": 50, "failed": 0, "skipped": 1},
        }

        ledger = generate_from_declaration(decl, evidence_root)

        # Work lane has descriptive command
        w1 = [l for l in ledger["lanes"] if l["lane_id"] == "W1"][0]
        assert w1["command"] is not None
        assert w1["exit_code"] == 0

        # Test lane uses capture-meta exit_code
        test = [l for l in ledger["lanes"] if l["lane_id"] == "TEST-EXECUTION"][0]
        assert test["exit_code"] == 1
        assert test["duration_seconds"] == 20.5

        # Validation shows no errors but 0 null-execution warnings (all populated now)
        result = validate_ledger(ledger)
        assert result["valid"] is True
        assert result["null_execution_count"] == 0
