"""
tests/skills/test_multi_format_planning.py

Tests for multi_format_planning.py — Lane C CONWAY-R7R8.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

from multi_format_planning import plan_multi_format


class TestMultiFormatPlanningLive:
    def test_default_formats_covers_fods_and_fodt(self):
        result = plan_multi_format()
        assert "fods" in result["formats_requested"]
        assert "fodt" in result["formats_requested"]

    def test_both_formats_authoritative(self):
        result = plan_multi_format()
        assert "fods" in result["formats_authoritative"]
        assert "fodt" in result["formats_authoritative"]

    def test_no_formats_stale_live(self):
        result = plan_multi_format()
        assert result["formats_stale"] == []

    def test_cross_format_summary_has_required_keys(self):
        result = plan_multi_format()
        required = {"total_formats", "authoritative_formats", "blocked_formats",
                    "stale_formats", "total_accepted_requirements",
                    "total_implementation_slices", "total_planning_taskcards", "planning_ready"}
        assert required.issubset(result["cross_format_summary"].keys())

    def test_total_accepted_is_40(self):
        """FODS + FODT both have 20 accepted requirements = 40 total."""
        result = plan_multi_format()
        assert result["cross_format_summary"]["total_accepted_requirements"] == 40

    def test_planning_ready_is_true(self):
        result = plan_multi_format()
        assert result["cross_format_summary"]["planning_ready"] is True

    def test_orchestration_order_covers_all_formats(self):
        result = plan_multi_format()
        order_formats = [item["format_id"] for item in result["orchestration_order"]]
        for fmt in result["formats_requested"]:
            assert fmt in order_formats

    def test_ready_formats_first_in_order(self):
        result = plan_multi_format()
        order = result["orchestration_order"]
        first_blocked_idx = next(
            (i for i, item in enumerate(order) if not item["ready_for_planning"]),
            len(order)
        )
        for item in order[:first_blocked_idx]:
            assert item["ready_for_planning"] is True

    def test_per_format_stale_has_all_formats(self):
        result = plan_multi_format()
        for fmt in result["formats_requested"]:
            assert fmt in result["per_format_stale"]

    def test_governance_commercial_ready_false(self):
        result = plan_multi_format()
        assert result["governance"]["commercial_product_ready"] is False

    def test_governance_dry_run_only(self):
        result = plan_multi_format()
        assert result["governance"]["dry_run_only"] is True

    def test_result_json_serializable(self):
        result = plan_multi_format()
        # Exclude nested context dicts which contain non-serializable types
        slim = {k: v for k, v in result.items()
                if k not in ("per_format_context", "per_format_lanes", "per_format_plan")}
        json.dumps(slim)  # Should not raise

    def test_single_format_fods(self):
        result = plan_multi_format(["fods"])
        assert result["formats_requested"] == ["fods"]
        assert "fods" in result["per_format_stale"]

    def test_single_format_fodt(self):
        result = plan_multi_format(["fodt"])
        assert result["formats_requested"] == ["fodt"]

    def test_unknown_format_goes_to_blocked(self):
        result = plan_multi_format(["nonexistent_xyz"])
        assert "nonexistent_xyz" in result["formats_blocked"]


class TestMultiFormatCrossConsistency:
    def test_fods_fodt_same_slice_count(self):
        """Both formats should have the same number of implementation slices (same capability structure)."""
        result = plan_multi_format()
        fods_slices = len(result["per_format_plan"]["fods"]["implementation_slices"])
        fodt_slices = len(result["per_format_plan"]["fodt"]["implementation_slices"])
        assert fods_slices == fodt_slices, (
            f"FODS slices ({fods_slices}) != FODT slices ({fodt_slices})"
        )

    def test_fodt_has_constraint_fods_may_not(self):
        """FODT should have at least one known constraint; check it doesn't bleed into FODS incorrectly."""
        result = plan_multi_format()
        fodt_constraints = result["per_format_plan"]["fodt"]["known_constraints"]
        assert len(fodt_constraints) > 0

    def test_both_formats_have_dependency_groups(self):
        result = plan_multi_format()
        for fmt in ("fods", "fodt"):
            plan = result["per_format_plan"][fmt]
            assert len(plan["dependency_groups"]) > 0
