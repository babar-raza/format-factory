"""Tests for V_DEPTH_SCORE, V_CHANGED_NO_TESTS, V_HELPERS_ONLY, V34-V37 validators."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from governance_validators import (
    validate_depth_score,
    validate_changed_without_tests,
    validate_helpers_only_overclaim,
    validate_class_count_minimum,
    validate_monolith_detection,
    validate_no_stub_tests,
    validate_spec_fact_authority_chain,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _base_item(**overrides):
    item = {
        "item_id": "TEST-001",
        "title": "Test item",
        "status": "completed",
        "item_type": "PRODUCT_SOURCE",
        "execution_method": "GOVERNED_SKILL_EXECUTION",
        "claim_classification": "GOVERNED_BUT_NOT_REPLAYED",
    }
    item.update(overrides)
    return item


def _decl(items):
    return {"planned_work_items": items}


# ── V_DEPTH_SCORE ──────────────────────────────────────────────────────────


class TestValidateDepthScore:
    """Tests for validate_depth_score (V_DEPTH_SCORE)."""

    def test_good_depth_score_passes(self):
        item = _base_item(
            implementation_depth_score={
                "source_loc_delta": 42,
                "tests_added": 3,
                "behavior_assertions": 7,
            }
        )
        result = validate_depth_score(_decl([item]))
        assert result["result"] == "PASS"

    def test_all_zero_release_gate_fails(self):
        item = _base_item(
            item_type_secondary="RELEASE_GATE",
            implementation_depth_score={
                "source_loc_delta": 0,
                "tests_added": 0,
                "behavior_assertions": 0,
            },
        )
        result = validate_depth_score(_decl([item]))
        assert result["result"] == "FAIL"
        assert len(result["items"]) == 1
        assert result["items"][0]["issue"] == "all depth scores zero on RELEASE_GATE item"

    def test_zero_tests_added_warns(self):
        item = _base_item(
            implementation_depth_score={
                "source_loc_delta": 10,
                "tests_added": 0,
                "behavior_assertions": 5,
            }
        )
        result = validate_depth_score(_decl([item]))
        assert result["result"] == "WARN"
        assert result["items"][0]["issue"] == "shallow_implementation"
        assert "tests_added" in result["items"][0]["zeroes"]

    def test_no_depth_score_passes(self):
        """Items without implementation_depth_score are skipped (PASS)."""
        item = _base_item()
        result = validate_depth_score(_decl([item]))
        assert result["result"] == "PASS"

    def test_non_product_source_passes(self):
        item = _base_item(item_type="GOVERNANCE_DOC")
        item["implementation_depth_score"] = {
            "source_loc_delta": 0,
            "tests_added": 0,
            "behavior_assertions": 0,
        }
        result = validate_depth_score(_decl([item]))
        assert result["result"] == "PASS"


# ── V_CHANGED_NO_TESTS ────────────────────────────────────────────────────


class TestValidateChangedWithoutTests:
    """Tests for validate_changed_without_tests (V_CHANGED_NO_TESTS)."""

    def test_product_source_changed_no_tests_warns(self):
        item = _base_item(
            changed_files=["src/python/csv/csv_parser.py"],
            tests_supporting=[],
        )
        result = validate_changed_without_tests(_decl([item]))
        assert result["result"] == "WARN"
        assert result["items"][0]["issue"] == "product_source_changed_without_tests"

    def test_product_source_with_tests_passes(self):
        item = _base_item(
            changed_files=["src/python/csv/csv_parser.py"],
            tests_supporting=["tests/python/csv/test_csv.py"],
        )
        result = validate_changed_without_tests(_decl([item]))
        assert result["result"] == "PASS"

    def test_non_product_files_changed_passes(self):
        item = _base_item(
            changed_files=["tools/supervisor/something.py"],
            tests_supporting=[],
        )
        result = validate_changed_without_tests(_decl([item]))
        assert result["result"] == "PASS"

    def test_non_product_item_passes(self):
        item = _base_item(
            item_type="GOVERNANCE_DOC",
            changed_files=["src/python/csv/csv_parser.py"],
            tests_supporting=[],
        )
        result = validate_changed_without_tests(_decl([item]))
        assert result["result"] == "PASS"


# ── V_HELPERS_ONLY ─────────────────────────────────────────────────────────


class TestValidateHelpersOnlyOverclaim:
    """Tests for validate_helpers_only_overclaim (V_HELPERS_ONLY)."""

    def test_helpers_only_with_replayable_claim_warns(self):
        item = _base_item(
            claim_classification="REPLAYABLE_NOT_YET_REPLAYED",
            changed_files=["src/python/csv/__init__.py", "src/python/csv/conftest.py"],
        )
        result = validate_helpers_only_overclaim(_decl([item]))
        assert result["result"] == "WARN"
        assert result["items"][0]["issue"] == "helpers_only_overclaim"

    def test_real_source_with_replayable_claim_passes(self):
        item = _base_item(
            claim_classification="REPLAYED_AND_PROVEN",
            changed_files=["src/python/csv/csv_parser.py"],
        )
        result = validate_helpers_only_overclaim(_decl([item]))
        assert result["result"] == "PASS"

    def test_helpers_suffix_files_warn(self):
        item = _base_item(
            claim_classification="REPLAYABLE_NOT_YET_REPLAYED",
            changed_files=["src/python/csv/csv_helpers.py", "src/python/csv/csv_utils.py"],
        )
        result = validate_helpers_only_overclaim(_decl([item]))
        assert result["result"] == "WARN"

    def test_non_replayable_claim_passes(self):
        item = _base_item(
            claim_classification="GOVERNED_BUT_NOT_REPLAYED",
            changed_files=["src/python/csv/__init__.py"],
        )
        result = validate_helpers_only_overclaim(_decl([item]))
        assert result["result"] == "PASS"

    def test_non_product_item_passes(self):
        item = _base_item(
            item_type="TEST",
            claim_classification="REPLAYABLE_NOT_YET_REPLAYED",
            changed_files=["src/python/csv/__init__.py"],
        )
        result = validate_helpers_only_overclaim(_decl([item]))
        assert result["result"] == "PASS"


# ── V34: CLASS_COUNT_MINIMUM ─────────────────────────────────────────────


class TestValidateClassCountMinimum:
    """Tests for validate_class_count_minimum (V34)."""

    def test_pass_when_no_product_source(self):
        decl = _decl([_base_item(item_type="TEST")])
        result = validate_class_count_minimum(decl, REPO_ROOT)
        assert result["result"] == "PASS"

    def test_pass_fods_meets_minimum(self):
        # FODS now has 20 .cs files (>= minimum of 15) after product deepening sprints
        item = _base_item(item_id="FODS-REBUILD", title="FODS rebuild")
        result = validate_class_count_minimum(_decl([item]), REPO_ROOT)
        assert result["result"] == "PASS"

    def test_pass_non_complex_format(self):
        item = _base_item(item_id="ZST-WORK", title="ZST compression")
        result = validate_class_count_minimum(_decl([item]), REPO_ROOT)
        assert result["result"] == "PASS"

    def test_does_not_block_sprint(self):
        item = _base_item(item_id="FODT-REBUILD", title="fodt rebuild")
        result = validate_class_count_minimum(_decl([item]), REPO_ROOT)
        assert result["blocks_sprint"] is False


# ── V35: MONOLITH_DETECTION ──────────────────────────────────────────────


class TestValidateMonolithDetection:
    """Tests for validate_monolith_detection (V35)."""

    def test_pass_empty_changed_files(self):
        result = validate_monolith_detection({"changed_files": []}, REPO_ROOT)
        assert result["result"] == "PASS"

    def test_pass_small_files(self):
        result = validate_monolith_detection(
            {"changed_files": ["tests/supervisor/test_depth_validators.py"]},
            REPO_ROOT,
        )
        assert result["result"] == "PASS"

    def test_warn_large_file(self):
        result = validate_monolith_detection(
            {"changed_files": ["tools/supervisor/governance_validators.py"]},
            REPO_ROOT,
        )
        assert result["result"] == "WARN"
        assert "governance_validators.py" in result["detail"]

    def test_does_not_block_sprint(self):
        result = validate_monolith_detection(
            {"changed_files": ["tools/supervisor/governance_validators.py"]},
            REPO_ROOT,
        )
        assert result["blocks_sprint"] is False


# ── V36: NO_STUB_TESTS ──────────────────────────────────────────────────


class TestValidateNoStubTests:
    """Tests for validate_no_stub_tests (V36)."""

    def test_pass_no_test_references(self):
        decl = _decl([_base_item(test_references=[])])
        result = validate_no_stub_tests(decl, REPO_ROOT)
        assert result["result"] == "PASS"

    def test_pass_strong_assertions(self):
        decl = _decl([_base_item(
            test_references=["tests/python/zst/test_zst_gap_closure_batch2.py"]
        )])
        result = validate_no_stub_tests(decl, REPO_ROOT)
        assert result["result"] == "PASS"

    def test_pass_missing_file(self):
        decl = _decl([_base_item(test_references=["nonexistent/test.py"])])
        result = validate_no_stub_tests(decl, REPO_ROOT)
        assert result["result"] == "PASS"

    def test_does_not_block_sprint(self):
        decl = _decl([_base_item(
            test_references=["tests/python/zst/test_zst_gap_closure_batch.py"]
        )])
        result = validate_no_stub_tests(decl, REPO_ROOT)
        assert result["blocks_sprint"] is False


# ── V37: validate_spec_fact_authority_chain ─────────────────────────────────


class TestValidateSpecFactAuthorityChain:
    """Tests for V37 validate_spec_fact_authority_chain."""

    def test_pass_no_odf_items(self):
        """Non-ODF items should pass without check."""
        decl = _decl([_base_item(format_id="CSV")])
        result = validate_spec_fact_authority_chain(decl, REPO_ROOT)
        assert result["result"] == "PASS"

    def test_pass_empty_declaration(self):
        result = validate_spec_fact_authority_chain({"planned_work_items": []}, REPO_ROOT)
        assert result["result"] == "PASS"

    def test_warn_odf_item_without_spec_fact_refs(self):
        """ODF PRODUCT_SOURCE without spec_fact_refs should WARN."""
        decl = _decl([_base_item(format_id="FODS", spec_fact_refs=[])])
        result = validate_spec_fact_authority_chain(decl, REPO_ROOT)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False

    def test_pass_odf_item_with_valid_fact_ref(self):
        """ODF PRODUCT_SOURCE with FACT-* ref should PASS."""
        decl = _decl([_base_item(format_id="FODS", spec_fact_refs=["FACT-FODS-001"])])
        result = validate_spec_fact_authority_chain(decl, REPO_ROOT)
        assert result["result"] == "PASS"

    def test_pass_odf_item_with_exception_classification(self):
        """ODF item with exception_classification should not WARN."""
        decl = _decl([_base_item(
            format_id="FODT",
            spec_fact_refs=[],
            exception_classification="format_has_no_spec"
        )])
        result = validate_spec_fact_authority_chain(decl, REPO_ROOT)
        assert result["result"] == "PASS"

    def test_never_blocks_sprint(self):
        """V37 must never block sprint (WARN-only)."""
        decl = _decl([_base_item(format_id="FODS", spec_fact_refs=[])])
        result = validate_spec_fact_authority_chain(decl, REPO_ROOT)
        assert result["blocks_sprint"] is False

    def test_non_product_source_odf_skipped(self):
        """Non-PRODUCT_SOURCE ODF items should be skipped."""
        decl = _decl([_base_item(format_id="FODS", item_type="TEST")])
        result = validate_spec_fact_authority_chain(decl, REPO_ROOT)
        assert result["result"] == "PASS"

    def test_multiple_items_mixed(self):
        """Mix of covered and uncovered ODF items."""
        decl = _decl([
            _base_item(item_id="GOOD-001", format_id="FODS", spec_fact_refs=["FACT-FODS-001"]),
            _base_item(item_id="BAD-001", format_id="FODT", spec_fact_refs=[]),
        ])
        result = validate_spec_fact_authority_chain(decl, REPO_ROOT)
        assert result["result"] == "WARN"
        assert any("BAD-001" in str(m.get("item_id", "")) for m in result["items"])
