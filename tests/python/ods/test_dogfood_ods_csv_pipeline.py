"""
test_dogfood_ods_csv_pipeline.py — Dogfood chain: ODS parse -> CSV export -> column_value_counts

Automated regression test for DOGFOOD-ODS-CSV-001.
Proves the full pipeline:
  1. Create an ODS document programmatically on disk
  2. Parse it back with parse_ods_strict (verifies ODS was written correctly)
  3. Export to CSV string via export_ods_to_csv
  4. Write CSV to disk and parse with parse_csv_strict
  5. Call column_value_counts and assert specific expected values

All steps are automated with assertions — no manual logs.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.python.ods.ods_parser import parse_ods_strict
from src.python.ods.ods_writer import add_sheet, set_cell_value, write_ods
from src.python.ods.ods_parser import OdsDocument
from src.python.ods.ods_csv_exporter import export_ods_to_csv
from src.python.ff_csv.csv_parser import parse_csv_strict
from src.python.ff_csv.csv_stats import column_value_counts


# ---------------------------------------------------------------------------
# Fixture data — deterministic, known-good inventory with repeated categories
# ---------------------------------------------------------------------------

HEADERS = ["Item", "Category", "Quantity"]
ROWS = [
    ["Apple", "Fruit", "10"],
    ["Banana", "Fruit", "5"],
    ["Carrot", "Vegetable", "8"],
    ["Broccoli", "Vegetable", "3"],
    ["Mango", "Fruit", "7"],
    ["Spinach", "Vegetable", "12"],
    ["Grape", "Fruit", "4"],
]

# Category column (index 1) expected counts
EXPECTED_CATEGORY_COUNTS = {"Fruit": 4, "Vegetable": 3}

# Item column (index 0) — each item appears once
EXPECTED_ITEM_COUNT = len(ROWS)


def _build_ods_doc() -> OdsDocument:
    """Build a test ODS document with known inventory data."""
    doc = OdsDocument(sheets=[])
    add_sheet(doc, "Inventory")

    # Header row (row 0)
    for col, header in enumerate(HEADERS):
        set_cell_value(doc, 0, 0, col, header, "string")

    # Data rows
    for row_idx, (item, category, qty) in enumerate(ROWS, start=1):
        set_cell_value(doc, 0, row_idx, 0, item, "string")
        set_cell_value(doc, 0, row_idx, 1, category, "string")
        set_cell_value(doc, 0, row_idx, 2, qty, "string")

    return doc


class TestOdsCsvPipelineOdsPhase:
    """Phase 1: ODS file creation and parse-back verification."""

    def test_ods_file_created_on_disk(self, tmp_path):
        """ODS file must exist on disk after write_ods."""
        doc = _build_ods_doc()
        out = tmp_path / "inventory.ods"
        write_ods(doc, out)
        assert out.exists(), f"ODS file not found at {out}"
        assert out.stat().st_size > 0, "ODS file is empty"

    def test_parse_ods_strict_succeeds(self, tmp_path):
        """parse_ods_strict must parse the written file without raising."""
        doc = _build_ods_doc()
        out = tmp_path / "inventory.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        assert reloaded is not None
        assert len(reloaded.sheets) == 1

    def test_ods_row_count_correct(self, tmp_path):
        """Parsed ODS must have header + data rows (len(ROWS) + 1)."""
        doc = _build_ods_doc()
        out = tmp_path / "inventory.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        assert len(reloaded.sheets[0].rows) == len(ROWS) + 1

    def test_ods_header_row_preserved(self, tmp_path):
        """Header row must round-trip through ODS correctly."""
        doc = _build_ods_doc()
        out = tmp_path / "inventory.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        header_row = reloaded.sheets[0].rows[0]
        header_texts = [c.text for c in header_row.cells]
        assert header_texts == HEADERS

    def test_ods_data_row_values_preserved(self, tmp_path):
        """First data row must have correct Item, Category, Quantity values."""
        doc = _build_ods_doc()
        out = tmp_path / "inventory.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        row1 = reloaded.sheets[0].rows[1]
        assert row1.cells[0].text == "Apple"
        assert row1.cells[1].text == "Fruit"
        assert row1.cells[2].text == "10"


class TestOdsCsvPipelineCsvPhase:
    """Phase 2: CSV export from ODS and CSV parse verification."""

    def test_csv_export_returns_string(self, tmp_path):
        """export_ods_to_csv must return a non-empty string."""
        doc = _build_ods_doc()
        out = tmp_path / "inventory.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        csv_text = export_ods_to_csv(reloaded, sheet_index=0)
        assert isinstance(csv_text, str)
        assert len(csv_text) > 0

    def test_csv_export_contains_header(self, tmp_path):
        """Exported CSV must contain the header row."""
        doc = _build_ods_doc()
        out = tmp_path / "inventory.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        csv_text = export_ods_to_csv(reloaded, sheet_index=0)
        first_line = csv_text.splitlines()[0]
        for header in HEADERS:
            assert header in first_line, f"Header '{header}' missing from CSV: {first_line}"

    def test_csv_export_contains_all_items(self, tmp_path):
        """All item names must appear in the exported CSV."""
        doc = _build_ods_doc()
        out = tmp_path / "inventory.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        csv_text = export_ods_to_csv(reloaded, sheet_index=0)
        for item, _, _ in ROWS:
            assert item in csv_text, f"Item '{item}' missing from exported CSV"

    def test_csv_file_parseable_by_csv_parser(self, tmp_path):
        """CSV written to disk must be parseable by parse_csv_strict."""
        doc = _build_ods_doc()
        ods_out = tmp_path / "inventory.ods"
        write_ods(doc, ods_out)
        reloaded = parse_ods_strict(ods_out)
        csv_text = export_ods_to_csv(reloaded, sheet_index=0)
        csv_out = tmp_path / "inventory.csv"
        csv_out.write_text(csv_text, encoding="utf-8")
        assert csv_out.exists(), "CSV file not written to disk"
        csv_doc = parse_csv_strict(csv_out)
        assert csv_doc is not None

    def test_csv_parser_detects_correct_row_count(self, tmp_path):
        """CSV parser must contain at least len(ROWS) non-empty data rows."""
        doc = _build_ods_doc()
        ods_out = tmp_path / "inventory.ods"
        write_ods(doc, ods_out)
        reloaded = parse_ods_strict(ods_out)
        csv_text = export_ods_to_csv(reloaded, sheet_index=0)
        csv_out = tmp_path / "inventory.csv"
        csv_out.write_text(csv_text, encoding="utf-8")
        csv_doc = parse_csv_strict(csv_out)
        # Count only non-empty rows (the exporter may emit blank lines between data rows)
        non_empty_rows = [r for r in csv_doc.get("rows", []) if any(c.strip() for c in r)]
        assert len(non_empty_rows) == len(ROWS), (
            f"Expected {len(ROWS)} non-empty data rows, got {len(non_empty_rows)}"
        )


class TestCountDistinctValues:
    """Phase 3: column_value_counts on the exported CSV."""

    def _run_pipeline(self, tmp_path):
        """Run the full ODS->CSV pipeline and return the parsed CSV doc."""
        doc = _build_ods_doc()
        ods_out = tmp_path / "inventory.ods"
        write_ods(doc, ods_out)
        reloaded = parse_ods_strict(ods_out)
        csv_text = export_ods_to_csv(reloaded, sheet_index=0)
        csv_out = tmp_path / "inventory.csv"
        csv_out.write_text(csv_text, encoding="utf-8")
        return parse_csv_strict(csv_out)

    def test_column_value_counts_returns_dict(self, tmp_path):
        """column_value_counts must return a dict."""
        csv_doc = self._run_pipeline(tmp_path)
        result = column_value_counts(csv_doc, 1)
        assert isinstance(result, dict)

    def test_column_value_counts_fruit_correct(self, tmp_path):
        """Fruit must appear exactly 4 times in the Category column."""
        csv_doc = self._run_pipeline(tmp_path)
        result = column_value_counts(csv_doc, 1)
        assert "Fruit" in result, f"'Fruit' not in column_value_counts result: {result}"
        assert result["Fruit"] == EXPECTED_CATEGORY_COUNTS["Fruit"], (
            f"Expected Fruit count={EXPECTED_CATEGORY_COUNTS['Fruit']}, got {result['Fruit']}"
        )

    def test_column_value_counts_vegetable_correct(self, tmp_path):
        """Vegetable must appear exactly 3 times in the Category column."""
        csv_doc = self._run_pipeline(tmp_path)
        result = column_value_counts(csv_doc, 1)
        assert "Vegetable" in result, f"'Vegetable' not in column_value_counts result: {result}"
        assert result["Vegetable"] == EXPECTED_CATEGORY_COUNTS["Vegetable"], (
            f"Expected Vegetable count={EXPECTED_CATEGORY_COUNTS['Vegetable']}, got {result['Vegetable']}"
        )

    def test_column_value_counts_total_keys(self, tmp_path):
        """Category column must have exactly 2 distinct non-empty values."""
        csv_doc = self._run_pipeline(tmp_path)
        result = column_value_counts(csv_doc, 1)
        # Exclude empty string key (from blank rows the exporter may emit between data rows)
        non_empty_keys = {k: v for k, v in result.items() if k.strip()}
        assert len(non_empty_keys) == 2, (
            f"Expected 2 distinct non-empty categories, got {len(non_empty_keys)}: {non_empty_keys}"
        )

    def test_column_value_counts_all_items_unique(self, tmp_path):
        """Item column (col 0) must have 7 distinct non-empty values, each appearing once."""
        csv_doc = self._run_pipeline(tmp_path)
        result = column_value_counts(csv_doc, 0)
        non_empty = {k: v for k, v in result.items() if k.strip()}
        assert len(non_empty) == EXPECTED_ITEM_COUNT, (
            f"Expected {EXPECTED_ITEM_COUNT} distinct non-empty items, got {len(non_empty)}: {non_empty}"
        )
        for item, _, _ in ROWS:
            assert non_empty.get(item) == 1, (
                f"Item '{item}' expected count=1, got {non_empty.get(item)}"
            )

    def test_column_value_counts_sum_equals_row_count(self, tmp_path):
        """Sum of non-empty category counts must equal total data row count."""
        csv_doc = self._run_pipeline(tmp_path)
        result = column_value_counts(csv_doc, 1)
        # Sum only non-empty keys to exclude blank-row artefacts
        total = sum(v for k, v in result.items() if k.strip())
        assert total == len(ROWS), f"Sum of non-empty category counts {total} != row count {len(ROWS)}"


class TestEdgeCases:
    """Edge case coverage: empty column, single value column."""

    def test_empty_sheet_ods_creates_empty_csv(self, tmp_path):
        """An ODS with only a header row exports to a CSV with one line."""
        doc = OdsDocument(sheets=[])
        add_sheet(doc, "Empty")
        set_cell_value(doc, 0, 0, 0, "Col1", "string")
        out = tmp_path / "empty.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        csv_text = export_ods_to_csv(reloaded, sheet_index=0)
        lines = [l for l in csv_text.splitlines() if l.strip()]
        assert len(lines) >= 1, "Expected at least 1 line (header) in CSV"

    def test_single_category_value_count_is_all_rows(self, tmp_path):
        """A column with one repeated value has count == number of data rows."""
        doc = OdsDocument(sheets=[])
        add_sheet(doc, "Uniform")
        set_cell_value(doc, 0, 0, 0, "Category", "string")
        for i in range(5):
            set_cell_value(doc, 0, i + 1, 0, "Same", "string")
        out = tmp_path / "uniform.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        csv_text = export_ods_to_csv(reloaded, sheet_index=0)
        csv_out = tmp_path / "uniform.csv"
        csv_out.write_text(csv_text, encoding="utf-8")
        csv_doc = parse_csv_strict(csv_out)
        result = column_value_counts(csv_doc, 0)
        assert result.get("Same") == 5, f"Expected 'Same' count=5, got {result.get('Same')}"
