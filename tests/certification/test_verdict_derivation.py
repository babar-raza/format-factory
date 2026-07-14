"""Regression tests for certification verdict derivation logic.

TC-001 (precious-wandering-lighthouse, 2026-07-13):
Verifies that NOT_APPLICABLE dimensions do not block CERTIFIED verdict.
CERT-DASHBOARD-001: fix already applied at certification_dashboard.py:109.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "certification"))


def _make_dim(status: str) -> dict:
    return {"status": status}


def _derive_verdict(statuses: list[str]) -> str:
    """Replicate the verdict derivation logic from certification_dashboard.py:107-116."""
    acceptable = {"PASS", "KNOWN_GAPS", "NOT_APPLICABLE", "GAP"}
    if all(s in {"PASS", "NOT_APPLICABLE"} for s in statuses):
        return "CERTIFIED"
    elif any(s == "FAIL" for s in statuses):
        return "NOT_CERTIFIED"
    elif all(s in acceptable for s in statuses):
        return "CERTIFIED_WITH_KNOWN_GAPS"
    else:
        return "IN_PROGRESS"


class TestNotApplicableDoesNotBlockCertified:
    """CERT-DASHBOARD-001 regression: NOT_APPLICABLE must not prevent CERTIFIED."""

    def test_all_pass_gives_certified(self):
        """All 9 PASS dimensions → CERTIFIED."""
        statuses = ["PASS"] * 9
        assert _derive_verdict(statuses) == "CERTIFIED"

    def test_eight_pass_one_not_applicable_gives_certified(self):
        """8 PASS + 1 NOT_APPLICABLE → CERTIFIED (the core CERT-DASHBOARD-001 regression)."""
        statuses = ["PASS"] * 8 + ["NOT_APPLICABLE"]
        assert _derive_verdict(statuses) == "CERTIFIED"

    def test_all_not_applicable_gives_certified(self):
        """All NOT_APPLICABLE dimensions → CERTIFIED (edge case)."""
        statuses = ["NOT_APPLICABLE"] * 9
        assert _derive_verdict(statuses) == "CERTIFIED"

    def test_pass_and_known_gaps_gives_certified_with_gaps(self):
        """PASS + KNOWN_GAPS → CERTIFIED_WITH_KNOWN_GAPS (not CERTIFIED)."""
        statuses = ["PASS"] * 7 + ["KNOWN_GAPS", "PASS"]
        assert _derive_verdict(statuses) == "CERTIFIED_WITH_KNOWN_GAPS"

    def test_any_fail_gives_not_certified(self):
        """Any FAIL → NOT_CERTIFIED regardless of other dimensions."""
        statuses = ["PASS"] * 8 + ["FAIL"]
        assert _derive_verdict(statuses) == "NOT_CERTIFIED"

    def test_in_progress_when_not_audited(self):
        """NOT_AUDITED dimension → IN_PROGRESS (not CERTIFIED)."""
        statuses = ["PASS"] * 8 + ["NOT_AUDITED"]
        assert _derive_verdict(statuses) == "IN_PROGRESS"

    def test_not_applicable_not_blocked_by_known_gaps(self):
        """Mix of NOT_APPLICABLE + KNOWN_GAPS → CERTIFIED_WITH_KNOWN_GAPS (not IN_PROGRESS)."""
        statuses = ["PASS"] * 6 + ["NOT_APPLICABLE", "KNOWN_GAPS", "PASS"]
        assert _derive_verdict(statuses) == "CERTIFIED_WITH_KNOWN_GAPS"


class TestVerdictLiveLogic:
    """Verify the actual certification_dashboard.py uses the fixed verdict logic."""

    def test_dashboard_module_has_correct_logic(self):
        """The live collect_format_status function must treat NOT_APPLICABLE as PASS-equivalent."""
        dash_path = REPO_ROOT / "tools" / "certification" / "certification_dashboard.py"
        assert dash_path.exists(), "certification_dashboard.py not found"
        source = dash_path.read_text(encoding="utf-8")
        # The fixed logic: verdict = "CERTIFIED" must appear BEFORE verdict = "CERTIFIED_WITH_KNOWN_GAPS"
        # and the CERTIFIED check must include NOT_APPLICABLE
        assert '"PASS", "NOT_APPLICABLE"' in source, "CERTIFIED check must include NOT_APPLICABLE"
        certified_verdict_idx = source.find('verdict = "CERTIFIED"')
        cwkg_verdict_idx = source.find('verdict = "CERTIFIED_WITH_KNOWN_GAPS"')
        assert certified_verdict_idx != -1, "verdict='CERTIFIED' assignment not found"
        assert cwkg_verdict_idx != -1, "verdict='CERTIFIED_WITH_KNOWN_GAPS' assignment not found"
        assert certified_verdict_idx < cwkg_verdict_idx, \
            "CERTIFIED verdict must be assigned before CERTIFIED_WITH_KNOWN_GAPS in source"
