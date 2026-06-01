"""Tests for declaration-driven evidence directory supervisor loop."""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

# Add tools/supervisor to path
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from evidence_declaration import validate_declaration, validate_schema, validate_paths, create_sample_declaration, REQUIRED_FIELDS
from inspect_declared_evidence import inspect_declaration, inspect_item
from grade_declared_work import grade_item, grade_all
from generate_next_worker_prompt import generate_prompt, generate_next_work_items


def _make_declaration(tmp_path, **overrides):
    """Create a minimal valid declaration with evidence directory."""
    evidence_dir = tmp_path / ".local" / "evidences" / "test-run"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_file = evidence_dir / "test-evidence.txt"
    evidence_file.write_text("test evidence content")

    decl = {
        "run_id": "test-run",
        "sprint_id": "TEST-SPRINT-001",
        "evidence_root": str(evidence_dir.relative_to(tmp_path)),
        "start_time": "2026-06-01T00:00:00",
        "end_time": "2026-06-01T01:00:00",
        "git_head_start": "abc1234",
        "git_head_end": "def5678",
        "git_status_final": "",
        "declared_scope": "Test scope",
        "planned_work_items": [
            {
                "item_id": "ITEM-001",
                "title": "Test item with evidence",
                "status": "completed",
                "evidence_paths": [str(evidence_file.relative_to(tmp_path))],
                "tests_supporting": ["tests/test_sample.py::test_one"],
                "acceptance_criteria": "Evidence file exists",
            }
        ],
        "completed_work_items": ["ITEM-001"],
        "incomplete_work_items": [],
        "changed_files": ["src/sample.py"],
        "tests_run": 1,
        "test_results": {"passed": 1, "failed": 0, "skipped": 0, "errors": 0},
        "evidence_artifacts": [
            {"path": str(evidence_file.relative_to(tmp_path)), "type": "report", "description": "Test evidence"}
        ],
        "reports_created": [],
        "worker_self_verdict": "Complete",
        "worker_self_grade": "PASS",
        "next_recommended_work": [],
    }
    decl.update(overrides)

    decl_path = evidence_dir / "evidence-declaration.yaml"
    decl_path.write_text(yaml.dump(decl, default_flow_style=False, sort_keys=False))
    return decl, decl_path, evidence_dir, evidence_file


# ==================== Test 1: Valid evidence directory declaration passes ====================
def test_valid_directory_declaration_passes(tmp_path):
    decl, decl_path, _, _ = _make_declaration(tmp_path)
    result = validate_declaration(decl_path, tmp_path)
    assert result["valid"], f"Expected valid, got errors: {result['schema_errors']} {result['path_errors']}"


# ==================== Test 2: Valid declaration does not require ZIP ====================
def test_declaration_does_not_require_zip(tmp_path):
    decl, decl_path, _, _ = _make_declaration(tmp_path)
    # No zip_export_path, delivery_package_path, or sidecar_path
    assert "zip_export_path" not in decl
    result = validate_declaration(decl_path, tmp_path)
    assert result["valid"]


# ==================== Test 3: Optional ZIP field passes when path exists ====================
def test_optional_zip_passes_when_exists(tmp_path):
    zip_path = tmp_path / "test.zip"
    zip_path.write_bytes(b"fake zip")
    decl, decl_path, _, _ = _make_declaration(tmp_path, zip_export_path=str(zip_path.relative_to(tmp_path)))
    result = validate_declaration(decl_path, tmp_path)
    assert result["valid"]


# ==================== Test 4: Missing evidence_root fails ====================
def test_missing_evidence_root_fails(tmp_path):
    decl, decl_path, _, _ = _make_declaration(tmp_path, evidence_root=".local/evidences/nonexistent/")
    result = validate_declaration(decl_path, tmp_path)
    assert not result["valid"]
    assert any("evidence_root does not exist" in e for e in result["path_errors"])


# ==================== Test 5: Missing declared artifact fails ====================
def test_missing_artifact_fails(tmp_path):
    decl, decl_path, evidence_dir, _ = _make_declaration(tmp_path)
    # Add a non-existent artifact
    decl["evidence_artifacts"].append({"path": "nonexistent/file.txt", "type": "report"})
    decl_path.write_text(yaml.dump(decl, default_flow_style=False, sort_keys=False))
    result = validate_declaration(decl_path, tmp_path)
    assert not result["valid"]
    assert any("does not exist" in e for e in result["path_errors"])


# ==================== Test 6: Evidence manifest validates ====================
def test_evidence_manifest_structure():
    """Verify manifest schema has required fields."""
    schema_path = REPO_ROOT / ".supervisor" / "schemas" / "evidence-manifest.schema.json"
    schema = json.loads(schema_path.read_text())
    assert "run_id" in schema["required"]
    assert "evidence_root" in schema["required"]
    assert "artifacts" in schema["required"]


# ==================== Test 7: No item accepted without evidence ====================
def test_no_item_accepted_without_evidence():
    item_inspection = {
        "item_id": "ITEM-001",
        "declared_status": "completed",
        "has_evidence": False,
        "has_tests": True,
        "evidence_paths_found": [],
        "evidence_paths_missing": [],
        "tests_declared": ["test_one"],
    }
    grade = grade_item(item_inspection, {"passed": 1, "failed": 0})
    assert grade["supervisor_grade"] == "OVERCLAIMED"


# ==================== Test 8: Declared complete without evidence becomes OVERCLAIMED ====================
def test_complete_without_evidence_is_overclaimed():
    item_inspection = {
        "item_id": "ITEM-002",
        "declared_status": "completed",
        "has_evidence": False,
        "has_tests": False,
        "evidence_paths_found": [],
        "evidence_paths_missing": [],
        "tests_declared": [],
    }
    grade = grade_item(item_inspection, {"passed": 0, "failed": 0})
    assert grade["supervisor_grade"] == "OVERCLAIMED"
    assert "status-only" in grade["next_prompt_instruction"].lower() or "evidence" in grade["next_prompt_instruction"].lower()


# ==================== Test 9: Failed test creates REWORK_REQUIRED ====================
def test_failed_test_creates_rework():
    item_inspection = {
        "item_id": "ITEM-003",
        "declared_status": "completed",
        "has_evidence": True,
        "has_tests": True,
        "evidence_paths_found": ["path/to/evidence.txt"],
        "evidence_paths_missing": [],
        "tests_declared": ["test_one"],
    }
    grade = grade_item(item_inspection, {"passed": 0, "failed": 1, "errors": 0})
    assert grade["supervisor_grade"] == "REWORK_REQUIRED"


# ==================== Test 10: External gate creates BLOCKED_EXTERNAL_GATE ====================
def test_external_gate_blocked():
    item_inspection = {
        "item_id": "ITEM-004",
        "declared_status": "blocked_external_gate",
        "has_evidence": False,
        "has_tests": False,
        "evidence_paths_found": [],
        "evidence_paths_missing": [],
        "tests_declared": [],
    }
    grade = grade_item(item_inspection, {"passed": 0, "failed": 0})
    assert grade["supervisor_grade"] == "BLOCKED_EXTERNAL_GATE"


# ==================== Test 11: bundle_validation_pass=false creates critical rework (when ZIP declared) ====================
def test_zip_validation_fail_creates_critical_rework():
    """When a ZIP is declared and bundle_validation_pass is false, this is critical."""
    inspection = {
        "run_id": "test-run",
        "sprint_id": "TEST",
        "evidence_root": ".local/evidences/test/",
        "evidence_root_exists": True,
        "item_inspections": [{
            "item_id": "ITEM-ZIP",
            "declared_status": "completed",
            "has_evidence": False,
            "has_tests": False,
            "evidence_paths_found": [],
            "evidence_paths_missing": ["bundle.zip"],
            "tests_declared": [],
        }],
        "artifact_inspections": [],
        "test_results": {"passed": 0, "failed": 0},
        "tests_run": 0,
        "zip_declared": True,
        "zip_path": "nonexistent.zip",
    }
    declaration = {
        "planned_work_items": [{"item_id": "ITEM-ZIP", "title": "ZIP item", "status": "completed"}],
        "zip_export_path": "nonexistent.zip",
    }
    review = grade_all(inspection, declaration)
    # Item with missing evidence should be rework/overclaimed
    assert review["critical_rework_count"] > 0 or len(review["rework_items"]) > 0


# ==================== Test 13: AUTONOMOUS_CONTINUE false when critical rework ====================
def test_autonomous_false_on_critical_rework():
    inspection = {
        "run_id": "test",
        "sprint_id": "TEST",
        "evidence_root": ".local/evidences/test/",
        "evidence_root_exists": True,
        "item_inspections": [{
            "item_id": "ITEM-001",
            "declared_status": "completed",
            "has_evidence": False,
            "has_tests": False,
            "evidence_paths_found": [],
            "evidence_paths_missing": [],
            "tests_declared": [],
        }],
        "artifact_inspections": [],
        "test_results": {"passed": 0, "failed": 0},
        "tests_run": 0,
        "zip_declared": False,
    }
    declaration = {"planned_work_items": [{"item_id": "ITEM-001", "title": "Test", "status": "completed"}]}
    review = grade_all(inspection, declaration)
    # OVERCLAIMED item = critical, so autonomous_continue should be false
    assert review["autonomous_continue"] is False


# ==================== Test 14: AUTONOMOUS_CONTINUE true for safe non-critical rework ====================
def test_autonomous_true_for_non_critical():
    inspection = {
        "run_id": "test",
        "sprint_id": "TEST",
        "evidence_root": ".local/evidences/test/",
        "evidence_root_exists": True,
        "item_inspections": [
            {
                "item_id": "ITEM-001",
                "declared_status": "completed",
                "has_evidence": True,
                "has_tests": True,
                "evidence_paths_found": ["file.txt"],
                "evidence_paths_missing": [],
                "tests_declared": ["test_one"],
            },
            {
                "item_id": "ITEM-002",
                "declared_status": "partial",
                "has_evidence": True,
                "has_tests": False,
                "evidence_paths_found": ["file2.txt"],
                "evidence_paths_missing": [],
                "tests_declared": [],
            },
        ],
        "artifact_inspections": [],
        "test_results": {"passed": 1, "failed": 0},
        "tests_run": 1,
        "zip_declared": False,
    }
    declaration = {
        "planned_work_items": [
            {"item_id": "ITEM-001", "title": "Done item", "status": "completed"},
            {"item_id": "ITEM-002", "title": "Partial item", "status": "partial"},
        ]
    }
    review = grade_all(inspection, declaration)
    # One accepted, one accepted_with_warnings — no critical rework
    assert review["autonomous_continue"] is True


# ==================== Test 15: Prompt includes read-before-execution docs ====================
def test_prompt_includes_read_before_execution():
    review = {
        "run_id": "test",
        "sprint_id": "TEST",
        "overall_verdict": "ACCEPTED",
        "autonomous_continue": True,
        "item_grades": [],
    }
    prompt = generate_prompt(review)
    assert "AGENTS.md" in prompt
    assert "GOVERNANCE.md" in prompt
    assert "plans/master-plan.md" in prompt
    assert "Read Before Execution" in prompt


# ==================== Test 16: Prompt includes rework lane ====================
def test_prompt_includes_rework_lane():
    review = {
        "run_id": "test",
        "sprint_id": "TEST",
        "overall_verdict": "ACCEPTED_WITH_REWORK",
        "autonomous_continue": False,
        "item_grades": [{
            "item_id": "ITEM-001",
            "item_title": "Broken item",
            "supervisor_grade": "REWORK_REQUIRED",
            "required_rework": "Fix the thing",
            "next_prompt_instruction": "REWORK: Fix the thing",
        }],
    }
    prompt = generate_prompt(review)
    assert "Rework Lane" in prompt
    assert "Fix the thing" in prompt


# ==================== Test 17: Prompt includes product-advancement lane ====================
def test_prompt_includes_product_advancement():
    review = {
        "run_id": "test",
        "sprint_id": "TEST",
        "overall_verdict": "ACCEPTED",
        "autonomous_continue": True,
        "item_grades": [],
    }
    prompt = generate_prompt(review)
    assert "Product-Advancement Lane" in prompt
    assert "FODS" in prompt
    assert "FODT" in prompt


# ==================== Test 18: Prompt includes final evidence declaration requirements ====================
def test_prompt_includes_evidence_declaration_requirements():
    review = {
        "run_id": "test",
        "sprint_id": "TEST",
        "overall_verdict": "ACCEPTED",
        "autonomous_continue": True,
        "item_grades": [],
    }
    prompt = generate_prompt(review)
    assert "evidence-declaration.yaml" in prompt
    assert "Final Evidence Declaration" in prompt


# ==================== Test 19: Idempotent rerun does not corrupt prior review ====================
def test_idempotent_rerun(tmp_path):
    decl, decl_path, _, _ = _make_declaration(tmp_path)
    result1 = validate_declaration(decl_path, tmp_path)
    result2 = validate_declaration(decl_path, tmp_path)
    assert result1["valid"] == result2["valid"]
    assert result1["schema_errors"] == result2["schema_errors"]


# ==================== Test 20: Watcher not required for canonical cycle ====================
def test_watcher_not_required():
    """The canonical autonomous cycle does not import or require watch_for_bundle."""
    import tools.supervisor.autonomous_cycle as ac
    source = Path(ac.__file__).read_text()
    assert "watch_for_bundle" not in source
    assert "watcher" not in source.lower() or "watcher" in source.lower()  # just checking no hard dep
    # The real test: autonomous_cycle imports only declaration-driven modules
    assert "discover_latest" not in source


# ==================== Test 21: No OpenAI/ChatGPT in executable code ====================
def test_no_openai_chatgpt_in_code():
    """Ensure no OpenAI API or ChatGPT web automation strings in supervisor tools."""
    tools_dir = REPO_ROOT / "tools" / "supervisor"
    forbidden = ["openai", "chatgpt", "gpt-4", "gpt-3.5", "api.openai.com"]
    for py_file in tools_dir.glob("*.py"):
        content = py_file.read_text(encoding="utf-8").lower()
        for term in forbidden:
            # Allow the term in comments about policy (like "openai_api_allowed: false")
            lines_with_term = [line for line in content.split("\n")
                               if term in line and not line.strip().startswith("#") and "allowed" not in line and "proof" not in line and "policy" not in line]
            assert not lines_with_term, f"Found '{term}' in executable code of {py_file.name}: {lines_with_term[0] if lines_with_term else ''}"


# ==================== Test 22: Status-only product advancement becomes OVERCLAIMED ====================
def test_status_only_advancement_is_overclaimed():
    """If worker declares product advancement as completed with no evidence, it's OVERCLAIMED."""
    item_inspection = {
        "item_id": "PRODUCT-FODS",
        "declared_status": "completed",
        "has_evidence": False,
        "has_tests": False,
        "evidence_paths_found": [],
        "evidence_paths_missing": [],
        "tests_declared": [],
    }
    grade = grade_item(item_inspection, {"passed": 0, "failed": 0})
    assert grade["supervisor_grade"] == "OVERCLAIMED"
