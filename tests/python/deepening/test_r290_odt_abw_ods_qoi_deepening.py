"""Sprint 60 — ODT / ABW / ODS / QOI product deepening (R290).

Tests 8 new analytics functions:
  ODT: odt_paragraph_variance, odt_is_single_paragraph
  ABW: abw_words_per_sentence, abw_paragraph_length_variance
  ODS: ods_column_value_variance, ods_has_formulas
  QOI: qoi_is_tall, qoi_channel_entropy
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.odt import odt_paragraph_variance, odt_is_single_paragraph
from src.python.abw import abw_words_per_sentence, abw_paragraph_length_variance
from src.python.ods import ods_column_value_variance, ods_has_formulas
from src.python.qoi import qoi_is_tall, qoi_channel_entropy

_ODT = _REPO / "samples" / "by-format" / "odt" / "valid" / "minimal-document.odt"
_ABW = _REPO / "samples" / "by-format" / "abw" / "minimal-document.abw"
_ODS = _REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods"
_QOI = _REPO / "samples" / "by-format" / "qoi" / "valid" / "4x1-gradient.qoi"


class TestOdtParagraphVariance:
    def test_returns_float(self):
        assert isinstance(odt_paragraph_variance(_ODT), (int, float))

    def test_nonnegative(self):
        assert odt_paragraph_variance(_ODT) >= 0.0


class TestOdtIsSingleParagraph:
    def test_returns_bool(self):
        assert isinstance(odt_is_single_paragraph(_ODT), bool)


class TestAbwWordsPerSentence:
    def test_returns_float(self):
        assert isinstance(abw_words_per_sentence(_ABW), (int, float))

    def test_nonnegative(self):
        assert abw_words_per_sentence(_ABW) >= 0.0


class TestAbwParagraphLengthVariance:
    def test_returns_float(self):
        assert isinstance(abw_paragraph_length_variance(_ABW), (int, float))

    def test_nonnegative(self):
        assert abw_paragraph_length_variance(_ABW) >= 0.0


class TestOdsColumnValueVariance:
    def test_returns_float(self):
        assert isinstance(ods_column_value_variance(_ODS), (int, float))

    def test_nonnegative(self):
        assert ods_column_value_variance(_ODS) >= 0.0


class TestOdsHasFormulas:
    def test_returns_bool(self):
        assert isinstance(ods_has_formulas(_ODS), bool)


class TestQoiIsTall:
    def test_returns_bool(self):
        assert isinstance(qoi_is_tall(_QOI), bool)

    def test_gradient_not_tall(self):
        assert qoi_is_tall(_QOI) is False


class TestQoiChannelEntropy:
    def test_returns_float(self):
        assert isinstance(qoi_channel_entropy(_QOI), (int, float))

    def test_bounded(self):
        val = qoi_channel_entropy(_QOI)
        assert 0.0 <= val <= 1.0
