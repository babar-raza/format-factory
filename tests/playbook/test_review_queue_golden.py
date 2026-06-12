"""
test_review_queue_golden.py — Golden tests for export_review_queue.py (S-F2F-04).

Tests that the review queue export produces expected deterministic output.
Uses checked-in golden fixtures in tests/playbook/golden/.

Normalization:
- queue_id (rq-{format_id}-{timestamp}) is replaced with rq-NORMALIZED.
- run_id (s-f2f-03-export-{timestamp}) is replaced with s-f2f-03-export-NORMALIZED.
- generated_at and provenance.created_at are replaced with NORMALIZED_TIMESTAMP.
"""

import copy
import os
import sys

import pytest
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GOLDEN_DIR = os.path.join(REPO_ROOT, "tests", "playbook", "golden")
FIXTURE_DIR = os.path.join(REPO_ROOT, "tests", "playbook", "fixtures")

MISSING_INPUTS = os.path.join(FIXTURE_DIR, "replay-with-missing-inputs.yaml")

_SENTINEL_TS = "NORMALIZED_TIMESTAMP"
_SENTINEL_QID = "rq-NORMALIZED"
_SENTINEL_RID = "s-f2f-03-export-NORMALIZED"


def _normalize_queue(queue: dict) -> dict:
    """Normalize unstable fields in a review queue dict."""
    q = copy.deepcopy(queue)
    q["generated_at"] = _SENTINEL_TS
    q["queue_id"] = _SENTINEL_QID
    q["run_id"] = _SENTINEL_RID
    for item in q.get("items", []):
        if "provenance" in item and "created_at" in item["provenance"]:
            item["provenance"]["created_at"] = _SENTINEL_TS
    return q


def _load_golden_yaml(filename: str) -> dict:
    path = os.path.join(GOLDEN_DIR, filename)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _make_missing_report() -> dict:
    """Run mode_dry_run on missing-inputs fixture and return report."""
    sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
    from replay_acquisition_playbook import mode_dry_run
    schema = os.path.join(REPO_ROOT, "schemas", "playbook", "acquisition-playbook.schema.json")
    _, report = mode_dry_run(MISSING_INPUTS, schema, "fods")
    return report


def _diff_yaml(actual: dict, expected: dict, label: str = "") -> str:
    import pprint
    if actual == expected:
        return ""
    return (
        f"\n--- ACTUAL {label} ---\n{pprint.pformat(actual)}"
        f"\n--- EXPECTED {label} ---\n{pprint.pformat(expected)}"
    )


# ---------------------------------------------------------------------------
# Test: golden fixtures exist
# ---------------------------------------------------------------------------
class TestReviewQueueGoldenFixtureExists:
    def test_review_queue_golden_exists(self):
        assert os.path.isfile(os.path.join(GOLDEN_DIR, "review-queue-missing-inputs.expected.yaml"))


# ---------------------------------------------------------------------------
# Test: review queue golden match
# ---------------------------------------------------------------------------
class TestReviewQueueGoldenMatch:
    def test_missing_inputs_queue_matches_golden(self):
        """Review queue from missing-inputs report matches golden fixture."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from export_review_queue import build_review_queue

        report = _make_missing_report()
        queue = build_review_queue("fods", report)
        actual = _normalize_queue(queue)
        expected = _load_golden_yaml("review-queue-missing-inputs.expected.yaml")
        diff = _diff_yaml(actual, expected, "review-queue-missing-inputs")
        assert actual == expected, f"Golden mismatch:{diff}"

    def test_review_queue_is_deterministic(self):
        """Two calls to build_review_queue produce identical queues (after normalization)."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from export_review_queue import build_review_queue

        report = _make_missing_report()
        q1 = _normalize_queue(build_review_queue("fods", report))
        q2 = _normalize_queue(build_review_queue("fods", report))
        assert q1 == q2, "Review queue must be deterministic"

    def test_item_count_matches_conflict_count(self):
        """Review queue item count equals total_conflicts in dry-run report."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from export_review_queue import build_review_queue

        report = _make_missing_report()
        queue = build_review_queue("fods", report)
        assert len(queue["items"]) == report["total_conflicts"]

    def test_item_ids_are_sequential(self):
        """Review queue items have IDs RQ-001, RQ-002, etc."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from export_review_queue import build_review_queue

        report = _make_missing_report()
        queue = build_review_queue("fods", report)
        for i, item in enumerate(queue["items"], 1):
            assert item["item_id"] == f"RQ-{i:03d}", (
                f"Expected RQ-{i:03d}, got {item['item_id']}"
            )


# ---------------------------------------------------------------------------
# Test: governance block always present
# ---------------------------------------------------------------------------
class TestGovernanceBlockGolden:
    def test_governance_block_present_in_golden(self):
        """Golden fixture has governance block with all required fields."""
        golden = _load_golden_yaml("review-queue-missing-inputs.expected.yaml")
        gov = golden.get("governance", {})
        assert gov.get("cannot_approve_gates") is True
        assert gov.get("high_severity_blocks_apply") is True
        assert gov.get("gate_progress_requires_resolution") is True
        assert gov.get("cannot_replace_dec034") is True
        assert gov.get("cannot_replace_human_approval") is True

    def test_governance_block_in_actual_queue(self):
        """Actual queue output always has governance block."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from export_review_queue import build_review_queue

        report = _make_missing_report()
        queue = build_review_queue("fods", report)
        gov = queue.get("governance", {})
        assert gov.get("cannot_approve_gates") is True
        assert gov.get("high_severity_blocks_apply") is True


# ---------------------------------------------------------------------------
# Test: high severity blocks apply mode
# ---------------------------------------------------------------------------
class TestSeverityGolden:
    def test_high_severity_items_block_apply_in_golden(self):
        """All items in golden fixture with severity=high have blocks_apply_mode=true."""
        golden = _load_golden_yaml("review-queue-missing-inputs.expected.yaml")
        for item in golden.get("items", []):
            if item["severity"] in ("high", "blocker"):
                assert item["blocks_apply_mode"] is True
                assert item["blocks_gate_progress"] is True

    def test_summary_blocks_apply_true_in_golden(self):
        """Golden summary.blocks_apply_mode is True when high-severity items are open."""
        golden = _load_golden_yaml("review-queue-missing-inputs.expected.yaml")
        assert golden["summary"]["blocks_apply_mode"] is True
        assert golden["summary"]["high_count"] == 2

    def test_empty_queue_does_not_block_apply(self):
        """An empty conflicts list produces a queue that does not block apply."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from export_review_queue import build_review_queue

        empty_report = {
            "playbook_id": "test-empty",
            "format_id": "fods",
            "conflicts": [],
        }
        queue = build_review_queue("fods", empty_report)
        assert queue["summary"]["blocks_apply_mode"] is False
        assert queue["summary"]["total_items"] == 0


# ---------------------------------------------------------------------------
# Test: output path guard for export tool
# ---------------------------------------------------------------------------
class TestExportToolOutputGuard:
    def test_export_tool_output_guard_blocks_committed_paths(self):
        """export_review_queue._guard_output_path must reject committed repo dirs."""
        sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "playbook"))
        from export_review_queue import _guard_output_path

        for prefix in ["tools", "schemas", "plans", "tests"]:
            bad_path = os.path.join(REPO_ROOT, prefix, "bad-queue.yaml")
            with pytest.raises(SystemExit) as exc_info:
                _guard_output_path(bad_path)
            assert exc_info.value.code == 2
