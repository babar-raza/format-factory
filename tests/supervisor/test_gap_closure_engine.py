"""Tests for gap_closure_engine.py — automated gap closure from graded evidence.

TC-FL-003: Phase 1 of the feedback loop redesign (pure-knitting-dusk plan).
"""
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from gap_closure_engine import (
    close_gaps_from_grades,
    _match_grades_to_gaps,
    _evaluate_closure_criteria,
    close_implementation_verified_gaps,
    _derive_function_name,
    _scan_test_files_for_function,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_gap(gap_id: str, status: str = "open", **kwargs) -> dict:
    base = {
        "gap_id": gap_id,
        "format": "CSV",
        "capability_name": "Probe Csv",
        "status": status,
        "priority": "P1",
        "product_type": "foss_reduced",
        "owning_lane": 1,
        "commercial_impact": "NONE",
    }
    base.update(kwargs)
    return base


def _make_grade(item_id: str, grade: str, evidence: list | None = None,
                tests_supporting: int = 5, tests_failing: int = 0) -> dict:
    return {
        "item_id": item_id,
        "supervisor_grade": grade,
        "evidence_paths_found": evidence or [],
        "tests_supporting": tests_supporting,
        "tests_failing": tests_failing,
    }


def _make_declaration(items: list[dict]) -> dict:
    return {
        "planned_work_items": items,
        "test_results": {"passed": 12, "failed": 0},
    }


def _make_review(grades: list[dict]) -> dict:
    return {
        "item_grades": grades,
        "accepted_items": [g["item_id"] for g in grades],
        "rework_items": [],
        "overclaimed_items": [],
    }


def _write_ledger(tmp_path: Path, gaps: list[dict]) -> Path:
    ledger = {"schema_version": "1.0", "gaps": gaps}
    gl_path = tmp_path / "gap-ledger.json"
    gl_path.write_text(json.dumps(ledger), encoding="utf-8")
    return gl_path


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestCloseGapAcceptedVerified:
    """Grade=ACCEPTED_VERIFIED + gap_ledger_ref + test evidence → gap closed."""

    def test_gap_closed(self, tmp_path):
        gl_path = _write_ledger(tmp_path, [_make_gap("GAP-CSV-FOSS-001")])

        declaration = _make_declaration([{
            "item_id": "WI-001", "gap_ledger_ref": "GAP-CSV-FOSS-001",
            "status": "completed",
            "evidence_paths": ["tests/python/csv/test_csv_probe.py"],
        }])
        review = _make_review([
            _make_grade("WI-001", "ACCEPTED_VERIFIED",
                        evidence=["tests/python/csv/test_csv_probe.py"]),
        ])

        result = close_gaps_from_grades(review, declaration, gl_path, "sprint-001")
        assert result["closed"] == 1
        assert result["matches"] == 1

        updated = json.loads(gl_path.read_text())
        gap = updated["gaps"][0]
        assert gap["status"] == "closed"
        assert gap["closed_by_engine"] is True
        assert gap["closed_by_sprint"] == "sprint-001"
        assert gap["closure_evidence"]["supervisor_grade"] == "ACCEPTED_VERIFIED"

    def test_closure_log_written(self, tmp_path):
        gl_path = _write_ledger(tmp_path, [_make_gap("GAP-CSV-FOSS-001")])
        declaration = _make_declaration([{
            "item_id": "WI-001", "gap_ledger_ref": "GAP-CSV-FOSS-001",
            "status": "completed",
            "evidence_paths": ["tests/python/csv/test_csv_probe.py"],
        }])
        review = _make_review([
            _make_grade("WI-001", "ACCEPTED_VERIFIED",
                        evidence=["tests/python/csv/test_csv_probe.py"]),
        ])

        close_gaps_from_grades(review, declaration, gl_path, "sprint-001")

        log_path = tmp_path / "gap-closure-log.json"
        assert log_path.exists()
        log = json.loads(log_path.read_text())
        assert len(log) == 1
        assert log[0]["gap_id"] == "GAP-CSV-FOSS-001"
        assert log[0]["sprint_id"] == "sprint-001"


class TestNoCloseOverclaimed:
    """Grade=OVERCLAIMED → gap stays open."""

    def test_gap_stays_open(self, tmp_path):
        gl_path = _write_ledger(tmp_path, [_make_gap("GAP-X")])
        declaration = _make_declaration([{
            "item_id": "WI-X", "gap_ledger_ref": "GAP-X",
            "status": "completed", "evidence_paths": [],
        }])
        review = _make_review([
            _make_grade("WI-X", "OVERCLAIMED", evidence=[]),
        ])

        result = close_gaps_from_grades(review, declaration, gl_path, "sprint-002")
        assert result["closed"] == 0
        assert json.loads(gl_path.read_text())["gaps"][0]["status"] == "open"


class TestNoCloseNoTestEvidence:
    """Grade=ACCEPTED but no test files in evidence → gap stays open."""

    def test_gap_stays_open(self, tmp_path):
        gl_path = _write_ledger(tmp_path, [_make_gap("GAP-Y")])
        declaration = _make_declaration([{
            "item_id": "WI-Y", "gap_ledger_ref": "GAP-Y",
            "status": "completed",
            "evidence_paths": ["src/python/csv/csv_parser.py"],
        }])
        review = _make_review([
            _make_grade("WI-Y", "ACCEPTED",
                        evidence=["src/python/csv/csv_parser.py"]),
        ])

        result = close_gaps_from_grades(review, declaration, gl_path, "sprint-003")
        assert result["closed"] == 0


class TestNoCloseTestFailures:
    """Grade=ACCEPTED but tests_failing > 0 → gap stays open."""

    def test_gap_stays_open(self, tmp_path):
        gl_path = _write_ledger(tmp_path, [_make_gap("GAP-Z")])
        declaration = _make_declaration([{
            "item_id": "WI-Z", "gap_ledger_ref": "GAP-Z",
            "status": "completed",
            "evidence_paths": ["tests/python/csv/test_x.py"],
        }])
        review = _make_review([
            _make_grade("WI-Z", "ACCEPTED_VERIFIED",
                        evidence=["tests/python/csv/test_x.py"],
                        tests_failing=2),
        ])

        result = close_gaps_from_grades(review, declaration, gl_path, "sprint-004")
        assert result["closed"] == 0


class TestAlreadyClosedNotDuplicated:
    """Gap already closed → no re-closure, no error."""

    def test_already_closed(self, tmp_path):
        gl_path = _write_ledger(tmp_path, [_make_gap("GAP-DONE", status="closed")])
        declaration = _make_declaration([{
            "item_id": "WI-DONE", "gap_ledger_ref": "GAP-DONE",
            "status": "completed",
            "evidence_paths": ["tests/python/csv/test_x.py"],
        }])
        review = _make_review([
            _make_grade("WI-DONE", "ACCEPTED_VERIFIED",
                        evidence=["tests/python/csv/test_x.py"]),
        ])

        result = close_gaps_from_grades(review, declaration, gl_path, "sprint-005")
        assert result["closed"] == 0
        assert result["skipped"] == 1


class TestIdempotentRerun:
    """Running closure twice with same data produces same result."""

    def test_idempotent(self, tmp_path):
        gl_path = _write_ledger(tmp_path, [_make_gap("GAP-IDEM")])
        declaration = _make_declaration([{
            "item_id": "WI-IDEM", "gap_ledger_ref": "GAP-IDEM",
            "status": "completed",
            "evidence_paths": ["tests/python/csv/test_x.py"],
        }])
        review = _make_review([
            _make_grade("WI-IDEM", "ACCEPTED_VERIFIED",
                        evidence=["tests/python/csv/test_x.py"]),
        ])

        r1 = close_gaps_from_grades(review, declaration, gl_path, "sprint-006")
        assert r1["closed"] == 1

        # Run again — gap already closed
        r2 = close_gaps_from_grades(review, declaration, gl_path, "sprint-006")
        assert r2["closed"] == 0
        assert r2["skipped"] == 1


class TestNoGapRefSkipped:
    """Item without gap_ledger_ref → no match."""

    def test_no_match(self, tmp_path):
        gl_path = _write_ledger(tmp_path, [_make_gap("GAP-ORPHAN")])
        declaration = _make_declaration([{
            "item_id": "WI-NOREF", "status": "completed",
            "evidence_paths": ["tests/python/csv/test_x.py"],
        }])
        review = _make_review([
            _make_grade("WI-NOREF", "ACCEPTED_VERIFIED",
                        evidence=["tests/python/csv/test_x.py"]),
        ])

        result = close_gaps_from_grades(review, declaration, gl_path, "sprint-007")
        assert result["matches"] == 0
        assert result["closed"] == 0


class TestMultipleGapsClosed:
    """3 items with different gap_refs → all 3 closed."""

    def test_three_closed(self, tmp_path):
        gaps = [_make_gap(f"GAP-MULTI-{i}") for i in range(3)]
        gl_path = _write_ledger(tmp_path, gaps)

        items = [
            {"item_id": f"WI-M{i}", "gap_ledger_ref": f"GAP-MULTI-{i}",
             "status": "completed",
             "evidence_paths": [f"tests/python/csv/test_m{i}.py"]}
            for i in range(3)
        ]
        grades = [
            _make_grade(f"WI-M{i}", "ACCEPTED_VERIFIED",
                        evidence=[f"tests/python/csv/test_m{i}.py"])
            for i in range(3)
        ]

        result = close_gaps_from_grades(
            _make_review(grades), _make_declaration(items), gl_path, "sprint-008"
        )
        assert result["closed"] == 3

        updated = json.loads(gl_path.read_text())
        assert all(g["status"] == "closed" for g in updated["gaps"])


class TestMixedGrades:
    """2 ACCEPTED + 1 OVERCLAIMED → only 2 closed."""

    def test_partial(self, tmp_path):
        gaps = [_make_gap(f"GAP-MIX-{i}") for i in range(3)]
        gl_path = _write_ledger(tmp_path, gaps)

        items = [
            {"item_id": f"WI-MIX-{i}", "gap_ledger_ref": f"GAP-MIX-{i}",
             "status": "completed",
             "evidence_paths": [f"tests/python/csv/test_mix{i}.py"]}
            for i in range(3)
        ]
        grades = [
            _make_grade("WI-MIX-0", "ACCEPTED_VERIFIED",
                        evidence=["tests/python/csv/test_mix0.py"]),
            _make_grade("WI-MIX-1", "ACCEPTED",
                        evidence=["tests/python/csv/test_mix1.py"]),
            _make_grade("WI-MIX-2", "OVERCLAIMED", evidence=[]),
        ]

        result = close_gaps_from_grades(
            _make_review(grades), _make_declaration(items), gl_path, "sprint-009"
        )
        assert result["closed"] == 2

        updated = json.loads(gl_path.read_text())
        statuses = {g["gap_id"]: g["status"] for g in updated["gaps"]}
        assert statuses["GAP-MIX-0"] == "closed"
        assert statuses["GAP-MIX-1"] == "closed"
        assert statuses["GAP-MIX-2"] == "open"


class TestEvaluateClosureCriteria:
    """Unit tests for _evaluate_closure_criteria."""

    def test_accepted_verified_with_test_evidence(self):
        grade = _make_grade("WI", "ACCEPTED_VERIFIED",
                            evidence=["tests/python/csv/test_x.py"])
        assert _evaluate_closure_criteria(grade, {}) is True

    def test_rework_required_rejected(self):
        grade = _make_grade("WI", "REWORK_REQUIRED",
                            evidence=["tests/python/csv/test_x.py"])
        assert _evaluate_closure_criteria(grade, {}) is False

    def test_no_test_files_rejected(self):
        grade = _make_grade("WI", "ACCEPTED_VERIFIED",
                            evidence=["src/python/csv/csv_parser.py"])
        assert _evaluate_closure_criteria(grade, {}) is False

    def test_with_failures_rejected(self):
        grade = _make_grade("WI", "ACCEPTED_VERIFIED",
                            evidence=["tests/python/csv/test_x.py"],
                            tests_failing=1)
        assert _evaluate_closure_criteria(grade, {}) is False


class TestMatchGradesToGaps:
    """Unit tests for _match_grades_to_gaps."""

    def test_match_via_gap_ledger_ref(self):
        review = _make_review([_make_grade("WI-1", "ACCEPTED")])
        decl = _make_declaration([{
            "item_id": "WI-1", "gap_ledger_ref": "GAP-A",
        }])
        matches = _match_grades_to_gaps(review, decl)
        assert len(matches) == 1
        assert matches[0][0] == "GAP-A"

    def test_match_via_gap_ref_fallback(self):
        review = _make_review([_make_grade("WI-2", "ACCEPTED")])
        decl = _make_declaration([{
            "item_id": "WI-2", "gap_ref": "GAP-B",
        }])
        matches = _match_grades_to_gaps(review, decl)
        assert len(matches) == 1
        assert matches[0][0] == "GAP-B"

    def test_no_ref_no_match(self):
        review = _make_review([_make_grade("WI-3", "ACCEPTED")])
        decl = _make_declaration([{"item_id": "WI-3"}])
        matches = _match_grades_to_gaps(review, decl)
        assert len(matches) == 0

    def test_no_grade_no_match(self):
        review = _make_review([])
        decl = _make_declaration([{
            "item_id": "WI-4", "gap_ledger_ref": "GAP-C",
        }])
        matches = _match_grades_to_gaps(review, decl)
        assert len(matches) == 0


# ── TC-BOOL-001 tests: close_implementation_verified_gaps ─────────────────────

def _make_impl_gap(gap_id: str, cap_id: str, current_state: str = "implementation_verified") -> dict:
    return {
        "gap_id": gap_id,
        "status": "open",
        "current_state": current_state,
        "related_capability_id": cap_id,
        "format": "DIF",
        "priority": "P1",
    }


class TestCloseImplVerifiedHappyPath:
    """TC-BOOL-001 test 1: happy path — gap closed when test file exists."""

    def test_gap_closed(self, tmp_path):
        gl_path = _write_ledger(tmp_path, [
            _make_impl_gap("GAP-DIF-FOSS-DIF_BOOLEAN_-001", "DIF-FOSS-DIF_BOOLEAN_CELL_COUNT-SRC-001"),
        ])
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_dif.py").write_text("def test_x():\n    dif_boolean_cell_count(data)\n")

        result = close_implementation_verified_gaps(gl_path, test_dir, sprint_id="test-sprint")

        assert result["closed"] == 1
        assert result["no_tests_found"] == 0
        ledger = json.loads(gl_path.read_text())
        gap = ledger["gaps"][0]
        assert gap["status"] == "closed"
        assert gap["closure_method"] == "implementation_verified_test_scan"


class TestCloseImplVerifiedNoTestFound:
    """TC-BOOL-001 test 2: no test file → promoted to implementation_verified_no_tests."""

    def test_promoted(self, tmp_path):
        gl_path = _write_ledger(tmp_path, [
            _make_impl_gap("GAP-DIF-001", "DIF-FOSS-DIF_SPECIAL_-001"),
        ])
        test_dir = tmp_path / "tests"
        test_dir.mkdir()  # Empty test dir — no matching files

        result = close_implementation_verified_gaps(gl_path, test_dir, sprint_id="test-sprint")

        assert result["closed"] == 0
        assert result["no_tests_found"] == 1
        ledger = json.loads(gl_path.read_text())
        gap = ledger["gaps"][0]
        assert gap["status"] == "open"
        assert gap["current_state"] == "implementation_verified_no_tests"


class TestCloseImplVerifiedAlreadyClosed:
    """TC-BOOL-001 test 3: already-closed gap is not re-processed."""

    def test_skipped(self, tmp_path):
        gap = _make_impl_gap("GAP-DIF-CLOSED", "DIF-FOSS-DIF_BOOLEAN_-001")
        gap["status"] = "closed"
        gl_path = _write_ledger(tmp_path, [gap])
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_dif.py").write_text("dif_boolean_cell_count(x)\n")

        result = close_implementation_verified_gaps(gl_path, test_dir, sprint_id="test-sprint")

        assert result["closed"] == 0  # Already closed, not re-processed


class TestCloseImplVerifiedClosureMethod:
    """TC-BOOL-001 test 4: closure_method field set correctly."""

    def test_closure_method(self, tmp_path):
        gl_path = _write_ledger(tmp_path, [
            _make_impl_gap("GAP-DIF-002", "DIF-FOSS-DIF_DECLARED-001"),
        ])
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_dif2.py").write_text("result = dif_declared(doc)\n")

        close_implementation_verified_gaps(gl_path, test_dir, sprint_id="test-sprint")

        ledger = json.loads(gl_path.read_text())
        assert ledger["gaps"][0]["closure_method"] == "implementation_verified_test_scan"


class TestCloseImplVerifiedCommentOnlyNoClose:
    """TC-BOOL-001 test 5: comment-only reference does not close gap."""

    def test_comment_not_counted(self, tmp_path):
        gl_path = _write_ledger(tmp_path, [
            _make_impl_gap("GAP-DIF-003", "DIF-FOSS-DIF_COMMENT_-001"),
        ])
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        # Only a comment reference — should NOT close
        (test_dir / "test_comment.py").write_text("# dif_comment_ is tested elsewhere\n")

        result = close_implementation_verified_gaps(gl_path, test_dir, sprint_id="test-sprint")

        assert result["closed"] == 0
        assert result["no_tests_found"] == 1


class TestSkipStatusesRegression:
    """TC-BOOL-001 test 6: assert implementation_verified not in _SKIP_STATUSES after fix."""

    def test_skip_statuses_correct(self):
        import importlib
        # We test the compiler
        import sys
        repo = Path(__file__).resolve().parents[2]
        if str(repo / "tools" / "supervisor") not in sys.path:
            sys.path.insert(0, str(repo / "tools" / "supervisor"))
        import capability_feature_compiler as cfc
        assert "implementation_verified" not in cfc._SKIP_STATUSES, (
            "implementation_verified must NOT be in _SKIP_STATUSES after TC-BOOL-003 fix"
        )
        assert "implementation_verified_no_tests" in cfc._SKIP_STATUSES, (
            "implementation_verified_no_tests must be in _SKIP_STATUSES after TC-BOOL-003 fix"
        )
