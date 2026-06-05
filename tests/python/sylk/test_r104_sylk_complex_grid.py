# R104 Wave 2: SYLK complex grid roundtrip and write hardening
# Lane F — SYLK FOSS hardening
# Ledger: R104-FOSS-SYLK-COMPLEX-GRID-001

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


class TestComplexGridRoundtrip:
    """Verify write/parse roundtrip with multi-row, multi-column grids."""

    def test_5x5_numeric_grid(self, tmp_path):
        doc = SylkDocument(rows=5, cols=5)
        for r in range(1, 6):
            for c in range(1, 6):
                doc.cells.append(SylkCell(row=r, col=c, value=r * 10 + c, value_type="numeric"))
        p = tmp_path / "5x5.sylk"
        write_sylk(doc, p)
        parsed = parse_sylk_strict(str(p))
        assert parsed.rows == 5
        assert parsed.cols == 5
        assert len(parsed.cells) == 25

    def test_3x3_string_grid(self, tmp_path):
        doc = SylkDocument(rows=3, cols=3)
        for r in range(1, 4):
            for c in range(1, 4):
                doc.cells.append(SylkCell(row=r, col=c, value=f"R{r}C{c}", value_type="string"))
        p = tmp_path / "3x3str.sylk"
        write_sylk(doc, p)
        parsed = parse_sylk_strict(str(p))
        vals = {(c.row, c.col): c.value for c in parsed.cells}
        assert vals[(1, 1)] == "R1C1"
        assert vals[(3, 3)] == "R3C3"

    def test_mixed_types_grid(self, tmp_path):
        doc = SylkDocument(rows=2, cols=3)
        doc.cells.append(SylkCell(row=1, col=1, value=42, value_type="numeric"))
        doc.cells.append(SylkCell(row=1, col=2, value="hello", value_type="string"))
        doc.cells.append(SylkCell(row=1, col=3, value=3.14, value_type="numeric"))
        doc.cells.append(SylkCell(row=2, col=1, value="world", value_type="string"))
        doc.cells.append(SylkCell(row=2, col=2, value=0, value_type="numeric"))
        doc.cells.append(SylkCell(row=2, col=3, value=-1.5, value_type="numeric"))
        p = tmp_path / "mixed.sylk"
        write_sylk(doc, p)
        parsed = parse_sylk_strict(str(p))
        vals = {(c.row, c.col): c.value for c in parsed.cells}
        assert vals[(1, 1)] == 42
        assert vals[(1, 2)] == "hello"

    def test_sparse_grid(self, tmp_path):
        doc = SylkDocument(rows=10, cols=10)
        doc.cells.append(SylkCell(row=1, col=1, value=1, value_type="numeric"))
        doc.cells.append(SylkCell(row=5, col=5, value=55, value_type="numeric"))
        doc.cells.append(SylkCell(row=10, col=10, value=100, value_type="numeric"))
        p = tmp_path / "sparse.sylk"
        write_sylk(doc, p)
        parsed = parse_sylk_strict(str(p))
        vals = {(c.row, c.col): c.value for c in parsed.cells}
        assert vals[(1, 1)] == 1
        assert vals[(5, 5)] == 55
        assert vals[(10, 10)] == 100

    def test_single_cell_roundtrip(self, tmp_path):
        doc = SylkDocument(rows=1, cols=1)
        doc.cells.append(SylkCell(row=1, col=1, value=99, value_type="numeric"))
        p = tmp_path / "single.sylk"
        write_sylk(doc, p)
        parsed = parse_sylk_strict(str(p))
        assert len(parsed.cells) == 1
        assert parsed.cells[0].value == 99

    def test_empty_document_roundtrip(self, tmp_path):
        doc = SylkDocument(rows=0, cols=0)
        p = tmp_path / "empty.sylk"
        write_sylk(doc, p)
        content = p.read_bytes()
        assert content.startswith(b"ID;P")
        assert content.rstrip().endswith(b"E")


class TestWriteSylkFileFormat:
    """Verify file format properties."""

    def test_crlf_line_endings(self, tmp_path):
        doc = SylkDocument(rows=1, cols=1)
        doc.cells.append(SylkCell(row=1, col=1, value=1, value_type="numeric"))
        p = tmp_path / "crlf.sylk"
        write_sylk(doc, p)
        raw = p.read_bytes()
        assert b"\r\n" in raw

    def test_id_header_present(self, tmp_path):
        doc = SylkDocument()
        p = tmp_path / "header.sylk"
        write_sylk(doc, p)
        content = p.read_bytes().decode("ascii")
        assert content.startswith("ID;P")

    def test_e_footer_present(self, tmp_path):
        doc = SylkDocument()
        p = tmp_path / "footer.sylk"
        write_sylk(doc, p)
        content = p.read_bytes().decode("ascii").strip()
        assert content.endswith("E")

    def test_ascii_encoding(self, tmp_path):
        doc = SylkDocument(rows=1, cols=1)
        doc.cells.append(SylkCell(row=1, col=1, value="hello", value_type="string"))
        p = tmp_path / "ascii.sylk"
        write_sylk(doc, p)
        raw = p.read_bytes()
        raw.decode("ascii")  # should not raise


class TestSylkToCsvComplex:
    """Verify CSV export with complex grids."""

    def test_3x3_csv_export(self, tmp_path):
        doc = SylkDocument(rows=3, cols=3)
        for r in range(1, 4):
            for c in range(1, 4):
                doc.cells.append(SylkCell(row=r, col=c, value=r * c, value_type="numeric"))
        p = tmp_path / "grid.sylk"
        write_sylk(doc, p)
        csv_text = sylk_to_csv(str(p))
        lines = csv_text.strip().split("\r\n")
        assert len(lines) == 3
        assert lines[0] == "1,2,3"
        assert lines[1] == "2,4,6"
        assert lines[2] == "3,6,9"

    def test_sparse_csv_has_empty_fields(self, tmp_path):
        doc = SylkDocument(rows=2, cols=3)
        doc.cells.append(SylkCell(row=1, col=1, value=1, value_type="numeric"))
        doc.cells.append(SylkCell(row=2, col=3, value=99, value_type="numeric"))
        p = tmp_path / "sparse.sylk"
        write_sylk(doc, p)
        csv_text = sylk_to_csv(str(p))
        lines = csv_text.strip().split("\r\n")
        assert lines[0] == "1,,"
        assert lines[1] == ",,99"
