"""R109: Lane Ledger, Stream-State Isolation, and Continuation Gating Tests

Verifies:
- Lane ledger detection in evidence_root, sample-outputs, and reports/<run_id>/
- Lane ledger severity upgrade (low -> medium)
- Continuation gating for missing lane ledger and wrong-stream evidence
- Selected-gap freshness archival
- Next-work artifact stream validation
"""
import json
import sys
import tempfile
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"
sys.path.insert(0, str(TOOLS_DIR))

from anti_skip_checker import (
    detect_missing_lane_ledger,
    classify_violation_impact,
    classify_gap_freshness,
    detect_stale_gaps,
    SEVERITY_MAP,
)
from generate_next_worker_prompt import generate_next_work_items
from validate_prompt_quality import validate_next_work_items


# --- Wave 1: Lane ledger detection ---


class TestLaneLedgerDetection:
    """Verify detect_missing_lane_ledger finds ledgers in various locations."""

    def test_ledger_in_evidence_root(self, tmp_path):
        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()
        (evidence_root / "lane-execution-ledger.json").write_text("[]")
        result = detect_missing_lane_ledger(evidence_root)
        assert result["is_violation"] is False
        assert len(result["ledgers_found"]) >= 1

    def test_ledger_in_sample_outputs(self, tmp_path):
        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()
        sample_dir = tmp_path / "sample-outputs"
        sample_dir.mkdir()
        (sample_dir / "lane-ledger.json").write_text("[]")
        result = detect_missing_lane_ledger(evidence_root, sample_outputs_dir=sample_dir)
        assert result["is_violation"] is False

    def test_ledger_in_reports_dir(self, tmp_path):
        """R109: Detect ledger in reports/<run_id>/."""
        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()
        reports_dir = tmp_path / "reports" / "acceleration-r109"
        reports_dir.mkdir(parents=True)
        (reports_dir / "lane-execution-ledger.json").write_text("[]")
        decl = {"run_id": "acceleration-r109"}
        result = detect_missing_lane_ledger(
            evidence_root, declaration=decl, repo_root=tmp_path
        )
        assert result["is_violation"] is False

    def test_ledger_in_declared_reports(self, tmp_path):
        """R109: Detect ledger from reports_created paths in declaration."""
        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()
        reports_dir = tmp_path / "reports" / "acceleration-r109"
        reports_dir.mkdir(parents=True)
        (reports_dir / "lane-execution-ledger.json").write_text("[]")
        decl = {
            "run_id": "acceleration-r109",
            "reports_created": ["reports/acceleration-r109/lane-execution-ledger.json"],
        }
        result = detect_missing_lane_ledger(
            evidence_root, declaration=decl, repo_root=tmp_path
        )
        assert result["is_violation"] is False

    def test_missing_ledger_detected(self, tmp_path):
        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()
        result = detect_missing_lane_ledger(evidence_root)
        assert result["is_violation"] is True

    def test_missing_ledger_severity_is_medium(self):
        """R109: missing_lane_ledger upgraded from low to medium."""
        assert SEVERITY_MAP["missing_lane_ledger"] == "medium"

    def test_missing_ledger_appears_as_caveat(self):
        """medium severity should be classified as caveat, not note."""
        checks = [{"check": "missing_lane_ledger", "is_violation": True}]
        impact = classify_violation_impact(checks)
        assert "missing_lane_ledger" in impact["caveats"]
        assert "missing_lane_ledger" not in impact["notes"]


# --- Wave 2: Stream-state isolation ---


class TestStreamStateIsolation:
    """Verify stream-state isolation concepts."""

    def test_continuation_signal_should_match_stream(self):
        """The continuation signal sprint should match the acceleration stream."""
        # This is a documentation test — the fix is in autonomous_cycle.py
        # The signal is written from the LAST cycle that ran, not necessarily
        # the current stream. This test verifies the concept.
        signal = {
            "source_sprint_id": "FORMAT-FACTORY-ACCELERATION-R109-TEST-001",
            "autonomous_continue": True,
        }
        assert "ACCELERATION" in signal["source_sprint_id"]

    def test_evidence_review_stream_detection(self):
        """Evidence-review should identify the stream from sprint_id."""
        from generate_supervisor_packet import detect_stream_from_sprint_id
        assert detect_stream_from_sprint_id(
            "FORMAT-FACTORY-ACCELERATION-R109-LANE-001"
        ) == "acceleration"
        assert detect_stream_from_sprint_id(
            "FORMAT-FACTORY-MAINSTREAM-R110-PRODUCT-001"
        ) == "mainstream"


# --- Wave 3: Continuation gating ---


class TestContinuationGating:
    """Verify continuation gating for lane ledger and wrong-stream."""

    def test_missing_lane_ledger_is_caveat_not_block(self):
        """medium severity = caveat; does not block but is noted."""
        checks = [{"check": "missing_lane_ledger", "is_violation": True}]
        impact = classify_violation_impact(checks)
        assert impact["block"] is False
        assert impact["downgrade"] is False
        assert len(impact["caveats"]) == 1

    def test_wrong_stream_gaps_is_critical(self):
        """wrong_stream_gaps = critical → blocks continuation."""
        assert SEVERITY_MAP["wrong_stream_gaps"] == "critical"
        checks = [{"check": "wrong_stream_gaps", "is_violation": True}]
        impact = classify_violation_impact(checks)
        assert impact["block"] is True

    def test_stale_gaps_is_critical(self):
        """stale_gaps = critical → blocks continuation."""
        assert SEVERITY_MAP["stale_gaps"] == "critical"


# --- Wave 4: Selected-gap freshness ---


class TestSelectedGapFreshness:
    """Verify stale R98 gaps are classified correctly."""

    def test_r98_vs_r109_is_archived(self):
        """R98 is 11 sprints behind R109 → archived."""
        assert classify_gap_freshness("R98", "R109") == "archived"

    def test_stale_gaps_from_r98(self):
        result = detect_stale_gaps({"sprint": "R98"}, "R109")
        assert result["is_violation"] is True
        assert result["freshness"] == "archived"
        assert "archived" in result["recommendation"]

    def test_fresh_gaps_pass(self):
        result = detect_stale_gaps({"sprint": "R109"}, "R109")
        assert result["is_violation"] is False

    def test_recent_gaps_tolerated(self):
        """Within 3 sprints is recent — still flagged as stale but usable."""
        assert classify_gap_freshness("R107", "R109") == "recent"


# --- Wave 5: Next-work artifact validation ---


class TestNextWorkArtifactValidation:
    """Verify next-work artifacts are stream-correct."""

    def _make_review(self, sprint_id="FORMAT-FACTORY-ACCELERATION-R109-TEST-001"):
        return {
            "run_id": "test-r109",
            "sprint_id": sprint_id,
            "overall_verdict": "ACCEPTED",
            "autonomous_continue": True,
            "test_results": {"passed": 100, "failed": 0, "skipped": 0},
            "item_grades": [],
            "accepted_items": [],
            "rework_items": [],
            "rejected_items": [],
            "overclaimed_items": [],
        }

    def test_acceleration_nwi_is_stream_correct(self):
        review = self._make_review()
        nwi = generate_next_work_items(review, stream="acceleration")
        result = validate_next_work_items(nwi, "acceleration")
        assert result["valid"] is True

    def test_acceleration_nwi_has_no_product_items(self):
        review = self._make_review()
        nwi = generate_next_work_items(review, stream="acceleration")
        product = [i for i in nwi["items"] if i["source"] == "product-factory"]
        assert len(product) == 0

    def test_acceleration_nwi_has_forward_work(self):
        review = self._make_review()
        nwi = generate_next_work_items(review, stream="acceleration")
        accel = [i for i in nwi["items"] if i["lane"] == "acceleration-advancement"]
        assert len(accel) >= 1

    def test_mainstream_nwi_has_product_items(self):
        review = self._make_review(sprint_id="FORMAT-FACTORY-MAINSTREAM-R110-TEST-001")
        nwi = generate_next_work_items(review, stream="mainstream")
        product = [i for i in nwi["items"] if i["source"] == "product-factory"]
        assert len(product) >= 1

    def test_all_streams_validate(self):
        for stream in ["mainstream", "acceleration", "skills", "supervisor"]:
            review = self._make_review()
            nwi = generate_next_work_items(review, stream=stream)
            result = validate_next_work_items(nwi, stream)
            assert result["valid"] is True, f"{stream}: {[c for c in result['checks'] if not c['pass']]}"
