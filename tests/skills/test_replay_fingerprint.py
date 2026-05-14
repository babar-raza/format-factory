"""
tests/skills/test_replay_fingerprint.py

Tests for replay_fingerprint.py — Lane E CONWAY-R7R8.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

import pytest
from replay_fingerprint import (
    fingerprint_requirements,
    fingerprint_lanes,
    fingerprint_prompt,
    fingerprint_stale,
    fingerprint_plan,
    compute_sprint_fingerprint,
    compare_fingerprints,
)


# ===========================================================================
# TestPrimitiveFingerprints
# ===========================================================================

class TestPrimitiveFingerprints:
    def test_requirements_fingerprint_deterministic(self):
        ids = ["FODS-REQ-001", "FODS-REQ-002", "FODS-REQ-003"]
        fp1 = fingerprint_requirements(ids)
        fp2 = fingerprint_requirements(ids)
        assert fp1 == fp2

    def test_requirements_fingerprint_order_independent(self):
        ids = ["FODS-REQ-001", "FODS-REQ-002", "FODS-REQ-003"]
        ids_shuffled = ["FODS-REQ-003", "FODS-REQ-001", "FODS-REQ-002"]
        assert fingerprint_requirements(ids) == fingerprint_requirements(ids_shuffled)

    def test_different_requirements_different_fingerprint(self):
        fp1 = fingerprint_requirements(["FODS-REQ-001"])
        fp2 = fingerprint_requirements(["FODS-REQ-002"])
        assert fp1 != fp2

    def test_lanes_fingerprint_deterministic(self):
        selected = ["LANE-I-LOAD", "LANE-K", "LANE-C"]
        blocked = ["LANE-R3", "LANE-R5"]
        fp1 = fingerprint_lanes(selected, blocked)
        fp2 = fingerprint_lanes(selected, blocked)
        assert fp1 == fp2

    def test_lanes_fingerprint_order_independent(self):
        fp1 = fingerprint_lanes(["LANE-K", "LANE-C"], ["LANE-R3"])
        fp2 = fingerprint_lanes(["LANE-C", "LANE-K"], ["LANE-R3"])
        assert fp1 == fp2

    def test_different_lanes_different_fingerprint(self):
        fp1 = fingerprint_lanes(["LANE-K"], [])
        fp2 = fingerprint_lanes(["LANE-C"], [])
        assert fp1 != fp2

    def test_prompt_fingerprint_deterministic(self):
        text = "EXECUTION MODE — TEST\n\nMission: test."
        fp1 = fingerprint_prompt(text)
        fp2 = fingerprint_prompt(text)
        assert fp1 == fp2

    def test_prompt_fingerprint_whitespace_normalized(self):
        """Trailing whitespace per line should not affect fingerprint."""
        fp1 = fingerprint_prompt("line one\nline two")
        fp2 = fingerprint_prompt("line one   \nline two   ")
        assert fp1 == fp2

    def test_stale_fingerprint_deterministic(self):
        stale = {"verdict": "FRESH", "checks": {"directory_exists": "PASS"}, "blocker_count": 0}
        fp1 = fingerprint_stale(stale)
        fp2 = fingerprint_stale(stale)
        assert fp1 == fp2

    def test_different_stale_verdicts_different_fingerprint(self):
        fresh = {"verdict": "FRESH", "checks": {}, "blocker_count": 0}
        blocked = {"verdict": "STALE_BLOCKED", "checks": {}, "blocker_count": 1}
        assert fingerprint_stale(fresh) != fingerprint_stale(blocked)

    def test_fingerprints_are_16_char_hex(self):
        fp = fingerprint_requirements(["FODS-REQ-001"])
        assert len(fp) == 16
        assert all(c in "0123456789abcdef" for c in fp)


# ===========================================================================
# TestSprintFingerprint (live)
# ===========================================================================

class TestSprintFingerprintLive:
    def test_fods_sprint_fingerprint_completes(self):
        result = compute_sprint_fingerprint("fods", "TEST-SPRINT-001")
        assert isinstance(result, dict)
        assert result["format_id"] == "fods"

    def test_fodt_sprint_fingerprint_completes(self):
        result = compute_sprint_fingerprint("fodt", "TEST-SPRINT-001")
        assert result["format_id"] == "fodt"

    def test_fods_replay_safe(self):
        result = compute_sprint_fingerprint("fods", "TEST-SPRINT-001")
        assert result["replay_safe"] is True

    def test_fodt_replay_safe(self):
        result = compute_sprint_fingerprint("fodt", "TEST-SPRINT-001")
        assert result["replay_safe"] is True

    def test_fods_has_all_fingerprint_components(self):
        result = compute_sprint_fingerprint("fods", "TEST-SPRINT-001")
        required = {"stale", "lanes", "requirements", "plan", "prompt"}
        assert required.issubset(result["fingerprints"].keys())

    def test_fods_fingerprint_is_deterministic(self):
        """Two runs should produce identical fingerprints."""
        r1 = compute_sprint_fingerprint("fods", "TEST-SPRINT-001")
        r2 = compute_sprint_fingerprint("fods", "TEST-SPRINT-001")
        assert r1["fingerprints"] == r2["fingerprints"]

    def test_fodt_fingerprint_is_deterministic(self):
        r1 = compute_sprint_fingerprint("fodt", "TEST-SPRINT-001")
        r2 = compute_sprint_fingerprint("fodt", "TEST-SPRINT-001")
        assert r1["fingerprints"] == r2["fingerprints"]

    def test_fods_fodt_different_fingerprints(self):
        """Different formats must produce different fingerprints for prompt/plan."""
        fods = compute_sprint_fingerprint("fods", "TEST-SPRINT-001")
        fodt = compute_sprint_fingerprint("fodt", "TEST-SPRINT-001")
        # At minimum, prompt fingerprints should differ (FODT has extra constraint)
        assert fods["fingerprints"]["prompt"] != fodt["fingerprints"]["prompt"]

    def test_result_json_serializable(self):
        result = compute_sprint_fingerprint("fods", "TEST-SPRINT-001")
        json.dumps(result)


# ===========================================================================
# TestCompareFingerprints
# ===========================================================================

class TestCompareFingerprints:
    def _make_fp(self, sprint_id: str, reqs: list[str]) -> dict:
        return {
            "sprint_id": sprint_id,
            "fingerprints": {
                "stale": fingerprint_stale({"verdict": "FRESH", "checks": {}, "blocker_count": 0}),
                "lanes": fingerprint_lanes(["LANE-K"], []),
                "requirements": fingerprint_requirements(reqs),
                "plan": "abcdef1234567890",
                "prompt": "abcdef1234567890",
            }
        }

    def test_identical_fingerprints_consistent(self):
        fp = self._make_fp("SPRINT-001", ["FODS-REQ-001"])
        result = compare_fingerprints(fp, fp)
        assert result["verdict"] == "CONSISTENT"
        assert result["changed"] == []

    def test_changed_requirements_inconsistent(self):
        baseline = self._make_fp("SPRINT-001", ["FODS-REQ-001"])
        current = self._make_fp("SPRINT-002", ["FODS-REQ-002"])
        result = compare_fingerprints(baseline, current)
        assert "requirements" in result["changed"]

    def test_partial_change_partial_verdict(self):
        baseline = self._make_fp("SPRINT-001", ["FODS-REQ-001"])
        current = {
            "sprint_id": "SPRINT-002",
            "fingerprints": {
                **baseline["fingerprints"],
                "requirements": fingerprint_requirements(["FODS-REQ-999"]),  # changed
            }
        }
        result = compare_fingerprints(baseline, current)
        # Some changed, some unchanged
        assert len(result["changed"]) >= 1
        assert len(result["unchanged"]) >= 1
