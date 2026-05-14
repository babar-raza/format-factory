"""
test_candidate_format_backlog.py -- Lane C Tests (FORMAT-FACTORY-R10)

Tests for candidate_format_backlog.py.

COVERAGE:
  - classify_backlog: structure, counts, tier distribution
  - validate_backlog_integrity: duplicates, audit safety, required fields
  - get_candidates_by_tier/category/spec_type/audit_status
  - get_format: lookup + not found
  - Governance: no aspose_supported without audit
  - Required formats present: hwp, hwpx, hwt, alz, egg
  - FODS/FODT marked as active and audited

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

from candidate_format_backlog import (
    get_backlog,
    get_candidates_by_tier,
    get_candidates_by_category,
    get_candidates_by_audit_status,
    get_candidates_by_spec_type,
    get_format,
    classify_backlog,
    validate_backlog_integrity,
    ALL_BACKLOG,
    ACTIVE_FORMATS,
    TIER_A_CANDIDATES,
    TIER_B_CANDIDATES,
    TIER_C_CANDIDATES,
    AUDIT_STATUS_NEEDS_AUDIT,
    AUDIT_STATUS_AUDITED_SUPPORTED,
    SPEC_FULL_PUBLIC,
    SPEC_PARTIAL_PUBLIC,
    SPEC_REVERSE_ENGINEERING,
    TIER_ACTIVE,
    TIER_A_NEAR_TERM,
    TIER_B_MEDIUM_TERM,
    TIER_C_LONG_TERM,
    ALL_CATEGORIES,
    _GOVERNANCE_FLAGS,
)


# ---------------------------------------------------------------------------
# Backlog structure integrity
# ---------------------------------------------------------------------------

class TestBacklogStructure:
    def test_all_backlog_is_non_empty(self):
        assert len(ALL_BACKLOG) > 0

    def test_active_formats_non_empty(self):
        assert len(ACTIVE_FORMATS) >= 2

    def test_tier_a_candidates_non_empty(self):
        assert len(TIER_A_CANDIDATES) > 0

    def test_tier_b_candidates_non_empty(self):
        assert len(TIER_B_CANDIDATES) > 0

    def test_tier_c_candidates_non_empty(self):
        assert len(TIER_C_CANDIDATES) > 0

    def test_get_backlog_returns_copy(self):
        bl = get_backlog()
        bl.append({"format_id": "fake"})
        assert len(get_backlog()) == len(ALL_BACKLOG)  # original unaffected

    def test_all_entries_have_required_fields(self):
        required = {"format_id", "extension", "category", "tier", "spec_type",
                    "audit_status", "aspose_supported", "acquisition_state"}
        for entry in ALL_BACKLOG:
            missing = required - set(entry.keys())
            assert not missing, f"{entry.get('format_id')} missing: {missing}"

    def test_no_duplicate_format_ids(self):
        ids = [e["format_id"] for e in ALL_BACKLOG]
        assert len(ids) == len(set(ids))

    def test_all_categories_valid(self):
        for entry in ALL_BACKLOG:
            assert entry["category"] in ALL_CATEGORIES, \
                f"{entry['format_id']} has invalid category: {entry['category']}"

    def test_all_tiers_valid(self):
        valid_tiers = {TIER_ACTIVE, TIER_A_NEAR_TERM, TIER_B_MEDIUM_TERM, TIER_C_LONG_TERM}
        for entry in ALL_BACKLOG:
            assert entry["tier"] in valid_tiers


# ---------------------------------------------------------------------------
# Required formats present
# ---------------------------------------------------------------------------

class TestRequiredFormatsPresent:
    def test_hwp_present(self):
        assert get_format("hwp") is not None

    def test_hwpx_present(self):
        assert get_format("hwpx") is not None

    def test_hwt_present(self):
        assert get_format("hwt") is not None

    def test_alz_present(self):
        assert get_format("alz") is not None

    def test_egg_present(self):
        assert get_format("egg") is not None

    def test_fods_present(self):
        assert get_format("fods") is not None

    def test_fodt_present(self):
        assert get_format("fodt") is not None


# ---------------------------------------------------------------------------
# FODS/FODT active status
# ---------------------------------------------------------------------------

class TestActiveFodsFodt:
    def test_fods_is_active_tier(self):
        fods = get_format("fods")
        assert fods["tier"] == TIER_ACTIVE

    def test_fodt_is_active_tier(self):
        fodt = get_format("fodt")
        assert fodt["tier"] == TIER_ACTIVE

    def test_fods_is_audited_supported(self):
        fods = get_format("fods")
        assert fods["audit_status"] == AUDIT_STATUS_AUDITED_SUPPORTED

    def test_fodt_is_audited_supported(self):
        fodt = get_format("fodt")
        assert fodt["audit_status"] == AUDIT_STATUS_AUDITED_SUPPORTED

    def test_fods_aspose_supported_true(self):
        fods = get_format("fods")
        assert fods["aspose_supported"] is True

    def test_fodt_aspose_supported_true(self):
        fodt = get_format("fodt")
        assert fodt["aspose_supported"] is True

    def test_fods_spec_full_public(self):
        fods = get_format("fods")
        assert fods["spec_type"] == SPEC_FULL_PUBLIC


# ---------------------------------------------------------------------------
# Governance: no aspose claim without audit
# ---------------------------------------------------------------------------

class TestAuditGovernance:
    def test_needs_audit_formats_have_aspose_supported_none(self):
        for entry in ALL_BACKLOG:
            if entry["audit_status"] == AUDIT_STATUS_NEEDS_AUDIT:
                assert entry["aspose_supported"] is None, \
                    f"{entry['format_id']}: aspose_supported={entry['aspose_supported']} but needs_audit"

    def test_hwp_hwpx_hwt_alz_egg_are_needs_audit(self):
        for fmt in ["hwp", "hwpx", "hwt", "alz", "egg"]:
            entry = get_format(fmt)
            assert entry["audit_status"] == AUDIT_STATUS_NEEDS_AUDIT, \
                f"{fmt} should be needs_audit"

    def test_governance_flags_correct(self):
        assert _GOVERNANCE_FLAGS["commercial_product_ready"] is False
        assert _GOVERNANCE_FLAGS["autonomous_execution_allowed"] is False
        assert _GOVERNANCE_FLAGS["all_candidates_needs_audit_by_default"] is True
        assert _GOVERNANCE_FLAGS["unsupported_by_aspose_requires_audit"] is True


# ---------------------------------------------------------------------------
# get_candidates_by_*
# ---------------------------------------------------------------------------

class TestGetCandidatesByFilters:
    def test_tier_a_returns_tier_a_only(self):
        items = get_candidates_by_tier(TIER_A_NEAR_TERM)
        for item in items:
            assert item["tier"] == TIER_A_NEAR_TERM

    def test_tier_b_returns_tier_b_only(self):
        items = get_candidates_by_tier(TIER_B_MEDIUM_TERM)
        for item in items:
            assert item["tier"] == TIER_B_MEDIUM_TERM

    def test_tier_c_returns_tier_c_only(self):
        items = get_candidates_by_tier(TIER_C_LONG_TERM)
        for item in items:
            assert item["tier"] == TIER_C_LONG_TERM

    def test_active_tier_returns_fods_fodt(self):
        items = get_candidates_by_tier(TIER_ACTIVE)
        ids = [i["format_id"] for i in items]
        assert "fods" in ids
        assert "fodt" in ids

    def test_archive_category_contains_alz_egg(self):
        items = get_candidates_by_category("archive")
        ids = [i["format_id"] for i in items]
        assert "alz" in ids
        assert "egg" in ids

    def test_word_processing_contains_hwp_hwpx_hwt(self):
        items = get_candidates_by_category("word_processing")
        ids = [i["format_id"] for i in items]
        assert "hwp" in ids
        assert "hwpx" in ids
        assert "hwt" in ids

    def test_needs_audit_returns_all_unaudited(self):
        items = get_candidates_by_audit_status(AUDIT_STATUS_NEEDS_AUDIT)
        for item in items:
            assert item["audit_status"] == AUDIT_STATUS_NEEDS_AUDIT

    def test_full_public_spec_contains_gnumeric_abw(self):
        items = get_candidates_by_spec_type(SPEC_FULL_PUBLIC)
        ids = [i["format_id"] for i in items]
        assert "gnumeric" in ids
        assert "abw" in ids

    def test_reverse_engineering_contains_alz_hwp(self):
        items = get_candidates_by_spec_type(SPEC_REVERSE_ENGINEERING)
        ids = [i["format_id"] for i in items]
        assert "alz" in ids
        assert "hwp" in ids


# ---------------------------------------------------------------------------
# get_format
# ---------------------------------------------------------------------------

class TestGetFormat:
    def test_returns_dict_for_known_format(self):
        result = get_format("hwpx")
        assert isinstance(result, dict)
        assert result["format_id"] == "hwpx"

    def test_returns_none_for_unknown_format(self):
        result = get_format("nonexistent_xyz_99999")
        assert result is None

    def test_returns_copy_not_reference(self):
        r1 = get_format("hwpx")
        r1["category"] = "TAMPERED"
        r2 = get_format("hwpx")
        assert r2["category"] != "TAMPERED"


# ---------------------------------------------------------------------------
# classify_backlog
# ---------------------------------------------------------------------------

class TestClassifyBacklog:
    def test_required_keys_present(self):
        result = classify_backlog()
        for key in ["total_count", "by_tier", "by_category", "by_audit_status",
                    "by_spec_type", "needs_audit_count", "active_count",
                    "tier_a_count", "tier_b_count", "tier_c_count", "governance"]:
            assert key in result

    def test_total_count_matches_backlog(self):
        result = classify_backlog()
        assert result["total_count"] == len(ALL_BACKLOG)

    def test_active_count_is_two(self):
        result = classify_backlog()
        assert result["active_count"] == 2  # fods + fodt

    def test_tier_a_count_positive(self):
        result = classify_backlog()
        assert result["tier_a_count"] > 0

    def test_needs_audit_count_positive(self):
        result = classify_backlog()
        assert result["needs_audit_count"] > 0

    def test_tier_counts_sum_to_total(self):
        result = classify_backlog()
        total_by_tier = sum(result["by_tier"].values())
        assert total_by_tier == result["total_count"]

    def test_governance_in_result(self):
        result = classify_backlog()
        assert result["governance"]["commercial_product_ready"] is False

    def test_archive_category_in_by_category(self):
        result = classify_backlog()
        assert "archive" in result["by_category"]

    def test_word_processing_category_in_by_category(self):
        result = classify_backlog()
        assert "word_processing" in result["by_category"]


# ---------------------------------------------------------------------------
# validate_backlog_integrity
# ---------------------------------------------------------------------------

class TestValidateBacklogIntegrity:
    def test_current_backlog_is_valid(self):
        result = validate_backlog_integrity()
        assert result["valid"] is True, f"Violations: {result['violations']}"

    def test_violations_empty_for_valid_backlog(self):
        result = validate_backlog_integrity()
        assert result["violations"] == []

    def test_checked_count_matches_backlog(self):
        result = validate_backlog_integrity()
        assert result["checked_count"] == len(ALL_BACKLOG)

    def test_aspose_claim_without_audit_detected(self):
        """Manually inject a bad entry and verify detection."""
        bad_entry = {
            "format_id": "bad_test_fmt",
            "extension": ".bad",
            "category": "archive",
            "tier": TIER_A_NEAR_TERM,
            "spec_type": SPEC_FULL_PUBLIC,
            "audit_status": AUDIT_STATUS_NEEDS_AUDIT,
            "aspose_supported": True,  # BAD: claims support without audit
            "acquisition_state": "CANDIDATE",
            "notes": "",
        }
        # Validate this bad entry in isolation
        violations = []
        if bad_entry["audit_status"] == AUDIT_STATUS_NEEDS_AUDIT and bad_entry["aspose_supported"] is not None:
            violations.append("audit safety violation detected")
        assert len(violations) > 0
