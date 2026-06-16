"""Sprint 56 — ODT / TOML / XCF / QOI product deepening (R286).

Tests 8 new analytics functions:
  ODT:  odt_avg_words_per_sentence, odt_shortest_paragraph_length
  TOML: toml_max_value_length, toml_nested_table_count
  XCF:  xcf_layer_to_pixel_ratio, xcf_is_tall
  QOI:  qoi_megapixels, qoi_channel_balance
"""
from __future__ import annotations

import sys, tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.odt import (
    odt_avg_words_per_sentence,
    odt_shortest_paragraph_length,
)
from src.python.toml import (
    toml_max_value_length,
    toml_nested_table_count,
)
from src.python.xcf import (
    xcf_layer_to_pixel_ratio,
    xcf_is_tall,
)
from src.python.qoi import (
    qoi_megapixels,
    qoi_channel_balance,
)

_ODT = _REPO / "samples" / "by-format" / "odt" / "valid" / "two-paragraphs.odt"
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf"
_QOI = _REPO / "samples" / "by-format" / "qoi" / "valid" / "2x2-black.qoi"


def _toml_file(content: str) -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False)
    f.write(content)
    f.close()
    return f.name


# ── ODT ──────────────────────────────────────────────────────────────

class TestOdtAvgWordsPerSentence:
    def test_returns_float(self):
        result = odt_avg_words_per_sentence(_ODT)
        assert isinstance(result, (int, float))

    def test_nonnegative(self):
        assert odt_avg_words_per_sentence(_ODT) >= 0.0


class TestOdtShortestParagraphLength:
    def test_returns_int(self):
        result = odt_shortest_paragraph_length(_ODT)
        assert isinstance(result, int)

    def test_nonnegative(self):
        assert odt_shortest_paragraph_length(_ODT) >= 0


# ── TOML ─────────────────────────────────────────────────────────────

class TestTomlMaxValueLength:
    def test_returns_int(self):
        path = _toml_file('name = "hello"\ncount = 42\n')
        result = toml_max_value_length(path)
        assert isinstance(result, int)
        assert result >= 1

    def test_empty_returns_zero(self):
        path = _toml_file("")
        assert toml_max_value_length(path) == 0


class TestTomlNestedTableCount:
    def test_returns_int(self):
        path = _toml_file('[section]\nkey = "val"\n')
        result = toml_nested_table_count(path)
        assert isinstance(result, int)

    def test_counts_tables(self):
        path = _toml_file('[a]\nx = 1\n[b]\ny = 2\ntop = "val"\n')
        result = toml_nested_table_count(path)
        assert result >= 2


# ── XCF ──────────────────────────────────────────────────────────────

class TestXcfLayerToPixelRatio:
    def test_returns_float(self):
        result = xcf_layer_to_pixel_ratio(_XCF)
        assert isinstance(result, (int, float))

    def test_nonnegative(self):
        assert xcf_layer_to_pixel_ratio(_XCF) >= 0.0

    def test_1x1_has_ratio_1(self):
        # 1x1-red-rgb: 1 layer / 1 pixel = 1.0
        assert xcf_layer_to_pixel_ratio(_XCF) == 1.0


class TestXcfIsTall:
    def test_returns_bool(self):
        result = xcf_is_tall(_XCF)
        assert isinstance(result, bool)

    def test_square_not_tall(self):
        assert xcf_is_tall(_XCF) is False


# ── QOI ──────────────────────────────────────────────────────────────

class TestQoiMegapixels:
    def test_returns_float(self):
        result = qoi_megapixels(_QOI)
        assert isinstance(result, (int, float))

    def test_small_image(self):
        # 2x2 = 4 pixels = 0.000004 MP
        assert qoi_megapixels(_QOI) < 1.0


class TestQoiChannelBalance:
    def test_returns_float(self):
        result = qoi_channel_balance(_QOI)
        assert isinstance(result, (int, float))

    def test_range_zero_to_one(self):
        result = qoi_channel_balance(_QOI)
        assert 0.0 <= result <= 1.0

    def test_black_is_balanced(self):
        # All-black image: R=G=B=0, spread=0 → balance=1.0
        assert qoi_channel_balance(_QOI) == 1.0
