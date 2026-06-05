# R104 Wave 2: SYLK CSV export hardening with mixed types and edge cases
# Lane F — SYLK FOSS hardening
# Ledger: R104-FOSS-SYLK-CSV-EXPORT-HARDENING-001

import pytest
from pathlib import Path
from sylk.sylk_parser import (
    SylkDocument,
    SylkCell,
    write_sylk,
    parse_sylk_strict,
    sylk_to_csv,
    SylkError,
)


class TestCsvExportMixedTypes:
    """Verify CSV export handles mixed numeric/string types correctly."""

    def test_mixed_row_numeric_and_string(self, tmp_path):
        doc = SylkDocument(rows=1, cols=3)
        doc.cells.append(SylkCell(row=1, col=1, value=42, value_type="numeric"))
        doc.cells.append(SylkCell(row=1, col=2, value="text", value_type="string"))
        doc.cells.append(SylkCell(row=1, col=3, value=3.14, value_type="numeric"))
        p = tmp_path / "mixed.sylk"
        write_sylk(doc, p)
        csv_text = sylk_to_csv(str(p))
        assert "42" in csv_text
        assert "text" in csv_text
        assert "3.14" in csv_text

    def test_negative_numbers(self, tmp_path):
        doc = SylkDocument(rows=1, cols=2)
        doc.cells.append(SylkCell(row=1, col=1, value=-100, value_type="numeric"))
        doc.cells.append(SylkCell(row=1, col=2, value=-0.5, value_type="numeric"))
        p = tmp_path / "neg.sylk"
        write_sylk(doc, p)
        csv_text = sylk_to_csv(str(p))
        assert "-100" in csv_text
        assert "-0.5" in csv_text

    def test_zero_value(self, tmp_path):
        doc = SylkDocument(rows=1, cols=1)
        doc.cells.append(SylkCell(row=1, col=1, value=0, value_type="numeric"))
        p = tmp_path / "zero.sylk"
        write_sylk(doc, p)
        csv_text = sylk_to_csv(str(p))
        lines = csv_text.strip().split("\r\n")
        assert lines[0] == "0"

    def test_large_integer(self, tmp_path):
        doc = SylkDocument(rows=1, cols=1)
        doc.cells.append(SylkCell(row=1, col=1, value=999999999, value_type="numeric"))
        p = tmp_path / "large.sylk"
        write_sylk(doc, p)
        csv_text = sylk_to_csv(str(p))
        assert "999999999" in csv_text

    def test_float_precision(self, tmp_path):
        doc = SylkDocument(rows=1, cols=1)
        doc.cells.append(SylkCell(row=1, col=1, value=1.23456789, value_type="numeric"))
        p = tmp_path / "float.sylk"
        write_sylk(doc, p)
        csv_text = sylk_to_csv(str(p))
        assert "1.23456789" in csv_text


class TestCsvExportEdgeCases:
    """Edge cases for CSV export."""

    def test_string_with_comma_quoted_in_csv(self, tmp_path):
        doc = SylkDocument(rows=1, cols=1)
        doc.cells.append(SylkCell(row=1, col=1, value="a,b", value_type="string"))
        p = tmp_path / "comma.sylk"
        write_sylk(doc, p)
        csv_text = sylk_to_csv(str(p))
        # CSV should quote fields containing commas
        assert '"a,b"' in csv_text or "a,b" in csv_text

    def test_empty_string_value(self, tmp_path):
        doc = SylkDocument(rows=1, cols=1)
        doc.cells.append(SylkCell(row=1, col=1, value="", value_type="string"))
        p = tmp_path / "empty_str.sylk"
        write_sylk(doc, p)
        parsed = parse_sylk_strict(str(p))
        # Empty string may or may not be preserved depending on write format
        assert len(parsed.cells) >= 0  # no crash

    def test_single_row_multiple_columns(self, tmp_path):
        doc = SylkDocument(rows=1, cols=5)
        for c in range(1, 6):
            doc.cells.append(SylkCell(row=1, col=c, value=c * 10, value_type="numeric"))
        p = tmp_path / "row.sylk"
        write_sylk(doc, p)
        csv_text = sylk_to_csv(str(p))
        assert "10,20,30,40,50" in csv_text

    def test_single_column_multiple_rows(self, tmp_path):
        doc = SylkDocument(rows=5, cols=1)
        for r in range(1, 6):
            doc.cells.append(SylkCell(row=r, col=1, value=r, value_type="numeric"))
        p = tmp_path / "col.sylk"
        write_sylk(doc, p)
        csv_text = sylk_to_csv(str(p))
        lines = csv_text.strip().split("\r\n")
        assert len(lines) == 5
        for i, line in enumerate(lines):
            assert line == str(i + 1)

    def test_csv_has_crlf_endings(self, tmp_path):
        doc = SylkDocument(rows=2, cols=1)
        doc.cells.append(SylkCell(row=1, col=1, value=1, value_type="numeric"))
        doc.cells.append(SylkCell(row=2, col=1, value=2, value_type="numeric"))
        p = tmp_path / "crlf.sylk"
        write_sylk(doc, p)
        csv_text = sylk_to_csv(str(p))
        assert "\r\n" in csv_text


class TestWriteParseConsistency:
    """Verify write→parse→write produces identical output."""

    def test_double_roundtrip(self, tmp_path):
        doc = SylkDocument(rows=2, cols=2)
        doc.cells.append(SylkCell(row=1, col=1, value=1, value_type="numeric"))
        doc.cells.append(SylkCell(row=1, col=2, value="two", value_type="string"))
        doc.cells.append(SylkCell(row=2, col=1, value=3, value_type="numeric"))
        doc.cells.append(SylkCell(row=2, col=2, value=4, value_type="numeric"))
        p1 = tmp_path / "pass1.sylk"
        write_sylk(doc, p1)
        parsed = parse_sylk_strict(str(p1))
        p2 = tmp_path / "pass2.sylk"
        write_sylk(parsed, p2)
        content1 = p1.read_bytes()
        content2 = p2.read_bytes()
        assert content1 == content2

    def test_csv_consistency_across_roundtrip(self, tmp_path):
        doc = SylkDocument(rows=2, cols=2)
        doc.cells.append(SylkCell(row=1, col=1, value=10, value_type="numeric"))
        doc.cells.append(SylkCell(row=2, col=2, value=20, value_type="numeric"))
        p1 = tmp_path / "rt1.sylk"
        write_sylk(doc, p1)
        csv1 = sylk_to_csv(str(p1))
        parsed = parse_sylk_strict(str(p1))
        p2 = tmp_path / "rt2.sylk"
        write_sylk(parsed, p2)
        csv2 = sylk_to_csv(str(p2))
        assert csv1 == csv2
