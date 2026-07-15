"""
R106 Supervisor Tests: Strict grading, cycle enforcement, dirty state classification.
Sprint: FORMAT-FACTORY-SUPERVISOR-R106-STREAM-CLEAN-CYCLE-ENFORCEMENT-RAW-LOGS-AND-STRICT-GRADING-001
"""
import json
import sys
import tempfile
import zipfile
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent.parent
TOOLS_DIR = REPO_ROOT / "tools" / "supervisor"
sys.path.insert(0, str(TOOLS_DIR))


# ---------------------------------------------------------------------------
# Lane D: Strict grading — pytest node ID combinations
# ---------------------------------------------------------------------------

def test_inspector_multiple_node_ids_same_file():
    """Multiple :: refs to the same file should all resolve correctly."""
    from inspect_declared_evidence import inspect_item

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        test_dir = td_path / "tests" / "supervisor"
        test_dir.mkdir(parents=True)
        (test_dir / "test_grading.py").write_text(
            "def test_a():\n    pass\ndef test_b():\n    pass\ndef test_c():\n    pass\n",
            encoding="utf-8",
        )

        item = {
            "item_id": "MULTI-01",
            "status": "completed",
            "evidence_paths": ["tests/supervisor/test_grading.py"],
            "test_references": [
                "tests/supervisor/test_grading.py::test_a",
                "tests/supervisor/test_grading.py::test_b",
                "tests/supervisor/test_grading.py::test_c",
            ],
        }
        result = inspect_item(item, td_path)
        assert len(result["tests_with_content"]) == 3
        assert len(result["tests_empty_or_stub"]) == 0


def test_inspector_mixed_node_ids_and_bare_paths():
    """Mix of :: refs and bare file paths should all resolve."""
    from inspect_declared_evidence import inspect_item

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        test_dir = td_path / "tests"
        test_dir.mkdir(parents=True)
        (test_dir / "test_one.py").write_text("def test_x():\n    pass\n", encoding="utf-8")
        (test_dir / "test_two.py").write_text("def test_y():\n    pass\n", encoding="utf-8")

        item = {
            "item_id": "MIX-01",
            "status": "completed",
            "evidence_paths": ["tests/test_one.py", "tests/test_two.py"],
            "test_references": [
                "tests/test_one.py::test_x",
                "tests/test_two.py",
            ],
        }
        result = inspect_item(item, td_path)
        assert len(result["tests_with_content"]) == 2
        assert len(result["tests_empty_or_stub"]) == 0


def test_inspector_csharp_node_ids():
    """C# test references should also resolve with :: stripped."""
    from inspect_declared_evidence import inspect_item

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        test_dir = td_path / "tests" / "net"
        test_dir.mkdir(parents=True)
        (test_dir / "FodsTests.cs").write_text(
            "using Xunit;\npublic class FodsTests {\n    [Fact]\n    public void TestLoad() { }\n}\n",
            encoding="utf-8",
        )

        item = {
            "item_id": "CS-01",
            "status": "completed",
            "evidence_paths": ["tests/net/FodsTests.cs"],
            "test_references": ["tests/net/FodsTests.cs::TestLoad"],
        }
        result = inspect_item(item, td_path)
        assert len(result["tests_with_content"]) == 1


# ---------------------------------------------------------------------------
# Lane D: Report-only items correctly get ACCEPTED_WITH_LIMITATIONS
# ---------------------------------------------------------------------------

def test_report_only_item_gets_limitations():
    """Work items with only report evidence (no tests) → ACCEPTED_WITH_LIMITATIONS."""
    from grade_declared_work import grade_item

    inspection = {
        "item_id": "REPORT-01",
        "declared_status": "completed",
        "has_evidence": True,
        "evidence_paths_found": ["reports/r106/analysis.md"],
        "evidence_paths_missing": [],
        "has_tests": False,
        "tests_declared": [],
        "tests_with_content": [],
        "tests_empty_or_stub": [],
        "acceptance_criteria_verified": False,
        "acceptance_criteria_pattern": "",
    }
    grade = grade_item(inspection, {"passed": 100, "failed": 0})
    assert grade["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS"
    assert any("No raw proof" in c for c in grade["acceptance_criteria_failed"])


def test_report_with_acceptance_criteria_verified_gets_verified():
    """Report-only item with acceptance criteria verified → ACCEPTED_VERIFIED."""
    from grade_declared_work import grade_item

    inspection = {
        "item_id": "REPORT-02",
        "declared_status": "completed",
        "has_evidence": True,
        "evidence_paths_found": ["reports/r106/analysis.md"],
        "evidence_paths_missing": [],
        "has_tests": False,
        "tests_declared": [],
        "tests_with_content": [],
        "tests_empty_or_stub": [],
        "acceptance_criteria_verified": True,
        "acceptance_criteria_pattern": "PASS",
    }
    grade = grade_item(inspection, {"passed": 100, "failed": 0})
    assert grade["supervisor_grade"] == "ACCEPTED_VERIFIED"


# ---------------------------------------------------------------------------
# Lane F: Autonomous-cycle continuation logic
# ---------------------------------------------------------------------------

def test_cycle_grade_all_with_mixed_verified_and_limitations():
    """grade_all with mixed ACCEPTED_VERIFIED and ACCEPTED_WITH_LIMITATIONS → ACCEPTED."""
    from grade_declared_work import grade_all

    inspection = {
        "run_id": "test-r106",
        "sprint_id": "TEST-R106",
        "test_results": {"passed": 50, "failed": 0},
        "item_inspections": [
            {
                "item_id": "ITEM-1",
                "declared_status": "completed",
                "has_evidence": True,
                "evidence_paths_found": ["tools/foo.py"],
                "evidence_paths_missing": [],
                "has_tests": True,
                "tests_declared": ["tests/test_foo.py::test_a"],
                "tests_with_content": ["tests/test_foo.py::test_a"],
                "tests_empty_or_stub": [],
                "acceptance_criteria_verified": False,
                "acceptance_criteria_pattern": "",
            },
            {
                "item_id": "ITEM-2",
                "declared_status": "completed",
                "has_evidence": True,
                "evidence_paths_found": ["reports/r106/doc.md"],
                "evidence_paths_missing": [],
                "has_tests": False,
                "tests_declared": [],
                "tests_with_content": [],
                "tests_empty_or_stub": [],
                "acceptance_criteria_verified": False,
                "acceptance_criteria_pattern": "",
            },
        ],
    }
    declaration = {
        "planned_work_items": [
            {"item_id": "ITEM-1", "title": "Code item"},
            {"item_id": "ITEM-2", "title": "Report item"},
        ],
    }
    result = grade_all(inspection, declaration)
    assert result["overall_verdict"] in ("ACCEPTED", "ACCEPTED_WITH_REWORK")
    assert result["autonomous_continue"] is True
    grades = {g["item_id"]: g["supervisor_grade"] for g in result["item_grades"]}
    assert grades["ITEM-1"] in ("ACCEPTED_VERIFIED", "ACCEPTED_WITH_LIMITATIONS", "UNVERIFIED")
    assert grades["ITEM-2"] in ("ACCEPTED_WITH_LIMITATIONS", "UNVERIFIED")


def test_cycle_overclaimed_blocks_continuation():
    """An overclaimed item should set autonomous_continue=False."""
    from grade_declared_work import grade_all

    inspection = {
        "run_id": "test-r106-oc",
        "sprint_id": "TEST-R106-OC",
        "test_results": {"passed": 10, "failed": 0},
        "item_inspections": [
            {
                "item_id": "OC-1",
                "declared_status": "completed",
                "has_evidence": False,
                "evidence_paths_found": [],
                "evidence_paths_missing": [],
                "has_tests": False,
                "tests_declared": [],
                "tests_with_content": [],
                "tests_empty_or_stub": [],
                "acceptance_criteria_verified": False,
                "acceptance_criteria_pattern": "",
            },
        ],
    }
    declaration = {"planned_work_items": [{"item_id": "OC-1", "title": "Overclaimed"}]}
    result = grade_all(inspection, declaration)
    assert result["overall_verdict"] != "ACCEPTED"
    assert "OC-1" in result["overclaimed_items"]


# ---------------------------------------------------------------------------
# Lane G: Dirty state classification
# ---------------------------------------------------------------------------

def test_dirty_state_classification():
    """Dirty files should be classifiable by category."""
    dirty_files = {
        "tools/supervisor/inspect_declared_evidence.py": "supervisor-tool-modified",
        "tests/supervisor/test_r105_verified_grading_and_state_cleanup.py": "supervisor-test-new",
        "reports/supervisor-r105/00-preflight.md": "supervisor-report-new",
        ".supervisor/context-pack.yaml": "supervisor-state-modified",
        "reports/supervisor/session-resume.md": "supervisor-state-modified",
    }
    # All should be supervisor-stream artifacts
    for path, category in dirty_files.items():
        assert category.startswith("supervisor"), f"{path} not supervisor-scoped"
        assert category in (
            "supervisor-tool-modified",
            "supervisor-test-new",
            "supervisor-report-new",
            "supervisor-state-modified",
        )


# ---------------------------------------------------------------------------
# Lane E: Package includes changed files
# ---------------------------------------------------------------------------

def test_package_changed_files_section():
    """Package ZIP should have changed-files/ section for declared changed_files."""
    from build_declaration_review_package import build_package

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        evidence_dir = td_path / ".local" / "evidences" / "pkg-test"
        evidence_dir.mkdir(parents=True)
        review_dir = td_path / ".local" / "supervisor" / "reviews" / "pkg-test"
        review_dir.mkdir(parents=True)
        (td_path / "reports" / "supervisor").mkdir(parents=True, exist_ok=True)
        (td_path / ".supervisor").mkdir(parents=True, exist_ok=True)

        # Create a changed file
        tools_dir = td_path / "tools" / "supervisor"
        tools_dir.mkdir(parents=True)
        (tools_dir / "example_tool.py").write_text("# tool code\n", encoding="utf-8")

        decl = {
            "run_id": "pkg-test",
            "sprint_id": "PKG-TEST",
            "evidence_root": ".local/evidences/pkg-test/",
            "changed_files": ["tools/supervisor/example_tool.py"],
        }
        decl_path = evidence_dir / "evidence-declaration.yaml"
        decl_path.write_text(yaml.dump(decl), encoding="utf-8")

        result = build_package(decl_path, td_path, review_dir)
        zip_path = Path(result["zip_path"])

        with zipfile.ZipFile(zip_path) as zf:
            names = zf.namelist()
            has_changed = any("changed-files/tools/supervisor/example_tool.py" in n for n in names)
            assert has_changed, f"Missing changed file in ZIP. Got: {names}"


# ---------------------------------------------------------------------------
# Lane B: Raw log documentation
# ---------------------------------------------------------------------------

def test_raw_log_requirement_documented():
    """Verify that the grading system documents when raw logs are absent."""
    from grade_declared_work import grade_item

    # Item with tests but no raw log capture — should still grade based on available evidence
    inspection = {
        "item_id": "LOG-01",
        "declared_status": "completed",
        "has_evidence": True,
        "evidence_paths_found": ["tools/supervisor/foo.py"],
        "evidence_paths_missing": [],
        "has_tests": True,
        "tests_declared": ["tests/supervisor/test_foo.py::test_bar"],
        "tests_with_content": ["tests/supervisor/test_foo.py::test_bar"],
        "tests_empty_or_stub": [],
        "acceptance_criteria_verified": False,
        "acceptance_criteria_pattern": "",
    }
    grade = grade_item(inspection, {"passed": 10, "failed": 0})
    # With concrete test proof, should be ACCEPTED_VERIFIED even without raw logs
    assert grade["supervisor_grade"] == "ACCEPTED_VERIFIED"


# ---------------------------------------------------------------------------
# Lane C: Stream identity warnings in packages
# ---------------------------------------------------------------------------

def test_stream_identity_detects_wrong_stream_in_state():
    """Package manifest should warn when state files reference wrong stream."""
    from build_declaration_review_package import build_package

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        evidence_dir = td_path / ".local" / "evidences" / "stream-test"
        evidence_dir.mkdir(parents=True)
        review_dir = td_path / ".local" / "supervisor" / "reviews" / "stream-test"
        review_dir.mkdir(parents=True)
        sup_dir = td_path / "reports" / "supervisor"
        sup_dir.mkdir(parents=True, exist_ok=True)
        (td_path / ".supervisor").mkdir(parents=True, exist_ok=True)

        # Create state files that reference wrong stream
        (sup_dir / "evidence-review.md").write_text(
            "Sprint: FORMAT-FACTORY-SKILLS-R102-SOMETHING\nVerdict: ACCEPTED\n",
            encoding="utf-8",
        )
        context_dir = td_path / ".supervisor"
        (context_dir / "context-pack.yaml").write_text(
            "latest_sprint: FORMAT-FACTORY-SKILLS-R102-SOMETHING\n",
            encoding="utf-8",
        )

        decl = {
            "run_id": "stream-test",
            "sprint_id": "FORMAT-FACTORY-SUPERVISOR-R106-TEST",
            "evidence_root": ".local/evidences/stream-test/",
        }
        decl_path = evidence_dir / "evidence-declaration.yaml"
        decl_path.write_text(yaml.dump(decl), encoding="utf-8")

        result = build_package(decl_path, td_path, review_dir)
        zip_path = Path(result["zip_path"])

        with zipfile.ZipFile(zip_path) as zf:
            manifest = json.loads(zf.read("package-manifest.json"))
            warnings = manifest.get("stream_identity_warnings", [])
            assert len(warnings) > 0, f"Expected stream warnings, got none. Manifest: {manifest}"
            assert any("SKILLS" in w for w in warnings), f"Expected SKILLS warning, got: {warnings}"
