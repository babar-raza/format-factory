"""Tests for generate_architecture_inventory.py."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

TOOLS_DOCS = Path(__file__).resolve().parents[2] / "tools" / "docs"
sys.path.insert(0, str(TOOLS_DOCS))

from generate_architecture_inventory import (
    LAYER_DEFINITIONS,
    _collect_capabilities,
    _collect_gates,
    _collect_validators,
    collect_architecture_inventory,
    render_architecture_markdown,
)

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "project_status"


class TestCollectValidators:
    def test_scans_def_validate_lines(self):
        result = _collect_validators(FIXTURE_ROOT)
        # Fixture governance_validators.py has 2 "def validate_" functions
        assert result["total"] == 2
        assert result["module_count"] == 1

    def test_module_breakdown(self):
        result = _collect_validators(FIXTURE_ROOT)
        modules = result.get("modules", {})
        assert "governance_validators.py" in modules
        assert modules["governance_validators.py"] == ["validate_csv_structure", "validate_csv_completeness"]

    def test_zero_when_no_validators(self, tmp_path):
        result = _collect_validators(tmp_path)
        assert result["total"] == 0


class TestCollectCapabilities:
    def test_total_and_active(self):
        result = _collect_capabilities(FIXTURE_ROOT)
        assert result["total"] == 5
        assert result["active"] == 4  # detect-duplicate-skills is deprecated

    def test_tracks_grouping(self):
        result = _collect_capabilities(FIXTURE_ROOT)
        tracks = result.get("tracks", {})
        assert "foss_python" in tracks
        assert "acquisition" in tracks
        # null/empty product_track → "unclassified" key
        assert "unclassified" in tracks

    def test_unclassified_count(self):
        result = _collect_capabilities(FIXTURE_ROOT)
        tracks = result.get("tracks", {})
        # 3 capabilities with no product_track: backfill, detect-duplicate-skills, new-cap-no-track
        assert tracks.get("unclassified", 0) == 3

    def test_zero_when_registry_missing(self, tmp_path):
        result = _collect_capabilities(tmp_path)
        assert result["total"] == 0
        assert result["active"] == 0


class TestCollectGates:
    def test_reads_gate_registry(self):
        result = _collect_gates(FIXTURE_ROOT)
        assert len(result) == 5

    def test_gate_11_not_autonomous(self):
        result = _collect_gates(FIXTURE_ROOT)
        gate11 = next((g for g in result if g["gate_id"] == "GATE_11"), None)
        assert gate11 is not None
        assert gate11["autonomous"] is False

    def test_gate_0_autonomous(self):
        result = _collect_gates(FIXTURE_ROOT)
        gate0 = next((g for g in result if g["gate_id"] == "GATE_0"), None)
        assert gate0 is not None
        assert gate0["autonomous"] is True

    def test_empty_when_missing(self, tmp_path):
        result = _collect_gates(tmp_path)
        assert result == []


class TestCollectArchitectureInventory:
    def test_all_top_level_keys(self):
        result = collect_architecture_inventory(FIXTURE_ROOT)
        for key in ("layers", "validators", "capabilities", "skills", "gates"):
            assert key in result

    def test_layers_count_matches_definitions(self):
        result = collect_architecture_inventory(FIXTURE_ROOT)
        # Should have same number of layers as LAYER_DEFINITIONS
        assert len(result["layers"]) == len(LAYER_DEFINITIONS)


class TestRenderArchitectureMarkdown:
    def test_contains_layer_table(self):
        arch = collect_architecture_inventory(FIXTURE_ROOT)
        md = render_architecture_markdown(arch)
        assert "## Architecture" in md
        assert "| Layer |" in md

    def test_contains_validator_section(self):
        arch = collect_architecture_inventory(FIXTURE_ROOT)
        md = render_architecture_markdown(arch)
        assert "## Governance Validators" in md

    def test_contains_capabilities_section(self):
        arch = collect_architecture_inventory(FIXTURE_ROOT)
        md = render_architecture_markdown(arch)
        assert "## Capabilities" in md
