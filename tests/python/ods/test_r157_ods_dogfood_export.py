"""
test_r157_ods_dogfood_export.py — Dogfood export: use ODS library to build a real spreadsheet.

Demonstrates practical usage of format-factory-ods by creating a format registry
spreadsheet from structured data, writing to ODS, and verifying roundtrip.
"""
from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from src.python.ods.ods_parser import (
    OdsDocument,
    parse_ods_strict,
)
from src.python.ods.ods_writer import add_sheet, set_cell_value, write_ods


# Simulated format registry data (dogfood: using our own library for project data)
FORMAT_REGISTRY = [
    {"format": "FODS", "track": "commercial", "gate": 11, "python": True, "dotnet": True},
    {"format": "FODT", "track": "commercial", "gate": 10, "python": True, "dotnet": True},
    {"format": "ABW", "track": "foss", "gate": 4, "python": True, "dotnet": False},
    {"format": "Gnumeric", "track": "foss", "gate": 4, "python": True, "dotnet": False},
    {"format": "DIF", "track": "foss", "gate": 10, "python": True, "dotnet": False},
    {"format": "SYLK", "track": "foss", "gate": 10, "python": True, "dotnet": False},
    {"format": "ODS", "track": "foss", "gate": 4, "python": True, "dotnet": False},
    {"format": "ZST", "track": "foss", "gate": 6, "python": True, "dotnet": False},
    {"format": "TSV", "track": "foss", "gate": 4, "python": True, "dotnet": False},
    {"format": "NDJSON", "track": "foss", "gate": 4, "python": True, "dotnet": False},
]

HEADERS = ["Format", "Track", "Gate", "Python", ".NET"]


def _build_registry_doc() -> OdsDocument:
    """Build an ODS document from the format registry data."""
    doc = OdsDocument(sheets=[])
    add_sheet(doc, "Format Registry")

    # Header row
    for col, header in enumerate(HEADERS):
        set_cell_value(doc, 0, 0, col, header, "string")

    # Data rows
    for row_idx, entry in enumerate(FORMAT_REGISTRY, start=1):
        set_cell_value(doc, 0, row_idx, 0, entry["format"], "string")
        set_cell_value(doc, 0, row_idx, 1, entry["track"], "string")
        set_cell_value(doc, 0, row_idx, 2, entry["gate"], "float")
        set_cell_value(doc, 0, row_idx, 3, "Yes" if entry["python"] else "No", "string")
        set_cell_value(doc, 0, row_idx, 4, "Yes" if entry["dotnet"] else "No", "string")

    return doc


class TestOdsDogfoodExport:
    def test_build_registry_doc(self):
        doc = _build_registry_doc()
        assert len(doc.sheets) == 1
        assert doc.sheets[0].name == "Format Registry"
        assert len(doc.sheets[0].rows) == len(FORMAT_REGISTRY) + 1  # header + data

    def test_write_and_reparse(self, tmp_path):
        doc = _build_registry_doc()
        out = tmp_path / "format-registry.ods"
        write_ods(doc, out)
        assert out.exists()
        reloaded = parse_ods_strict(out)
        assert len(reloaded.sheets) == 1
        assert reloaded.sheets[0].name == "Format Registry"

    def test_roundtrip_preserves_header(self, tmp_path):
        doc = _build_registry_doc()
        out = tmp_path / "format-registry.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        header_row = reloaded.sheets[0].rows[0]
        header_texts = [c.text for c in header_row.cells]
        assert header_texts == HEADERS

    def test_roundtrip_preserves_data_row(self, tmp_path):
        doc = _build_registry_doc()
        out = tmp_path / "format-registry.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        # Check first data row (FODS)
        row1 = reloaded.sheets[0].rows[1]
        assert row1.cells[0].text == "FODS"
        assert row1.cells[1].text == "commercial"

    def test_roundtrip_preserves_row_count(self, tmp_path):
        doc = _build_registry_doc()
        out = tmp_path / "format-registry.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        assert len(reloaded.sheets[0].rows) == len(FORMAT_REGISTRY) + 1

    def test_all_formats_present(self, tmp_path):
        doc = _build_registry_doc()
        out = tmp_path / "format-registry.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        format_names = [r.cells[0].text for r in reloaded.sheets[0].rows[1:]]
        expected = [e["format"] for e in FORMAT_REGISTRY]
        assert format_names == expected

    def test_numeric_gate_values(self, tmp_path):
        doc = _build_registry_doc()
        out = tmp_path / "format-registry.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        # FODS gate should be 11
        fods_row = reloaded.sheets[0].rows[1]
        assert fods_row.cells[2].value_type == "float"
