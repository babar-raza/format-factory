"""
test_authority_conveyor.py
Sprint: SPEC-AUTHORITY-LAYER-CONVEYOR-ACCELERATION-AND-OPS-CLEANUP-001
Added: 2026-06-08

Tests for tools/supervisor/authority_conveyor.py
"""
import sys
import json
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))

_SPEC_CACHE = _REPO_ROOT / ".local" / "spec-cache"

from authority_conveyor import run_conveyor


# ============================================================
# Smoke tests against real repo state
# ============================================================


class TestRealFormatConveyor:
    """Smoke tests using real repo state."""

    pytestmark = pytest.mark.skipif(
        not _SPEC_CACHE.is_dir(),
        reason="SAL spec-cache not present in this environment",
    )

    def test_fods_already_at_p6(self):
        """FODS is P6 — already at or above target P6."""
        result = run_conveyor("fods", target_level=6)
        assert result["current_level_int"] >= 6
        assert result["already_at_or_above_target"]
        assert result["gap_count"] == 0

    def test_zst_is_p5_after_citations(self):
        """ZST should be P5+ after code and test citations added this sprint."""
        result = run_conveyor("zst", target_level=5)
        # ZST has code citations and test citations now
        assert result["current_level_int"] >= 4, f"ZST should be P4+, got {result['current_level']}"

    def test_zst_conveyor_to_p6_has_steps(self):
        """ZST conveyor to P6 should have gap steps (proof graph missing)."""
        result = run_conveyor("zst", target_level=6)
        assert result["format_id"] == "zst"
        assert "gap_steps" in result
        # ZST at P5 → needs proof graph for P6
        if result["current_level_int"] < 6:
            assert result["gap_count"] > 0

    def test_gnumeric_p1_no_conveyor_path(self):
        """Gnumeric is P1 (schema only) — any target above P1 has gap steps."""
        result = run_conveyor("gnumeric", target_level=4)
        assert result["current_level_int"] == 1
        assert not result["already_at_or_above_target"]
        assert result["exception_allowed"] == "schema_authority_available"

    def test_csv_p3_has_gap_to_p4(self):
        """CSV is P3 (verified_with_note facts counted as candidate, RFC not cached) — needs verified facts."""
        result = run_conveyor("csv", target_level=4)
        assert result["current_level_int"] == 3  # P3: candidate facts only (verified_with_note)
        assert result["gap_count"] >= 1  # still needs deterministic RFC 4180 verification for P4

    def test_unknown_format_p0(self):
        """Unknown format is P0."""
        result = run_conveyor("totally-unknown-format-xyz", target_level=4)
        assert result["current_level_int"] == 0
        assert result["gap_count"] >= 1

    def test_target_below_current_is_already_complete(self):
        """If target is below current level, already_at_or_above_target=True."""
        # FODS is P6; targeting P2 should be trivially satisfied
        result = run_conveyor("fods", target_level=2)
        assert result["already_at_or_above_target"]
        assert result["gap_count"] == 0


# ============================================================
# Structural correctness tests
# ============================================================


class TestConveyorStructure:
    """Tests for result structure and field presence."""

    def test_result_has_all_required_fields(self):
        """run_conveyor result must contain all required fields."""
        result = run_conveyor("fods", target_level=6)
        required = [
            "format_id", "current_level", "current_level_int",
            "target_level", "target_level_int", "already_at_or_above_target",
            "authority_blockers", "readiness_allowed", "product_expansion_allowed",
            "facts_summary", "citations_summary", "gap_steps", "gap_count",
            "matrix_update", "next_action",
        ]
        for field in required:
            assert field in result, f"Missing field: {field}"

    def test_facts_summary_has_required_keys(self):
        """facts_summary must have total, verified, candidate, and ID lists."""
        result = run_conveyor("fods", target_level=6)
        fs = result["facts_summary"]
        for key in ["total", "verified", "candidate", "verified_ids", "candidate_ids"]:
            assert key in fs, f"facts_summary missing key: {key}"

    def test_citations_summary_has_required_keys(self):
        """citations_summary must have code, test, and proof graph lists."""
        result = run_conveyor("fods", target_level=6)
        cs = result["citations_summary"]
        for key in ["code_cited_files", "test_cited_files", "proof_graph_files"]:
            assert key in cs, f"citations_summary missing key: {key}"

    def test_matrix_update_has_required_keys(self):
        """matrix_update must have all tracking fields."""
        result = run_conveyor("fods", target_level=6)
        mu = result["matrix_update"]
        for key in ["format_id", "current_level", "target_level", "gap_steps",
                    "already_complete", "verified_facts_count"]:
            assert key in mu, f"matrix_update missing key: {key}"

    def test_gap_steps_are_ordered_list_of_dicts(self):
        """gap_steps must be a list of dicts with required fields."""
        result = run_conveyor("csv", target_level=6)
        for step in result["gap_steps"]:
            assert "step" in step
            assert "from_level" in step
            assert "to_level" in step
            assert "action" in step
            assert "type" in step

    def test_result_is_json_serializable(self):
        """run_conveyor result must be fully JSON-serializable."""
        result = run_conveyor("fods", target_level=6)
        serialized = json.dumps(result)
        parsed = json.loads(serialized)
        assert parsed["format_id"] == "fods"


# ============================================================
# Gap step content tests
# ============================================================


class TestGapStepContent:
    """Tests for gap step action plan correctness."""

    def test_p0_to_p4_gap_includes_spec_cache_step(self):
        """P0 format targeting P4 must include SPEC_CACHE step."""
        result = run_conveyor("totally-unknown-format-xyz", target_level=4)
        step_types = [s["type"] for s in result["gap_steps"]]
        assert "SPEC_CACHE" in step_types

    def test_p0_to_p4_gap_includes_fact_extraction_step(self):
        """P0 format targeting P4 must include FACT_EXTRACTION step."""
        result = run_conveyor("totally-unknown-format-xyz", target_level=4)
        step_types = [s["type"] for s in result["gap_steps"]]
        assert "FACT_EXTRACTION" in step_types

    def test_p4_to_p5_gap_includes_fact_citation_step(self):
        """P4 format targeting P5 must include FACT_CITATION step."""
        result = run_conveyor("csv", target_level=5)
        step_types = [s["type"] for s in result["gap_steps"]]
        if result["current_level_int"] <= 4:
            assert "FACT_CITATION" in step_types

    def test_steps_are_numbered_sequentially(self):
        """Gap steps must be numbered starting from 1."""
        result = run_conveyor("totally-unknown-format-xyz", target_level=6)
        for i, step in enumerate(result["gap_steps"], start=1):
            assert step["step"] == i, f"Step {i} has step number {step['step']}"

    def test_fods_p6_has_no_gap_steps(self):
        """FODS at P6 targeting P6 has zero gap steps."""
        result = run_conveyor("fods", target_level=6)
        if result["current_level_int"] >= 6:
            assert result["gap_steps"] == []
            assert result["gap_count"] == 0


# ============================================================
# Authority-aware product gate tests
# ============================================================


class TestAuthorityProductGate:
    """Tests that conveyor correctly gates product expansion."""

    def test_p1_format_blocks_product_expansion(self):
        """P1 (schema-only or no-public-spec) formats must have product_expansion_allowed=False."""
        result = run_conveyor("gnumeric", target_level=6)
        assert not result["product_expansion_allowed"]

    def test_p4_format_allows_product_expansion(self):
        """P4+ formats must have product_expansion_allowed=True."""
        import pytest
        spec_cache = _REPO_ROOT / ".local" / "spec-cache" / "fods"
        if not spec_cache.exists():
            pytest.skip(".local/spec-cache/fods not present (gitignored, CI skip)")
        result = run_conveyor("fods", target_level=6)
        assert result["product_expansion_allowed"]
        assert result["readiness_allowed"]

    def test_p3_format_blocks_readiness(self):
        """P3 (candidate facts only) must have readiness_allowed=False."""
        result = run_conveyor("csv", target_level=6)
        if result["current_level_int"] <= 3:
            assert not result["readiness_allowed"]
