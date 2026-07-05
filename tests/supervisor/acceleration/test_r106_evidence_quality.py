"""Tests for R106 evidence quality scoring in grade_declared_work.py."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"))

from grade_declared_work import grade_all


def _make_inspection(items, test_results=None):
    """Build a minimal inspection dict."""
    return {
        "run_id": "test-r106",
        "sprint_id": "SPRINT-TEST",
        "evidence_root": "reports/test",
        "test_results": test_results or {"passed": 10, "failed": 0, "skipped": 0, "errors": 0},
        "item_inspections": items,
    }


def _make_item(item_id, status="completed", has_evidence=True, has_tests=False,
               missing_paths=None, found_paths=None, tests_with_content=None):
    """Build a minimal item inspection."""
    return {
        "item_id": item_id,
        "declared_status": status,
        "has_evidence": has_evidence,
        "has_tests": has_tests,
        "evidence_paths_missing": missing_paths or [],
        "evidence_paths_found": found_paths or ["reports/test/evidence.md"],
        "tests_declared": [],
        "tests_with_content": tests_with_content or [],
        "tests_empty_or_stub": [],
    }


def _make_declaration(items):
    """Build a minimal declaration."""
    return {
        "planned_work_items": [{"item_id": i["item_id"], "title": f"Item {i['item_id']}"} for i in items],
    }


def test_evidence_quality_score_all_path_only():
    """All path-only items → score 0.0."""
    items = [_make_item("W0"), _make_item("W1")]
    inspection = _make_inspection(items)
    decl = _make_declaration(items)
    review = grade_all(inspection, decl)

    assert review["evidence_quality_score"] == 0.0
    assert review["verified_item_count"] == 0


@pytest.mark.xfail(strict=False, reason="TC-CQGA-015: ACCEPTED_VERIFIED requires LLM; without LLM items capped at ACCEPTED_WITH_LIMITATIONS → score 0.0")
def test_evidence_quality_score_all_verified():
    """All verified items → score 1.0 (requires LLM; 0.0 in LLM-unavailable environments per TC-CQGA-015)."""
    items = [
        _make_item("W0", tests_with_content=["test_w0.py"], has_tests=True),
        _make_item("W1", tests_with_content=["test_w1.py"], has_tests=True),
    ]
    inspection = _make_inspection(items)
    decl = _make_declaration(items)
    review = grade_all(inspection, decl)

    assert review["evidence_quality_score"] == 1.0
    assert review["verified_item_count"] == 2


@pytest.mark.xfail(strict=False, reason="TC-CQGA-015: ACCEPTED_VERIFIED requires LLM; without LLM items capped at ACCEPTED_WITH_LIMITATIONS → score 0.0")
def test_evidence_quality_score_mixed():
    """Mixed verified and path-only → fractional score (requires LLM per TC-CQGA-015)."""
    items = [
        _make_item("W0", tests_with_content=["test_w0.py"], has_tests=True),
        _make_item("W1"),
    ]
    inspection = _make_inspection(items)
    decl = _make_declaration(items)
    review = grade_all(inspection, decl)

    assert review["evidence_quality_score"] == 0.5
    assert review["verified_item_count"] == 1


def test_evidence_quality_score_no_items():
    """No items → score 0.0."""
    inspection = _make_inspection([])
    decl = _make_declaration([])
    review = grade_all(inspection, decl)

    assert review["evidence_quality_score"] == 0.0
    assert review["verified_item_count"] == 0
