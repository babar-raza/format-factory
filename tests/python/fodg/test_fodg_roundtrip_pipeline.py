"""
test_fodg_roundtrip_pipeline.py -- FODG roundtrip pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-70
Tests roundtrip returns dict, roundtrip page_count preserved, write_fodg creates file,
roundtrip is_fodg, roundtrip page names.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    create_fodg,
    write_fodg,
    roundtrip,
    get_page_count,
    page_names,
)

_PAGES = [{"name": "Slide1"}, {"name": "Slide2"}, {"name": "Slide3"}]


def _write(tmp_path):
    model = create_fodg(_PAGES)
    dest = tmp_path / "src.fodg"
    write_fodg(model, str(dest))
    return dest


def test_roundtrip_returns_dict(tmp_path):
    src = _write(tmp_path)
    result = roundtrip(str(src), str(tmp_path / "rt.fodg"))
    assert isinstance(result, dict)


def test_roundtrip_page_count_preserved(tmp_path):
    src = _write(tmp_path)
    result = roundtrip(str(src), str(tmp_path / "rt.fodg"))
    assert get_page_count(result) == 3


def test_write_fodg_creates_file(tmp_path):
    model = create_fodg(_PAGES)
    dest = tmp_path / "doc.fodg"
    write_fodg(model, str(dest))
    assert dest.exists()


def test_roundtrip_is_fodg(tmp_path):
    src = _write(tmp_path)
    result = roundtrip(str(src), str(tmp_path / "rt.fodg"))
    assert result.get("is_fodg") is True


def test_roundtrip_page_names(tmp_path):
    src = _write(tmp_path)
    result = roundtrip(str(src), str(tmp_path / "rt.fodg"))
    names = page_names(result)
    assert "Slide1" in names
