"""
R103 — Cross-Stream Contamination and Deep Grading Tests

Tests:
  - Inspector reads both tests_supporting and test_references fields
  - Evidence manifest includes declared artifacts outside evidence_root
  - Package builder includes sprint-specific reports
  - Continuation states include wrong_stream_context and missing_raw_logs
  - Grade tests_supporting is populated when test_references provided
  - Package self-containment: sprint reports in ZIP
"""
import json
import sys
import tempfile
import zipfile
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from inspect_declared_evidence import inspect_item
from grade_declared_work import grade_item
from autonomous_cycle import classify_continuation_state


# ---------------------------------------------------------------------------
# Inspector: tests_supporting vs test_references
# ---------------------------------------------------------------------------

def test_inspector_reads_tests_supporting():
    """Inspector reads tests_supporting field."""
    item = {
        "item_id": "TEST-01",
        "status": "completed",
        "evidence_paths": [],
        "tests_supporting": ["tests/test_foo.py"],
    }
    result = inspect_item(item, REPO_ROOT)
    assert result["has_tests"] is True
    assert "tests/test_foo.py" in result["tests_declared"]


def test_inspector_reads_test_references():
    """Inspector reads test_references field (R103 alias fix)."""
    item = {
        "item_id": "TEST-02",
        "status": "completed",
        "evidence_paths": [],
        "test_references": ["tests/supervisor/test_r102_legacy_review_fix.py::test_something"],
    }
    result = inspect_item(item, REPO_ROOT)
    assert result["has_tests"] is True
    assert any("test_r102" in t for t in result["tests_declared"])


def test_inspector_prefers_tests_supporting_over_test_references():
    """If both fields present, tests_supporting wins (schema field)."""
    item = {
        "item_id": "TEST-03",
        "status": "completed",
        "evidence_paths": [],
        "tests_supporting": ["a.py"],
        "test_references": ["b.py"],
    }
    result = inspect_item(item, REPO_ROOT)
    assert "a.py" in result["tests_declared"]


def test_inspector_empty_both_fields():
    """If neither field has data, has_tests is False."""
    item = {
        "item_id": "TEST-04",
        "status": "completed",
        "evidence_paths": [],
    }
    result = inspect_item(item, REPO_ROOT)
    assert result["has_tests"] is False


# ---------------------------------------------------------------------------
# Grade: tests_supporting populated from test_references
# ---------------------------------------------------------------------------

def test_grade_populates_tests_supporting_from_test_references():
    """When inspector has tests from test_references, grade includes them."""
    inspection = {
        "item_id": "GRADE-01",
        "declared_status": "completed",
        "has_evidence": True,
        "has_tests": True,
        "evidence_paths_missing": [],
        "evidence_paths_found": ["some/file.py"],
        "tests_declared": ["tests/supervisor/test_r102_legacy_review_fix.py::test_something"],
        "tests_with_content": [],
        "tests_empty_or_stub": [],
    }
    g = grade_item(inspection, {"failed": 0})
    assert len(g["tests_supporting"]) > 0


# ---------------------------------------------------------------------------
# Evidence manifest: includes declared artifacts outside evidence_root
# ---------------------------------------------------------------------------

def test_manifest_includes_declared_artifacts():
    """Evidence manifest should include artifacts declared outside evidence_root."""
    from evidence_manifest import generate_from_declaration

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        # Create a mini repo structure
        evidence_dir = td_path / ".local" / "evidences" / "test-run"
        evidence_dir.mkdir(parents=True)
        reports_dir = td_path / "reports" / "test-run"
        reports_dir.mkdir(parents=True)

        # Write declaration
        decl = {
            "run_id": "test-run",
            "evidence_root": ".local/evidences/test-run/",
            "evidence_artifacts": [
                {"path": "reports/test-run/report.md", "type": "report"},
            ],
        }
        decl_path = evidence_dir / "evidence-declaration.yaml"
        decl_path.write_text(yaml.dump(decl), encoding="utf-8")

        # Write the report file
        (reports_dir / "report.md").write_text("# Test Report\nContent here.", encoding="utf-8")

        manifest = generate_from_declaration(decl_path, td_path)
        artifact_paths = [a["path"] for a in manifest["artifacts"]]
        assert any("reports/test-run/report.md" in p for p in artifact_paths), \
            f"Missing declared artifact. Got: {artifact_paths}"


# ---------------------------------------------------------------------------
# Package builder: sprint reports in ZIP
# ---------------------------------------------------------------------------

def test_package_includes_sprint_reports():
    """Package should include evidence_artifacts from declaration."""
    from build_declaration_review_package import build_package

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        # Create structure
        evidence_dir = td_path / ".local" / "evidences" / "test-pkg"
        evidence_dir.mkdir(parents=True)
        reports_dir = td_path / "reports" / "test-pkg"
        reports_dir.mkdir(parents=True)
        review_dir = td_path / ".local" / "supervisor" / "reviews" / "test-pkg"
        review_dir.mkdir(parents=True)
        (td_path / "reports" / "supervisor").mkdir(parents=True, exist_ok=True)
        (td_path / ".supervisor").mkdir(parents=True, exist_ok=True)

        # Write report
        (reports_dir / "preflight.md").write_text("# Preflight", encoding="utf-8")

        # Write declaration
        decl = {
            "run_id": "test-pkg",
            "sprint_id": "TEST-PKG",
            "evidence_root": ".local/evidences/test-pkg/",
            "evidence_artifacts": [
                {"path": "reports/test-pkg/preflight.md", "type": "report"},
            ],
        }
        decl_path = evidence_dir / "evidence-declaration.yaml"
        decl_path.write_text(yaml.dump(decl), encoding="utf-8")

        result = build_package(decl_path, td_path, review_dir)
        zip_path = Path(result["zip_path"])

        with zipfile.ZipFile(zip_path) as zf:
            names = zf.namelist()
            # R104: prefix changed from sprint-reports/ to sprint-evidence/
            has_report = any("reports/test-pkg/preflight.md" in n for n in names)
            assert has_report, f"Missing sprint report in ZIP. Got: {names}"


# ---------------------------------------------------------------------------
# Continuation states: new R103 states
# ---------------------------------------------------------------------------

def test_wrong_stream_context_state():
    cs = classify_continuation_state(
        False, False, ["wrong_stream_context"], [], [], {},
        REPO_ROOT / ".supervisor" / "policies.yaml"
    )
    assert cs == "NO_WRONG_STREAM_CONTEXT"


def test_missing_raw_logs_state():
    cs = classify_continuation_state(
        False, False, ["missing_raw_logs_for_verified_claims"], [], [], {},
        REPO_ROOT / ".supervisor" / "policies.yaml"
    )
    assert cs == "NO_MISSING_RAW_LOGS_FOR_VERIFIED_CLAIMS"


def test_yes_with_rework_state():
    cs = classify_continuation_state(
        "true_with_rework", False, [], [], ["item-1"], {},
        REPO_ROOT / ".supervisor" / "policies.yaml"
    )
    assert cs == "YES_WITH_REWORK"


def test_continuation_all_states_recognized():
    """All declared states should be reachable."""
    expected_states = {
        "YES", "YES_WITH_REWORK", "NO_MAX_ITERATIONS", "NO_EXTERNAL_GATE",
        "NO_BROKEN_BASELINE", "NO_UNSAFE_SOURCE_STATE", "NO_POLICY_BLOCK",
        "NO_GENERIC_NEXT_PROMPT", "NO_LEGACY_REVIEW_CONTRADICTION",
        "NO_STALE_GAPS", "NO_MISSING_EVIDENCE_MANIFEST",
        "NO_WRONG_STREAM_CONTEXT", "NO_MISSING_RAW_LOGS_FOR_VERIFIED_CLAIMS",
    }
    # Test each hard stop maps to a state
    hard_stop_map = {
        "generic_next_prompt": "NO_GENERIC_NEXT_PROMPT",
        "legacy_review_contradiction": "NO_LEGACY_REVIEW_CONTRADICTION",
        "stale_gaps": "NO_STALE_GAPS",
        "missing_evidence_manifest": "NO_MISSING_EVIDENCE_MANIFEST",
        "wrong_stream_context": "NO_WRONG_STREAM_CONTEXT",
        "missing_raw_logs_for_verified_claims": "NO_MISSING_RAW_LOGS_FOR_VERIFIED_CLAIMS",
    }
    for hs, expected in hard_stop_map.items():
        cs = classify_continuation_state(
            False, False, [hs], [], [], {},
            REPO_ROOT / ".supervisor" / "policies.yaml"
        )
        assert cs == expected, f"Hard stop '{hs}' -> '{cs}', expected '{expected}'"


# ---------------------------------------------------------------------------
# Cross-stream contamination: replay packages
# ---------------------------------------------------------------------------

REVIEW_BASE = REPO_ROOT / ".local" / "supervisor" / "reviews"

REPLAY_PACKAGES = {
    "mainstream-r105": "mainstream",
    "acceleration-r103": "acceleration",
    "supervisor-r102": "supervisor",
    "skills-r101": "skills",
}


@pytest.mark.parametrize("run_id", list(REPLAY_PACKAGES.keys()))
def test_replay_package_exists(run_id):
    path = REVIEW_BASE / run_id / "declaration-review-package.zip"
    assert path.exists(), f"Missing: {path}"


@pytest.mark.parametrize("run_id,expected_stream", list(REPLAY_PACKAGES.items()))
def test_replay_stream_detection(run_id, expected_stream):
    from generate_supervisor_packet import detect_stream_from_sprint_id
    path = REVIEW_BASE / run_id / "declaration-review-package.zip"
    if not path.exists():
        pytest.skip("missing")
    with zipfile.ZipFile(path) as zf:
        decl_names = [n for n in zf.namelist() if n.endswith("evidence-declaration.yaml")]
        if not decl_names:
            pytest.skip("no declaration")
        with zf.open(decl_names[0]) as f:
            decl = yaml.safe_load(f.read().decode("utf-8"))
    sid = decl.get("sprint_id", "")
    assert detect_stream_from_sprint_id(sid) == expected_stream


@pytest.mark.parametrize("run_id", list(REPLAY_PACKAGES.keys()))
def test_replay_is_declaration_package(run_id):
    """All replay packages should be declaration-review, not legacy."""
    path = REVIEW_BASE / run_id / "declaration-review-package.zip"
    if not path.exists():
        pytest.skip("missing")
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        has_decl = any("evidence-declaration.yaml" in n for n in names)
        has_legacy = any("final-verdict.md" in n for n in names)
    assert has_decl, "Not a declaration-review package"
    assert not has_legacy, "Contains legacy final-verdict.md"


@pytest.mark.parametrize("run_id", list(REPLAY_PACKAGES.keys()))
def test_replay_grades_valid(run_id):
    """Grades in replay packages must be valid enums."""
    valid_grades = {
        "ACCEPTED_VERIFIED", "ACCEPTED_WITH_LIMITATIONS", "ACCEPTED",
        "ACCEPTED_WITH_WARNINGS", "REWORK_REQUIRED", "REJECTED",
        "BLOCKED_EXTERNAL_GATE", "NOT_ATTEMPTED", "NOT_IN_SCOPE",
        "OVERCLAIMED", "INSUFFICIENT_EVIDENCE", "DEFERRED_WITH_REASON",
    }
    path = REVIEW_BASE / run_id / "declaration-review-package.zip"
    if not path.exists():
        pytest.skip("missing")
    with zipfile.ZipFile(path) as zf:
        grade_files = [n for n in zf.namelist() if "item-grades" in n and n.endswith(".json")]
        if not grade_files:
            pytest.skip("no grades")
        with zf.open(grade_files[0]) as f:
            data = json.loads(f.read().decode("utf-8"))
    grades_list = data if isinstance(data, list) else data.get("grades", [])
    for g in grades_list:
        assert g["supervisor_grade"] in valid_grades


# ---------------------------------------------------------------------------
# Grading engine: not rubber-stamp
# ---------------------------------------------------------------------------

def test_grade_overclaimed_no_evidence():
    g = grade_item({
        "item_id": "X", "declared_status": "completed",
        "has_evidence": False, "has_tests": False,
        "evidence_paths_missing": ["x"], "evidence_paths_found": [],
    }, {"failed": 0})
    assert g["supervisor_grade"] == "OVERCLAIMED"


def test_grade_rework_missing_paths():
    g = grade_item({
        "item_id": "X", "declared_status": "completed",
        "has_evidence": True, "has_tests": False,
        "evidence_paths_missing": ["missing.py"], "evidence_paths_found": ["found.py"],
    }, {"failed": 0})
    assert g["supervisor_grade"] == "REWORK_REQUIRED"


def test_grade_rework_failed_tests():
    g = grade_item({
        "item_id": "X", "declared_status": "completed",
        "has_evidence": True, "has_tests": True,
        "evidence_paths_missing": [], "evidence_paths_found": ["f"],
        "tests_declared": ["t"],
    }, {"failed": 1})
    assert g["supervisor_grade"] == "REWORK_REQUIRED"


def test_grade_limitations_stub_tests():
    g = grade_item({
        "item_id": "X", "declared_status": "completed",
        "has_evidence": True, "has_tests": True,
        "evidence_paths_missing": [], "evidence_paths_found": ["f"],
        "tests_declared": ["t"], "tests_with_content": [],
        "tests_empty_or_stub": ["stub.py"],
    }, {"failed": 0})
    assert g["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS"


def test_grade_mixed_input_not_all_accepted():
    items = [
        {"item_id": "A", "declared_status": "completed", "has_evidence": True,
         "has_tests": True, "evidence_paths_missing": [], "evidence_paths_found": ["f"],
         "tests_declared": ["t"]},
        {"item_id": "B", "declared_status": "completed", "has_evidence": False,
         "has_tests": False, "evidence_paths_missing": ["m"], "evidence_paths_found": []},
        {"item_id": "C", "declared_status": "not_started", "has_evidence": False,
         "has_tests": False},
    ]
    grades = [grade_item(i, {"failed": 0})["supervisor_grade"] for i in items]
    non_accepted = [g for g in grades if "ACCEPTED" not in g]
    assert len(non_accepted) >= 2, f"Expected mixed grades, got: {grades}"
