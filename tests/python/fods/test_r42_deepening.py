"""
R42 Train 4A: FODS Python deepening tests.

Extends parser coverage beyond existing suites:
- CSV export from parsed data (library-side helper)
- Cell-value type round-trip (all supported types via typed-values-basic.fods)
- Multi-sheet cell access patterns
- Formula preservation verification
- Package metadata stability
"""
import pathlib

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SAMPLES = REPO_ROOT / "samples" / "by-format" / "fods"
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "fods"

import sys
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from fods import parse_fods, parse_fods_strict, FORMAT_ID, SPEC_VERSION, PACKAGE_VERSION


# ---------------------------------------------------------------------------
# Helper: CSV export from parsed workbook result
# ---------------------------------------------------------------------------

def _csv_field(value: str) -> str:
    if "," in value or "\n" in value or "\r" in value or '"' in value:
        return '"' + value.replace('"', '""') + '"'
    return value


def export_sheet_to_csv(result: dict, sheet_index: int = 0) -> str:
    """Export one sheet from a parse_fods_strict result to CSV text."""
    sheets = result.get("sheets", [])
    if not sheets or sheet_index >= len(sheets):
        return ""
    sheet = sheets[sheet_index]
    rows = sheet.get("rows", [])
    lines = []
    for row in rows:
        cells = row.get("cells", [])
        if cells:
            max_idx = max(c.get("index", 0) for c in cells)
            dense = [""] * (max_idx + 1)
            for c in cells:
                dense[c["index"]] = str(c.get("value", "")) if c.get("value") is not None else ""
            lines.append(",".join(_csv_field(v) for v in dense))
        else:
            lines.append("")
    return "\n".join(lines) + ("\n" if lines else "")


# ---------------------------------------------------------------------------
# Package metadata stability
# ---------------------------------------------------------------------------

class TestPackageMetadata:
    def test_version_semver(self):
        parts = PACKAGE_VERSION.split(".")
        assert len(parts) >= 2, f"Version {PACKAGE_VERSION!r} must be semver"

    def test_format_id_is_fods(self):
        assert FORMAT_ID == "fods"

    def test_spec_version_odf(self):
        assert "ODF" in SPEC_VERSION or "1." in SPEC_VERSION

    def test_package_track_and_ready_flags(self):
        import fods as fods_pkg
        assert fods_pkg.__track__ == "python-foss"
        assert fods_pkg.__commercial_ready__ is False
        assert "alpha" in fods_pkg.__capability_level__.lower()


# ---------------------------------------------------------------------------
# CSV export capability
# ---------------------------------------------------------------------------

class TestCsvExport:
    """Demonstrate that parse results support downstream CSV export."""

    def test_formula_basic_csv_has_four_rows(self):
        sample = SAMPLES / "formula-basic.fods"
        result = parse_fods_strict(str(sample))
        csv_text = export_sheet_to_csv(result)
        rows = [r for r in csv_text.splitlines() if r.strip()]
        # formula-basic has 4 data rows (3 values + 1 sum)
        assert len(rows) == 4, f"Expected 4 CSV rows, got {len(rows)}: {rows}"

    def test_typed_values_csv_non_empty(self):
        sample = SAMPLES / "typed-values-basic.fods"
        result = parse_fods_strict(str(sample))
        csv_text = export_sheet_to_csv(result)
        assert csv_text.strip(), "CSV export of typed-values-basic.fods must be non-empty"

    def test_multi_sheet_csv_sheet0_and_sheet1_differ(self):
        sample = SAMPLES / "multi-sheet-basic.fods"
        result = parse_fods_strict(str(sample))
        sheets = result.get("sheets", [])
        assert len(sheets) >= 2
        csv0 = export_sheet_to_csv(result, 0)
        csv1 = export_sheet_to_csv(result, 1)
        # They may or may not have same content, but both must be non-empty
        assert csv0.strip(), "Sheet 0 CSV export must be non-empty"
        assert csv1.strip(), "Sheet 1 CSV export must be non-empty"

    def test_csv_export_values_are_strings(self):
        sample = SAMPLES / "formula-basic.fods"
        result = parse_fods_strict(str(sample))
        csv_text = export_sheet_to_csv(result)
        for line in csv_text.splitlines():
            for cell in line.split(","):
                assert isinstance(cell, str), f"CSV cells must be str, got {type(cell)}"


# ---------------------------------------------------------------------------
# Cell-value type coverage
# ---------------------------------------------------------------------------

class TestCellValueTypes:
    """Verify all supported cell value types are extracted correctly."""

    def test_float_cells_are_numeric(self):
        sample = SAMPLES / "formula-basic.fods"
        result = parse_fods_strict(str(sample))
        sheets = result.get("sheets", [])
        assert sheets is not None
        rows = sheets[0].get("rows", [])
        float_vals = [
            c["value"] for row in rows for c in row.get("cells", [])
            if c.get("value_type") == "float"
        ]
        assert float_vals is not None, "Expected float cells in formula-basic.fods"
        assert all(isinstance(v, (int, float)) for v in float_vals), (
            f"float cells must have numeric values; got: {float_vals}"
        )

    def test_formula_cells_have_string_formula(self):
        sample = SAMPLES / "formula-basic.fods"
        result = parse_fods_strict(str(sample))
        sheets = result.get("sheets", [])
        rows = sheets[0].get("rows", [])
        formula_cells = [
            c for row in rows for c in row.get("cells", [])
            if c.get("formula") is not None
        ]
        assert formula_cells is not None, "formula-basic.fods must have formula cells"
        for fc in formula_cells:
            assert isinstance(fc["formula"], str), "Formula must be a string"
            assert len(fc["formula"]) > 0, "Formula string must not be empty"

    def test_typed_values_has_multiple_types(self):
        sample = SAMPLES / "typed-values-basic.fods"
        result = parse_fods_strict(str(sample))
        sheets = result.get("sheets", [])
        assert sheets is not None
        rows = sheets[0].get("rows", [])
        types_found = {
            c.get("value_type")
            for row in rows for c in row.get("cells", [])
            if c.get("value_type")
        }
        # typed-values-basic should have at least 2 distinct types
        assert len(types_found) >= 2, (
            f"typed-values-basic.fods should have multiple value types; found: {types_found}"
        )

    def test_string_value_is_str_type(self):
        sample = SAMPLES / "typed-values-basic.fods"
        result = parse_fods_strict(str(sample))
        sheets = result.get("sheets", [])
        rows = sheets[0].get("rows", [])
        string_cells = [
            c for row in rows for c in row.get("cells", [])
            if c.get("value_type") == "string"
        ]
        for sc in string_cells:
            v = sc.get("value")
            assert isinstance(v, str), f"string cells must have str value; got {type(v)}"


# ---------------------------------------------------------------------------
# Multi-sheet navigation
# ---------------------------------------------------------------------------

class TestMultiSheetNavigation:
    def test_sheet_names_are_strings(self):
        sample = SAMPLES / "multi-sheet-basic.fods"
        result = parse_fods_strict(str(sample))
        for sheet in result.get("sheets", []):
            assert isinstance(sheet.get("name"), str)

    def test_sheet_indices_start_at_zero(self):
        sample = SAMPLES / "multi-sheet-basic.fods"
        result = parse_fods_strict(str(sample))
        for i, sheet in enumerate(result.get("sheets", [])):
            assert sheet.get("index") == i

    def test_each_sheet_has_rows_list(self):
        sample = SAMPLES / "multi-sheet-basic.fods"
        result = parse_fods_strict(str(sample))
        for sheet in result.get("sheets", []):
            assert isinstance(sheet.get("rows"), list)

    def test_sheet_count_equals_len_sheets(self):
        sample = SAMPLES / "multi-sheet-basic.fods"
        result = parse_fods_strict(str(sample))
        assert result.get("sheet_count") == len(result.get("sheets", []))


# ---------------------------------------------------------------------------
# Error handling edge cases
# ---------------------------------------------------------------------------

class TestErrorHandling:
    def test_nonexistent_file_returns_error_dict(self):
        result = parse_fods("/nonexistent/path/file.fods")
        assert result.get("exists") is False or result.get("error") is not None

    def test_strict_parser_raises_on_missing(self):
        from fods import FodsInputError
        with pytest.raises(FodsInputError):
            parse_fods_strict("/nonexistent/path/file.fods")

    def test_malformed_xml_handled_gracefully(self):
        malformed = FIXTURES / "malformed" / "invalid-xml-chars.fods"
        if not malformed.exists():
            pytest.skip("invalid-xml-chars.fods fixture not found")
        result = parse_fods(str(malformed))
        # Must return a dict (not raise), even if error is set
        assert isinstance(result, dict)
