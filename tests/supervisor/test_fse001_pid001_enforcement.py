"""Tests for FSE-001/PID-001 enforcement — auto-repair + warning propagation.

TC-FL-006: Phase 2 of the feedback loop redesign (pure-knitting-dusk plan).
Tests the public check_fix_sprint_evidence and check_parent_id_evidence_tagging
functions from sprint_executor_validate.py.
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from sprint_executor_validate import (
    check_fix_sprint_evidence,
    check_parent_id_evidence_tagging,
)


# ── FSE-001 Tests ─────────────────────────────────────────────────────────────

class TestFSE001:
    """FSE-001: test files in changed_files but not evidence_paths."""

    def test_warning_when_test_file_missing_from_evidence(self):
        doc = {
            "changed_files": [
                "src/python/csv/csv_parser.py",
                "tests/python/csv/test_csv_probe.py",
            ],
            "planned_work_items": [{
                "item_id": "WI-1",
                "evidence_paths": ["src/python/csv/csv_parser.py"],
            }],
        }
        warnings = check_fix_sprint_evidence(doc)
        assert len(warnings) == 1
        assert "FSE-001" in warnings[0]
        assert "test_csv_probe.py" in warnings[0]

    def test_no_warning_when_test_file_in_evidence(self):
        doc = {
            "changed_files": [
                "src/python/csv/csv_parser.py",
                "tests/python/csv/test_csv_probe.py",
            ],
            "planned_work_items": [{
                "item_id": "WI-1",
                "evidence_paths": [
                    "src/python/csv/csv_parser.py",
                    "tests/python/csv/test_csv_probe.py",
                ],
            }],
        }
        warnings = check_fix_sprint_evidence(doc)
        assert len(warnings) == 0

    def test_no_warning_when_no_test_files_changed(self):
        doc = {
            "changed_files": ["src/python/csv/csv_parser.py"],
            "planned_work_items": [{
                "item_id": "WI-1",
                "evidence_paths": ["src/python/csv/csv_parser.py"],
            }],
        }
        warnings = check_fix_sprint_evidence(doc)
        assert len(warnings) == 0

    def test_multiple_missing_test_files(self):
        doc = {
            "changed_files": [
                "tests/python/csv/test_a.py",
                "tests/python/csv/test_b.py",
            ],
            "planned_work_items": [{
                "item_id": "WI-1",
                "evidence_paths": [],
            }],
        }
        warnings = check_fix_sprint_evidence(doc)
        assert len(warnings) == 2

    def test_empty_changed_files(self):
        doc = {
            "changed_files": [],
            "planned_work_items": [{
                "item_id": "WI-1",
                "evidence_paths": [],
            }],
        }
        warnings = check_fix_sprint_evidence(doc)
        assert len(warnings) == 0

    def test_test_file_in_one_item_not_another(self):
        """Test file covered by any item should not warn."""
        doc = {
            "changed_files": ["tests/python/csv/test_a.py"],
            "planned_work_items": [
                {"item_id": "WI-1", "evidence_paths": []},
                {"item_id": "WI-2", "evidence_paths": ["tests/python/csv/test_a.py"]},
            ],
        }
        warnings = check_fix_sprint_evidence(doc)
        assert len(warnings) == 0


# ── PID-001 Tests ─────────────────────────────────────────────────────────────

class TestPID001:
    """PID-001: parent items with status=completed but no evidence_paths."""

    def test_warning_completed_no_evidence(self):
        doc = {
            "planned_work_items": [{
                "item_id": "PARENT-1",
                "status": "completed",
                "evidence_paths": [],
            }],
        }
        warnings = check_parent_id_evidence_tagging(doc)
        assert len(warnings) == 1
        assert "PARENT-ID" in warnings[0]
        assert "PARENT-1" in warnings[0]

    def test_no_warning_completed_with_evidence(self):
        doc = {
            "planned_work_items": [{
                "item_id": "PARENT-1",
                "status": "completed",
                "evidence_paths": ["tests/test_something.py"],
            }],
        }
        warnings = check_parent_id_evidence_tagging(doc)
        assert len(warnings) == 0

    def test_no_warning_partial_no_evidence(self):
        """Partial status should not trigger PID-001."""
        doc = {
            "planned_work_items": [{
                "item_id": "WI-1",
                "status": "partial",
                "evidence_paths": [],
            }],
        }
        warnings = check_parent_id_evidence_tagging(doc)
        assert len(warnings) == 0

    def test_no_warning_not_started_no_evidence(self):
        doc = {
            "planned_work_items": [{
                "item_id": "WI-1",
                "status": "not_started",
                "evidence_paths": [],
            }],
        }
        warnings = check_parent_id_evidence_tagging(doc)
        assert len(warnings) == 0

    def test_warning_none_evidence_paths(self):
        """evidence_paths=None should trigger warning for completed items."""
        doc = {
            "planned_work_items": [{
                "item_id": "WI-NULL",
                "status": "completed",
                "evidence_paths": None,
            }],
        }
        warnings = check_parent_id_evidence_tagging(doc)
        assert len(warnings) == 1

    def test_multiple_items_mixed(self):
        doc = {
            "planned_work_items": [
                {"item_id": "WI-OK", "status": "completed",
                 "evidence_paths": ["tests/test_x.py"]},
                {"item_id": "WI-BAD", "status": "completed",
                 "evidence_paths": []},
                {"item_id": "WI-PARTIAL", "status": "partial",
                 "evidence_paths": []},
            ],
        }
        warnings = check_parent_id_evidence_tagging(doc)
        assert len(warnings) == 1
        assert "WI-BAD" in warnings[0]


# ── Backward Compat Tests ────────────────────────────────────────────────────

class TestBackwardCompat:
    """Verify underscore-prefixed aliases still work."""

    def test_fse_alias_exists(self):
        from sprint_executor_validate import _check_fix_sprint_evidence
        assert _check_fix_sprint_evidence is check_fix_sprint_evidence

    def test_pid_alias_exists(self):
        from sprint_executor_validate import _check_parent_id_evidence_tagging
        assert _check_parent_id_evidence_tagging is check_parent_id_evidence_tagging
