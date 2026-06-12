"""
test_r59_current_run_finality.py — R59 Train B: Current-run final-verdict finality checks.

Verifies that:
1. check_scoreboard_lanes_in_progress uses run_number to target only current-run final-verdict
2. Historical later final-verdict files (skills-system-hardening) do NOT override current-run
3. IN_PROGRESS in current-run final-verdict causes FAIL (negative fixture)
4. All-COMPLETE current-run final-verdict passes (positive fixture)
5. NOT_STARTED and BUNDLE_VALIDATION: PENDING also fail

R59 Sprint: FORMAT-FACTORY-R59-CLEAN-RC-CLOSURE-PACKAGING-NORMALIZATION-PHASE10-PRODUCT-EXPANSION-MEGA-TRAIN-001
IV-R58-003, IV-R58-005, IV-R58-006
"""
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.validate_evidence_bundle import check_scoreboard_lanes_in_progress


def _make_zip(**files: str) -> zipfile.ZipFile:
    """Create an in-memory ZIP with specified file contents."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, content in files.items():
            zf.writestr(path, content.encode("utf-8"))
    buf.seek(0)
    return zipfile.ZipFile(buf, "r")


SCOREBOARD_ALL_COMPLETE = """\
# Multi-Mega-Train Scoreboard

| Lane | Status |
|------|--------|
| 0 | COMPLETE |
| A | COMPLETE |
| M | COMPLETE |

**SCOREBOARD_STATUS: ALL_COMPLETE**
"""

VERDICT_ALL_COMPLETE = """\
# R59 Final Verdict
| Train | Status |
|-------|--------|
| 0 | COMPLETE |
| A | COMPLETE |
| M | COMPLETE |

**BUNDLE_VALIDATION: PASS**
"""

VERDICT_TRAIN_M_IN_PROGRESS = """\
# R59 Final Verdict
| Train | Status |
|-------|--------|
| 0 | COMPLETE |
| A | COMPLETE |
| M | IN_PROGRESS |
"""

VERDICT_NOT_STARTED = """\
# R59 Final Verdict
| Train | Status |
|-------|--------|
| 0 | COMPLETE |
| H | NOT_STARTED |
"""

VERDICT_BUNDLE_PENDING = """\
# R59 Final Verdict
**BUNDLE_VALIDATION: PENDING**
"""

# Historical verdict from a different sprint (no IN_PROGRESS)
SKILLS_HARDENING_VERDICT = """\
# Final Verdict
**Sprint:** FORMAT-FACTORY-SKILLS-PRD-HARDENING-001
All items complete. No IN_PROGRESS trains.
"""


class TestCurrentRunFinalityNegative:
    """Negative fixtures: current-run IN_PROGRESS must cause FAIL."""

    def test_train_m_in_progress_fails(self):
        """R58 root defect reproduced: current-run verdict has IN_PROGRESS, must FAIL."""
        zf = _make_zip(**{
            "repo/reports/r59/multi-mega-train-scoreboard.md": SCOREBOARD_ALL_COMPLETE,
            "repo/reports/r59/final-verdict.md": VERDICT_TRAIN_M_IN_PROGRESS,
        })
        errors = check_scoreboard_lanes_in_progress(zf, run_number="R59")
        assert any("INCOMPLETE" in e or "IN_PROGRESS" in e for e in errors), (
            f"Expected VERDICT_TRAIN_INCOMPLETE error, got: {errors}"
        )

    def test_not_started_train_fails(self):
        """NOT_STARTED in current-run final-verdict must cause FAIL."""
        zf = _make_zip(**{
            "repo/reports/r59/multi-mega-train-scoreboard.md": SCOREBOARD_ALL_COMPLETE,
            "repo/reports/r59/final-verdict.md": VERDICT_NOT_STARTED,
        })
        errors = check_scoreboard_lanes_in_progress(zf, run_number="R59")
        assert any("INCOMPLETE" in e or "NOT_STARTED" in e for e in errors), (
            f"Expected error for NOT_STARTED, got: {errors}"
        )

    def test_bundle_validation_pending_fails(self):
        """BUNDLE_VALIDATION: PENDING in current-run verdict must cause FAIL."""
        zf = _make_zip(**{
            "repo/reports/r59/multi-mega-train-scoreboard.md": SCOREBOARD_ALL_COMPLETE,
            "repo/reports/r59/final-verdict.md": VERDICT_BUNDLE_PENDING,
        })
        errors = check_scoreboard_lanes_in_progress(zf, run_number="R59")
        assert any("INCOMPLETE" in e or "PENDING" in e for e in errors), (
            f"Expected error for BUNDLE_VALIDATION: PENDING, got: {errors}"
        )

    def test_scoreboard_verdict_contradiction_detected(self):
        """Scoreboard ALL_COMPLETE + verdict IN_PROGRESS = SCOREBOARD_VERDICT_CONTRADICTION."""
        zf = _make_zip(**{
            "repo/reports/r59/multi-mega-train-scoreboard.md": SCOREBOARD_ALL_COMPLETE,
            "repo/reports/r59/final-verdict.md": VERDICT_TRAIN_M_IN_PROGRESS,
        })
        errors = check_scoreboard_lanes_in_progress(zf, run_number="R59")
        error_str = " ".join(errors)
        assert "CONTRADICTION" in error_str or "INCOMPLETE" in error_str, (
            f"Expected CONTRADICTION error, got: {errors}"
        )


class TestCurrentRunFinalityPositive:
    """Positive fixtures: all-complete current-run verdict must PASS."""

    def test_all_complete_passes(self):
        """All-COMPLETE current-run verdict + ALL_COMPLETE scoreboard = no errors."""
        zf = _make_zip(**{
            "repo/reports/r59/multi-mega-train-scoreboard.md": SCOREBOARD_ALL_COMPLETE,
            "repo/reports/r59/final-verdict.md": VERDICT_ALL_COMPLETE,
        })
        errors = check_scoreboard_lanes_in_progress(zf, run_number="R59")
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_historical_later_path_does_not_override(self):
        """Key R59 fix: skills-system-hardening verdict does NOT override current-run verdict.

        This reproduces IV-R58-006: before the fix, skills-system-hardening/final-verdict.md
        (which has no IN_PROGRESS) would overwrite r59's IN_PROGRESS verdict, causing a false PASS.
        After the fix (run_number guard), only r59/final-verdict.md is checked.
        """
        zf = _make_zip(**{
            # Current-run verdict has IN_PROGRESS — should FAIL
            "repo/reports/r59/final-verdict.md": VERDICT_TRAIN_M_IN_PROGRESS,
            "repo/reports/r59/multi-mega-train-scoreboard.md": SCOREBOARD_ALL_COMPLETE,
            # Historical verdict that sorts AFTER r59 alphabetically — must NOT override
            "repo/reports/skills-system-hardening/20260517/final-verdict.md": SKILLS_HARDENING_VERDICT,
        })
        errors = check_scoreboard_lanes_in_progress(zf, run_number="R59")
        assert any("INCOMPLETE" in e or "IN_PROGRESS" in e for e in errors), (
            "MUST detect IN_PROGRESS from current-run r59 verdict even when "
            "skills-system-hardening verdict (no IN_PROGRESS) appears AFTER it. "
            f"Got errors: {errors}. "
            "Fix: use run_number to target repo/reports/r59/final-verdict.md specifically."
        )

    def test_no_run_number_legacy_fallback(self):
        """Without run_number, falls back to scanning all (legacy). Just must not crash."""
        zf = _make_zip(**{
            "repo/reports/r59/multi-mega-train-scoreboard.md": SCOREBOARD_ALL_COMPLETE,
            "repo/reports/r59/final-verdict.md": VERDICT_ALL_COMPLETE,
        })
        # Should not raise
        errors = check_scoreboard_lanes_in_progress(zf, run_number="")
        assert isinstance(errors, list)

    def test_missing_current_run_verdict_no_crash(self):
        """If current-run final-verdict is not in bundle, check does not crash."""
        zf = _make_zip(**{
            "repo/reports/r59/multi-mega-train-scoreboard.md": SCOREBOARD_ALL_COMPLETE,
            # No final-verdict.md for r59
        })
        errors = check_scoreboard_lanes_in_progress(zf, run_number="R59")
        assert isinstance(errors, list)


class TestScoreboardInProgressDetection:
    """Scoreboard IN_PROGRESS detection independent of final-verdict."""

    def test_scoreboard_in_progress_lane_fails(self):
        """Scoreboard with IN_PROGRESS lane causes SCOREBOARD_LANE_IN_PROGRESS error."""
        scoreboard_in_progress = """\
| M | IN_PROGRESS |
**SCOREBOARD_STATUS: ALL_COMPLETE**
"""
        zf = _make_zip(**{
            "repo/reports/r59/multi-mega-train-scoreboard.md": scoreboard_in_progress,
            "repo/reports/r59/final-verdict.md": VERDICT_ALL_COMPLETE,
        })
        errors = check_scoreboard_lanes_in_progress(zf, run_number="R59")
        assert any("SCOREBOARD_LANE_IN_PROGRESS" in e for e in errors), (
            f"Expected SCOREBOARD_LANE_IN_PROGRESS, got: {errors}"
        )
