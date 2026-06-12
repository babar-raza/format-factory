"""
test_public_spec_readiness_scorer.py -- Lane D Tests (FORMAT-FACTORY-R10)

Tests for public_spec_readiness_scorer.py.

COVERAGE:
  - score_format: structure, composite scoring, tier classification
  - score_multiple_formats: ranking, tier distribution
  - score_standard_candidates: smoke test
  - Dimension weights sum to 1.0
  - Readiness tier thresholds
  - Determinism: same inputs → same score_id
  - Governance flags

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

from public_spec_readiness_scorer import (
    score_format,
    score_multiple_formats,
    score_standard_candidates,
    DIMENSION_WEIGHTS,
    SPEC_TYPE_SCORES,
    READINESS_NOT_READY,
    READINESS_NEEDS_INVESTIGATION,
    READINESS_CANDIDATE_READY,
    READINESS_ACQUISITION_READY,
    THRESHOLD_NOT_READY,
    THRESHOLD_CANDIDATE_READY,
    _classify_readiness,
    _GOVERNANCE_FLAGS,
)


# ---------------------------------------------------------------------------
# DIMENSION_WEIGHTS
# ---------------------------------------------------------------------------

class TestDimensionWeights:
    def test_weights_sum_to_one(self):
        total = sum(DIMENSION_WEIGHTS.values())
        assert abs(total - 1.0) < 1e-9

    def test_all_weights_positive(self):
        for dim, w in DIMENSION_WEIGHTS.items():
            assert w > 0, f"{dim} weight is not positive"

    def test_eight_dimensions(self):
        assert len(DIMENSION_WEIGHTS) == 8


# ---------------------------------------------------------------------------
# _classify_readiness
# ---------------------------------------------------------------------------

class TestClassifyReadiness:
    def test_zero_is_not_ready(self):
        assert _classify_readiness(0.0) == READINESS_NOT_READY

    def test_threshold_not_ready_boundary(self):
        assert _classify_readiness(THRESHOLD_NOT_READY) == READINESS_NOT_READY
        assert _classify_readiness(THRESHOLD_NOT_READY + 0.1) == READINESS_NEEDS_INVESTIGATION

    def test_threshold_candidate_ready_boundary(self):
        assert _classify_readiness(THRESHOLD_CANDIDATE_READY) == READINESS_CANDIDATE_READY
        assert _classify_readiness(THRESHOLD_CANDIDATE_READY + 0.1) == READINESS_ACQUISITION_READY

    def test_ten_is_acquisition_ready(self):
        assert _classify_readiness(10.0) == READINESS_ACQUISITION_READY


# ---------------------------------------------------------------------------
# score_format
# ---------------------------------------------------------------------------

class TestScoreFormat:
    def _score_full_public(self, fmt="gnumeric"):
        return score_format(
            fmt=fmt,
            spec_type="full_public",
            category="spreadsheet",
            sample_files_known=True,
            legal_use_clear=True,
            open_source_reference=True,
        )

    def _score_no_spec(self, fmt="hwp"):
        return score_format(
            fmt=fmt,
            spec_type="reverse_engineering",
            category="word_processing",
            binary_format=True,
        )

    def test_required_keys_present(self):
        r = self._score_full_public()
        for key in ["format_id", "score_id", "composite_score", "readiness_tier",
                    "dimension_scores", "dimension_weights", "spec_type", "category",
                    "recommendations", "governance", "dry_run_only"]:
            assert key in r

    def test_composite_score_is_float(self):
        r = self._score_full_public()
        assert isinstance(r["composite_score"], float)

    def test_composite_score_in_range(self):
        r = self._score_full_public()
        assert 0.0 <= r["composite_score"] <= 10.0

    def test_full_public_higher_than_no_spec(self):
        r_full = self._score_full_public()
        r_none = self._score_no_spec()
        assert r_full["composite_score"] > r_none["composite_score"]

    def test_full_public_is_candidate_ready_or_above(self):
        r = self._score_full_public()
        assert r["readiness_tier"] in (READINESS_CANDIDATE_READY, READINESS_ACQUISITION_READY)

    def test_no_spec_binary_is_not_ready_or_needs_investigation(self):
        r = score_format("test_none", spec_type="none", category="cad_3d", binary_format=True)
        assert r["readiness_tier"] in (READINESS_NOT_READY, READINESS_NEEDS_INVESTIGATION)

    def test_dimension_scores_has_eight_entries(self):
        r = self._score_full_public()
        assert len(r["dimension_scores"]) == 8

    def test_dimension_scores_all_in_range(self):
        r = self._score_full_public()
        for dim, val in r["dimension_scores"].items():
            assert 0 <= val <= 10, f"{dim}: {val} out of range"

    def test_governance_flags_correct(self):
        r = self._score_full_public()
        gov = r["governance"]
        assert gov["commercial_product_ready"] is False
        assert gov["autonomous_execution_allowed"] is False
        assert gov["no_internet_access"] is True
        assert gov["scores_are_estimates_not_decisions"] is True

    def test_dry_run_only_true(self):
        assert self._score_full_public()["dry_run_only"] is True

    def test_score_id_is_hex(self):
        r = self._score_full_public()
        int(r["score_id"], 16)

    def test_determinism_same_inputs(self):
        r1 = self._score_full_public()
        r2 = self._score_full_public()
        assert r1["score_id"] == r2["score_id"]
        assert r1["composite_score"] == r2["composite_score"]

    def test_cross_format_different_score_ids(self):
        r1 = score_format("gnumeric", "full_public", "spreadsheet")
        r2 = score_format("abw", "full_public", "word_processing")
        assert r1["score_id"] != r2["score_id"]

    def test_recommendations_non_empty_for_needs_investigation(self):
        r = score_format("hwpx", spec_type="partial_public", category="word_processing")
        assert len(r["recommendations"]) > 0

    def test_recommendations_are_rec_prefixed(self):
        r = self._score_full_public()
        for rec in r["recommendations"]:
            assert rec.startswith("[REC]"), f"Non-REC recommendation: {rec}"

    def test_binary_format_reduces_score(self):
        r_xml = score_format("hwpx", "partial_public", "word_processing", binary_format=False)
        r_bin = score_format("hwp", "partial_public", "word_processing", binary_format=True)
        assert r_xml["composite_score"] >= r_bin["composite_score"]

    def test_open_source_reference_increases_score(self):
        r_no_oss = score_format("f1", "full_public", "spreadsheet", legal_use_clear=True)
        r_oss = score_format("f1", "full_public", "spreadsheet", legal_use_clear=True, open_source_reference=True)
        assert r_oss["composite_score"] >= r_no_oss["composite_score"]

    def test_json_serializable(self):
        r = self._score_full_public()
        json.dumps(r)

    def test_score_note_mentions_estimate(self):
        r = self._score_full_public()
        assert "ESTIMATE" in r["score_note"] or "estimate" in r["score_note"].lower()


# ---------------------------------------------------------------------------
# score_multiple_formats
# ---------------------------------------------------------------------------

class TestScoreMultipleFormats:
    def _standard_specs(self):
        return [
            {"fmt": "gnumeric", "spec_type": "full_public", "category": "spreadsheet",
             "sample_files_known": True, "legal_use_clear": True, "open_source_reference": True},
            {"fmt": "hwp", "spec_type": "reverse_engineering", "category": "word_processing", "binary_format": True},
            {"fmt": "alz", "spec_type": "reverse_engineering", "category": "archive", "binary_format": True},
        ]

    def test_required_keys_present(self):
        r = score_multiple_formats(self._standard_specs())
        for key in ["scored_formats", "scores", "ranked", "tier_distribution",
                    "top_candidate", "governance", "dry_run_only"]:
            assert key in r

    def test_ranked_is_sorted_descending(self):
        r = score_multiple_formats(self._standard_specs())
        scores_in_order = [item["score"] for item in r["ranked"]]
        assert scores_in_order == sorted(scores_in_order, reverse=True)

    def test_top_candidate_has_highest_score(self):
        r = score_multiple_formats(self._standard_specs())
        top_id = r["top_candidate"]
        top_score = r["scores"][top_id]["composite_score"]
        for fmt_id, result in r["scores"].items():
            assert result["composite_score"] <= top_score + 1e-9

    def test_tier_distribution_sums_to_format_count(self):
        r = score_multiple_formats(self._standard_specs())
        total = sum(r["tier_distribution"].values())
        assert total == len(self._standard_specs())

    def test_governance_in_result(self):
        r = score_multiple_formats(self._standard_specs())
        assert r["governance"]["commercial_product_ready"] is False

    def test_empty_list_returns_valid_result(self):
        r = score_multiple_formats([])
        assert r["top_candidate"] is None
        assert r["scored_formats"] == []

    def test_gnumeric_scores_higher_than_hwp(self):
        r = score_multiple_formats(self._standard_specs())
        gnumeric_score = r["scores"]["gnumeric"]["composite_score"]
        hwp_score = r["scores"]["hwp"]["composite_score"]
        assert gnumeric_score > hwp_score

    def test_json_serializable(self):
        r = score_multiple_formats(self._standard_specs())
        json.dumps(r)


# ---------------------------------------------------------------------------
# score_standard_candidates
# ---------------------------------------------------------------------------

class TestScoreStandardCandidates:
    def test_returns_dict(self):
        r = score_standard_candidates()
        assert isinstance(r, dict)

    def test_contains_hwpx_alz_egg(self):
        r = score_standard_candidates()
        for fmt in ["hwpx", "alz", "egg", "gnumeric", "abw"]:
            assert fmt in r["scores"]

    def test_gnumeric_abw_score_higher_than_hwp(self):
        r = score_standard_candidates()
        for high_fmt in ["gnumeric", "abw"]:
            assert r["scores"][high_fmt]["composite_score"] > r["scores"]["hwp"]["composite_score"]

    def test_governance_preserved(self):
        r = score_standard_candidates()
        assert r["governance"]["no_internet_access"] is True

    def test_governance_flags_immutable(self):
        r = score_standard_candidates()
        r["governance"]["commercial_product_ready"] = True
        assert _GOVERNANCE_FLAGS["commercial_product_ready"] is False


# ---------------------------------------------------------------------------
# SPEC_TYPE_SCORES
# ---------------------------------------------------------------------------

class TestSpecTypeScores:
    def test_full_public_highest_availability(self):
        assert SPEC_TYPE_SCORES["full_public"]["spec_availability"] >= \
               SPEC_TYPE_SCORES["partial_public"]["spec_availability"]

    def test_none_spec_zero_scores(self):
        assert SPEC_TYPE_SCORES["none"]["spec_availability"] == 0
        assert SPEC_TYPE_SCORES["none"]["spec_completeness"] == 0

    def test_all_spec_types_have_required_keys(self):
        for spec_type, scores in SPEC_TYPE_SCORES.items():
            assert "spec_availability" in scores
            assert "spec_completeness" in scores
