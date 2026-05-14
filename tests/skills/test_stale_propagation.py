"""
test_stale_propagation.py -- Lane R9-5 Tests (CONWAY-R9)

Tests for stale_propagation.py.

COVERAGE:
  - classify_stale_tier: all verdict inputs, blocker/warning escalation
  - build_propagation_report: structure, domain propagation, governance
  - _propagate_tier: chain propagation, cycle prevention
  - _max_tier: correct maximum selection
  - propagate_stale_state: live smoke test
  - propagate_all_formats: aggregate structure
  - simulation_allowed / planning_allowed alignment
  - Governance flags always correct

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

from stale_propagation import (
    classify_stale_tier,
    build_propagation_report,
    propagate_stale_state,
    propagate_all_formats,
    _propagate_tier,
    _max_tier,
    TIER_0_CLEAN,
    TIER_1_ADVISORY,
    TIER_2_REVIEW,
    TIER_3_BLOCKED,
    TIER_4_CORRUPTED,
    TIER_ORDER,
    PROPAGATION_RULES,
    REMEDIATION_GUIDANCE,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_checks(overrides: dict | None = None) -> dict:
    base = {
        "directory_exists": {"status": "PASS", "severity": "BLOCKER"},
        "timestamp_consistency": {"status": "PASS", "severity": "BLOCKER"},
        "verifier_after_generation": {"status": "PASS", "severity": "BLOCKER"},
        "iv_after_verification": {"status": "PASS", "severity": "BLOCKER"},
        "accepted_count_consistent": {"status": "PASS", "severity": "BLOCKER"},
        "no_modification_after_iv": {"status": "PASS", "severity": "WARN"},
    }
    if overrides:
        for k, v in overrides.items():
            base[k] = v
    return base


# ---------------------------------------------------------------------------
# TIER_ORDER
# ---------------------------------------------------------------------------

class TestTierOrder:
    def test_clean_is_lowest(self):
        assert TIER_ORDER[TIER_0_CLEAN] < TIER_ORDER[TIER_1_ADVISORY]

    def test_blocked_higher_than_review(self):
        assert TIER_ORDER[TIER_3_BLOCKED] > TIER_ORDER[TIER_2_REVIEW]

    def test_corrupted_is_highest(self):
        assert TIER_ORDER[TIER_4_CORRUPTED] > TIER_ORDER[TIER_3_BLOCKED]

    def test_all_tiers_in_order(self):
        tiers = [TIER_0_CLEAN, TIER_1_ADVISORY, TIER_2_REVIEW, TIER_3_BLOCKED, TIER_4_CORRUPTED]
        for i in range(len(tiers) - 1):
            assert TIER_ORDER[tiers[i]] < TIER_ORDER[tiers[i + 1]]


# ---------------------------------------------------------------------------
# _max_tier
# ---------------------------------------------------------------------------

class TestMaxTier:
    def test_empty_returns_clean(self):
        assert _max_tier([]) == TIER_0_CLEAN

    def test_single_tier(self):
        assert _max_tier([TIER_2_REVIEW]) == TIER_2_REVIEW

    def test_max_of_mixed(self):
        assert _max_tier([TIER_0_CLEAN, TIER_3_BLOCKED, TIER_1_ADVISORY]) == TIER_3_BLOCKED

    def test_all_clean(self):
        assert _max_tier([TIER_0_CLEAN, TIER_0_CLEAN]) == TIER_0_CLEAN


# ---------------------------------------------------------------------------
# _propagate_tier
# ---------------------------------------------------------------------------

class TestPropagateTier:
    def test_source_domain_included(self):
        result = _propagate_tier("requirements", TIER_3_BLOCKED)
        assert "requirements" in result
        assert result["requirements"] == TIER_3_BLOCKED

    def test_downstream_domains_propagated(self):
        result = _propagate_tier("requirements", TIER_3_BLOCKED)
        for downstream in PROPAGATION_RULES["requirements"]:
            assert downstream in result

    def test_advisory_tier_does_not_propagate(self):
        """TIER_1_ADVISORY should not propagate downstream."""
        result = _propagate_tier("requirements", TIER_1_ADVISORY)
        for downstream in PROPAGATION_RULES["requirements"]:
            assert downstream not in result

    def test_clean_tier_does_not_propagate(self):
        result = _propagate_tier("requirements", TIER_0_CLEAN)
        for downstream in PROPAGATION_RULES["requirements"]:
            assert downstream not in result

    def test_cycle_prevention(self):
        """Propagation must not loop infinitely."""
        result = _propagate_tier("requirements", TIER_3_BLOCKED)
        assert isinstance(result, dict)  # must complete

    def test_leaf_domains_have_no_downstream(self):
        result = _propagate_tier("simulation", TIER_3_BLOCKED)
        assert "simulation" in result
        # simulation has no downstream in PROPAGATION_RULES
        assert len(result) == 1


# ---------------------------------------------------------------------------
# classify_stale_tier
# ---------------------------------------------------------------------------

class TestClassifyStaleT:
    def test_fresh_no_blockers_is_clean(self):
        tier = classify_stale_tier("FRESH", 0, 0, _make_checks())
        assert tier == TIER_0_CLEAN

    def test_review_required_is_tier_2(self):
        tier = classify_stale_tier("REVIEW_REQUIRED", 0, 1, _make_checks())
        assert tier == TIER_2_REVIEW

    def test_stale_blocked_is_tier_3(self):
        tier = classify_stale_tier("STALE_BLOCKED", 1, 0, _make_checks())
        assert tier == TIER_3_BLOCKED

    def test_two_blockers_escalate_to_tier_3(self):
        tier = classify_stale_tier("FRESH", 2, 0, _make_checks())
        assert tier == TIER_3_BLOCKED

    def test_three_blockers_escalate_to_tier_4(self):
        tier = classify_stale_tier("FRESH", 3, 0, _make_checks())
        assert tier == TIER_4_CORRUPTED

    def test_dir_missing_with_blocker_escalates_to_tier_4(self):
        checks = _make_checks({"directory_exists": {"status": "FAIL", "severity": "BLOCKER"}})
        tier = classify_stale_tier("STALE_BLOCKED", 1, 0, checks)
        assert tier == TIER_4_CORRUPTED

    def test_many_warnings_on_fresh_escalates_to_advisory(self):
        tier = classify_stale_tier("FRESH", 0, 3, _make_checks())
        assert tier == TIER_1_ADVISORY

    def test_one_warning_on_fresh_stays_clean(self):
        tier = classify_stale_tier("FRESH", 0, 1, _make_checks())
        assert tier == TIER_0_CLEAN


# ---------------------------------------------------------------------------
# build_propagation_report
# ---------------------------------------------------------------------------

class TestBuildPropagationReport:
    def test_required_keys_present(self):
        report = build_propagation_report("fods", "FRESH", 0, 0, _make_checks(), [])
        for key in ["format_id", "verdict", "aggregate_tier", "source_domains",
                    "propagated_tiers", "affected_domains", "remediation",
                    "simulation_allowed", "planning_allowed", "governance"]:
            assert key in report

    def test_format_id_correct(self):
        report = build_propagation_report("fods", "FRESH", 0, 0, _make_checks(), [])
        assert report["format_id"] == "fods"

    def test_clean_verdict_simulation_allowed(self):
        report = build_propagation_report("fods", "FRESH", 0, 0, _make_checks(), [])
        assert report["simulation_allowed"] is True
        assert report["planning_allowed"] is True

    def test_blocked_verdict_simulation_not_allowed(self):
        report = build_propagation_report("fods", "STALE_BLOCKED", 1, 0, _make_checks(), [])
        assert report["simulation_allowed"] is False
        assert report["planning_allowed"] is False

    def test_review_required_simulation_allowed(self):
        report = build_propagation_report("fods", "REVIEW_REQUIRED", 0, 1, _make_checks(), [])
        assert report["simulation_allowed"] is True

    def test_tier_4_simulation_not_allowed(self):
        report = build_propagation_report("fods", "FRESH", 3, 0, _make_checks(), [])
        assert report["simulation_allowed"] is False

    def test_governance_flags_correct(self):
        report = build_propagation_report("fods", "FRESH", 0, 0, _make_checks(), [])
        gov = report["governance"]
        assert gov["commercial_product_ready"] is False
        assert gov["autonomous_execution_allowed"] is False

    def test_remediation_non_empty(self):
        for verdict in ["FRESH", "REVIEW_REQUIRED", "STALE_BLOCKED"]:
            report = build_propagation_report("fods", verdict, 0, 0, _make_checks(), [])
            assert len(report["remediation"]) > 0

    def test_affected_domains_empty_when_clean(self):
        report = build_propagation_report("fods", "FRESH", 0, 0, _make_checks(), [])
        assert report["affected_domains"] == []

    def test_affected_domains_non_empty_when_stale(self):
        checks = _make_checks({"iv_after_verification": {"status": "FAIL", "severity": "BLOCKER"}})
        report = build_propagation_report("fods", "STALE_BLOCKED", 1, 0, checks, ["IV check failed"])
        assert len(report["affected_domains"]) > 0

    def test_reasons_propagated(self):
        reasons = ["requirement timestamp mismatch", "IV not found"]
        report = build_propagation_report("fods", "REVIEW_REQUIRED", 0, 1, _make_checks(), reasons)
        assert report["reasons"] == reasons

    def test_propagated_tiers_is_dict(self):
        report = build_propagation_report("fods", "FRESH", 0, 0, _make_checks(), [])
        assert isinstance(report["propagated_tiers"], dict)

    def test_verifier_check_fail_propagates(self):
        checks = _make_checks({"verifier_after_generation": {"status": "FAIL", "severity": "BLOCKER"}})
        report = build_propagation_report("fods", "STALE_BLOCKED", 1, 0, checks, [])
        assert "verifier_review" in report["source_domains"] or len(report["propagated_tiers"]) > 0


# ---------------------------------------------------------------------------
# propagate_stale_state (live)
# ---------------------------------------------------------------------------

class TestPropagateStaleStateLive:
    def test_fods_returns_report(self):
        result = propagate_stale_state("fods")
        assert isinstance(result, dict)
        assert "verdict" in result
        assert "aggregate_tier" in result

    def test_fodt_returns_report(self):
        result = propagate_stale_state("fodt")
        assert isinstance(result, dict)
        assert "verdict" in result

    def test_governance_flags_in_live_result(self):
        result = propagate_stale_state("fods")
        if "governance" in result:
            assert result["governance"]["commercial_product_ready"] is False

    def test_simulation_allowed_is_bool(self):
        result = propagate_stale_state("fods")
        assert isinstance(result.get("simulation_allowed"), bool)


# ---------------------------------------------------------------------------
# propagate_all_formats (mocked + live)
# ---------------------------------------------------------------------------

class TestPropagateAllFormats:
    def test_required_keys_present(self):
        result = propagate_all_formats(["fods", "fodt"])
        for key in ["formats", "per_format", "all_clean", "any_blocked",
                    "aggregate_tier", "simulation_allowed"]:
            assert key in result

    def test_per_format_has_both_formats(self):
        result = propagate_all_formats(["fods", "fodt"])
        assert "fods" in result["per_format"]
        assert "fodt" in result["per_format"]

    def test_default_formats_are_fods_fodt(self):
        result = propagate_all_formats()
        assert set(result["formats"]) == {"fods", "fodt"}

    def test_any_blocked_false_when_none_blocked(self):
        fresh = {"verdict": "FRESH", "aggregate_tier": TIER_0_CLEAN,
                 "simulation_allowed": True, "planning_allowed": True}
        with patch("stale_propagation.propagate_stale_state", return_value=fresh):
            result = propagate_all_formats(["fods", "fodt"])
        assert result["any_blocked"] is False
        assert result["simulation_allowed"] is True

    def test_any_blocked_true_when_one_blocked(self):
        blocked = {"verdict": "STALE_BLOCKED", "aggregate_tier": TIER_3_BLOCKED,
                   "simulation_allowed": False, "planning_allowed": False}
        fresh = {"verdict": "FRESH", "aggregate_tier": TIER_0_CLEAN,
                 "simulation_allowed": True, "planning_allowed": True}

        call_count = [0]
        def mock_propagate(fmt):
            call_count[0] += 1
            return blocked if fmt == "fods" else fresh

        with patch("stale_propagation.propagate_stale_state", side_effect=mock_propagate):
            result = propagate_all_formats(["fods", "fodt"])

        assert result["any_blocked"] is True
        assert result["simulation_allowed"] is False

    def test_governance_flags_in_aggregate(self):
        result = propagate_all_formats()
        assert result["governance"]["commercial_product_ready"] is False

    def test_aggregate_tier_is_max(self):
        r1 = {"verdict": "FRESH", "aggregate_tier": TIER_0_CLEAN,
              "simulation_allowed": True, "planning_allowed": True}
        r2 = {"verdict": "REVIEW_REQUIRED", "aggregate_tier": TIER_2_REVIEW,
              "simulation_allowed": True, "planning_allowed": True}

        def mock_propagate(fmt):
            return r1 if fmt == "fods" else r2

        with patch("stale_propagation.propagate_stale_state", side_effect=mock_propagate):
            result = propagate_all_formats(["fods", "fodt"])

        assert TIER_ORDER[result["aggregate_tier"]] >= TIER_ORDER[TIER_2_REVIEW]


# ---------------------------------------------------------------------------
# PROPAGATION_RULES completeness
# ---------------------------------------------------------------------------

class TestPropagationRules:
    def test_all_domains_defined(self):
        expected_domains = {
            "requirements", "verifier_review", "iv_state",
            "planning_slices", "gate_state", "replay_fingerprint",
            "simulation", "planning_bundle",
        }
        assert set(PROPAGATION_RULES.keys()) == expected_domains

    def test_downstream_domains_are_valid(self):
        all_domains = set(PROPAGATION_RULES.keys())
        for domain, downstream in PROPAGATION_RULES.items():
            for d in downstream:
                assert d in all_domains, f"Domain {d} in {domain}'s downstream is not a valid domain"


# ---------------------------------------------------------------------------
# REMEDIATION_GUIDANCE completeness
# ---------------------------------------------------------------------------

class TestRemediationGuidance:
    def test_all_tiers_have_guidance(self):
        for tier in [TIER_0_CLEAN, TIER_1_ADVISORY, TIER_2_REVIEW, TIER_3_BLOCKED, TIER_4_CORRUPTED]:
            assert tier in REMEDIATION_GUIDANCE
            assert len(REMEDIATION_GUIDANCE[tier]) > 0

    def test_blocked_guidance_mentions_human(self):
        assert "human" in REMEDIATION_GUIDANCE[TIER_3_BLOCKED].lower()

    def test_corrupted_guidance_mentions_intervention(self):
        assert "intervention" in REMEDIATION_GUIDANCE[TIER_4_CORRUPTED].lower()
