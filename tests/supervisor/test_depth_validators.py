"""Tests for V_DEPTH_SCORE, V_CHANGED_NO_TESTS, V_HELPERS_ONLY validators."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from governance_validators import (
    validate_depth_score,
    validate_changed_without_tests,
    validate_helpers_only_overclaim,
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
