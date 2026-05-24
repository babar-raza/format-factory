"""
test_r59_scoreboard_verdict_consistency.py — R59 Train B: Scoreboard/verdict consistency checks.

Verifies:
1. Scoreboard ALL_COMPLETE + verdict ALL_COMPLETE = PASS
2. Scoreboard ALL_COMPLETE + verdict IN_PROGRESS = FAIL (contradiction)
3. Scoreboard IN_PROGRESS + verdict COMPLETE = FAIL
4. Both IN_PROGRESS = FAIL

R59 Sprint: FORMAT-FACTORY-R59-CLEAN-RC-CLOSURE-PACKAGING-NORMALIZATION-PHASE10-PRODUCT-EXPANSION-MEGA-TRAIN-001
IV-R58-004
"""
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.validate_evidence_bundle import check_scoreboard_lanes_in_progress


def _make_zip(**files: str) -> zipfile.ZipFile:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, content in files.items():
            zf.writestr(path, content.encode("utf-8"))
    buf.seek(0)
    return zipfile.ZipFile(buf, "r")


class TestScoreboardVerdictConsistency:
    """Cross-check scoreboard and current-run final-verdict consistency."""

    def test_both_complete_passes(self):
        """Scoreboard ALL_COMPLETE + verdict no incomplete tokens = PASS."""
        zf = _make_zip(**{
            "repo/reports/r59/multi-mega-train-scoreboard.md":
                "**SCOREBOARD_STATUS: ALL_COMPLETE**\n| M | COMPLETE |",
            "repo/reports/r59/final-verdict.md":
                "| M | COMPLETE | Done |\n**BUNDLE_VALIDATION: PASS**",
        })
        errors = check_scoreboard_lanes_in_progress(zf, run_number="R59")
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_scoreboard_complete_verdict_in_progress_fails(self):
        """Scoreboard ALL_COMPLETE but verdict has IN_PROGRESS = contradiction."""
        zf = _make_zip(**{
            "repo/reports/r59/multi-mega-train-scoreboard.md":
                "**SCOREBOARD_STATUS: ALL_COMPLETE**",
            "repo/reports/r59/final-verdict.md":
                "| M | IN_PROGRESS | Not done yet |",
        })
        errors = check_scoreboard_lanes_in_progress(zf, run_number="R59")
        assert len(errors) >= 1, f"Expected contradiction error, got: {errors}"
        error_str = " ".join(errors)
        assert "INCOMPLETE" in error_str or "CONTRADICTION" in error_str, (
            f"Expected INCOMPLETE or CONTRADICTION error, got: {errors}"
        )

    def test_scoreboard_in_progress_lane_fails(self):
        """Scoreboard with IN_PROGRESS lane fails regardless of verdict."""
        zf = _make_zip(**{
            "repo/reports/r59/multi-mega-train-scoreboard.md":
                "| M | IN_PROGRESS |\n**SCOREBOARD_STATUS: ALL_COMPLETE**",
            "repo/reports/r59/final-verdict.md":
                "| M | COMPLETE | Done |",
        })
        errors = check_scoreboard_lanes_in_progress(zf, run_number="R59")
        assert any("SCOREBOARD_LANE_IN_PROGRESS" in e for e in errors), (
            f"Expected SCOREBOARD_LANE_IN_PROGRESS error, got: {errors}"
        )

    def test_r58_scenario_reproduced(self):
        """Reproduces R58 defect: scoreboard ALL_COMPLETE, verdict IN_PROGRESS, validator MUST FAIL.

        Before R59 fix: the loop overwrites r58 verdict with skills-hardening verdict (no IN_PROGRESS),
        causing a false PASS. After fix: run_number="R58" targets r58/final-verdict.md specifically.
        """
        zf = _make_zip(**{
            # R58 scoreboard: ALL_COMPLETE
            "repo/reports/r58/multi-mega-train-scoreboard.md":
                "**SCOREBOARD_STATUS: ALL_COMPLETE**\n| M | COMPLETE |",
            # R58 final-verdict: Train M IN_PROGRESS (actual R58 defect)
            "repo/reports/r58/final-verdict.md":
                "| M | IN_PROGRESS | Final adversarial IV + evidence bundle |",
            # Skills-hardening verdict sorts AFTER r58/ — had no IN_PROGRESS, caused false PASS
            "repo/reports/skills-system-hardening/20260517/final-verdict.md":
                "All items complete. No IN_PROGRESS trains.",
        })
        errors = check_scoreboard_lanes_in_progress(zf, run_number="R58")
        assert any("INCOMPLETE" in e or "IN_PROGRESS" in e or "CONTRADICTION" in e for e in errors), (
            "R58 scenario must FAIL: r58/final-verdict has IN_PROGRESS, "
            "skills-hardening verdict must not override it. "
            f"Got errors: {errors}"
        )
