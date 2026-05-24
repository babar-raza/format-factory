"""
test_r58_scoreboard_finality_strictness.py — R58 Train C: Scoreboard finality checks.

Verifies that IN_PROGRESS lanes in scoreboard and final-verdict are caught.

R58 Sprint: FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
IV-R57-006
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


class TestScoreboardFinalityStrictness:
    """check_scoreboard_lanes_in_progress must catch IN_PROGRESS in scoreboard."""

    def test_in_progress_lane_fails(self, tmp_path):
        scoreboard = "| L | Final | IN_PROGRESS | — |\n**SCOREBOARD_STATUS: TRAIN_L_IN_PROGRESS**"
        zp = tmp_path / "r58.zip"
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/reports/r58/multi-mega-train-scoreboard.md", scoreboard)
        from tools.evidence.validate_evidence_bundle import check_scoreboard_lanes_in_progress
        with zipfile.ZipFile(zp) as zf:
            errors = check_scoreboard_lanes_in_progress(zf)
        assert any("IN_PROGRESS" in e for e in errors)

    def test_all_complete_passes(self, tmp_path):
        scoreboard = "| L | Final | COMPLETE | reports/r58/final-verdict.md |\n**SCOREBOARD_STATUS: ALL_COMPLETE**"
        zp = tmp_path / "r58.zip"
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/reports/r58/multi-mega-train-scoreboard.md", scoreboard)
        from tools.evidence.validate_evidence_bundle import check_scoreboard_lanes_in_progress
        with zipfile.ZipFile(zp) as zf:
            errors = check_scoreboard_lanes_in_progress(zf)
        assert errors == []

    def test_final_verdict_in_progress_fails(self, tmp_path):
        verdict = "**Verdict:** R58_PROGRESS\n| L | IN_PROGRESS | Final bundle |"
        zp = tmp_path / "r58.zip"
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/reports/r58/final-verdict.md", verdict)
        from tools.evidence.validate_evidence_bundle import check_scoreboard_lanes_in_progress
        with zipfile.ZipFile(zp) as zf:
            errors = check_scoreboard_lanes_in_progress(zf)
        # R59 Train B renamed error code from VERDICT_TRAIN_IN_PROGRESS to VERDICT_TRAIN_INCOMPLETE
        assert any("VERDICT_TRAIN_INCOMPLETE" in e or "IN_PROGRESS" in e for e in errors)

    def test_no_scoreboard_no_error(self, tmp_path):
        zp = tmp_path / "r58.zip"
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/README.md", "test")
        from tools.evidence.validate_evidence_bundle import check_scoreboard_lanes_in_progress
        with zipfile.ZipFile(zp) as zf:
            errors = check_scoreboard_lanes_in_progress(zf)
        assert errors == []
