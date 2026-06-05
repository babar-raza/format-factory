"""
R100 — Inspector Unit Tests
Tests inspect_item(), inspect_declaration(), and check_test_file_content().
"""
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from inspect_declared_evidence import inspect_item, inspect_declaration, check_test_file_content


# ---------------------------------------------------------------------------
# check_test_file_content
# ---------------------------------------------------------------------------

def test_check_python_test_file_with_methods(tmp_path):
    f = tmp_path / "test_example.py"
    f.write_text("import pytest\n\ndef test_foo():\n    assert True\n\ndef test_bar():\n    assert 1 == 1\n")
    result = check_test_file_content(f)
    assert result["has_content"] is True
    assert result["method_count"] == 2


def test_check_python_file_without_tests(tmp_path):
    f = tmp_path / "test_empty.py"
    f.write_text("# just a comment\npass\n")
    result = check_test_file_content(f)
    assert result["has_content"] is False


def test_check_cs_test_file_with_facts(tmp_path):
    f = tmp_path / "TestExample.cs"
    f.write_text('[Fact]\npublic void TestSomething() { }\n[Theory]\npublic void TestOther() { }\n')
    result = check_test_file_content(f)
    assert result["has_content"] is True
    assert result["method_count"] == 2


def test_check_cs_file_without_tests(tmp_path):
    f = tmp_path / "Model.cs"
    f.write_text("public class Model { }\n")
    result = check_test_file_content(f)
    assert result["has_content"] is False


def test_check_nonexistent_file():
    result = check_test_file_content(Path("/nonexistent/test_foo.py"))
    assert result["has_content"] is False
    assert "not found" in result["reason"]


# ---------------------------------------------------------------------------
# inspect_item
# ---------------------------------------------------------------------------

def test_inspect_item_all_paths_found(tmp_path):
    (tmp_path / "evidence.md").write_text("proof")
    item = {
        "item_id": "ITEM-1",
        "status": "completed",
        "evidence_paths": ["evidence.md"],
        "tests_supporting": [],
        "acceptance_criteria": "",
    }
    result = inspect_item(item, tmp_path)
    assert result["has_evidence"] is True
    assert result["evidence_paths_found"] == ["evidence.md"]
    assert result["evidence_paths_missing"] == []


def test_inspect_item_missing_path(tmp_path):
    item = {
        "item_id": "ITEM-2",
        "status": "completed",
        "evidence_paths": ["missing.md"],
        "tests_supporting": [],
        "acceptance_criteria": "",
    }
    result = inspect_item(item, tmp_path)
    assert result["has_evidence"] is False
    assert "missing.md" in result["evidence_paths_missing"]


def test_inspect_item_summary_string_in_tests(tmp_path):
    """R98 fix: summary strings like '8 new tests, all passed' should NOT be treated as file paths."""
    item = {
        "item_id": "ITEM-3",
        "status": "completed",
        "evidence_paths": [],
        "tests_supporting": ["8 new tests, all passed"],
        "acceptance_criteria": "",
    }
    result = inspect_item(item, tmp_path)
    assert result["test_summaries"] == ["8 new tests, all passed"]
    assert result["tests_empty_or_stub"] == []
    assert result["tests_with_content"] == []


def test_inspect_item_test_file_paths_classified(tmp_path):
    """Test file paths (containing / or ending .py) are classified, not treated as summaries."""
    test_file = tmp_path / "tests" / "test_foo.py"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("def test_bar():\n    assert True\n")
    item = {
        "item_id": "ITEM-4",
        "status": "completed",
        "evidence_paths": [],
        "tests_supporting": ["tests/test_foo.py"],
        "acceptance_criteria": "",
    }
    result = inspect_item(item, tmp_path)
    assert "tests/test_foo.py" in result["tests_with_content"]
    assert result["test_summaries"] == []


def test_inspect_item_acceptance_criteria_pattern(tmp_path):
    """Acceptance criteria with a quoted pattern is checked against evidence files."""
    evidence = tmp_path / "proof.md"
    evidence.write_text('Result: REPRODUCE_RESULT: PASS\n')
    item = {
        "item_id": "ITEM-5",
        "status": "completed",
        "evidence_paths": ["proof.md"],
        "tests_supporting": [],
        "acceptance_criteria": 'The output must contain "PASS"',
    }
    result = inspect_item(item, tmp_path)
    assert result["acceptance_criteria_verified"] is True
    assert result["acceptance_criteria_pattern"] == "PASS"


# ---------------------------------------------------------------------------
# inspect_declaration
# ---------------------------------------------------------------------------

def test_inspect_declaration_basic(tmp_path):
    (tmp_path / "a.md").write_text("evidence A")
    decl = {
        "run_id": "test-run",
        "sprint_id": "test-sprint",
        "evidence_root": "",
        "test_results": {"passed": 5, "failed": 0},
        "planned_work_items": [
            {
                "item_id": "W1",
                "status": "completed",
                "evidence_paths": ["a.md"],
                "tests_supporting": [],
                "acceptance_criteria": "",
            },
        ],
        "evidence_artifacts": [
            {"path": "a.md", "type": "report", "related_work_items": ["W1"]},
        ],
    }
    result = inspect_declaration(decl, tmp_path)
    assert result["run_id"] == "test-run"
    assert len(result["item_inspections"]) == 1
    assert result["item_inspections"][0]["has_evidence"] is True
    assert len(result["artifact_inspections"]) == 1
    assert result["artifact_inspections"][0]["exists"] is True


def test_inspect_declaration_missing_artifact(tmp_path):
    decl = {
        "run_id": "test-run",
        "sprint_id": "test-sprint",
        "evidence_root": "",
        "planned_work_items": [],
        "evidence_artifacts": [
            {"path": "nonexistent.md", "type": "report", "related_work_items": []},
        ],
    }
    result = inspect_declaration(decl, tmp_path)
    assert result["artifact_inspections"][0]["exists"] is False
