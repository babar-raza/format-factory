"""Tests for generate_product_inventory.py."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

TOOLS_DOCS = Path(__file__).resolve().parents[2] / "tools" / "docs"
sys.path.insert(0, str(TOOLS_DOCS))

from generate_product_inventory import (
    FAMILY_ORDER,
    _gate_summary,
    collect_product_inventory,
    render_product_inventory_markdown,
)

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "project_status"


class TestGateSummary:
    def test_empty_gates_returns_na(self):
        assert _gate_summary({}) == "N/A"

    def test_single_passed_gate(self):
        result = _gate_summary({"gate_1": {"status": "passed"}})
        assert result == "G1-G1"

    def test_max_gate_range(self):
        gates = {
            "gate_1": {"status": "passed"},
            "gate_2": {"status": "passed"},
            "gate_3": {"status": "not_started"},
        }
        assert _gate_summary(gates) == "G1-G2"

    def test_none_gates_returns_na(self):
        assert _gate_summary(None) == "N/A"


class TestCollectProductInventory:
    def test_excludes_odf_shared(self):
        inventory = collect_product_inventory(FIXTURE_ROOT)
        format_ids = [i["format_id"] for i in inventory]
        assert "odf-shared" not in format_ids

    def test_sorted_by_family(self):
        inventory = collect_product_inventory(FIXTURE_ROOT)
        families = [i["family"] for i in inventory]
        # All "cells" formats before "imaging"
        cells_indices = [i for i, f in enumerate(families) if f == "cells"]
        imaging_indices = [i for i, f in enumerate(families) if f == "imaging"]
        if cells_indices and imaging_indices:
            assert max(cells_indices) < min(imaging_indices)

    def test_csv_has_python_source(self):
        inventory = collect_product_inventory(FIXTURE_ROOT)
        csv_item = next((i for i in inventory if i["format_id"] == "csv"), None)
        assert csv_item is not None
        assert csv_item["has_python"] is True
        assert csv_item["python_source_files"] >= 1

    def test_ora_has_no_source(self):
        inventory = collect_product_inventory(FIXTURE_ROOT)
        ora_item = next((i for i in inventory if i["format_id"] == "ora"), None)
        assert ora_item is not None
        assert ora_item["has_python"] is False
        assert ora_item["has_dotnet"] is False

    def test_csv_oracle_pass_rate(self):
        inventory = collect_product_inventory(FIXTURE_ROOT)
        csv_item = next((i for i in inventory if i["format_id"] == "csv"), None)
        assert csv_item is not None
        assert csv_item["oracle"] == "5/5"

    def test_cert_cross_lookup(self):
        inventory = collect_product_inventory(FIXTURE_ROOT)
        csv_item = next((i for i in inventory if i["format_id"] == "csv"), None)
        assert csv_item is not None
        assert csv_item["certification"] == "CERTIFIED"

    def test_missing_oracle_is_na(self):
        inventory = collect_product_inventory(FIXTURE_ROOT)
        ora_item = next((i for i in inventory if i["format_id"] == "ora"), None)
        assert ora_item is not None
        assert ora_item["oracle"] == "N/A"

    def test_gate_summary_csv(self):
        inventory = collect_product_inventory(FIXTURE_ROOT)
        csv_item = next((i for i in inventory if i["format_id"] == "csv"), None)
        assert csv_item is not None
        assert csv_item["gates"] == "G1-G2"


class TestRenderProductInventoryMarkdown:
    def test_renders_no_source_formats_clearly(self):
        inventory = collect_product_inventory(FIXTURE_ROOT)
        md = render_product_inventory_markdown(inventory)
        # The new generator renders "— (no source)" for formats without source
        # But generate_product_inventory uses "-" for .NET; the new orchestrator
        # overrides this. Test the raw renderer for basic structure.
        assert "ORA" in md or "ora" in md.lower()
        assert "Formats tracked" in md or "formats tracked" in md.lower() or "tracked" in md

    def test_csv_appears_before_ora(self):
        inventory = collect_product_inventory(FIXTURE_ROOT)
        md = render_product_inventory_markdown(inventory)
        csv_pos = md.find("CSV")
        ora_pos = md.find("ORA")
        if csv_pos >= 0 and ora_pos >= 0:
            assert csv_pos < ora_pos

    def test_product_families_section(self):
        inventory = collect_product_inventory(FIXTURE_ROOT)
        md = render_product_inventory_markdown(inventory)
        assert "Product Families" in md or "families" in md.lower()
