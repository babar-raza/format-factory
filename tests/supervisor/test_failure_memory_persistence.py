import sys
import json
import tempfile
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from failure_memory import FailureMemory


class TestFailureMemoryPersistence:
    def test_record_and_save(self, tmp_path):
        fm = FailureMemory(tmp_path, store_path=".local/test-fm.json")
        fm.record_failure(
            category="GOVERNANCE_FALSE_TRIGGER",
            root_cause="test_root_cause",
            sprint_id="TEST-001",
        )
        fm.save()
        assert (tmp_path / ".local" / "test-fm.json").exists()
        data = json.loads((tmp_path / ".local" / "test-fm.json").read_text())
        assert data["failure_count"] == 1

    def test_duplicate_increments_count(self, tmp_path):
        fm = FailureMemory(tmp_path, store_path=".local/test-fm.json")
        fm.record_failure(category="OVERCLAIM_FAILURE", root_cause="dup_test", sprint_id="S1")
        fm.record_failure(category="OVERCLAIM_FAILURE", root_cause="dup_test", sprint_id="S2")
        assert fm.entries[0]["occurrence_count"] == 2

    def test_escalation_at_threshold(self, tmp_path):
        fm = FailureMemory(tmp_path, store_path=".local/test-fm.json")
        for i in range(3):
            fm.record_failure(category="STALE_STATE_FAILURE", root_cause="esc_test", sprint_id=f"S{i}")
        assert fm.entries[0]["escalated"] is True

    def test_find_unresolved(self, tmp_path):
        fm = FailureMemory(tmp_path, store_path=".local/test-fm.json")
        fm.record_failure(category="OVERCLAIM_FAILURE", root_cause="r1", sprint_id="S1")
        fm.record_failure(category="STALE_STATE_FAILURE", root_cause="r2", sprint_id="S1")
        fm.mark_resolved("FM-0001", "fixed")
        assert len(fm.find_unresolved()) == 1

    def test_reload_from_disk(self, tmp_path):
        fm = FailureMemory(tmp_path, store_path=".local/test-fm.json")
        fm.record_failure(category="SCHEMA_VALIDATION_FAILURE", root_cause="reload_test", sprint_id="S1")
        fm.save()
        fm2 = FailureMemory(tmp_path, store_path=".local/test-fm.json")
        assert len(fm2.entries) == 1
        assert fm2.entries[0]["root_cause"] == "reload_test"

    def test_generated_repair_taskcard(self, tmp_path):
        """Escalated failure should be suitable for repair taskcard generation."""
        fm = FailureMemory(tmp_path, store_path=".local/test-fm.json")
        for i in range(4):
            fm.record_failure(
                category="IMPLEMENTATION_DEPTH_FAILURE",
                root_cause="shallow_product_code",
                correction="add behavior tests",
                sprint_id=f"S{i}",
            )
        escalated = fm.find_escalated()
        assert len(escalated) == 1
        e = escalated[0]
        taskcard = {
            "id": f"REPAIR-{e['id']}",
            "title": f"Repair: {e['root_cause']}",
            "category": e["category"],
            "priority": "P0" if e["occurrence_count"] >= 5 else "P1",
            "correction": e.get("correction", ""),
        }
        assert taskcard["priority"] == "P1"
        assert taskcard["correction"] == "add behavior tests"
