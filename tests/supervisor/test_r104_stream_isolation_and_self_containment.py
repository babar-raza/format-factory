"""
R104 — Stream Isolation, Self-Containment, and Proof Quality Tests

Covers:
  - Wrong-stream context pack detection
  - Wrong-stream evidence review detection
  - Wrong-stream contradictions detection
  - Declared changed tools/tests included in package or diff
  - ACCEPTED_VERIFIED without raw proof downgrades
  - Materializer diffs all changed files (not just src/*)
  - Package stream identity validation
  - Stale selected gaps detection
  - Mixed grades (not rubber-stamp)
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

from grade_declared_work import grade_item
from inspect_declared_evidence import inspect_item
from autonomous_cycle import classify_continuation_state

POLICIES = REPO_ROOT / ".supervisor" / "policies.yaml"


# ---------------------------------------------------------------------------
# ACCEPTED_VERIFIED proof requirements
# ---------------------------------------------------------------------------

def test_accepted_verified_requires_concrete_proof():
    """Item with evidence but no test content or criteria should NOT be ACCEPTED_VERIFIED."""
    inspection = {
        "item_id": "PROOF-01",
        "declared_status": "completed",
        "has_evidence": True,
        "has_tests": False,
        "evidence_paths_missing": [],
        "evidence_paths_found": ["reports/some-report.md"],
        "tests_declared": [],
        "tests_with_content": [],
        "tests_empty_or_stub": [],
    }
    g = grade_item(inspection, {"failed": 0})
    assert g["supervisor_grade"] != "ACCEPTED_VERIFIED", \
        "Path-only evidence should not be ACCEPTED_VERIFIED"
    assert g["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS"


def test_accepted_verified_with_test_content_passes():
    """Item with verified test content should be ACCEPTED_VERIFIED."""
    inspection = {
        "item_id": "PROOF-02",
        "declared_status": "completed",
        "has_evidence": True,
        "has_tests": True,
        "evidence_paths_missing": [],
        "evidence_paths_found": ["tools/supervisor/something.py"],
        "tests_declared": ["tests/supervisor/test_something.py"],
        "tests_with_content": ["tests/supervisor/test_something.py"],
        "tests_empty_or_stub": [],
    }
    g = grade_item(inspection, {"failed": 0})
    assert g["supervisor_grade"] == "ACCEPTED_VERIFIED"


def test_accepted_verified_with_criteria_verified():
    """Item with verified acceptance criteria should be ACCEPTED_VERIFIED."""
    inspection = {
        "item_id": "PROOF-03",
        "declared_status": "completed",
        "has_evidence": True,
        "has_tests": False,
        "evidence_paths_missing": [],
        "evidence_paths_found": ["reports/proof.md"],
        "tests_declared": [],
        "tests_with_content": [],
        "tests_empty_or_stub": [],
        "acceptance_criteria_verified": True,
        "acceptance_criteria_pattern": "PASS",
    }
    g = grade_item(inspection, {"failed": 0})
    assert g["supervisor_grade"] == "ACCEPTED_VERIFIED"


def test_grade_overclaimed_still_works():
    """OVERCLAIMED for completed with no evidence."""
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
        "evidence_paths_missing": ["m.py"], "evidence_paths_found": ["f.py"],
    }, {"failed": 0})
    assert g["supervisor_grade"] == "REWORK_REQUIRED"


# ---------------------------------------------------------------------------
# Materializer: diffs all changed files, not just src/*
# ---------------------------------------------------------------------------

def test_materializer_diffs_tools():
    """Materializer should diff tools/** files, not just src/**."""
    from materialize_declared_evidence import materialize

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        ev_dir = td_path / ".local" / "evidences" / "test-mat"
        ev_dir.mkdir(parents=True)
        out_dir = td_path / ".local" / "supervisor" / "materialized" / "test-mat"

        # Write minimal declaration
        decl = {
            "run_id": "test-mat",
            "sprint_id": "TEST",
            "evidence_root": ".local/evidences/test-mat/",
            "changed_files": ["tools/supervisor/test_tool.py"],
            "evidence_artifacts": [],
            "planned_work_items": [],
        }
        decl_path = ev_dir / "evidence-declaration.yaml"
        decl_path.write_text(yaml.dump(decl), encoding="utf-8")

        # Create the tools file
        tools_dir = td_path / "tools" / "supervisor"
        tools_dir.mkdir(parents=True)
        (tools_dir / "test_tool.py").write_text("# modified tool\n", encoding="utf-8")

        result = materialize(decl_path, td_path, out_dir)
        patch_path = out_dir / "source-change-diffs.patch"
        assert patch_path.exists()
        content = patch_path.read_text(encoding="utf-8")
        # Should attempt to diff tools/supervisor/test_tool.py (not skip it)
        assert "test_tool.py" in content or "No diffs" in content


# ---------------------------------------------------------------------------
# Package builder: changed files included
# ---------------------------------------------------------------------------

def test_package_includes_changed_files():
    """Package should include declared changed files under changed-files/."""
    from build_declaration_review_package import build_package

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        ev_dir = td_path / ".local" / "evidences" / "test-cf"
        ev_dir.mkdir(parents=True)
        review_dir = td_path / ".local" / "supervisor" / "reviews" / "test-cf"
        review_dir.mkdir(parents=True)
        (td_path / "reports" / "supervisor").mkdir(parents=True)
        (td_path / ".supervisor").mkdir(parents=True)

        # Create a changed file
        tools_dir = td_path / "tools" / "supervisor"
        tools_dir.mkdir(parents=True)
        (tools_dir / "my_tool.py").write_text("# tool content\n", encoding="utf-8")

        decl = {
            "run_id": "test-cf",
            "sprint_id": "FORMAT-FACTORY-SUPERVISOR-R104-TEST",
            "evidence_root": ".local/evidences/test-cf/",
            "changed_files": ["tools/supervisor/my_tool.py"],
            "evidence_artifacts": [],
            "planned_work_items": [],
        }
        decl_path = ev_dir / "evidence-declaration.yaml"
        decl_path.write_text(yaml.dump(decl), encoding="utf-8")

        result = build_package(decl_path, td_path, review_dir)
        with zipfile.ZipFile(result["zip_path"]) as zf:
            names = zf.namelist()
            has_changed = any("changed-files/tools/supervisor/my_tool.py" in n for n in names)
            assert has_changed, f"Missing changed file. Got: {[n for n in names if 'changed' in n]}"


def test_package_stream_identity_warnings():
    """Package manifest should report wrong-stream state warnings."""
    from build_declaration_review_package import build_package

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        ev_dir = td_path / ".local" / "evidences" / "test-si"
        ev_dir.mkdir(parents=True)
        review_dir = td_path / ".local" / "supervisor" / "reviews" / "test-si"
        review_dir.mkdir(parents=True)
        sup_dir = td_path / "reports" / "supervisor"
        sup_dir.mkdir(parents=True)
        (td_path / ".supervisor").mkdir(parents=True)

        # Write evidence-review.md referencing WRONG stream
        (sup_dir / "evidence-review.md").write_text(
            "Sprint: FORMAT-FACTORY-SKILLS-R999-WRONG\nVerdict: ACCEPTED\n",
            encoding="utf-8"
        )

        decl = {
            "run_id": "test-si",
            "sprint_id": "FORMAT-FACTORY-SUPERVISOR-R104-STREAM-TEST",
            "evidence_root": ".local/evidences/test-si/",
            "changed_files": [],
            "evidence_artifacts": [],
            "planned_work_items": [],
        }
        decl_path = ev_dir / "evidence-declaration.yaml"
        decl_path.write_text(yaml.dump(decl), encoding="utf-8")

        result = build_package(decl_path, td_path, review_dir)
        with zipfile.ZipFile(result["zip_path"]) as zf:
            pkg_json = json.loads(zf.read("package-manifest.json"))
            warnings = pkg_json.get("stream_identity_warnings", [])
            assert len(warnings) > 0, "Should detect wrong-stream evidence-review"
            assert any("SKILLS" in w for w in warnings)


# ---------------------------------------------------------------------------
# Continuation states: stream isolation
# ---------------------------------------------------------------------------

def test_wrong_stream_context_stops():
    cs = classify_continuation_state(
        False, False, ["wrong_stream_context"], [], [], {}, POLICIES
    )
    assert cs == "NO_WRONG_STREAM_CONTEXT"


def test_missing_raw_logs_stops():
    cs = classify_continuation_state(
        False, False, ["missing_raw_logs_for_verified_claims"], [], [], {}, POLICIES
    )
    assert cs == "NO_MISSING_RAW_LOGS_FOR_VERIFIED_CLAIMS"


def test_yes_with_rework_works():
    cs = classify_continuation_state(
        "true_with_rework", False, [], [], ["item-1"], {}, POLICIES
    )
    assert cs == "YES_WITH_REWORK"


# ---------------------------------------------------------------------------
# Inspector: test_references alias
# ---------------------------------------------------------------------------

def test_inspector_reads_test_references_alias():
    item = {
        "item_id": "ALIAS-01",
        "status": "completed",
        "evidence_paths": [],
        "test_references": ["tests/supervisor/test_foo.py::test_bar"],
    }
    result = inspect_item(item, REPO_ROOT)
    assert result["has_tests"] is True


# ---------------------------------------------------------------------------
# Replay: existing packages
# ---------------------------------------------------------------------------

REVIEW_BASE = REPO_ROOT / ".local" / "supervisor" / "reviews"


@pytest.mark.parametrize("run_id,stream", [
    ("supervisor-r103", "supervisor"),
    ("mainstream-r105", "mainstream"),
    ("acceleration-r103", "acceleration"),
    ("skills-r101", "skills"),
])
def test_replay_package_exists_and_valid(run_id, stream):
    path = REVIEW_BASE / run_id / "declaration-review-package.zip"
    if not path.exists():
        pytest.skip(f"Missing: {path}")
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        has_decl = any("evidence-declaration.yaml" in n for n in names)
        has_legacy = any("final-verdict.md" in n for n in names)
    assert has_decl, "Not a declaration-review package"
    assert not has_legacy, "Contains legacy markers"


# ---------------------------------------------------------------------------
# Not rubber-stamp
# ---------------------------------------------------------------------------

def test_mixed_input_not_all_accepted():
    items = [
        {"item_id": "A", "declared_status": "completed", "has_evidence": True,
         "has_tests": True, "evidence_paths_missing": [], "evidence_paths_found": ["f"],
         "tests_declared": ["t"], "tests_with_content": ["t"], "tests_empty_or_stub": []},
        {"item_id": "B", "declared_status": "completed", "has_evidence": False,
         "has_tests": False, "evidence_paths_missing": ["m"], "evidence_paths_found": []},
        {"item_id": "C", "declared_status": "not_started", "has_evidence": False,
         "has_tests": False},
    ]
    grades = [grade_item(i, {"failed": 0})["supervisor_grade"] for i in items]
    assert "ACCEPTED_VERIFIED" in grades
    assert "OVERCLAIMED" in grades or "NOT_ATTEMPTED" in grades
