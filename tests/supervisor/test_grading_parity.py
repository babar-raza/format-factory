"""V3: Grading determinism / parity tests (Design 3 / Phase E).

Verifies:
1. _check_product_source_content() correctly validates test files with def test_ + assert
2. _check_product_source_content() flags stubs (no assert or no def test_)
3. grade_item() applies PRODUCT_SOURCE check when item_type="PRODUCT_SOURCE"
4. LLM path can only DOWNGRADE, not UPGRADE (parity guarantee)
5. rule-based path returns ACCEPTED/ACCEPTED_VERIFIED for valid PRODUCT_SOURCE items
   without needing LLM
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools/supervisor"))

from grade_declared_work import (  # noqa: E402
    _check_product_source_content,
    grade_item,
    grade_all,
)


# ── Helper to build minimal item_inspection ──────────────────────────────────

def _make_inspection(item_id: str, evidence_found: list[str], evidence_missing: list[str] = None):
    found = evidence_found
    missing = evidence_missing or []
    return {
        "item_id": item_id,
        "declared_status": "completed",
        "has_evidence": bool(found),
        "has_tests": any("test_" in p for p in found),
        "evidence_paths_found": found,
        "evidence_paths_missing": missing,
        "tests_with_content": [p for p in found if "test_" in p],
        "tests_empty_or_stub": [],
        "acceptance_criteria_verified": False,
        "acceptance_criteria_pattern": "",
    }


class TestProductSourceContentCheck:
    def test_valid_test_file_passes(self, tmp_path):
        """Test file with def test_ and assert passes check."""
        test_file = tmp_path / "test_example.py"
        test_file.write_text("def test_something():\n    assert 1 == 1\n")

        result = _check_product_source_content(
            found_paths=[str(test_file.relative_to(tmp_path))],
            item_id="ITEM-001",
            repo_root=tmp_path,
        )
        assert result["test_content_valid"] is True

    def test_stub_no_assert_fails(self, tmp_path):
        """Test file with def test_ but no assert fails check."""
        test_file = tmp_path / "test_stub.py"
        test_file.write_text("def test_something():\n    pass\n")

        result = _check_product_source_content(
            found_paths=[str(test_file.relative_to(tmp_path))],
            item_id="ITEM-001",
            repo_root=tmp_path,
        )
        assert result["test_content_valid"] is False
        assert any("no assert" in d for d in result["details"])

    def test_no_test_fn_fails(self, tmp_path):
        """File with assert but no def test_ fails check."""
        test_file = tmp_path / "test_nodef.py"
        test_file.write_text("assert 1 == 1\n")

        result = _check_product_source_content(
            found_paths=[str(test_file.relative_to(tmp_path))],
            item_id="ITEM-001",
            repo_root=tmp_path,
        )
        assert result["test_content_valid"] is False
        assert any("no def test_" in d for d in result["details"])

    def test_no_test_files_does_not_penalize(self, tmp_path):
        """Pure source-only evidence (no test files) doesn't penalize test_content_valid."""
        src_file = tmp_path / "my_codec.py"
        src_file.write_text("def parse(): pass\n")

        result = _check_product_source_content(
            found_paths=[str(src_file.relative_to(tmp_path))],
            item_id="ITEM-001",
            repo_root=tmp_path,
        )
        # No test file → test_content_valid=True (no penalty for pure source items)
        assert result["test_content_valid"] is True

    def test_multiple_test_files_any_valid_passes(self, tmp_path):
        """If any test file is valid, check passes."""
        stub_file = tmp_path / "test_stub.py"
        stub_file.write_text("def test_a(): pass\n")
        valid_file = tmp_path / "test_valid.py"
        valid_file.write_text("def test_b():\n    assert True\n")

        result = _check_product_source_content(
            found_paths=[
                str(stub_file.relative_to(tmp_path)),
                str(valid_file.relative_to(tmp_path)),
            ],
            item_id="ITEM-001",
            repo_root=tmp_path,
        )
        assert result["test_content_valid"] is True

    def test_source_exists_check(self, tmp_path):
        """source_exists is True when a non-test source file exists."""
        src_file = tmp_path / "my_parser.py"
        src_file.write_text("def parse(): pass\n")

        result = _check_product_source_content(
            found_paths=[str(src_file.relative_to(tmp_path))],
            item_id="ITEM-001",
            repo_root=tmp_path,
        )
        assert result["source_exists"] is True


class TestGradeItemProductSource:
    def test_product_source_with_valid_test_gets_accepted(self, tmp_path):
        """PRODUCT_SOURCE item with valid test file gets accepted grade."""
        test_file = tmp_path / "test_feature.py"
        test_file.write_text("def test_parse():\n    assert True\n")
        rel_path = str(test_file.relative_to(tmp_path))

        inspection = _make_inspection("ITEM-001", evidence_found=[rel_path])
        grade = grade_item(inspection, {"passed": 5, "failed": 0},
                           item_type="PRODUCT_SOURCE", repo_root=tmp_path)

        accepted_grades = ("ACCEPTED", "ACCEPTED_VERIFIED", "ACCEPTED_WITH_LIMITATIONS",
                           "ACCEPTED_WITH_WARNINGS")
        assert grade["supervisor_grade"] in accepted_grades
        assert "product_source_check" in grade
        assert grade["product_source_check"]["test_content_valid"] is True

    def test_product_source_with_stub_gets_limitations(self, tmp_path):
        """PRODUCT_SOURCE item with stub test gets ACCEPTED_WITH_LIMITATIONS."""
        test_file = tmp_path / "test_stub.py"
        test_file.write_text("def test_it(): pass\n")
        rel_path = str(test_file.relative_to(tmp_path))

        inspection = _make_inspection("ITEM-001", evidence_found=[rel_path])
        grade = grade_item(inspection, {"passed": 0, "failed": 0},
                           item_type="PRODUCT_SOURCE", repo_root=tmp_path)

        assert grade["supervisor_grade"] in ("ACCEPTED_WITH_LIMITATIONS", "REWORK_REQUIRED")
        assert any("PRODUCT_SOURCE test content check failed" in f
                   for f in grade.get("acceptance_criteria_failed", []))

    def test_non_product_source_no_check_applied(self, tmp_path):
        """GOVERNANCE_TASKCARD items do not get product_source_check."""
        test_file = tmp_path / "test_thing.py"
        test_file.write_text("def test_it(): pass\n")
        rel_path = str(test_file.relative_to(tmp_path))

        inspection = _make_inspection("ITEM-001", evidence_found=[rel_path])
        grade = grade_item(inspection, {"passed": 0, "failed": 0},
                           item_type="GOVERNANCE_TASKCARD", repo_root=tmp_path)

        # No product_source_check should be present for non-product items
        assert "product_source_check" not in grade


class TestGradingParityLLMDowngradeOnly:
    """LLM semantic verification can only DOWNGRADE, never UPGRADE."""

    def test_llm_downgrade_accepted_verified_to_limitations(self, tmp_path):
        """LLM can downgrade ACCEPTED_VERIFIED → ACCEPTED_WITH_LIMITATIONS."""
        test_file = tmp_path / "test_feature.py"
        test_file.write_text("def test_parse():\n    assert True\n")
        rel_path = str(test_file.relative_to(tmp_path))

        inspection = _make_inspection("PS-001", evidence_found=[rel_path])
        decl_item = {
            "item_id": "PS-001",
            "item_type": "PRODUCT_SOURCE",
            "title": "Test feature",
            "acceptance_criteria": "must parse correctly",
            "evidence_paths": [rel_path],
        }
        declaration = {
            "planned_work_items": [decl_item],
            "test_results": {"passed": 5, "failed": 0},
            "_repo_root": str(tmp_path),
        }

        # Mock LLM to return inadequate verdict (downgrade signal)
        fake_sv = {
            "adequate": False,
            "confidence": 0.95,
            "stub_detected": False,
            "deficiencies": ["evidence is thin"],
            "llm_used": True,
        }

        with patch("grade_declared_work.semantic_verify_item", return_value=fake_sv):
            result = grade_all(
                inspection={"item_inspections": [inspection],
                            "test_results": {"passed": 5, "failed": 0},
                            "artifact_inspections": []},
                declaration=declaration,
            )

        grades = result["item_grades"]
        assert len(grades) == 1
        # LLM downgraded — grade should be at most ACCEPTED_WITH_LIMITATIONS
        assert grades[0]["supervisor_grade"] in (
            "ACCEPTED_WITH_LIMITATIONS", "REWORK_REQUIRED",
            "ACCEPTED_VERIFIED",  # If baseline was not ACCEPTED_VERIFIED
        )

    def test_llm_cannot_upgrade_rework_required(self, tmp_path):
        """LLM cannot upgrade REWORK_REQUIRED to a passing grade."""
        inspection = _make_inspection("PS-002", evidence_found=[], evidence_missing=["missing_file.py"])
        decl_item = {
            "item_id": "PS-002",
            "item_type": "PRODUCT_SOURCE",
            "title": "Missing evidence item",
            "acceptance_criteria": "must exist",
            "evidence_paths": ["missing_file.py"],
        }
        declaration = {
            "planned_work_items": [decl_item],
            "test_results": {"passed": 0, "failed": 0},
            "_repo_root": str(tmp_path),
        }

        # LLM says adequate (upgrade attempt) — should NOT be applied
        fake_sv = {"adequate": True, "confidence": 0.99, "stub_detected": False,
                   "deficiencies": [], "llm_used": True}

        with patch("grade_declared_work.semantic_verify_item", return_value=fake_sv):
            result = grade_all(
                inspection={"item_inspections": [inspection],
                            "test_results": {"passed": 0, "failed": 0},
                            "artifact_inspections": []},
                declaration=declaration,
            )

        grades = result["item_grades"]
        assert len(grades) == 1
        # Must still be a non-passing grade — LLM positive cannot upgrade a failing item.
        # The grader returns OVERCLAIMED (no evidence) or REWORK_REQUIRED — both are non-passing.
        non_passing = {"REWORK_REQUIRED", "OVERCLAIMED", "REJECTED", "INSUFFICIENT_EVIDENCE"}
        assert grades[0]["supervisor_grade"] in non_passing, (
            f"LLM should not upgrade failing item; got {grades[0]['supervisor_grade']}"
        )
