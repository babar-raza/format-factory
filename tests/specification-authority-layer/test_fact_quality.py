"""Tests for fact_quality module — core of the fact quality contract."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "specification-authority-layer"))

from fact_quality import (
    ITEM_TYPE_THRESHOLDS,
    quality_level,
    check_fact_quality_for_item,
    build_fact_quality_index,
    load_registered_source_ids,
)


class TestQualityLevel:
    """quality_level() correctly classifies facts into levels 0-3."""

    def test_null_source_id_is_level_0(self):
        fact = {"fact_status": "bootstrap_only", "source_id": None}
        assert quality_level(fact, set()) == 0

    def test_missing_source_id_is_level_0(self):
        fact = {"fact_status": "bootstrap_only"}
        assert quality_level(fact, set()) == 0

    def test_unregistered_source_id_is_level_0(self):
        fact = {"fact_status": "bootstrap_only", "source_id": "SPEC-FAKE-999"}
        assert quality_level(fact, {"SPEC-FODS-1_3"}) == 0

    def test_registered_source_bootstrap_is_level_1(self):
        fact = {"fact_status": "bootstrap_only", "source_id": "SPEC-FODS-1_3"}
        assert quality_level(fact, {"SPEC-FODS-1_3"}) == 1

    def test_registered_source_registered_status_is_level_1(self):
        fact = {"fact_status": "source_registered", "source_id": "SPEC-FODS-1_3"}
        assert quality_level(fact, {"SPEC-FODS-1_3"}) == 1

    def test_verified_fact_is_level_2(self):
        fact = {"fact_status": "verified", "source_id": "SPEC-FODS-1_3"}
        assert quality_level(fact, {"SPEC-FODS-1_3"}) == 2

    def test_text_verified_fact_is_level_2(self):
        fact = {"fact_status": "text_verified", "source_id": "SPEC-FODS-1_3"}
        assert quality_level(fact, {"SPEC-FODS-1_3"}) == 2

    def test_normative_verified_is_level_3(self):
        fact = {"fact_status": "normative_verified", "source_id": "SPEC-FODS-1_3"}
        assert quality_level(fact, {"SPEC-FODS-1_3"}) == 3

    def test_verified_without_registered_source_is_level_0(self):
        """Even verified status is Level 0 if source_id is not registered."""
        fact = {"fact_status": "verified", "source_id": "SPEC-UNKNOWN"}
        assert quality_level(fact, {"SPEC-FODS-1_3"}) == 0

    def test_empty_registered_set_all_level_0(self):
        fact = {"fact_status": "verified", "source_id": "SPEC-FODS-1_3"}
        assert quality_level(fact, set()) == 0


class TestItemTypeThresholds:
    """ITEM_TYPE_THRESHOLDS contains expected entries."""

    def test_product_source_threshold_0(self):
        assert ITEM_TYPE_THRESHOLDS["PRODUCT_SOURCE"] == 0

    def test_readiness_threshold_1(self):
        assert ITEM_TYPE_THRESHOLDS["READINESS"] == 1

    def test_release_gate_threshold_2(self):
        assert ITEM_TYPE_THRESHOLDS["RELEASE_GATE"] == 2

    def test_governance_taskcard_threshold_0(self):
        assert ITEM_TYPE_THRESHOLDS["GOVERNANCE_TASKCARD"] == 0


class TestCheckFactQuality:
    """check_fact_quality_for_item() enforces quality thresholds."""

    def _make_index(self):
        return {
            "FACT-FODS-001": {
                "quality": 0,
                "fact_status": "bootstrap_only",
                "source_id": None,
                "format_id": "fods",
            },
            "FACT-FODS-002": {
                "quality": 1,
                "fact_status": "bootstrap_only",
                "source_id": "SPEC-FODS-1_3",
                "format_id": "fods",
            },
            "FACT-FODS-003": {
                "quality": 2,
                "fact_status": "text_verified",
                "source_id": "SPEC-FODS-1_3",
                "format_id": "fods",
            },
        }

    def test_product_source_accepts_level_0(self):
        violations = check_fact_quality_for_item(
            ["FACT-FODS-001"], "PRODUCT_SOURCE", self._make_index()
        )
        assert violations == []

    def test_readiness_rejects_level_0(self):
        violations = check_fact_quality_for_item(
            ["FACT-FODS-001"], "READINESS", self._make_index()
        )
        assert len(violations) == 1
        assert "quality=0" in violations[0]

    def test_readiness_accepts_level_1(self):
        violations = check_fact_quality_for_item(
            ["FACT-FODS-002"], "READINESS", self._make_index()
        )
        assert violations == []

    def test_release_gate_rejects_level_1(self):
        violations = check_fact_quality_for_item(
            ["FACT-FODS-002"], "RELEASE_GATE", self._make_index()
        )
        assert len(violations) == 1
        assert "quality=1" in violations[0]

    def test_release_gate_accepts_level_2(self):
        violations = check_fact_quality_for_item(
            ["FACT-FODS-003"], "RELEASE_GATE", self._make_index()
        )
        assert violations == []

    def test_missing_fact_reported(self):
        violations = check_fact_quality_for_item(
            ["FACT-NONEXISTENT"], "PRODUCT_SOURCE", self._make_index()
        )
        assert len(violations) == 1
        assert "not found" in violations[0]

    def test_multiple_refs_mixed(self):
        """One good + one bad = one violation."""
        violations = check_fact_quality_for_item(
            ["FACT-FODS-003", "FACT-FODS-001"],
            "READINESS",
            self._make_index(),
        )
        assert len(violations) == 1
        assert "FACT-FODS-001" in violations[0]


class TestLoadRegisteredSourceIds:
    """load_registered_source_ids() reads spec-source-registry."""

    def test_loads_from_repo(self):
        ids = load_registered_source_ids(repo_root=_REPO)
        # Should have at least fods, zst entries
        assert len(ids) >= 2

    def test_nonexistent_path_returns_empty(self):
        ids = load_registered_source_ids(repo_root=Path("/nonexistent"))
        assert ids == set()


class TestBuildFactQualityIndex:
    """build_fact_quality_index() produces a usable index."""

    def test_builds_from_production(self):
        index = build_fact_quality_index(repo_root=_REPO)
        assert len(index) > 0
        # Every entry has required keys
        sample = next(iter(index.values()))
        assert "quality" in sample
        assert "fact_status" in sample
        assert "source_id" in sample

    def test_registered_formats_have_bootstrap_level_1(self):
        """Bootstrap facts for registered formats should be Level 1+.

        Workbench-verified facts may have non-registry source_ids (e.g.
        'fods-normalized') that don't match spec-source-registry entries,
        so they remain Level 0. Only bootstrap facts with the registered
        source_id should be Level 1.
        """
        index = build_fact_quality_index(repo_root=_REPO)
        registered = load_registered_source_ids(repo_root=_REPO)
        fods_bootstrap = {
            k: v
            for k, v in index.items()
            if v["format_id"] == "fods" and v.get("source_id") in registered
        }
        assert len(fods_bootstrap) > 0
        levels = [v["quality"] for v in fods_bootstrap.values()]
        assert all(l >= 1 for l in levels), (
            f"FODS bootstrap facts with registered source_id should be Level 1+, "
            f"but found levels: {set(levels)}"
        )

    def test_nonexistent_path_returns_empty(self):
        index = build_fact_quality_index(
            sal_facts_path=Path("/nonexistent/sal-facts-latest.json")
        )
        assert index == {}
