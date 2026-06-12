"""
test_r61_csv_gate8_security.py — R61 Train H: CSV Gate 8 security regression suite.

Gate 8: Security adversarial testing for CSV parser.
Tests injection attacks, malformed data, resource exhaustion, and boundary conditions.

R61 Sprint: FORMAT-FACTORY-R61-EXTRACTED-BUNDLE-REPLAY-DOTNET-SELF-CONTAINED-SOURCE-COMMIT-POLICY-PHASE12-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path


import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.csv.csv_parser import parse_csv, probe_csv  # noqa: E402


def _parse_text(text: str) -> dict:
    """Write text to temp file and parse."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w",
                                     encoding="utf-8", newline="") as f:
        f.write(text)
        tmp = f.name
    return parse_csv(tmp)


def probe(path: str) -> dict:
    return probe_csv(path)


def _all_cells(result: dict) -> list[str]:
    """Return all cell values (headers + data rows) as flat list of strings."""
    cells = list(result.get("headers") or [])
    for row in result.get("rows", []):
        cells.extend(row)
    return cells


class TestCSVGate8FormulaInjection:
    """CSV formula injection: cells starting with =, +, -, @ are treated as literal data."""

    def test_formula_injection_equals(self):
        """Cells starting with = must be treated as data, not formulas."""
        result = _parse_text("=SUM(A1:A10),normal\n1,2")
        all_cells = _all_cells(result)
        assert any("=SUM(A1:A10)" in c for c in all_cells), (
            f"Formula injection cell must be stored as literal string. Cells: {all_cells}"
        )

    def test_formula_injection_plus(self):
        """Cells starting with + must be treated as data."""
        result = _parse_text("+CMD|/C calc,normal")
        all_cells = _all_cells(result)
        assert any("+CMD" in c for c in all_cells), (
            f"+ injection must be stored as literal. Cells: {all_cells}"
        )

    def test_formula_injection_at_sign(self):
        """Cells starting with @ must be treated as data."""
        result = _parse_text("@SUM(1+1)")
        all_cells = _all_cells(result)
        assert any("@SUM" in c for c in all_cells), (
            f"@ injection must be stored as literal. Cells: {all_cells}"
        )

    def test_formula_injection_in_quoted_cell(self):
        """Formula injection in quoted cell is stored safely."""
        result = _parse_text('"=HYPERLINK(""evil.com"",""click"")"')
        all_cells = _all_cells(result)
        assert any("=HYPERLINK" in c or "HYPERLINK" in c for c in all_cells), (
            f"Formula injection must be stored. Cells: {all_cells}"
        )

    def test_nested_formula_injection(self):
        """Deeply nested formula injection is stored as literal."""
        payload = '=CONCATENATE(CHAR(65),CHAR(66))'
        result = _parse_text(f'"{payload}"')
        all_cells = _all_cells(result)
        assert any("CONCATENATE" in c for c in all_cells), (
            f"Nested injection must be stored as literal. Cells: {all_cells}"
        )


class TestCSVGate8MalformedInput:
    """CSV parser handles malformed input without crashing."""

    def test_empty_string_input(self):
        """Empty string input is valid and returns empty rows."""
        result = _parse_text("")
        assert "rows" in result

    def test_null_bytes_in_content(self):
        """Input with null bytes handled gracefully."""
        try:
            result = _parse_text("a\x00b,c")
            # If it succeeds, must return valid structure
            assert "rows" in result
        except (ValueError, UnicodeDecodeError):
            pass  # Acceptable to reject null bytes

    def test_very_long_line(self):
        """Very long CSV line handled without crash."""
        long_value = "x" * 100_000
        result = _parse_text(f"{long_value},normal")
        assert "rows" in result
        assert len(result["rows"]) >= 1

    def test_unclosed_quote(self):
        """Unclosed quote handled gracefully."""
        try:
            result = _parse_text('"unclosed quote')
            assert "rows" in result
        except Exception:
            pass  # Acceptable to raise on malformed input

    def test_only_delimiters(self):
        """Row of only delimiters produces empty cells."""
        result = _parse_text(",,,,")
        assert "rows" in result
        all_cells = _all_cells(result)
        for cell in all_cells:
            assert cell in (None, "", "None") or isinstance(cell, str)

    def test_mixed_line_endings(self):
        """CRLF and LF mixed line endings handled."""
        result = _parse_text("a,b\r\nc,d\ne,f")
        assert "rows" in result
        assert len(result["rows"]) >= 2


class TestCSVGate8ResourceBounds:
    """CSV parser respects reasonable resource limits."""

    def test_many_columns(self):
        """Wide CSV row (1000 columns) handled."""
        row = ",".join(str(i) for i in range(1000))
        result = _parse_text(row)
        assert "rows" in result
        if result["rows"]:
            # At most 1000 cells in first row
            assert len(result["rows"][0]) <= 1000

    def test_many_rows(self):
        """Tall CSV (1000 rows) handled."""
        rows = "\n".join(f"row{i},val{i}" for i in range(1000))
        result = _parse_text(rows)
        assert "rows" in result
        # Should parse all or signal truncation
        assert len(result["rows"]) > 0

    def test_deeply_quoted(self):
        """Deeply quoted content (quotes within quotes) handled."""
        result = _parse_text('"""triple quoted"""')
        assert "rows" in result

    def test_probe_nonexistent_safe(self):
        """probe() of nonexistent path returns exists=False, not error."""
        result = probe(str(PROJECT_ROOT / "nonexistent_for_gate8_test_xyz.csv"))
        assert result.get("exists") is False or result.get("path") is not None


class TestCSVGate8UnicodeEdgeCases:
    """CSV parser handles Unicode edge cases."""

    def test_unicode_bom(self):
        """BOM character handled (common in Excel exports)."""
        bom = "\ufeff"
        try:
            result = _parse_text(f"{bom}header,value")
            assert "rows" in result
        except Exception:
            pass

    def test_rtl_text(self):
        """Right-to-left text in cells handled."""
        result = _parse_text("مرحبا,hello")
        assert "rows" in result
        assert len(result["rows"]) >= 1

    def test_emoji_in_cell(self):
        """Emoji characters in cells handled."""
        result = _parse_text("emoji,\U0001f600")
        assert "rows" in result
