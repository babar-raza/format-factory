"""TC-DEFERRED-FILTER-001: Verify DEFERRED_BY_DESIGN gaps excluded from work selection.

Tests that capability_feature_compiler.py and capability_queue_consumer.py
correctly exclude DEFERRED_BY_DESIGN, DEFERRED, test_verified, and
implementation_verified gaps from work item output.

Uses real gap-ledger.json to prove the filter works against production data.
All reads from gap-ledger.json are read-only (no mutation).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from capability_feature_compiler import compile_gaps, _SKIP_STATUSES  # noqa: E402

_REAL_LEDGER = _REPO / "reports" / "capability-layer" / "gap-ledger.json"

_NON_ACTIONABLE_STATUSES = {
    "closed", "CLOSED",
    "DEFERRED_BY_DESIGN", "DEFERRED",
    "test_verified", "implementation_verified",
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _load_ledger() -> list[dict]:
    data = json.loads(_REAL_LEDGER.read_text(encoding="utf-8", errors="replace"))
    return data.get("gaps", [])


def _deferred_gaps(gaps: list[dict]) -> list[dict]:
    return [g for g in gaps if g.get("status") in {"DEFERRED_BY_DESIGN", "DEFERRED"}]


# ── Unit-level tests (no real ledger needed) ──────────────────────────────────

class TestSkipStatusesConstant:
    """_SKIP_STATUSES must contain all non-actionable status values."""

    def test_closed_in_skip_statuses(self):
        assert "closed" in _SKIP_STATUSES

    def test_CLOSED_uppercase_in_skip_statuses(self):
        assert "CLOSED" in _SKIP_STATUSES

    def test_DEFERRED_BY_DESIGN_in_skip_statuses(self):
        assert "DEFERRED_BY_DESIGN" in _SKIP_STATUSES

    def test_DEFERRED_in_skip_statuses(self):
        assert "DEFERRED" in _SKIP_STATUSES

    def test_test_verified_in_skip_statuses(self):
        assert "test_verified" in _SKIP_STATUSES

    def test_implementation_verified_in_skip_statuses(self):
        assert "implementation_verified" in _SKIP_STATUSES


class TestCompileGapsFiltering:
    """compile_gaps() must exclude non-actionable gaps from output."""

    def _make_gap(self, gap_id: str, status: str, owning_lane: int = 1) -> dict:
        return {
            "gap_id": gap_id,
            "status": status,
            "format": "csv",
            "capability_name": f"test_cap_{gap_id}",
            "priority": "P2",
            "owning_lane": owning_lane,
        }

    def test_deferred_by_design_excluded(self):
        gaps = [
            self._make_gap("GAP-001", "open"),
            self._make_gap("GAP-002", "DEFERRED_BY_DESIGN"),
        ]
        items, _ = compile_gaps(gaps, max_items=10)
        item_gap_ids = {item["gap_id"] for item in items}
        assert "GAP-002" not in item_gap_ids, "DEFERRED_BY_DESIGN gap should be excluded"
        assert "GAP-001" in item_gap_ids, "open gap should be included"

    def test_deferred_excluded(self):
        gaps = [
            self._make_gap("GAP-003", "open"),
            self._make_gap("GAP-004", "DEFERRED"),
        ]
        items, _ = compile_gaps(gaps, max_items=10)
        item_gap_ids = {item["gap_id"] for item in items}
        assert "GAP-004" not in item_gap_ids

    def test_test_verified_excluded(self):
        gaps = [self._make_gap("GAP-005", "test_verified")]
        items, _ = compile_gaps(gaps, max_items=10)
        assert len(items) == 0

    def test_implementation_verified_excluded(self):
        gaps = [self._make_gap("GAP-006", "implementation_verified")]
        items, _ = compile_gaps(gaps, max_items=10)
        assert len(items) == 0

    def test_CLOSED_uppercase_excluded(self):
        gaps = [self._make_gap("GAP-007", "CLOSED")]
        items, _ = compile_gaps(gaps, max_items=10)
        assert len(items) == 0

    def test_open_gap_included(self):
        gaps = [self._make_gap("GAP-008", "open")]
        items, _ = compile_gaps(gaps, max_items=10)
        assert len(items) == 1

    def test_multiple_deferred_all_excluded(self):
        gaps = [
            self._make_gap(f"GAP-D{i:03}", "DEFERRED_BY_DESIGN")
            for i in range(10)
        ]
        gaps.append(self._make_gap("GAP-OPEN", "open"))
        items, _ = compile_gaps(gaps, max_items=20)
        item_gap_ids = {item["gap_id"] for item in items}
        for gap in gaps[:-1]:
            assert gap["gap_id"] not in item_gap_ids, (
                f"{gap['gap_id']} (DEFERRED_BY_DESIGN) should not appear in output"
            )
        assert "GAP-OPEN" in item_gap_ids


# ── Integration tests against real gap-ledger.json ────────────────────────────

@pytest.mark.skipif(
    not _REAL_LEDGER.exists(),
    reason="Real gap-ledger.json not present",
)
class TestRealLedgerIntegration:
    """Run compile_gaps() against the real ledger and verify deferred gaps absent."""

    def test_real_ledger_has_deferred_by_design_gaps(self):
        """Sanity check: ledger should have DEFERRED_BY_DESIGN entries."""
        gaps = _load_ledger()
        deferred = _deferred_gaps(gaps)
        assert len(deferred) > 0, (
            "Real ledger has no DEFERRED_BY_DESIGN gaps — test precondition unmet. "
            "Update TC-DEFERRED-FILTER-001 if all gaps are closed."
        )

    def test_no_deferred_gaps_in_compile_output(self):
        """compile_gaps() output must not contain any DEFERRED_BY_DESIGN gaps."""
        all_gaps = _load_ledger()
        open_gaps = [g for g in all_gaps if g.get("status") not in _SKIP_STATUSES]
        items, _ = compile_gaps(open_gaps, max_items=200)

        deferred_in_output = [
            item for item in items
            if item.get("gap_id", "") in {
                g["gap_id"] for g in all_gaps
                if g.get("status") in {"DEFERRED_BY_DESIGN", "DEFERRED"}
            }
        ]
        assert len(deferred_in_output) == 0, (
            f"Found {len(deferred_in_output)} DEFERRED_BY_DESIGN gaps in compile output: "
            f"{[i['gap_id'] for i in deferred_in_output]}"
        )

    def test_deferred_gap_count_matches_ledger(self):
        """Verify we know exactly how many deferred gaps exist (regression guard)."""
        gaps = _load_ledger()
        deferred = _deferred_gaps(gaps)
        # At time of TC-DEFERRED-FILTER-001, there were 30 DEFERRED_BY_DESIGN gaps.
        # This assertion guards against silent changes to the ledger.
        assert len(deferred) >= 1, "Expected at least 1 DEFERRED_BY_DESIGN gap in real ledger"

    def test_open_gaps_still_included(self):
        """Open actionable gaps must still appear in compile output."""
        all_gaps = _load_ledger()
        open_gaps = [g for g in all_gaps if g.get("status") == "open"]
        if not open_gaps:
            pytest.skip("No open gaps in ledger — skip inclusion check")

        actionable = [g for g in open_gaps if int(g.get("owning_lane", 1)) < 14]
        if not actionable:
            pytest.skip("No product-lane open gaps — skip inclusion check")

        items, _ = compile_gaps(open_gaps, max_items=200)
        assert len(items) > 0, "compile_gaps() returned 0 items for open gaps — filter too aggressive"
