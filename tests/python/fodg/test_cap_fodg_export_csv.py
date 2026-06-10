"""Tests for FODG export_to_csv capability (gap: GAP-FODG-FOSS-EXPORT_TO_CS-001).

Sprint: FORMAT-FACTORY-BROAD-CAPABILITY-LAYER-HEALING-VERIFICATION-PRODUCT-AUTONOMY-MEGA-SPRINT
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))

from src.python.fodg.fodg_codec import create_fodg, write_fodg, export_to_csv, FodgError


def _make_fodg(tmp_path, pages):
    p = tmp_path / "sample.fodg"
    model = create_fodg(pages)
    write_fodg(model, p)
    return p


def test_export_to_csv_returns_string(tmp_path):
    """export_to_csv returns a non-empty CSV string."""
    p = _make_fodg(tmp_path, [{"name": "Page1", "texts": ["Hello", "World"]}])
    csv_str = export_to_csv(p)
    assert isinstance(csv_str, str)
    assert len(csv_str) > 0


def test_export_to_csv_header_row(tmp_path):
    """CSV output includes page_name, shape_index, text header."""
    p = _make_fodg(tmp_path, [{"name": "Page1", "texts": ["A"]}])
    csv_str = export_to_csv(p)
    lines = csv_str.strip().splitlines()
    assert lines[0] == "page_name,shape_index,text"


def test_export_to_csv_data_rows(tmp_path):
    """Each text string becomes a data row with correct columns."""
    p = _make_fodg(tmp_path, [{"name": "Slide1", "texts": ["First", "Second"]}])
    csv_str = export_to_csv(p)
    lines = csv_str.strip().splitlines()
    assert len(lines) == 3  # header + 2 rows
    assert lines[1] == "Slide1,0,First"
    assert lines[2] == "Slide1,1,Second"


def test_export_to_csv_multiple_pages(tmp_path):
    """Rows from multiple pages are all included."""
    p = _make_fodg(tmp_path, [
        {"name": "P1", "texts": ["A"]},
        {"name": "P2", "texts": ["B", "C"]},
    ])
    csv_str = export_to_csv(p)
    lines = csv_str.strip().splitlines()
    assert len(lines) == 4  # header + 3 data rows
    assert any("P1" in l for l in lines)
    assert any("P2" in l for l in lines)


def test_export_to_csv_empty_document(tmp_path):
    """Empty FODG document produces only header row."""
    p = _make_fodg(tmp_path, [])
    csv_str = export_to_csv(p)
    lines = csv_str.strip().splitlines()
    assert len(lines) == 1
    assert lines[0] == "page_name,shape_index,text"


def test_export_to_csv_writes_file(tmp_path):
    """When dest is provided, CSV is written to file."""
    src = _make_fodg(tmp_path, [{"name": "P1", "texts": ["hello"]}])
    dest = tmp_path / "out.csv"
    result = export_to_csv(src, dest)
    assert dest.exists()
    content = dest.read_text(encoding="utf-8")
    assert "hello" in content
    assert result == content


def test_export_to_csv_commas_in_text_are_quoted(tmp_path):
    """Text values containing commas are properly quoted."""
    p = _make_fodg(tmp_path, [{"name": "P1", "texts": ["a, b, c"]}])
    csv_str = export_to_csv(p)
    lines = csv_str.strip().splitlines()
    data_line = lines[1]
    assert '"a, b, c"' in data_line


def test_export_to_csv_page_name_with_comma_is_quoted(tmp_path):
    """Page names containing commas are properly quoted."""
    p = _make_fodg(tmp_path, [{"name": "Slide, One", "texts": ["text"]}])
    csv_str = export_to_csv(p)
    lines = csv_str.strip().splitlines()
    assert '"Slide, One"' in lines[1]


def test_export_to_csv_from_bytes(tmp_path):
    """export_to_csv works when source is bytes."""
    p = _make_fodg(tmp_path, [{"name": "B", "texts": ["bytes_test"]}])
    raw = p.read_bytes()
    csv_str = export_to_csv(raw)
    assert "bytes_test" in csv_str


def test_export_to_csv_shape_index_increments(tmp_path):
    """shape_index column increments per page (resets at each page)."""
    p = _make_fodg(tmp_path, [
        {"name": "P1", "texts": ["t0", "t1", "t2"]},
    ])
    csv_str = export_to_csv(p)
    lines = csv_str.strip().splitlines()[1:]  # skip header
    indices = [int(l.split(",")[1]) for l in lines]
    assert indices == [0, 1, 2]
