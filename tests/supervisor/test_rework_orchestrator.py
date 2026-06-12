"""
tests/supervisor/test_rework_orchestrator.py
Tests for tools/supervisor/rework_orchestrator.py

Sprint: FORMAT-FACTORY-SELF-HEALING-QUEUE-PROFESSIONALIZE-RNEXT-001
Lane: L1-healing-loop

Covers:
- StaleQueueDetector: load_queue, function_exists_in_source, detect_stale
- ReworkOrchestrator: detect, classify, create_repair_taskcard, execute_repair,
  verify_repair, check_idempotency, run_cycle
- Pre-repair: stale items detected as STALE_QUEUE_ITEM
- Repair: items marked done, no source mutation
- Post-repair: verification confirms repair (item no longer pending)
- Idempotency: second cycle produces no new stale items for repaired IDs
- Stop condition: CAPABILITY_GAP items block auto-repair
- Dry-run mode: detects and classifies without mutating queue
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from tools.supervisor.rework_orchestrator import (
    DefectClass,
    DetectedDefect,
    QueueItem,
    ReworkOrchestrator,
    StaleQueueDetector,
    run_healing_cycle,
)


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

STALE_QUEUE_JSONL = """\
{"action_id": "test-stale-001", "action_type": "PRODUCT_SOURCE_PATCH_BOUNDED", "target_path": "src/python/abw/abw_codec.py", "status": "pending", "priority": 1, "function_name": "search_text", "description": "Add search_text", "sprint_id": "TEST-SPRINT", "queued_at": "2026-01-01T00:00:00Z", "stream": "product"}
{"action_id": "test-real-gap-002", "action_type": "PRODUCT_SOURCE_PATCH_BOUNDED", "target_path": "src/python/abw/abw_codec.py", "status": "pending", "priority": 2, "function_name": "nonexistent_function_xyz", "description": "Add nonexistent_function_xyz", "sprint_id": "TEST-SPRINT", "queued_at": "2026-01-01T00:00:00Z", "stream": "product"}
{"action_id": "test-done-003", "action_type": "PRODUCT_SOURCE_PATCH_BOUNDED", "target_path": "src/python/gnumeric/gnumeric_codec.py", "status": "done", "priority": 3, "function_name": "rename_sheet", "description": "Already done", "sprint_id": "TEST-SPRINT", "queued_at": "2026-01-01T00:00:00Z", "stream": "product"}
"""

STALE_ONLY_QUEUE_JSONL = """\
{"action_id": "stale-only-001", "action_type": "PRODUCT_SOURCE_PATCH_BOUNDED", "target_path": "src/python/gnumeric/gnumeric_codec.py", "status": "pending", "priority": 1, "function_name": "rename_sheet", "description": "Add rename_sheet", "sprint_id": "TEST-SPRINT", "queued_at": "2026-01-01T00:00:00Z", "stream": "product"}
{"action_id": "stale-only-002", "action_type": "PRODUCT_SOURCE_PATCH_BOUNDED", "target_path": "src/python/ndjson/ndjson_codec.py", "status": "pending", "priority": 2, "function_name": "count_records", "description": "Add count_records", "sprint_id": "TEST-SPRINT", "queued_at": "2026-01-01T00:00:00Z", "stream": "product"}
"""

SAMPLE_SOURCE = """\
def search_text(model, query):
    \"\"\"Search paragraphs.\"\"\"
    results = []
    for i, para in enumerate(model.get("paragraphs", [])):
        if query in para:
            results.append(i)
    return results

def get_paragraph(model, index):
    return model["paragraphs"][index]
"""


@pytest.fixture
def tmp_repo(tmp_path: Path) -> Path:
    """Create a minimal fake repo structure."""
    # Source files
    abw_dir = tmp_path / "src" / "python" / "abw"
    abw_dir.mkdir(parents=True)
    (abw_dir / "abw_codec.py").write_text(SAMPLE_SOURCE, encoding="utf-8")

    # Queue
    local_sup = tmp_path / ".local" / "supervisor"
    local_sup.mkdir(parents=True)
    (local_sup / "action-queue.jsonl").write_text(STALE_QUEUE_JSONL, encoding="utf-8")

    return tmp_path


@pytest.fixture
def stale_only_repo(tmp_path: Path) -> Path:
    """Repo with only stale queue items (all functions already exist in source)."""
    # Gnumeric source with rename_sheet
    gnumeric_dir = tmp_path / "src" / "python" / "gnumeric"
    gnumeric_dir.mkdir(parents=True)
    (gnumeric_dir / "gnumeric_codec.py").write_text(
        "def rename_sheet(model, index, new_name):\n    pass\n",
        encoding="utf-8",
    )

    # NDJSON source with count_records
    ndjson_dir = tmp_path / "src" / "python" / "ndjson"
    ndjson_dir.mkdir(parents=True)
    (ndjson_dir / "ndjson_codec.py").write_text(
        "def count_records(source):\n    pass\n",
        encoding="utf-8",
    )

    local_sup = tmp_path / ".local" / "supervisor"
    local_sup.mkdir(parents=True)
    (local_sup / "action-queue.jsonl").write_text(STALE_ONLY_QUEUE_JSONL, encoding="utf-8")

    return tmp_path


@pytest.fixture
def empty_queue_repo(tmp_path: Path) -> Path:
    """Repo with an empty queue."""
    local_sup = tmp_path / ".local" / "supervisor"
    local_sup.mkdir(parents=True)
    (local_sup / "action-queue.jsonl").write_text("", encoding="utf-8")
    return tmp_path


# ---------------------------------------------------------------------------
# Test: StaleQueueDetector.load_queue
# ---------------------------------------------------------------------------


class TestStaleQueueDetector:
    def test_load_queue_returns_items(self, tmp_repo: Path) -> None:
        detector = StaleQueueDetector(
            queue_path=tmp_repo / ".local" / "supervisor" / "action-queue.jsonl",
            repo_root=tmp_repo,
        )
        items = detector.load_queue()
        assert len(items) >= 1

    def test_load_queue_parses_action_id(self, tmp_repo: Path) -> None:
        detector = StaleQueueDetector(
            queue_path=tmp_repo / ".local" / "supervisor" / "action-queue.jsonl",
            repo_root=tmp_repo,
        )
        items = detector.load_queue()
        ids = [i.action_id for i in items]
        assert "test-stale-001" in ids

    def test_load_queue_empty_file(self, empty_queue_repo: Path) -> None:
        detector = StaleQueueDetector(
            queue_path=empty_queue_repo / ".local" / "supervisor" / "action-queue.jsonl",
            repo_root=empty_queue_repo,
        )
        items = detector.load_queue()
        assert items == []

    def test_load_queue_missing_file(self, tmp_path: Path) -> None:
        detector = StaleQueueDetector(
            queue_path=tmp_path / "nonexistent.jsonl",
            repo_root=tmp_path,
        )
        items = detector.load_queue()
        assert items == []

    def test_function_exists_in_source_true(self, tmp_repo: Path) -> None:
        detector = StaleQueueDetector(
            queue_path=tmp_repo / ".local" / "supervisor" / "action-queue.jsonl",
            repo_root=tmp_repo,
        )
        assert detector.function_exists_in_source(
            "src/python/abw/abw_codec.py", "search_text"
        )

    def test_function_exists_in_source_false(self, tmp_repo: Path) -> None:
        detector = StaleQueueDetector(
            queue_path=tmp_repo / ".local" / "supervisor" / "action-queue.jsonl",
            repo_root=tmp_repo,
        )
        assert not detector.function_exists_in_source(
            "src/python/abw/abw_codec.py", "nonexistent_function_xyz"
        )

    def test_function_exists_missing_source_file(self, tmp_repo: Path) -> None:
        detector = StaleQueueDetector(
            queue_path=tmp_repo / ".local" / "supervisor" / "action-queue.jsonl",
            repo_root=tmp_repo,
        )
        assert not detector.function_exists_in_source(
            "src/python/notreal/notreal_codec.py", "some_func"
        )

    def test_detect_stale_returns_stale_items(self, tmp_repo: Path) -> None:
        """search_text exists in source → test-stale-001 is stale."""
        detector = StaleQueueDetector(
            queue_path=tmp_repo / ".local" / "supervisor" / "action-queue.jsonl",
            repo_root=tmp_repo,
        )
        defects = detector.detect_stale()
        stale = [d for d in defects if d.defect_class == DefectClass.STALE_QUEUE_ITEM]
        assert any(d.queue_item.action_id == "test-stale-001" for d in stale)

    def test_detect_stale_skips_done_items(self, tmp_repo: Path) -> None:
        """test-done-003 has status=done — should not appear in defects."""
        detector = StaleQueueDetector(
            queue_path=tmp_repo / ".local" / "supervisor" / "action-queue.jsonl",
            repo_root=tmp_repo,
        )
        defects = detector.detect_stale()
        ids = [d.queue_item.action_id for d in defects]
        assert "test-done-003" not in ids

    def test_detect_stale_real_gap_is_capability_gap(self, tmp_repo: Path) -> None:
        """nonexistent_function_xyz is not in source → CAPABILITY_GAP."""
        detector = StaleQueueDetector(
            queue_path=tmp_repo / ".local" / "supervisor" / "action-queue.jsonl",
            repo_root=tmp_repo,
        )
        defects = detector.detect_stale()
        gaps = [d for d in defects if d.defect_class == DefectClass.CAPABILITY_GAP]
        assert any(d.queue_item.action_id == "test-real-gap-002" for d in gaps)


# ---------------------------------------------------------------------------
# Test: ReworkOrchestrator — classification
# ---------------------------------------------------------------------------


class TestReworkOrchestratorClassify:
    def test_classify_stale(self, tmp_repo: Path) -> None:
        orch = ReworkOrchestrator(
            queue_path=tmp_repo / ".local" / "supervisor" / "action-queue.jsonl",
            repo_root=tmp_repo,
        )
        defect = DetectedDefect(
            queue_item=QueueItem(
                action_id="x", action_type="PRODUCT_SOURCE_PATCH_BOUNDED",
                target_path="src/python/abw/abw_codec.py", status="pending",
                function_name="search_text",
            ),
            defect_class=DefectClass.STALE_QUEUE_ITEM,
            detail="test",
        )
        assert orch.classify(defect) == DefectClass.STALE_QUEUE_ITEM

    def test_classify_gap(self, tmp_repo: Path) -> None:
        orch = ReworkOrchestrator(
            queue_path=tmp_repo / ".local" / "supervisor" / "action-queue.jsonl",
            repo_root=tmp_repo,
        )
        defect = DetectedDefect(
            queue_item=QueueItem(
                action_id="y", action_type="PRODUCT_SOURCE_PATCH_BOUNDED",
                target_path="src/python/abw/abw_codec.py", status="pending",
                function_name="not_here",
            ),
            defect_class=DefectClass.CAPABILITY_GAP,
            detail="test",
        )
        assert orch.classify(defect) == DefectClass.CAPABILITY_GAP


# ---------------------------------------------------------------------------
# Test: ReworkOrchestrator — repair taskcard creation
# ---------------------------------------------------------------------------


class TestRepairTaskcard:
    def test_create_repair_taskcard_stale(self, tmp_repo: Path) -> None:
        orch = ReworkOrchestrator(repo_root=tmp_repo)
        item = QueueItem(
            action_id="stale-x", action_type="PRODUCT_SOURCE_PATCH_BOUNDED",
            target_path="src/python/abw/abw_codec.py", status="pending",
            function_name="search_text",
        )
        defect = DetectedDefect(
            queue_item=item,
            defect_class=DefectClass.STALE_QUEUE_ITEM,
            detail="test",
        )
        tc = orch.create_repair_taskcard(defect)
        assert tc.defect_class == DefectClass.STALE_QUEUE_ITEM.value
        assert "stale-x" in tc.taskcard_id.lower() or "STALE-X" in tc.taskcard_id
        assert tc.repair_action == "MARK_QUEUE_ITEM_DONE"
        assert "search_text" in tc.repair_note

    def test_create_repair_taskcard_non_stale_raises(self, tmp_repo: Path) -> None:
        orch = ReworkOrchestrator(repo_root=tmp_repo)
        item = QueueItem(
            action_id="gap-y", action_type="PRODUCT_SOURCE_PATCH_BOUNDED",
            target_path="src/python/abw/abw_codec.py", status="pending",
            function_name="nonexistent_fn",
        )
        defect = DetectedDefect(
            queue_item=item,
            defect_class=DefectClass.CAPABILITY_GAP,
            detail="test",
        )
        with pytest.raises(ValueError):
            orch.create_repair_taskcard(defect)

    def test_taskcard_yaml_written(self, tmp_path: Path, stale_only_repo: Path) -> None:
        taskcards_dir = tmp_path / "taskcards" / "test-repair"
        orch = ReworkOrchestrator(
            queue_path=stale_only_repo / ".local" / "supervisor" / "action-queue.jsonl",
            repo_root=stale_only_repo,
            taskcards_root=taskcards_dir,
        )
        item = QueueItem(
            action_id="stale-write-test", action_type="PRODUCT_SOURCE_PATCH_BOUNDED",
            target_path="src/python/gnumeric/gnumeric_codec.py", status="pending",
            function_name="rename_sheet",
        )
        defect = DetectedDefect(
            queue_item=item,
            defect_class=DefectClass.STALE_QUEUE_ITEM,
            detail="test",
        )
        tc = orch.create_repair_taskcard(defect)
        path = orch._write_taskcard_yaml(tc)
        assert path.exists()
        content = path.read_text()
        assert "STALE_QUEUE_ITEM" in content
        assert "rename_sheet" in content


# ---------------------------------------------------------------------------
# Test: ReworkOrchestrator — execute repair
# ---------------------------------------------------------------------------


class TestExecuteRepair:
    def test_execute_repair_marks_item_done(self, stale_only_repo: Path, tmp_path: Path) -> None:
        orch = ReworkOrchestrator(
            queue_path=stale_only_repo / ".local" / "supervisor" / "action-queue.jsonl",
            repo_root=stale_only_repo,
            taskcards_root=tmp_path / "tc",
        )
        item = QueueItem(
            action_id="stale-only-001", action_type="PRODUCT_SOURCE_PATCH_BOUNDED",
            target_path="src/python/gnumeric/gnumeric_codec.py", status="pending",
            function_name="rename_sheet",
        )
        defect = DetectedDefect(
            queue_item=item,
            defect_class=DefectClass.STALE_QUEUE_ITEM,
            detail="test",
        )
        tc = orch.create_repair_taskcard(defect)
        outcome = orch.execute_repair(defect, tc)
        assert outcome.success is True
        assert outcome.action_taken == "MARKED_QUEUE_ITEM_DONE"

    def test_execute_repair_no_source_mutation(
        self, stale_only_repo: Path, tmp_path: Path
    ) -> None:
        """Source file must not be modified during stale-item repair."""
        src = stale_only_repo / "src" / "python" / "gnumeric" / "gnumeric_codec.py"
        original = src.read_text()

        orch = ReworkOrchestrator(
            queue_path=stale_only_repo / ".local" / "supervisor" / "action-queue.jsonl",
            repo_root=stale_only_repo,
            taskcards_root=tmp_path / "tc",
        )
        item = QueueItem(
            action_id="stale-only-001", action_type="PRODUCT_SOURCE_PATCH_BOUNDED",
            target_path="src/python/gnumeric/gnumeric_codec.py", status="pending",
            function_name="rename_sheet",
        )
        defect = DetectedDefect(
            queue_item=item,
            defect_class=DefectClass.STALE_QUEUE_ITEM,
            detail="test",
        )
        tc = orch.create_repair_taskcard(defect)
        orch.execute_repair(defect, tc)

        assert src.read_text() == original, "Source file must NOT be modified"

    def test_execute_repair_capability_gap_blocked(
        self, tmp_repo: Path, tmp_path: Path
    ) -> None:
        orch = ReworkOrchestrator(
            queue_path=tmp_repo / ".local" / "supervisor" / "action-queue.jsonl",
            repo_root=tmp_repo,
            taskcards_root=tmp_path / "tc",
        )
        item = QueueItem(
            action_id="gap-z", action_type="PRODUCT_SOURCE_PATCH_BOUNDED",
            target_path="src/python/abw/abw_codec.py", status="pending",
            function_name="nonexistent_fn",
        )
        defect = DetectedDefect(
            queue_item=item,
            defect_class=DefectClass.CAPABILITY_GAP,
            detail="test",
        )
        item_with_matching_tc = QueueItem(
            action_id="stale-dummy", action_type="PRODUCT_SOURCE_PATCH_BOUNDED",
            target_path="src/python/abw/abw_codec.py", status="pending",
            function_name="search_text",
        )
        stale_defect = DetectedDefect(
            queue_item=item_with_matching_tc,
            defect_class=DefectClass.STALE_QUEUE_ITEM,
            detail="for tc",
        )
        tc = orch.create_repair_taskcard(stale_defect)
        # Use the gap defect with a stale-type taskcard (mismatch test)
        outcome = orch.execute_repair(defect, tc)
        assert outcome.success is False
        assert "SKIPPED_NOT_STALE" in outcome.action_taken


# ---------------------------------------------------------------------------
# Test: ReworkOrchestrator — verify repair
# ---------------------------------------------------------------------------


class TestVerifyRepair:
    def test_verify_repair_post_mark_done(
        self, stale_only_repo: Path, tmp_path: Path
    ) -> None:
        orch = ReworkOrchestrator(
            queue_path=stale_only_repo / ".local" / "supervisor" / "action-queue.jsonl",
            repo_root=stale_only_repo,
            taskcards_root=tmp_path / "tc",
        )
        item = QueueItem(
            action_id="stale-only-001", action_type="PRODUCT_SOURCE_PATCH_BOUNDED",
            target_path="src/python/gnumeric/gnumeric_codec.py", status="pending",
            function_name="rename_sheet",
        )
        defect = DetectedDefect(
            queue_item=item,
            defect_class=DefectClass.STALE_QUEUE_ITEM,
            detail="test",
        )
        tc = orch.create_repair_taskcard(defect)
        orch.execute_repair(defect, tc)

        # After repair, item should no longer be pending
        verified = orch.verify_repair(defect)
        assert verified is True


# ---------------------------------------------------------------------------
# Test: ReworkOrchestrator — full cycle
# ---------------------------------------------------------------------------


class TestRunCycle:
    def test_run_cycle_stale_only_all_repaired(
        self, stale_only_repo: Path, tmp_path: Path
    ) -> None:
        orch = ReworkOrchestrator(
            queue_path=stale_only_repo / ".local" / "supervisor" / "action-queue.jsonl",
            repo_root=stale_only_repo,
            taskcards_root=tmp_path / "tc",
        )
        summary = orch.run_cycle()
        assert summary["repairs_succeeded"] == len(summary["stale_items"])
        assert summary["stop_condition_hit"] is False

    def test_run_cycle_no_defects_idempotent(self, empty_queue_repo: Path) -> None:
        orch = ReworkOrchestrator(
            queue_path=empty_queue_repo / ".local" / "supervisor" / "action-queue.jsonl",
            repo_root=empty_queue_repo,
        )
        summary = orch.run_cycle()
        assert summary["defects_detected"] == 0
        assert summary["idempotent"] is True
        assert summary["stop_condition_hit"] is False

    def test_run_cycle_capability_gap_stops(self, tmp_repo: Path) -> None:
        """If a real gap exists, cycle hits stop condition (no auto-repair)."""
        orch = ReworkOrchestrator(
            queue_path=tmp_repo / ".local" / "supervisor" / "action-queue.jsonl",
            repo_root=tmp_repo,
        )
        summary = orch.run_cycle()
        # tmp_repo has test-real-gap-002 (CAPABILITY_GAP) → stop condition
        assert summary["stop_condition_hit"] is True
        assert "test-real-gap-002" in summary["gap_items"]

    def test_run_cycle_idempotent_second_run(
        self, stale_only_repo: Path, tmp_path: Path
    ) -> None:
        """Second run after repair should find zero stale items."""
        orch = ReworkOrchestrator(
            queue_path=stale_only_repo / ".local" / "supervisor" / "action-queue.jsonl",
            repo_root=stale_only_repo,
            taskcards_root=tmp_path / "tc",
        )
        summary1 = orch.run_cycle()
        assert summary1["repairs_succeeded"] > 0

        # Second run: repaired items are now done, should not re-appear
        summary2 = orch.run_cycle()
        assert summary2["defects_detected"] == 0
        assert summary2["idempotent"] is True

    def test_run_cycle_outcomes_have_required_fields(
        self, stale_only_repo: Path, tmp_path: Path
    ) -> None:
        orch = ReworkOrchestrator(
            queue_path=stale_only_repo / ".local" / "supervisor" / "action-queue.jsonl",
            repo_root=stale_only_repo,
            taskcards_root=tmp_path / "tc",
        )
        summary = orch.run_cycle()
        for outcome in summary["outcomes"]:
            assert "action_id" in outcome
            assert "function_name" in outcome
            assert "defect_class" in outcome
            assert "success" in outcome
            assert "verified" in outcome
            assert "action_taken" in outcome

    def test_run_cycle_dry_run_no_queue_mutation(
        self, stale_only_repo: Path, tmp_path: Path
    ) -> None:
        queue_path = stale_only_repo / ".local" / "supervisor" / "action-queue.jsonl"
        original_content = queue_path.read_text()

        orch = ReworkOrchestrator(
            queue_path=queue_path,
            repo_root=stale_only_repo,
            taskcards_root=tmp_path / "tc",
            dry_run=True,
        )
        summary = orch.run_cycle()

        # Queue must be unchanged in dry-run mode
        assert queue_path.read_text() == original_content
        # But detects still work
        assert summary["defects_detected"] > 0


# ---------------------------------------------------------------------------
# Test: run_healing_cycle convenience function
# ---------------------------------------------------------------------------


class TestRunHealingCycle:
    def test_returns_dict(self, empty_queue_repo: Path) -> None:
        summary = run_healing_cycle(repo_root=empty_queue_repo)
        assert isinstance(summary, dict)
        assert "defects_detected" in summary
        assert "idempotent" in summary

    def test_dry_run_does_not_mutate(self, stale_only_repo: Path) -> None:
        queue_path = stale_only_repo / ".local" / "supervisor" / "action-queue.jsonl"
        original = queue_path.read_text()
        run_healing_cycle(repo_root=stale_only_repo, dry_run=True)
        assert queue_path.read_text() == original
