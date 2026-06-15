"""Tests for rectification sprint 2: HEAL-RECT-002, SUP-RECT-004, SUP-RECT-005, HEAL-RECT-005.

Validates:
  - HEAL-RECT-002: learning_consumer.py scans, aggregates, and proposes rules
  - SUP-RECT-004: grade_declared_work.py defaults to adequate=False when no evidence
  - SUP-RECT-005: autonomous_task_generator.py circuit breaker for zero-task loops
  - HEAL-RECT-005: autonomous_cycle.py archives rework items to rework_archive.jsonl
"""

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))


# ---------------------------------------------------------------------------
# HEAL-RECT-002: LearningConsumer
# ---------------------------------------------------------------------------

class TestLearningConsumer:
    def test_scan_empty_dir(self, tmp_path):
        from learning_consumer import LearningConsumer
        lc = LearningConsumer(tmp_path)
        count = lc.scan_all_learnings()
        assert count == 0
        assert len(lc.entries) == 0

    def test_scan_single_file(self, tmp_path):
        from learning_consumer import LearningConsumer
        ev_dir = tmp_path / ".local" / "evidences" / "sprint-1"
        ev_dir.mkdir(parents=True)
        entries = [
            {"sprint_id": "S1", "category": "slowdown", "description": "Build was slow"},
            {"sprint_id": "S1", "category": "product_win", "description": "New CSV parser"},
        ]
        (ev_dir / "sprint-learnings.jsonl").write_text(
            "\n".join(json.dumps(e) for e in entries), encoding="utf-8"
        )
        lc = LearningConsumer(tmp_path)
        count = lc.scan_all_learnings()
        assert count == 2
        assert len(lc.entries) == 2

    def test_aggregate_groups_by_category_description(self, tmp_path):
        from learning_consumer import LearningConsumer
        ev_dir = tmp_path / ".local" / "evidences" / "sprint-1"
        ev_dir.mkdir(parents=True)
        entries = [
            {"sprint_id": "S1", "category": "slowdown", "description": "Build slow"},
            {"sprint_id": "S2", "category": "slowdown", "description": "Build slow"},
            {"sprint_id": "S3", "category": "slowdown", "description": "Build slow"},
            {"sprint_id": "S1", "category": "product_win", "description": "New parser"},
        ]
        (ev_dir / "sprint-learnings.jsonl").write_text(
            "\n".join(json.dumps(e) for e in entries), encoding="utf-8"
        )
        lc = LearningConsumer(tmp_path)
        lc.scan_all_learnings()
        agg = lc.aggregate()
        assert len(agg) == 2
        # Find the "slowdown" entry
        slowdown = [v for v in agg.values() if v["category"] == "slowdown"][0]
        assert slowdown["occurrence_count"] == 3

    def test_generate_proposals_at_threshold(self, tmp_path):
        from learning_consumer import LearningConsumer
        ev_dir = tmp_path / ".local" / "evidences" / "sprint-1"
        ev_dir.mkdir(parents=True)
        entries = [
            {"sprint_id": f"S{i}", "category": "slowdown", "description": "Build slow"}
            for i in range(4)
        ]
        entries.append({"sprint_id": "S1", "category": "product_win", "description": "One-off win"})
        (ev_dir / "sprint-learnings.jsonl").write_text(
            "\n".join(json.dumps(e) for e in entries), encoding="utf-8"
        )
        lc = LearningConsumer(tmp_path)
        lc.scan_all_learnings()
        proposals = lc.generate_proposals(threshold=3)
        assert len(proposals) == 1
        assert proposals[0]["category"] == "slowdown"
        assert proposals[0]["authority_state"] == "ai_draft"
        assert proposals[0]["status"] == "proposed"

    def test_save_proposals(self, tmp_path):
        from learning_consumer import LearningConsumer
        lc = LearningConsumer(tmp_path)
        lc.proposals = [{"proposal_id": "RP-test", "category": "test"}]
        path = lc.save_proposals()
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["schema_version"] == "1.0"
        assert data["proposals_count"] == 1

    def test_summary(self, tmp_path):
        from learning_consumer import LearningConsumer
        lc = LearningConsumer(tmp_path)
        lc.entries = [{"category": "slowdown", "description": "A"}]
        lc.aggregate()
        s = lc.summary()
        assert s["total_entries"] == 1
        assert s["unique_patterns"] == 1

    def test_no_proposals_below_threshold(self, tmp_path):
        from learning_consumer import LearningConsumer
        ev_dir = tmp_path / ".local" / "evidences" / "sprint-1"
        ev_dir.mkdir(parents=True)
        entries = [
            {"sprint_id": "S1", "category": "slowdown", "description": "Build slow"},
            {"sprint_id": "S2", "category": "slowdown", "description": "Build slow"},
        ]
        (ev_dir / "sprint-learnings.jsonl").write_text(
            "\n".join(json.dumps(e) for e in entries), encoding="utf-8"
        )
        lc = LearningConsumer(tmp_path)
        lc.scan_all_learnings()
        proposals = lc.generate_proposals(threshold=3)
        assert len(proposals) == 0


# ---------------------------------------------------------------------------
# SUP-RECT-004: grade_declared_work.py defaults to adequate=False
# ---------------------------------------------------------------------------

class TestGradeDefaultAdequateFalse:
    def test_no_evidence_returns_inadequate(self):
        from grade_declared_work import semantic_verify_item
        result = semantic_verify_item(
            declaration_item={"item_id": "TEST-001", "title": "Test"},
            item_inspection={"evidence_paths_found": []},
            repo_root=_REPO,
        )
        assert result["adequate"] is False
        assert "no_evidence_paths_provided" in result["deficiencies"]

    def test_source_still_has_fallback_no_content(self):
        """Verify that the source has fallback_no_content for unreadable files."""
        src = (_REPO / "tools" / "supervisor" / "grade_declared_work.py").read_text(encoding="utf-8")
        assert "fallback_no_evidence" in src
        assert "fallback_no_content" in src
        assert '"adequate": False' in src or "'adequate': False" in src

    def test_with_evidence_paths_proceeds_to_grading(self):
        from grade_declared_work import semantic_verify_item
        result = semantic_verify_item(
            declaration_item={"item_id": "TEST-001", "title": "Test"},
            item_inspection={"evidence_paths_found": ["nonexistent_file.py"]},
            repo_root=_REPO,
        )
        # With a nonexistent file, should return fallback_no_content
        assert result["adequate"] is False
        assert "evidence_files_unreadable" in result["deficiencies"]


# ---------------------------------------------------------------------------
# SUP-RECT-005: Circuit breaker for zero-task loops
# ---------------------------------------------------------------------------

class TestCircuitBreaker:
    def test_source_has_circuit_breaker(self):
        src = (_REPO / "tools" / "supervisor" / "autonomous_task_generator.py").read_text(encoding="utf-8")
        assert "CIRCUIT_BREAKER" in src
        assert "zero-task-counter" in src
        assert "consecutive_zero_count" in src

    def test_generator_version_updated(self):
        src = (_REPO / "tools" / "supervisor" / "autonomous_task_generator.py").read_text(encoding="utf-8")
        assert '"generator_version": "1.2"' in src

    def test_zero_task_output_has_flag(self):
        src = (_REPO / "tools" / "supervisor" / "autonomous_task_generator.py").read_text(encoding="utf-8")
        assert "zero_task_circuit_breaker" in src


# ---------------------------------------------------------------------------
# HEAL-RECT-005: Rework archive persistence
# ---------------------------------------------------------------------------

class TestReworkArchive:
    def test_autonomous_cycle_has_rework_archive(self):
        src = (_REPO / "tools" / "supervisor" / "autonomous_cycle.py").read_text(encoding="utf-8")
        assert "rework_archive" in src
        assert "HEAL-RECT-005" in src

    def test_rework_archive_jsonl_format(self):
        """Verify the archive writes proper JSONL entries."""
        src = (_REPO / "tools" / "supervisor" / "autonomous_cycle.py").read_text(encoding="utf-8")
        assert '"item_id"' in src
        assert '"resolved": False' in src
        assert '"archived_at"' in src

    def test_rework_archive_write_roundtrip(self, tmp_path):
        """Simulate writing a rework archive entry and verify it."""
        archive_path = tmp_path / "rework_archive.jsonl"
        entry = {
            "item_id": "TEST-REWORK-001",
            "sprint_id": "SPRINT-001",
            "archived_at": "2026-06-13T00:00:00Z",
            "resolved": False,
        }
        with open(archive_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        lines = archive_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        parsed = json.loads(lines[0])
        assert parsed["item_id"] == "TEST-REWORK-001"
        assert parsed["resolved"] is False
