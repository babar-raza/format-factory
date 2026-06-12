"""
tests/python/dif/test_r166_dif_export_html.py

Tests for DIF export_to_html function.

Sprint: FORMAT-FACTORY-BROAD-SELF-HEALING-PRODUCT-ACCELERATION-RNEXT-001
Queue: broad-accel-q-006
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import export_to_html, write_dif, DifDocument, DifCell


def _make_dif(tmp_path: Path, rows: list[list[object]]) -> Path:
    """Helper: write a DIF file with the given data rows."""
    dif_rows: list[list[DifCell]] = []
    for row in rows:
        dif_row = []
        for val in row:
            if isinstance(val, (int, float)):
                dif_row.append(DifCell(value=val, value_type="numeric"))
            else:
                dif_row.append(DifCell(value=val, value_type="string"))
        dif_rows.append(dif_row)
    doc = DifDocument(
        title="test",
        vectors=max((len(r) for r in rows), default=0),
        tuples=len(rows),
        rows=dif_rows,
    )
    path = tmp_path / "test.dif"
    write_dif(doc, path)
    return path


class TestExportToHtml:
    def test_basic_table_structure(self, tmp_path: Path) -> None:
        path = _make_dif(tmp_path, [["A", "B"], ["1", "2"]])
        html = export_to_html(path)
        assert "<table>" in html
        assert "</table>" in html
        assert "<tr>" in html
        assert "<td>" in html

    def test_values_present(self, tmp_path: Path) -> None:
        path = _make_dif(tmp_path, [["hello", "world"]])
        html = export_to_html(path)
        assert "hello" in html
        assert "world" in html

    def test_html_escaping(self, tmp_path: Path) -> None:
        path = _make_dif(tmp_path, [["<b>bold</b>", "&amp;"]])
        html = export_to_html(path)
        assert "&lt;b&gt;" in html or "b&gt;" in html  # escaped
        assert "<b>" not in html  # raw HTML not present

    def test_empty_dif_returns_empty_table(self, tmp_path: Path) -> None:
        path = _make_dif(tmp_path, [])
        html = export_to_html(path)
        assert html == "<table></table>"

    def test_numeric_values(self, tmp_path: Path) -> None:
        path = _make_dif(tmp_path, [[1.0, 2.0], [3.0, 4.0]])
        html = export_to_html(path)
        # Numeric values should appear as strings
        assert "1" in html
        assert "4" in html

    def test_returns_string(self, tmp_path: Path) -> None:
        path = _make_dif(tmp_path, [["x"]])
        result = export_to_html(path)
        assert isinstance(result, str)

    def test_multiple_rows(self, tmp_path: Path) -> None:
        path = _make_dif(tmp_path, [["r1c1"], ["r2c1"], ["r3c1"]])
        html = export_to_html(path)
        assert html.count("<tr>") == 3
