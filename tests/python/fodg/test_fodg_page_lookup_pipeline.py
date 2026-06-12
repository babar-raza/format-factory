"""
test_fodg_page_lookup_pipeline.py -- FODG page lookup pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-64
Tests get_page_by_name returns dict, get_page_by_name None on missing,
get_page_index int, has_page true, has_page false.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    create_fodg,
    get_page_by_name,
    get_page_index,
    has_page,
)

_PAGES = [{"name": "Intro"}, {"name": "Body"}, {"name": "Conclusion"}]
_MODEL = create_fodg(_PAGES)


def test_get_page_by_name_returns_dict():
    result = get_page_by_name(_MODEL, "Intro")
    assert isinstance(result, dict)


def test_get_page_by_name_none_on_missing():
    result = get_page_by_name(_MODEL, "NonExistent")
    assert result is None


def test_get_page_index_int():
    idx = get_page_index(_MODEL, "Body")
    assert isinstance(idx, int)
    assert idx == 1


def test_has_page_true():
    result = has_page(_MODEL, "Conclusion")
    assert result is True


def test_has_page_false():
    result = has_page(_MODEL, "Missing")
    assert result is False
