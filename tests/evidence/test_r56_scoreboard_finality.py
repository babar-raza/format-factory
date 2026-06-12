"""
test_r56_scoreboard_finality.py — R56 Train B: Scoreboard finality enforcement tests.

Validates the new R56 rule: if a sprint scoreboard contains status IN_PROGRESS or
trains with PENDING status, the final verdict must NOT claim COMPLETE/PASS.

R56 Sprint: FORMAT-FACTORY-R56-R55-CLOSURE-REPAIR-PACKAGE-RC-PHASE7-PRODUCT-EXPANSION-MEGA-TRAIN-001
IV-R55-004
"""
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.validate_evidence_bundle import check_scoreboard_finality


def _make_bundle_with_scoreboard(
    scoreboard_content: str,
    verdict_content: str,
    verdict_file: str = "final-verdict.md",
) -> "zipfile.ZipFile":
    """Create an in-memory ZipFile with the given scoreboard and verdict content."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("repo/reports/rXX/multi-mega-train-scoreboard.md", scoreboard_content)
        zf.writestr(f"bundle-metadata/{verdict_file}", verdict_content)
    buf.seek(0)
    return zipfile.ZipFile(buf, "r")


SCOREBOARD_IN_PROGRESS = """\
# R55 Multi-Mega-Train Scoreboard
**Status:** IN_PROGRESS

| Train | Status |
|-------|--------|
| A | PENDING |
| B | PENDING |
"""

SCOREBOARD_COMPLETE = """\
# R55 Multi-Mega-Train Scoreboard
**Status:** COMPLETE

| Train | Status | Tests Added |
|-------|--------|-------------|
| A | COMPLETE | 8 |
| B | COMPLETE | 14 |
"""

VERDICT_COMPLETE = """\
**Verdict:** R55_STATE_MULTI_MEGA_TRAIN_RC_PHASE6_COMPLETE
BUNDLE_VALIDATION: PASS
"""

VERDICT_IN_PROGRESS = """\
**Verdict:** R55_STATE_IN_PROGRESS
"""


class TestScoreboardFinality:

    def test_in_progress_scoreboard_with_complete_verdict_fails(self):
        """Scoreboard IN_PROGRESS + verdict COMPLETE is a contradiction (IV-R55-004)."""
        meta = {"final-verdict.md": VERDICT_COMPLETE}
        with _make_bundle_with_scoreboard(SCOREBOARD_IN_PROGRESS, VERDICT_COMPLETE) as zf:
            errors = check_scoreboard_finality(zf, meta)
        assert errors, "IN_PROGRESS scoreboard with COMPLETE verdict must fail"
        assert any("SCOREBOARD_NOT_FINALIZED" in e for e in errors)

    def test_complete_scoreboard_with_complete_verdict_passes(self):
        """Scoreboard COMPLETE + verdict COMPLETE is valid."""
        meta = {"final-verdict.md": VERDICT_COMPLETE}
        with _make_bundle_with_scoreboard(SCOREBOARD_COMPLETE, VERDICT_COMPLETE) as zf:
            errors = check_scoreboard_finality(zf, meta)
        assert errors == [], f"Completed scoreboard must pass: {errors}"

    def test_in_progress_scoreboard_with_non_complete_verdict_passes(self):
        """Scoreboard IN_PROGRESS is acceptable when verdict itself says IN_PROGRESS (planning doc)."""
        meta = {"final-verdict.md": VERDICT_IN_PROGRESS}
        with _make_bundle_with_scoreboard(SCOREBOARD_IN_PROGRESS, VERDICT_IN_PROGRESS) as zf:
            errors = check_scoreboard_finality(zf, meta)
        assert errors == [], f"IN_PROGRESS verdict with IN_PROGRESS scoreboard must pass: {errors}"

    def test_no_scoreboard_in_bundle_passes(self):
        """Bundle without any scoreboard file is not penalized."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("bundle-metadata/final-verdict.md", VERDICT_COMPLETE)
        buf.seek(0)
        meta = {"final-verdict.md": VERDICT_COMPLETE}
        with zipfile.ZipFile(buf, "r") as zf:
            errors = check_scoreboard_finality(zf, meta)
        assert errors == [], f"Missing scoreboard should not fail: {errors}"

    def test_r55_exact_defect_scenario(self):
        """Reproduce the exact R55 IV-R55-004 defect: scoreboard PENDING + verdict COMPLETE."""
        # R55 scoreboard had Status: IN_PROGRESS, all trains PENDING, all test counts 0
        r55_scoreboard = """\
# R55 Multi-Mega-Train Scoreboard
**Sprint:** FORMAT-FACTORY-R55-MULTI-MEGA-TRAIN-PRODUCT-RC-PHASE6-ACQUISITION-AI-VALIDATOR-001
**Date:** 2026-05-23
**Status:** IN_PROGRESS

| Train | Name | Status | Tests Added |
|-------|------|--------|-------------|
| A | Validator Repair | PENDING | 0 |
| B | FODT Full Preservation | PENDING | 0 |
| K | Final IV + Bundle | PENDING | — |

**Total tests added so far:** 0 (sprint not yet started)
"""
        r55_verdict = """\
**Verdict:** R55_STATE_MULTI_MEGA_TRAIN_RC_PHASE6_COMPLETE
BUNDLE_VALIDATION: PASS
"""
        meta = {"final-verdict.md": r55_verdict}
        with _make_bundle_with_scoreboard(r55_scoreboard, r55_verdict) as zf:
            errors = check_scoreboard_finality(zf, meta)
        assert errors, "R55 defect IV-R55-004 scenario must fail validation"
        assert any("SCOREBOARD_NOT_FINALIZED" in e for e in errors)
