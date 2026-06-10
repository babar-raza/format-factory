"""
test_r157_gnumeric_load_capability.py — Capability coverage test for Gnumeric load function.

Closes GAP-Gnumeric-FOSS-LOAD-001 (missing_test_coverage).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))
from gnumeric.gnumeric_codec import load, create_gnumeric, write_gnumeric


def _make_gnumeric(cells: list[tuple[int, int, str]] | None = None) -> bytes:
    """Create a minimal Gnumeric document as bytes."""
    doc = create_gnumeric([{"name": "Sheet1"}])
    if cells:
        from gnumeric.gnumeric_codec import set_cell_value
        for r, c, v in cells:
            doc = set_cell_value(doc, 0, r, c, v)
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".gnumeric", delete=False) as f:
        path = Path(f.name)
    write_gnumeric(doc, str(path))
    data = path.read_bytes()
    path.unlink()
    return data


class TestGnumericLoadCapability:
    def test_load_returns_dict(self):
        data = _make_gnumeric()
        result = load(data)
        assert isinstance(result, dict)

    def test_load_has_sheets(self):
        data = _make_gnumeric()
        result = load(data)
        assert "sheets" in result

    def test_load_from_path(self, tmp_path):
        doc = create_gnumeric([{"name": "Sheet1"}])
        p = tmp_path / "test.gnumeric"
        write_gnumeric(doc, str(p))
        result = load(str(p))
        assert isinstance(result, dict)

    def test_load_with_data(self):
        data = _make_gnumeric([(0, 0, "Hello"), (1, 0, "World")])
        result = load(data)
        assert result["sheets"][0]["cell_count"] > 0

    def test_load_sheet_name(self):
        data = _make_gnumeric()
        result = load(data)
        assert len(result["sheets"]) >= 1
        assert "name" in result["sheets"][0]

    def test_load_bytes_input(self):
        data = _make_gnumeric()
        assert isinstance(data, bytes)
        result = load(data)
        assert result is not None
