"""
test_rnext_abw_truncate_paragraphs.py -- Dedicated test coverage for truncate_paragraphs.

Gap: GAP-ABW-FOSS-TRUNCATE_PAR-001 (missing_test_coverage)
"""
from __future__ import annotations

import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import create_abw, truncate_paragraphs


def _model(*paragraphs: str) -> dict:
    return create_abw(list(paragraphs))


class TestTruncateParagraphsBasic:
    def test_truncate_to_one(self):
        m = _model("A", "B", "C")
        m2 = truncate_paragraphs(m, 1)
        assert m2["paragraphs"] == ["A"]
        assert m2["paragraph_count"] == 1

    def test_truncate_to_zero(self):
        m = _model("A", "B")
        m2 = truncate_paragraphs(m, 0)
        assert m2["paragraphs"] == []
        assert m2["paragraph_count"] == 0

    def test_truncate_beyond_length(self):
        m = _model("A", "B")
        m2 = truncate_paragraphs(m, 10)
        assert m2["paragraphs"] == ["A", "B"]
        assert m2["paragraph_count"] == 2

    def test_truncate_exact_length(self):
        m = _model("X", "Y", "Z")
        m2 = truncate_paragraphs(m, 3)
        assert len(m2["paragraphs"]) == 3

    def test_empty_model(self):
        m = _model()
        m2 = truncate_paragraphs(m, 5)
        assert m2["paragraphs"] == []

    def test_immutability(self):
        m = _model("A", "B", "C")
        m2 = truncate_paragraphs(m, 1)
        assert len(m["paragraphs"]) == 3
        assert len(m2["paragraphs"]) == 1


class TestTruncateParagraphsErrors:
    def test_model_not_dict_raises(self):
        with pytest.raises(TypeError):
            truncate_paragraphs("not a dict", 1)

    def test_negative_n_raises(self):
        m = _model("A")
        with pytest.raises(ValueError):
            truncate_paragraphs(m, -1)
