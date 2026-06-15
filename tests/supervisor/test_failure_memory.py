"""Tests for HEAL-RECT-001: failure_memory.py — persistent failure memory store.

Validates:
  - Failure recording with category/root_cause
  - Duplicate detection and count increment
  - Escalation at threshold (3+ occurrences)
  - Save/load roundtrip
  - Query functions (find_duplicates, find_by_category, find_unresolved, etc.)
  - Mark resolved
"""

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from failure_memory import FailureMemory, VALID_CATEGORIES, ESCALATION_THRESHOLD


class TestFailureMemoryRecord:
    def test_record_single_failure(self, tmp_path):
        fm = FailureMemory(tmp_path)
        entry = fm.record_failure(
            category="EVIDENCE_DECLARATION_FAILURE",
            root_cause="missing_type_field",
            correction="added type to evidence_artifacts",
            sprint_id="TEST-001",
        )
        assert entry["id"] == "FM-0001"
        assert entry["category"] == "EVIDENCE_DECLARATION_FAILURE"
        assert entry["root_cause"] == "missing_type_field"
        assert entry["occurrence_count"] == 1
        assert entry["escalated"] is False
        assert len(fm.entries) == 1

    def test_duplicate_increments_count(self, tmp_path):
        fm = FailureMemory(tmp_path)
        fm.record_failure("SCHEMA_VALIDATION_FAILURE", "missing_type_field", sprint_id="S1")
        fm.record_failure("SCHEMA_VALIDATION_FAILURE", "missing_type_field", sprint_id="S2")
        assert len(fm.entries) == 1
        assert fm.entries[0]["occurrence_count"] == 2
        assert fm.entries[0]["last_seen_sprint"] == "S2"

    def test_escalation_at_threshold(self, tmp_path):
        fm = FailureMemory(tmp_path)
        for i in range(ESCALATION_THRESHOLD):
            fm.record_failure("IMPORT_COLLISION", "csv_stdlib", sprint_id=f"S{i}")
        assert fm.entries[0]["occurrence_count"] == ESCALATION_THRESHOLD
        assert fm.entries[0]["escalated"] is True

    def test_different_root_causes_separate_entries(self, tmp_path):
        fm = FailureMemory(tmp_path)
        fm.record_failure("API_SIGNATURE_MISMATCH", "wrong_arg_count")
        fm.record_failure("API_SIGNATURE_MISMATCH", "wrong_return_type")
        assert len(fm.entries) == 2

    def test_invalid_category_defaults_to_other(self, tmp_path):
        fm = FailureMemory(tmp_path)
        entry = fm.record_failure("NONEXISTENT_CATEGORY", "some_cause")
        assert entry["category"] == "OTHER"


class TestFailureMemorySaveLoad:
    def test_save_creates_file(self, tmp_path):
        fm = FailureMemory(tmp_path)
        fm.record_failure("OVERCLAIM_FAILURE", "helpers_only", sprint_id="T1")
        path = fm.save()
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["schema_version"] == "1.0"
        assert data["failure_count"] == 1
        assert len(data["failures"]) == 1

    def test_load_roundtrip(self, tmp_path):
        fm1 = FailureMemory(tmp_path)
        fm1.record_failure("STALE_STATE_FAILURE", "signal_expired", sprint_id="T1")
        fm1.record_failure("STALE_STATE_FAILURE", "signal_expired", sprint_id="T2")
        fm1.save()

        fm2 = FailureMemory(tmp_path)
        assert len(fm2.entries) == 1
        assert fm2.entries[0]["occurrence_count"] == 2

    def test_load_missing_file(self, tmp_path):
        fm = FailureMemory(tmp_path)
        assert len(fm.entries) == 0


class TestFailureMemoryQuery:
    def test_find_duplicates(self, tmp_path):
        fm = FailureMemory(tmp_path)
        for i in range(4):
            fm.record_failure("IMPORT_COLLISION", "csv", sprint_id=f"S{i}")
        fm.record_failure("API_SIGNATURE_MISMATCH", "other")
        dups = fm.find_duplicates(threshold=3)
        assert len(dups) == 1
        assert dups[0]["category"] == "IMPORT_COLLISION"

    def test_find_by_category(self, tmp_path):
        fm = FailureMemory(tmp_path)
        fm.record_failure("OVERCLAIM_FAILURE", "a")
        fm.record_failure("OVERCLAIM_FAILURE", "b")
        fm.record_failure("STALE_STATE_FAILURE", "c")
        results = fm.find_by_category("OVERCLAIM_FAILURE")
        assert len(results) == 2

    def test_find_unresolved(self, tmp_path):
        fm = FailureMemory(tmp_path)
        fm.record_failure("OVERCLAIM_FAILURE", "a")
        fm.record_failure("STALE_STATE_FAILURE", "b")
        fm.mark_resolved("FM-0001", "fixed")
        unresolved = fm.find_unresolved()
        assert len(unresolved) == 1
        assert unresolved[0]["id"] == "FM-0002"

    def test_find_escalated(self, tmp_path):
        fm = FailureMemory(tmp_path)
        for i in range(3):
            fm.record_failure("IMPORT_COLLISION", "csv", sprint_id=f"S{i}")
        fm.record_failure("OTHER", "something")
        escalated = fm.find_escalated()
        assert len(escalated) == 1

    def test_summary(self, tmp_path):
        fm = FailureMemory(tmp_path)
        fm.record_failure("OVERCLAIM_FAILURE", "a")
        fm.record_failure("STALE_STATE_FAILURE", "b")
        s = fm.summary()
        assert s["total"] == 2
        assert s["unresolved"] == 2
        assert s["escalated"] == 0
        assert s["by_category"]["OVERCLAIM_FAILURE"] == 1


class TestFailureMemoryMarkResolved:
    def test_mark_resolved(self, tmp_path):
        fm = FailureMemory(tmp_path)
        fm.record_failure("OVERCLAIM_FAILURE", "a")
        ok = fm.mark_resolved("FM-0001", "fixed in sprint X")
        assert ok is True
        assert fm.entries[0]["resolved"] is True
        assert fm.entries[0]["resolution"] == "fixed in sprint X"

    def test_mark_resolved_nonexistent(self, tmp_path):
        fm = FailureMemory(tmp_path)
        ok = fm.mark_resolved("FM-9999")
        assert ok is False


class TestValidCategories:
    def test_categories_exist(self):
        assert len(VALID_CATEGORIES) >= 20
        assert "EVIDENCE_DECLARATION_FAILURE" in VALID_CATEGORIES
        assert "OVERCLAIM_FAILURE" in VALID_CATEGORIES
        assert "IMPORT_COLLISION" in VALID_CATEGORIES
        assert "OTHER" in VALID_CATEGORIES
