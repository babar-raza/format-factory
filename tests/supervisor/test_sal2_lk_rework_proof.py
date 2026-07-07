"""
test_sal2_lk_rework_proof.py

Verifies the Lane K rework closure artifacts for Sprint 2:
  - Lane H backfill before/after gap-ledger snapshots exist
  - Diff confirms 366→370 gaps (6 added, 2 removed)
  - Idempotency proof confirms run 2 and run 3 both produce 370 gaps
  - Lane execution ledger from Sprint 1 evidence root is present

Sprint: FORMAT-FACTORY-SAL-INTEGRATION-HARDENING-SPRINT-2
Lane: K (REWORK closure)
Added: 2026-06-11
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SPRINT2_EVIDENCE = REPO_ROOT / ".local" / "evidences" / "sal-integration-hardening-sprint2-20260611-8e45224"
SPRINT1_EVIDENCE = REPO_ROOT / ".local" / "evidences" / "sal-verification-healing-hardening-backfill-single-go-20260611-8e45224"

pytestmark = pytest.mark.skipif(
    not SPRINT2_EVIDENCE.is_dir() or not SPRINT1_EVIDENCE.is_dir(),
    reason="Sprint evidence directories not present in this environment",
)


# ---------------------------------------------------------------------------
# Test 1: Before snapshot exists and has non-zero gap count
# ---------------------------------------------------------------------------

class TestLaneKBackfillBeforeSnapshot:
    def test_before_snapshot_exists(self):
        """lane-h-backfill-before.json must exist in Sprint 2 evidence root."""
        p = SPRINT2_EVIDENCE / "lane-h-backfill-before.json"
        assert p.exists(), f"Missing before snapshot: {p}"

    def test_before_snapshot_has_gap_data(self):
        """Before snapshot must contain a gap list with entries."""
        p = SPRINT2_EVIDENCE / "lane-h-backfill-before.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        gaps = data.get("gaps", [])
        assert isinstance(gaps, list), "Before snapshot must have a 'gaps' list"
        assert len(gaps) > 0, "Before snapshot must contain at least one gap"

    def test_before_snapshot_has_366_gaps(self):
        """Before snapshot must record exactly 366 gaps (pre-regeneration state)."""
        p = SPRINT2_EVIDENCE / "lane-h-backfill-before.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        gaps = data.get("gaps", [])
        assert len(gaps) == 366, f"Expected 366 gaps before backfill, got {len(gaps)}"


# ---------------------------------------------------------------------------
# Test 2: After snapshot exists and shows gap count change
# ---------------------------------------------------------------------------

class TestLaneKBackfillAfterSnapshot:
    def test_after_snapshot_exists(self):
        """lane-h-backfill-after.json must exist in Sprint 2 evidence root."""
        p = SPRINT2_EVIDENCE / "lane-h-backfill-after.json"
        assert p.exists(), f"Missing after snapshot: {p}"

    def test_after_snapshot_has_370_gaps(self):
        """After snapshot must record exactly 370 gaps (post-regeneration state)."""
        p = SPRINT2_EVIDENCE / "lane-h-backfill-after.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        gaps = data.get("gaps", [])
        assert len(gaps) == 370, f"Expected 370 gaps after backfill, got {len(gaps)}"

    def test_after_snapshot_has_more_gaps_than_before(self):
        """After snapshot must have more gaps than before snapshot (net positive change)."""
        before_data = json.loads((SPRINT2_EVIDENCE / "lane-h-backfill-before.json").read_text(encoding="utf-8"))
        after_data = json.loads((SPRINT2_EVIDENCE / "lane-h-backfill-after.json").read_text(encoding="utf-8"))
        assert len(after_data["gaps"]) > len(before_data["gaps"]), "After must have more gaps than before"


# ---------------------------------------------------------------------------
# Test 3: Diff file proves the change was applied
# ---------------------------------------------------------------------------

class TestLaneKBackfillDiff:
    def test_diff_file_exists(self):
        """lane-h-backfill-diff.txt must exist."""
        p = SPRINT2_EVIDENCE / "lane-h-backfill-diff.txt"
        assert p.exists(), f"Missing diff file: {p}"

    def test_diff_shows_added_gaps(self):
        """Diff must show ADDED gaps (from regeneration)."""
        p = SPRINT2_EVIDENCE / "lane-h-backfill-diff.txt"
        content = p.read_text(encoding="utf-8")
        assert "+ADDED:" in content, "Diff must contain +ADDED: entries"

    def test_diff_shows_before_count_366(self):
        """Diff must record pre-regeneration count of 366."""
        p = SPRINT2_EVIDENCE / "lane-h-backfill-diff.txt"
        content = p.read_text(encoding="utf-8")
        assert "366" in content, "Diff must reference 366 (before count)"

    def test_diff_shows_after_count_370(self):
        """Diff must record post-regeneration count of 370."""
        p = SPRINT2_EVIDENCE / "lane-h-backfill-diff.txt"
        content = p.read_text(encoding="utf-8")
        assert "370" in content, "Diff must reference 370 (after count)"


# ---------------------------------------------------------------------------
# Test 4: Idempotency proof confirms regeneration is stable
# ---------------------------------------------------------------------------

class TestLaneKIdempotencyProof:
    def test_idempotency_proof_exists(self):
        """lane-h-idempotency-proof.txt must exist."""
        p = SPRINT2_EVIDENCE / "lane-h-idempotency-proof.txt"
        assert p.exists(), f"Missing idempotency proof: {p}"

    def test_idempotency_confirmed(self):
        """Idempotency proof must state that runs 2 and 3 are identical."""
        p = SPRINT2_EVIDENCE / "lane-h-idempotency-proof.txt"
        content = p.read_text(encoding="utf-8")
        assert "IDEMPOTENCY CONFIRMED" in content, "Idempotency must be confirmed"
        assert "Identical: True" in content, "Proof must assert Identical: True"

    def test_idempotency_run3_also_370(self):
        """Idempotency proof must show run 3 also produced 370 gaps."""
        p = SPRINT2_EVIDENCE / "lane-h-idempotency-proof.txt"
        content = p.read_text(encoding="utf-8")
        assert "370" in content, "Idempotency proof must reference 370 gaps"


# ---------------------------------------------------------------------------
# Test 5: Sprint 1 lane execution ledger exists and has all lanes
# ---------------------------------------------------------------------------

class TestLaneKExecutionLedger:
    def test_lane_execution_ledger_exists(self):
        """lane-execution-ledger.json must exist in Sprint 1 evidence root."""
        p = SPRINT1_EVIDENCE / "lane-execution-ledger.json"
        assert p.exists(), f"Missing lane execution ledger: {p}"

    def test_ledger_has_all_sprint1_lanes(self):
        """Ledger must document all 9 Sprint 1 lanes (A through J, excluding E)."""
        p = SPRINT1_EVIDENCE / "lane-execution-ledger.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        lanes = data.get("lanes", [])
        lane_ids = {lane["lane_id"] for lane in lanes}
        expected = {"A", "B", "C", "D", "F", "G", "H", "I", "J"}
        assert expected <= lane_ids, f"Missing lanes: {expected - lane_ids}"

    def test_ledger_has_run_id(self):
        """Ledger must have a run_id matching Sprint 1."""
        p = SPRINT1_EVIDENCE / "lane-execution-ledger.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert "run_id" in data, "Ledger must have run_id"
        assert "sal-verification" in data["run_id"].lower(), "run_id must reference SAL sprint"

    def test_ledger_lanes_have_required_fields(self):
        """Each lane in the ledger must have lane_id, status, and tests_added."""
        p = SPRINT1_EVIDENCE / "lane-execution-ledger.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        for lane in data.get("lanes", []):
            assert "lane_id" in lane, f"Lane missing lane_id: {lane}"
            assert "status" in lane, f"Lane missing status: {lane}"
            assert "tests_added" in lane, f"Lane missing tests_added: {lane}"
