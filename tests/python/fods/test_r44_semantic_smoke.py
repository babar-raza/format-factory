"""
R44 MT2 Lane 2B: FODS Python semantic smoke tests.

Verifies the FODS Python package produces correct semantic output
for all 4 valid samples. These are the RC-level contract tests:
- ok is not False (no parse error)
- format_id == 'fods'
- sheet_count > 0
- sheets list is non-empty
- Each sheet has rows
- At least one cell has a typed value
- Formula cells have non-None formula string
- Typed-values sample contains mixed types

Sprint: FORMAT-FACTORY-R44-TWO-PRODUCT-LOCAL-RC-BASELINE-001
"""

import pathlib
import sys


REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SAMPLES = REPO_ROOT / "samples" / "by-format" / "fods"

sys.path.insert(0, str(REPO_ROOT / "src" / "python"))
from fods.parser import parse_fods  # noqa: E402


def _parse(filename):
    return parse_fods(str(SAMPLES / filename))


class TestFodsSemanticSmoke:
    """RC-level semantic smoke: every sample must parse with real content."""

    def test_minimal_spreadsheet_ok(self):
        r = _parse("minimal-spreadsheet.fods")
        assert r.get("error") is None, f"Parse error: {r.get('error')}"
        assert r.get("format_id") == "fods"
        assert r.get("sheet_count", 0) >= 1
        sheets = r.get("sheets", [])
        assert sheets, "sheets list must be non-empty"
        rows = sheets[0].get("rows", [])
        assert rows, "first sheet must have at least one row"
        cells = rows[0].get("cells", [])
        assert cells, "first row must have at least one cell"
        assert cells[0]["value_type"] == "string"
        assert cells[0]["value"] == "Hello"

    def test_formula_basic_has_formula_cells(self):
        r = _parse("formula-basic.fods")
        assert r.get("error") is None
        sheets = r.get("sheets", [])
        assert sheets
        all_cells = [
            cell
            for sheet in sheets
            for row in sheet.get("rows", [])
            for cell in row.get("cells", [])
        ]
        formula_cells = [c for c in all_cells if c.get("formula") is not None]
        assert formula_cells, "formula-basic.fods must contain at least one formula cell"
        for fc in formula_cells:
            assert isinstance(fc["formula"], str) and fc["formula"], (
                f"Formula must be a non-empty string, got: {fc['formula']!r}"
            )

    def test_multi_sheet_has_two_sheets(self):
        r = _parse("multi-sheet-basic.fods")
        assert r.get("error") is None
        assert r.get("sheet_count") == 2, (
            f"multi-sheet-basic.fods must have 2 sheets, got: {r.get('sheet_count')}"
        )
        sheets = r.get("sheets", [])
        assert len(sheets) == 2
        # Each sheet must have rows
        for i, sh in enumerate(sheets):
            assert sh.get("rows"), f"Sheet {i} must have rows"

    def test_typed_values_has_multiple_value_types(self):
        r = _parse("typed-values-basic.fods")
        assert r.get("error") is None
        sheets = r.get("sheets", [])
        assert sheets
        all_cells = [
            cell
            for sheet in sheets
            for row in sheet.get("rows", [])
            for cell in row.get("cells", [])
        ]
        types_seen = {c["value_type"] for c in all_cells if c.get("value_type")}
        assert len(types_seen) >= 2, (
            f"typed-values-basic.fods must contain multiple value types, got: {types_seen}"
        )

    def test_all_samples_return_format_id_fods(self):
        for fods_file in sorted(SAMPLES.glob("*.fods")):
            r = parse_fods(str(fods_file))
            assert r.get("format_id") == "fods", (
                f"{fods_file.name}: expected format_id='fods', got {r.get('format_id')!r}"
            )

    def test_all_samples_have_nonempty_sheets(self):
        for fods_file in sorted(SAMPLES.glob("*.fods")):
            r = parse_fods(str(fods_file))
            if r.get("error"):
                continue  # skip if parse error
            sheets = r.get("sheets", [])
            assert sheets, f"{fods_file.name}: sheets list must not be empty"
            assert r.get("sheet_count", 0) == len(sheets), (
                f"{fods_file.name}: sheet_count {r.get('sheet_count')} != len(sheets) {len(sheets)}"
            )

    def test_all_samples_no_unexpected_parse_errors(self):
        """Valid FODS samples must parse without errors."""
        for fods_file in sorted(SAMPLES.glob("*.fods")):
            r = parse_fods(str(fods_file))
            assert r.get("error") is None, (
                f"{fods_file.name}: unexpected parse error: {r.get('error')}"
            )
            errors = r.get("parse_errors", [])
            assert not errors, f"{fods_file.name}: unexpected parse_errors: {errors}"
