"""Tests for dif_column_types and dif_row_value_counts.

Product deepening: DIF analytics — TC-H3-001 / PDC-DIF-COLUMN-TYPES-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif import (
    dif_column_types,
    dif_row_value_counts,
    parse_dif_strict,
    write_dif,
    DifDocument,
    DifCell,
)

VALID_SAMPLES = _REPO / "samples" / "by-format" / "dif" / "valid"


def _make_dif_file(tmp_path, title, rows):
    """Create a DIF file from row data and return its path."""
    doc = DifDocument(title=title, vectors=max(len(r) for r in rows) if rows else 0,
                      tuples=len(rows), rows=rows)
    path = tmp_path / f"{title}.dif"
    write_dif(doc, path)
    return path


class TestDifColumnTypesSynthetic:
    def test_all_numeric(self, tmp_path):
        rows = [[DifCell(1.0, "numeric"), DifCell(2.0, "numeric")],
                [DifCell(3.0, "numeric"), DifCell(4.0, "numeric")]]
        f = _make_dif_file(tmp_path, "allnum", rows)
        result = dif_column_types(f)
        assert result == ["numeric", "numeric"]

    def test_all_string(self, tmp_path):
        rows = [[DifCell("a", "string"), DifCell("b", "string")],
                [DifCell("c", "string"), DifCell("d", "string")]]
        f = _make_dif_file(tmp_path, "allstr", rows)
        result = dif_column_types(f)
        assert result == ["string", "string"]

    def test_mixed_columns(self, tmp_path):
        rows = [[DifCell(1.0, "numeric"), DifCell("a", "string")],
                [DifCell(2.0, "numeric"), DifCell("b", "string")]]
        f = _make_dif_file(tmp_path, "mixed", rows)
        result = dif_column_types(f)
        assert result == ["numeric", "string"]

    def test_empty_document(self, tmp_path):
        doc = DifDocument(title="empty", vectors=0, tuples=0, rows=[])
        path = tmp_path / "empty.dif"
        write_dif(doc, path)
        result = dif_column_types(path)
        assert result == []

    def test_returns_list_of_strings(self, tmp_path):
        rows = [[DifCell(1.0, "numeric")]]
        f = _make_dif_file(tmp_path, "types", rows)
        result = dif_column_types(f)
        assert isinstance(result, list)
        assert all(isinstance(t, str) for t in result)

    def test_numeric_tie_with_string(self, tmp_path):
        rows = [[DifCell(1.0, "numeric")], [DifCell("x", "string")]]
        f = _make_dif_file(tmp_path, "tie", rows)
        result = dif_column_types(f)
        assert result[0] in ("numeric", "string")


class TestDifColumnTypesFromSamples:
    def test_numeric_row_sample(self):
        path = VALID_SAMPLES / "numeric-row.dif"
        if path.exists():
            result = dif_column_types(path)
            assert isinstance(result, list)
            assert len(result) > 0

    def test_minimal_2x2_sample(self):
        path = VALID_SAMPLES / "minimal-2x2.dif"
        if path.exists():
            result = dif_column_types(path)
            assert isinstance(result, list)
            assert len(result) >= 2


class TestDifRowValueCountsSynthetic:
    def test_all_filled(self, tmp_path):
        rows = [[DifCell(1.0, "numeric"), DifCell("a", "string")],
                [DifCell(2.0, "numeric"), DifCell("b", "string")]]
        f = _make_dif_file(tmp_path, "filled", rows)
        result = dif_row_value_counts(f)
        assert result == [2, 2]

    def test_with_none_values(self, tmp_path):
        """DIF write/parse round-trip converts None to non-None; count reflects parsed state."""
        rows = [[DifCell(1.0, "numeric"), DifCell(None, "string")],
                [DifCell(None, "string"), DifCell("b", "string")]]
        f = _make_dif_file(tmp_path, "nones", rows)
        result = dif_row_value_counts(f)
        assert result == [2, 2]

    def test_empty_document(self, tmp_path):
        doc = DifDocument(title="empty", vectors=0, tuples=0, rows=[])
        path = tmp_path / "empty2.dif"
        write_dif(doc, path)
        result = dif_row_value_counts(path)
        assert result == []

    def test_returns_list_of_ints(self, tmp_path):
        rows = [[DifCell(1.0, "numeric")]]
        f = _make_dif_file(tmp_path, "ints", rows)
        result = dif_row_value_counts(f)
        assert isinstance(result, list)
        assert all(isinstance(c, int) for c in result)

    def test_from_sample(self):
        path = VALID_SAMPLES / "minimal-2x2.dif"
        if path.exists():
            result = dif_row_value_counts(path)
            assert isinstance(result, list)
            assert len(result) > 0
