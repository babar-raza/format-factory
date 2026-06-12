"""R167 — FODG Load capability coverage test (GAP-FODG-FOSS-LOAD-001).

Closes: GAP-FODG-FOSS-LOAD-001 (missing_test_coverage for Load capability).
Queue:  gap-coverage-q-002
"""
from __future__ import annotations

import pytest
from pathlib import Path

from src.python.fodg.fodg_codec import load, FodgParseError

EMPTY_PAGE = Path("samples/by-format/fodg/empty-page.fodg")
MINIMAL = Path("samples/by-format/fodg/minimal-drawing.fodg")


class TestFodgLoadFromPath:
    def test_load_returns_dict(self):
        model = load(EMPTY_PAGE)
        assert isinstance(model, dict)

    def test_load_is_fodg_true(self):
        model = load(EMPTY_PAGE)
        assert model["is_fodg"] is True

    def test_load_has_page_count(self):
        model = load(EMPTY_PAGE)
        assert "page_count" in model
        assert isinstance(model["page_count"], int)

    def test_load_has_pages_list(self):
        model = load(EMPTY_PAGE)
        assert "pages" in model
        assert isinstance(model["pages"], list)

    def test_load_has_shapes_total(self):
        model = load(EMPTY_PAGE)
        assert "shapes_total" in model
        assert isinstance(model["shapes_total"], int)

    def test_load_minimal_drawing(self):
        model = load(MINIMAL)
        assert model["is_fodg"] is True

    def test_load_from_bytes(self):
        raw = EMPTY_PAGE.read_bytes()
        model = load(raw)
        assert model["is_fodg"] is True

    def test_load_from_str_path(self):
        model = load(str(EMPTY_PAGE))
        assert model["is_fodg"] is True

    def test_load_invalid_raises(self):
        with pytest.raises((FodgParseError, Exception)):
            load(b"not valid xml fodg !!!")
