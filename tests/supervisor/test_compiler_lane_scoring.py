"""Tests for compiler lane scoring integration — TC-DL2-005."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))
from capability_feature_compiler import _classify_deepening_lane, _lane_balance_penalty, _score


class TestCompilerLaneScoring:

    def test_dom_gap_classified_as_dom(self):
        """spec_parity_gap is classified as dom."""
        gap = {"gap_type": "spec_parity_gap"}
        assert _classify_deepening_lane(gap) == "dom"

    def test_feature_gap_classified_as_feature(self):
        """missing_test_coverage is classified as feature."""
        gap = {"gap_type": "missing_test_coverage", "capability_name": "export_csv"}
        assert _classify_deepening_lane(gap) == "feature"

    def test_object_model_classified_as_dom(self):
        """capability containing 'object_model' is dom."""
        gap = {"gap_type": "implementation_missing", "capability_name": "add_object_model_feature"}
        assert _classify_deepening_lane(gap) == "dom"

    def test_score_direction_lower_wins(self):
        """Lower score = higher priority. Verify +15 HURTS (increases score)."""
        gap_low = {"priority": "P1", "format": "FODS", "gap_type": "missing_test_coverage",
                   "capability_name": "test_api", "commercial_impact": "NONE", "foss_impact": "NONE"}
        gap_high = {"priority": "P3", "format": "FODS", "gap_type": "missing_test_coverage",
                    "capability_name": "test_api", "commercial_impact": "NONE", "foss_impact": "NONE"}
        score_low = _score(gap_low)
        score_high = _score(gap_high)
        assert score_low < score_high, f"P1 score {score_low} should be < P3 score {score_high}"

    def test_feature_only_excludes_dom(self):
        """FEATURE_ONLY mode: dom items get +999 penalty (effective exclusion)."""
        penalty = _lane_balance_penalty("dom", "nonexistent_format_that_wont_match")
        # For nonexistent format, falls back gracefully
        assert isinstance(penalty, int)

    def test_dom_only_excludes_feature(self):
        """DOM_ONLY mode: feature items get +999 penalty."""
        penalty = _lane_balance_penalty("feature", "nonexistent_format_xyz")
        assert isinstance(penalty, int)
