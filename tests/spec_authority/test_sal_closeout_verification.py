"""
test_sal_closeout_verification.py

Verification tests for SAL Main Goal closeout sprint evidence integrity.

Addresses rework items:
  - SAL-CLOSE-L0: Verify lane-supervisor-ledger.json has all 12 lanes with required fields
  - SAL-CLOSE-L5: Verify sal-gap-root-cause-matrix.json has 6 gaps, exactly 1 healed

Sprint: FORMAT-FACTORY-SAL-MAIN-GOAL-VERIFICATION-HEALING-PILOT-BACKFILL-CLOSEOUT-001
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_EVIDENCE = _REPO / ".local" / "evidences" / \
    "sal-main-goal-verification-healing-pilot-backfill-closeout-20260612-8e45224"

pytestmark = pytest.mark.skipif(
    not _EVIDENCE.is_dir(),
    reason="SAL closeout evidence not present in this environment",
)


class TestLaneSupervisorLedger:
    """SAL-CLOSE-L0: Verify lane-supervisor-ledger.json has correct 12-lane structure."""

    def _load(self):
        path = _EVIDENCE / "lane-supervisor-ledger.json"
        assert path.exists(), f"Lane ledger not found: {path}"
        with open(path) as f:
            return json.load(f)

    def test_file_exists(self):
        assert (_EVIDENCE / "lane-supervisor-ledger.json").exists()

    def test_has_sprint_id(self):
        data = self._load()
        assert "sprint_id" in data
        assert data["sprint_id"] == \
            "FORMAT-FACTORY-SAL-MAIN-GOAL-VERIFICATION-HEALING-PILOT-BACKFILL-CLOSEOUT-001"

    def test_has_12_lanes(self):
        data = self._load()
        assert "lanes" in data
        assert len(data["lanes"]) == 12

    def test_all_lanes_have_lane_id(self):
        data = self._load()
        for lane in data["lanes"]:
            assert "lane_id" in lane, f"Lane missing lane_id: {lane}"

    def test_all_lanes_have_supervisor(self):
        data = self._load()
        for lane in data["lanes"]:
            assert "supervisor" in lane, f"Lane {lane.get('lane_id')} missing supervisor"

    def test_all_lanes_have_stop_condition(self):
        data = self._load()
        for lane in data["lanes"]:
            assert "stop_condition" in lane, \
                f"Lane {lane.get('lane_id')} missing stop_condition"

    def test_all_lanes_have_acceptance_criteria(self):
        data = self._load()
        for lane in data["lanes"]:
            assert "acceptance_criteria" in lane, \
                f"Lane {lane.get('lane_id')} missing acceptance_criteria"

    def test_all_lanes_completed(self):
        data = self._load()
        for lane in data["lanes"]:
            assert lane.get("status") == "COMPLETED", \
                f"Lane {lane.get('lane_id')} status: {lane.get('status')}"

    def test_all_lanes_have_evidence_produced(self):
        data = self._load()
        for lane in data["lanes"]:
            assert "evidence_produced" in lane and len(lane["evidence_produced"]) > 0, \
                f"Lane {lane.get('lane_id')} missing evidence_produced"

    def test_lane_ids_are_l0_through_l11(self):
        data = self._load()
        lane_ids = {lane["lane_id"] for lane in data["lanes"]}
        expected = {f"L{i}" for i in range(12)}
        assert lane_ids == expected, f"Lane IDs mismatch: {lane_ids}"

    def test_anti_skip_controls_present(self):
        data = self._load()
        assert "anti_skip_controls" in data
        assert data["anti_skip_controls"].get("lane_ledger_required") is True


class TestGapRootCauseMatrix:
    """SAL-CLOSE-L5: Verify sal-gap-root-cause-matrix.json is complete with 6 gaps, 1 healed."""

    def _load(self):
        path = _EVIDENCE / "sal-gap-root-cause-matrix.json"
        assert path.exists(), f"Gap matrix not found: {path}"
        with open(path) as f:
            return json.load(f)

    def test_file_exists(self):
        assert (_EVIDENCE / "sal-gap-root-cause-matrix.json").exists()

    def test_has_gaps_array(self):
        data = self._load()
        assert "gaps" in data
        assert isinstance(data["gaps"], list)

    def test_has_exactly_6_gaps(self):
        data = self._load()
        assert len(data["gaps"]) == 6, \
            f"Expected 6 gaps, got {len(data['gaps'])}"

    def test_all_gaps_have_gap_id(self):
        data = self._load()
        for gap in data["gaps"]:
            assert "gap_id" in gap, f"Gap missing gap_id: {gap}"

    def test_gap_ids_are_sequential(self):
        data = self._load()
        gap_ids = {g["gap_id"] for g in data["gaps"]}
        expected = {f"SAL-GAP-{i:03d}" for i in range(1, 7)}
        assert gap_ids == expected, f"Gap IDs: {gap_ids}"

    def test_exactly_one_gap_healed(self):
        data = self._load()
        healed = [g for g in data["gaps"] if g.get("healing_applied") is True]
        assert len(healed) == 1, \
            f"Expected exactly 1 healed gap, found {len(healed)}: {[g['gap_id'] for g in healed]}"

    def test_healed_gap_is_sal_gap_006(self):
        data = self._load()
        healed = [g for g in data["gaps"] if g.get("healing_applied") is True]
        assert healed[0]["gap_id"] == "SAL-GAP-006", \
            f"Expected SAL-GAP-006 healed, got {healed[0]['gap_id']}"

    def test_healed_gap_status_healed_in_sprint(self):
        data = self._load()
        gap_006 = next(g for g in data["gaps"] if g["gap_id"] == "SAL-GAP-006")
        assert gap_006["status"] == "HEALED_IN_THIS_SPRINT"

    def test_non_healed_gaps_have_acceptable_statuses(self):
        data = self._load()
        allowed_statuses = {
            "ACCEPTABLE_WITH_EXCEPTION",
            "KNOWN_NOT_BLOCKING",
            "DEFERRED_PHASE2",
            "INTENTIONAL_DEFERRAL",
        }
        for gap in data["gaps"]:
            if not gap.get("healing_applied"):
                assert gap["status"] in allowed_statuses, \
                    f"Gap {gap['gap_id']} has unexpected status: {gap['status']}"

    def test_has_summary(self):
        data = self._load()
        assert "summary" in data

    def test_summary_total_gaps_is_6(self):
        data = self._load()
        assert data["summary"]["total_gaps"] == 6

    def test_summary_healed_in_sprint_is_1(self):
        data = self._load()
        assert data["summary"]["healed_in_sprint"] == 1

    def test_all_gaps_have_severity(self):
        data = self._load()
        for gap in data["gaps"]:
            assert "severity" in gap, f"Gap {gap.get('gap_id')} missing severity"
            assert gap["severity"] in ("LOW", "MEDIUM", "HIGH")
