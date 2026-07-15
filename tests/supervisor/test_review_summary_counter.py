"""TC-REVIEW-COUNTER-FIX-001: Regression tests for supervisor review summary Rework counter.

The summary header "Rework: N" and "Critical Rework: N" must reflect actual item-grade-based
rework counts, NOT governance structural blocks (GOV_BLOCK: entries added to rework_items
by autonomous_cycle.py governance validation logic).

Root cause: When all items are ACCEPTED_VERIFIED but a governance validator blocks_sprint,
autonomous_cycle.py appended 'GOV_BLOCK:monolith_detection_validator' to review['rework_items']
and incremented review['critical_rework_count']. write_outputs() then wrote misleading counts
to supervisor-review.md (copied to latest-review.md).

Fix: write_outputs() now computes Rework/Critical Rework from item_grades directly.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


def _make_review(
    item_grades: list[dict],
    rework_items: list | None = None,
    critical_rework_count: int = 0,
) -> dict:
    """Build a minimal review dict for testing write_outputs()."""
    accepted = [g["item_id"] for g in item_grades if g["supervisor_grade"] in
                ("ACCEPTED", "ACCEPTED_VERIFIED", "UNVERIFIED", "ACCEPTED_WITH_LIMITATIONS")]
    rework = [g["item_id"] for g in item_grades if g["supervisor_grade"] in
              ("REWORK_REQUIRED", "OVERCLAIMED")]
    return {
        "run_id": "TEST-RUN-001",
        "sprint_id": "test-sprint",
        "timestamp": datetime.now().isoformat(),
        "overall_verdict": "ACCEPTED",
        "autonomous_continue": True,
        "stop_reason": "",
        "item_grades": item_grades,
        "accepted_items": accepted,
        "rework_items": rework_items if rework_items is not None else rework,
        "rejected_items": [],
        "overclaimed_items": [],
        "critical_rework_count": critical_rework_count,
        "evidence_quality_score": 1.0,
        "verified_item_count": len(accepted),
        "cycle_number": 1,
        "deferred_items": [],
        "evidence_quality_breakdown": {},
        "forward_work_items": [],
    }


def _accepted_verified(item_id: str) -> dict:
    return {
        "item_id": item_id,
        "item_title": f"Test {item_id}",
        "supervisor_grade": "ACCEPTED_VERIFIED",
        "required_rework": "",
        "tests_supporting": [],
    }


def _overclaimed(item_id: str) -> dict:
    return {
        "item_id": item_id,
        "item_title": f"Test {item_id}",
        "supervisor_grade": "OVERCLAIMED",
        "required_rework": "Provide better evidence",
        "tests_supporting": [],
    }


class TestReviewSummaryCounter:
    """TC-REVIEW-COUNTER-FIX-001: Rework counter in supervisor-review.md must reflect item grades."""

    def _get_summary_line(self, review: dict, label: str) -> str:
        """Write review to temp dir and read the generated summary line."""
        from grade_declared_work import write_outputs
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            write_outputs(review, output_dir)
            text = (output_dir / "supervisor-review.md").read_text(encoding="utf-8")
            for line in text.splitlines():
                if line.startswith(f"- {label}:"):
                    return line
        return ""

    def test_all_accepted_with_gov_block_rework_shows_zero(self) -> None:
        """All items ACCEPTED_VERIFIED + GOV_BLOCK in rework_items → Rework: 0 in header.

        This is the core regression: the header must NOT count GOV_BLOCK: entries.
        """
        review = _make_review(
            item_grades=[_accepted_verified("TC-T-001"), _accepted_verified("TC-T-002")],
            rework_items=["GOV_BLOCK:monolith_detection_validator"],  # simulates polluted state
            critical_rework_count=1,  # inflated by autonomous_cycle
        )
        line = self._get_summary_line(review, "Rework")
        assert line == "- Rework: 0", (
            f"Expected '- Rework: 0' when all items are ACCEPTED_VERIFIED; got '{line}'. "
            f"The GOV_BLOCK: entry in rework_items must NOT inflate the displayed count."
        )

    def test_critical_rework_with_gov_block_shows_zero(self) -> None:
        """All items ACCEPTED_VERIFIED + inflated critical_rework_count → Critical Rework: 0."""
        review = _make_review(
            item_grades=[_accepted_verified("TC-T-001")],
            rework_items=["GOV_BLOCK:monolith_detection_validator"],
            critical_rework_count=1,  # inflated by autonomous_cycle governance check
        )
        line = self._get_summary_line(review, "Critical Rework")
        assert line == "- Critical Rework: 0", (
            f"Expected '- Critical Rework: 0' when no items are REJECTED/OVERCLAIMED; got '{line}'. "
            f"The governance-block-inflated critical_rework_count must NOT appear in the header."
        )

    def test_actual_rework_item_shows_correct_count(self) -> None:
        """An OVERCLAIMED item → Rework: 1 in header."""
        review = _make_review(
            item_grades=[_accepted_verified("TC-T-001"), _overclaimed("TC-T-002")],
        )
        line = self._get_summary_line(review, "Rework")
        assert line == "- Rework: 1", (
            f"Expected '- Rework: 1' when one item is OVERCLAIMED; got '{line}'"
        )

    def test_actual_critical_rework_shows_correct_count(self) -> None:
        """An OVERCLAIMED item → Critical Rework: 1 in header (OVERCLAIMED counts as critical)."""
        review = _make_review(
            item_grades=[_overclaimed("TC-T-001")],
        )
        line = self._get_summary_line(review, "Critical Rework")
        assert line == "- Critical Rework: 1", (
            f"Expected '- Critical Rework: 1' when one item is OVERCLAIMED; got '{line}'"
        )

    def test_empty_items_shows_zero_for_both(self) -> None:
        """No items → Rework: 0 and Critical Rework: 0."""
        review = _make_review(item_grades=[])
        rework_line = self._get_summary_line(review, "Rework")
        crit_line = self._get_summary_line(review, "Critical Rework")
        assert rework_line == "- Rework: 0", f"Expected Rework: 0; got '{rework_line}'"
        assert crit_line == "- Critical Rework: 0", f"Expected Critical Rework: 0; got '{crit_line}'"
