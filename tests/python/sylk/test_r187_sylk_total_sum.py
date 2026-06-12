"""
Tests for sylk_total_sum — sum ALL numeric cell values in a SYLK document.
Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT80-001
"""

import sys
import pytest

sys.path.insert(0, "src/python")

from sylk import sylk_total_sum, write_sylk, SylkCell, SylkDocument


def _make_sylk(cells: list[SylkCell], tmp_path, name: str = "test.slk"):
    doc = SylkDocument(rows=0, cols=0, cells=cells)
    path = tmp_path / name
    write_sylk(doc, path)
    return path


def test_total_sum_all_positive(tmp_path):
    cells = [SylkCell(1, 1, 10), SylkCell(1, 2, 20), SylkCell(1, 3, 30)]
    path = _make_sylk(cells, tmp_path)
    assert sylk_total_sum(path) == 60.0


def test_total_sum_includes_floats(tmp_path):
    cells = [SylkCell(1, 1, 1.5), SylkCell(1, 2, 2.5)]
    path = _make_sylk(cells, tmp_path)
    assert abs(sylk_total_sum(path) - 4.0) < 1e-9


def test_total_sum_skips_strings(tmp_path):
    cells = [SylkCell(1, 1, 10), SylkCell(1, 2, "hello"), SylkCell(1, 3, 5)]
    path = _make_sylk(cells, tmp_path)
    assert sylk_total_sum(path) == 15.0


def test_total_sum_empty_document(tmp_path):
    path = _make_sylk([], tmp_path)
    assert sylk_total_sum(path) == 0.0


def test_total_sum_single_cell(tmp_path):
    cells = [SylkCell(1, 1, 42)]
    path = _make_sylk(cells, tmp_path)
    assert sylk_total_sum(path) == 42.0


def test_total_sum_all_strings_returns_zero(tmp_path):
    cells = [SylkCell(1, 1, "a"), SylkCell(1, 2, "b"), SylkCell(1, 3, "c")]
    path = _make_sylk(cells, tmp_path)
    assert sylk_total_sum(path) == 0.0


def test_total_sum_negative_values(tmp_path):
    cells = [SylkCell(1, 1, -10), SylkCell(1, 2, -5), SylkCell(1, 3, 15)]
    path = _make_sylk(cells, tmp_path)
    assert sylk_total_sum(path) == 0.0


def test_total_sum_multi_row(tmp_path):
    cells = [
        SylkCell(1, 1, 1), SylkCell(1, 2, 2),
        SylkCell(2, 1, 3), SylkCell(2, 2, 4),
    ]
    path = _make_sylk(cells, tmp_path)
    assert sylk_total_sum(path) == 10.0


def test_total_sum_skips_none(tmp_path):
    cells = [SylkCell(1, 1, None), SylkCell(1, 2, 7), SylkCell(1, 3, 3)]
    path = _make_sylk(cells, tmp_path)
    assert sylk_total_sum(path) == 10.0


def test_total_sum_large_values(tmp_path):
    cells = [SylkCell(1, 1, 1_000_000), SylkCell(1, 2, 2_000_000)]
    path = _make_sylk(cells, tmp_path)
    assert sylk_total_sum(path) == 3_000_000.0
