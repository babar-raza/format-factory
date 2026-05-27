"""R68 Train E: Verify R67 final reports have no closeout-hygiene placeholders.

Proves that the repaired R67 final-independent-verification.md and
lane-ownership.md do NOT contain [to be filled] or PENDING tokens.

R68 Sprint: FORMAT-FACTORY-R68-FINAL-CLOSEOUT-HYGIENE-LOCAL-RC-SEAL-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORTS_R67 = PROJECT_ROOT / "reports" / "r67"

# Tokens that must NOT appear in these final report files
FORBIDDEN_TOKENS = [
    "[to be filled]",
    "[to be filled at closeout]",
    "[commit sha to be filled]",
]


class TestR67FinalReportsNoPLaceholders:
    """Verify that R67 final reports were properly filled in (R68 Train C repair)."""

    @pytest.mark.parametrize("token", FORBIDDEN_TOKENS)
    def test_final_iv_no_placeholder(self, token):
        """reports/r67/final-independent-verification.md has no [to be filled] tokens."""
        fpath = REPORTS_R67 / "final-independent-verification.md"
        assert fpath.exists(), f"Missing: {fpath}"
        content = fpath.read_text(encoding="utf-8").lower()
        assert token not in content, (
            f"final-independent-verification.md contains stale placeholder {token!r} "
            f"— R68 Train C repair incomplete."
        )

    def test_final_iv_has_final_iv_verdict(self):
        """final-independent-verification.md must have FINAL_IV: line (not [to be filled])."""
        fpath = REPORTS_R67 / "final-independent-verification.md"
        assert fpath.exists(), f"Missing: {fpath}"
        content = fpath.read_text(encoding="utf-8")
        assert "FINAL_IV:" in content, "Missing FINAL_IV: line"
        iv_lines = [l for l in content.splitlines() if l.strip().startswith("FINAL_IV:")]
        assert iv_lines, "FINAL_IV: line not found"
        iv_value = iv_lines[0].split(":", 1)[1].strip()
        assert "[to be filled" not in iv_value.lower(), (
            f"FINAL_IV value is still a placeholder: {iv_value!r}"
        )

    def test_lane_ownership_no_pending_closures(self):
        """reports/r67/lane-ownership.md should have no PENDING rows for core trains."""
        fpath = REPORTS_R67 / "lane-ownership.md"
        assert fpath.exists(), f"Missing: {fpath}"
        content = fpath.read_text(encoding="utf-8")
        # Core closure lanes A-F must be COMPLETE, not PENDING
        closure_lanes = ["| A —", "| B —", "| C —", "| D —", "| E —", "| F —"]
        for lane_prefix in closure_lanes:
            lines = [l for l in content.splitlines() if lane_prefix in l]
            for line in lines:
                assert "PENDING" not in line, (
                    f"Core closure lane line has PENDING status: {line.strip()!r}"
                )


class TestR67PythonTestsSummaryNoPLaceholders:
    """Verify R67 python-tests-summary.txt is finalized (no TBD/UNKNOWN)."""

    def test_no_tbd_in_summary(self):
        fpath = PROJECT_ROOT / ".local" / "r67-metadata" / "python-tests-summary.txt"
        if not fpath.exists():
            pytest.skip("R67 metadata not in local dev path")
        content = fpath.read_text(encoding="utf-8")
        assert "TBD" not in content, (
            "python-tests-summary.txt still contains TBD token — not finalized"
        )

    def test_no_unknown_failures_in_summary(self):
        fpath = PROJECT_ROOT / ".local" / "r67-metadata" / "python-tests-summary.txt"
        if not fpath.exists():
            pytest.skip("R67 metadata not in local dev path")
        content = fpath.read_text(encoding="utf-8")
        # UNKNOWN (N — pattern indicates unresolved unknown failures
        import re
        assert not re.search(r"UNKNOWN \(\d+", content), (
            "python-tests-summary.txt still contains UNKNOWN failures — not resolved"
        )
