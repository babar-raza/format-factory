"""
test_r157_fodg_load_capability.py — Capability coverage test for FODG load function.

Closes GAP-FODG-FOSS-LOAD-001 (missing_test_coverage).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))
from fodg.fodg_codec import load, create_fodg, write_fodg


def _make_fodg() -> bytes:
    """Create a minimal FODG document as bytes."""
    doc = create_fodg([{"name": "Page1"}])
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".fodg", delete=False) as f:
        path = Path(f.name)
    write_fodg(doc, str(path))
    data = path.read_bytes()
    path.unlink()
    return data


class TestFodgLoadCapability:
    def test_load_returns_dict(self):
        data = _make_fodg()
        result = load(data)
        assert isinstance(result, dict)

    def test_load_has_page_count(self):
        data = _make_fodg()
        result = load(data)
        assert "page_count" in result

    def test_load_from_path(self, tmp_path):
        doc = create_fodg([{"name": "Page1"}])
        p = tmp_path / "test.fodg"
        write_fodg(doc, str(p))
        result = load(str(p))
        assert isinstance(result, dict)

    def test_load_has_pages(self):
        data = _make_fodg()
        result = load(data)
        assert "pages" in result

    def test_load_page_structure(self):
        data = _make_fodg()
        result = load(data)
        if result["page_count"] > 0:
            page = result["pages"][0]
            assert "name" in page

    def test_load_bytes_input(self):
        data = _make_fodg()
        result = load(data)
        assert result is not None
        assert isinstance(result, dict)
