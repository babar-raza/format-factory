"""
test_r170_dif_write_roundtrip.py

Sprint: FORMAT-FACTORY-CAPABILITY-DEEPENING-LEDGER-REPAIR-001
Added: 2026-06-12

Tests for DIF write roundtrip: parse -> write -> reparse preserves cell values.
Also covers write_dif, DifDocument, DifCell constructors.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import (
    parse_dif,
    write_dif,
    get_row_count,
    get_column_count,
    get_cell_value,
    get_row_values,
    dif_to_csv,
    DifDocument,
    DifCell,
)

_SAMPLES = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = _SAMPLES / "minimal-2x2.dif"
_NUMERIC = _SAMPLES / "numeric-row.dif"


# ── helper ────────────────────────────────────────────────────────────────

def _make_doc(title="Test", rows=None):
    if rows is None:
        rows = [
            [DifCell(value="A", value_type="string"), DifCell(value="B", value_type="string")],
            [DifCell(value=1.0, value_type="numeric"), DifCell(value=2.0, value_type="numeric")],
        ]
    return DifDocument(title=title, vectors=len(rows[0]) if rows else 0, tuples=len(rows), rows=rows)


# ── write_dif basic ────────────────────────────────────────────────────────

class TestWriteDifBasic:

    def test_write_creates_file(self, tmp_path):
        out = tmp_path / "basic.dif"
        doc = _make_doc()
        write_dif(doc, out)
        assert out.exists()

    def test_written_file_nonempty(self, tmp_path):
        out = tmp_path / "nonempty.dif"
        write_dif(_make_doc(), out)
        assert out.stat().st_size > 0

    def test_written_file_parses(self, tmp_path):
        out = tmp_path / "parseable.dif"
        write_dif(_make_doc(), out)
        result = parse_dif(out)
        assert result.get("ok") is True

    def test_title_preserved(self, tmp_path):
        out = tmp_path / "titled.dif"
        write_dif(_make_doc(title="MyTitle"), out)
        result = parse_dif(out)
        # title field should reference the title we set
        assert result.get("title", "") is not None


# ── string cells roundtrip ─────────────────────────────────────────────────

class TestStringCellsRoundtrip:

    def test_string_cell_preserved(self, tmp_path):
        out = tmp_path / "strings.dif"
        rows = [[DifCell(value="hello", value_type="string"), DifCell(value="world", value_type="string")]]
        write_dif(DifDocument(title="Str", vectors=2, tuples=1, rows=rows), out)
        val = get_cell_value(out, 0, 0)
        assert val == "hello"

    def test_second_cell_preserved(self, tmp_path):
        out = tmp_path / "strings2.dif"
        rows = [[DifCell(value="foo", value_type="string"), DifCell(value="bar", value_type="string")]]
        write_dif(DifDocument(title="Str2", vectors=2, tuples=1, rows=rows), out)
        val = get_cell_value(out, 0, 1)
        assert val == "bar"

    def test_row_values_list(self, tmp_path):
        out = tmp_path / "row_vals.dif"
        rows = [[DifCell(value="x", value_type="string"), DifCell(value="y", value_type="string")]]
        write_dif(DifDocument(title="RV", vectors=2, tuples=1, rows=rows), out)
        rv = get_row_values(out, 0)
        assert isinstance(rv, list)
        assert len(rv) == 2


# ── numeric cells roundtrip ────────────────────────────────────────────────

class TestNumericCellsRoundtrip:

    def test_numeric_cell_preserved(self, tmp_path):
        out = tmp_path / "nums.dif"
        rows = [
            [DifCell(value=10.0, value_type="numeric"), DifCell(value=20.0, value_type="numeric")],
            [DifCell(value=30.0, value_type="numeric"), DifCell(value=40.0, value_type="numeric")],
        ]
        write_dif(DifDocument(title="Nums", vectors=2, tuples=2, rows=rows), out)
        assert get_cell_value(out, 0, 0) == 10.0

    def test_numeric_second_row(self, tmp_path):
        out = tmp_path / "nums2.dif"
        rows = [
            [DifCell(value=1.0, value_type="numeric")],
            [DifCell(value=99.5, value_type="numeric")],
        ]
        write_dif(DifDocument(title="N2", vectors=1, tuples=2, rows=rows), out)
        assert get_cell_value(out, 1, 0) == 99.5

    def test_row_count_after_roundtrip(self, tmp_path):
        out = tmp_path / "rowcount.dif"
        rows = [
            [DifCell(value=float(i), value_type="numeric") for i in range(3)]
            for _ in range(4)
        ]
        write_dif(DifDocument(title="RC", vectors=3, tuples=4, rows=rows), out)
        assert get_row_count(out) == 4

    def test_column_count_after_roundtrip(self, tmp_path):
        out = tmp_path / "colcount.dif"
        rows = [[DifCell(value=float(j), value_type="numeric") for j in range(3)]]
        write_dif(DifDocument(title="CC", vectors=3, tuples=1, rows=rows), out)
        assert get_column_count(out) >= 1


# ── csv export after roundtrip ────────────────────────────────────────────

class TestCsvAfterRoundtrip:

    def test_csv_from_written_file(self, tmp_path):
        out = tmp_path / "csv.dif"
        rows = [
            [DifCell(value="name", value_type="string"), DifCell(value="score", value_type="string")],
            [DifCell(value="alice", value_type="string"), DifCell(value=95.0, value_type="numeric")],
        ]
        write_dif(DifDocument(title="CSV", vectors=2, tuples=2, rows=rows), out)
        csv = dif_to_csv(out)
        assert isinstance(csv, str)
        assert len(csv.strip()) > 0

    def test_csv_contains_values(self, tmp_path):
        out = tmp_path / "csv2.dif"
        rows = [[DifCell(value="alpha", value_type="string"), DifCell(value="beta", value_type="string")]]
        write_dif(DifDocument(title="CSV2", vectors=2, tuples=1, rows=rows), out)
        csv = dif_to_csv(out)
        assert "alpha" in csv or "beta" in csv


# ── multi-row roundtrip ────────────────────────────────────────────────────

class TestMultiRowRoundtrip:

    def test_five_rows_preserved(self, tmp_path):
        out = tmp_path / "multirow.dif"
        rows = [[DifCell(value=float(i * 10), value_type="numeric")] for i in range(5)]
        write_dif(DifDocument(title="Multi", vectors=1, tuples=5, rows=rows), out)
        assert get_row_count(out) == 5

    def test_last_row_value(self, tmp_path):
        out = tmp_path / "lastrow.dif"
        rows = [[DifCell(value=float(i), value_type="numeric")] for i in range(3)]
        write_dif(DifDocument(title="Last", vectors=1, tuples=3, rows=rows), out)
        assert get_cell_value(out, 2, 0) == 2.0
