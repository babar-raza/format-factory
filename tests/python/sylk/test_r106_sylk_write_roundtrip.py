# R106 Wave 3: SYLK write roundtrip with multi-cell grids
# Lane F — SYLK FOSS
# Ledger: R106-FOSS-SYLK-WRITE-ROUNDTRIP-001

from sylk.sylk_parser import (
    parse_sylk_strict,
    write_sylk,
    SylkDocument,
    SylkCell,
)


class TestSylkWriteRoundtrip:
    """SYLK write/parse roundtrip tests."""

    def test_single_cell_numeric(self, tmp_path):
        p = tmp_path / "single.sylk"
        cells = [SylkCell(row=1, col=1, value=42)]
        doc = SylkDocument(cells=cells)
        write_sylk(doc, str(p))
        result = parse_sylk_strict(str(p))
        vals = {(c.row, c.col): c.value for c in result.cells}
        assert vals[(1, 1)] == 42

    def test_single_cell_string(self, tmp_path):
        p = tmp_path / "str.sylk"
        cells = [SylkCell(row=1, col=1, value="hello")]
        doc = SylkDocument(cells=cells)
        write_sylk(doc, str(p))
        result = parse_sylk_strict(str(p))
        vals = {(c.row, c.col): c.value for c in result.cells}
        assert vals[(1, 1)] == "hello"

    def test_2x2_grid(self, tmp_path):
        p = tmp_path / "grid.sylk"
        cells = [
            SylkCell(row=1, col=1, value=1),
            SylkCell(row=1, col=2, value=2),
            SylkCell(row=2, col=1, value=3),
            SylkCell(row=2, col=2, value=4),
        ]
        doc = SylkDocument(cells=cells)
        write_sylk(doc, str(p))
        result = parse_sylk_strict(str(p))
        vals = {(c.row, c.col): c.value for c in result.cells}
        assert vals[(1, 1)] == 1
        assert vals[(1, 2)] == 2
        assert vals[(2, 1)] == 3
        assert vals[(2, 2)] == 4

    def test_mixed_types(self, tmp_path):
        p = tmp_path / "mixed.sylk"
        cells = [
            SylkCell(row=1, col=1, value="Name"),
            SylkCell(row=1, col=2, value="Score"),
            SylkCell(row=2, col=1, value="Alice"),
            SylkCell(row=2, col=2, value=95.5),
        ]
        doc = SylkDocument(cells=cells)
        write_sylk(doc, str(p))
        result = parse_sylk_strict(str(p))
        vals = {(c.row, c.col): c.value for c in result.cells}
        assert vals[(1, 1)] == "Name"
        assert vals[(2, 2)] == 95.5

    def test_empty_doc(self, tmp_path):
        p = tmp_path / "empty.sylk"
        doc = SylkDocument(cells=[])
        write_sylk(doc, str(p))
        result = parse_sylk_strict(str(p))
        assert len(result.cells) == 0

    def test_sparse_grid(self, tmp_path):
        p = tmp_path / "sparse.sylk"
        cells = [
            SylkCell(row=1, col=1, value=1),
            SylkCell(row=5, col=5, value=55),
        ]
        doc = SylkDocument(cells=cells)
        write_sylk(doc, str(p))
        result = parse_sylk_strict(str(p))
        vals = {(c.row, c.col): c.value for c in result.cells}
        assert vals[(1, 1)] == 1
        assert vals[(5, 5)] == 55
        assert len(result.cells) == 2

    def test_float_value(self, tmp_path):
        p = tmp_path / "float.sylk"
        cells = [SylkCell(row=1, col=1, value=3.14159)]
        doc = SylkDocument(cells=cells)
        write_sylk(doc, str(p))
        result = parse_sylk_strict(str(p))
        vals = {(c.row, c.col): c.value for c in result.cells}
        assert abs(vals[(1, 1)] - 3.14159) < 0.001

    def test_negative_value(self, tmp_path):
        p = tmp_path / "neg.sylk"
        cells = [SylkCell(row=1, col=1, value=-99)]
        doc = SylkDocument(cells=cells)
        write_sylk(doc, str(p))
        result = parse_sylk_strict(str(p))
        vals = {(c.row, c.col): c.value for c in result.cells}
        assert vals[(1, 1)] == -99

    def test_file_starts_with_id(self, tmp_path):
        p = tmp_path / "id.sylk"
        doc = SylkDocument(cells=[SylkCell(row=1, col=1, value=1)])
        write_sylk(doc, str(p))
        content = p.read_text()
        assert content.startswith("ID")
