"""Tests for abw_average_word_length function."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import abw_average_word_length, load, create_abw, write_abw

_SAMPLES = _REPO / "samples" / "by-format" / "abw"


def _make_abw(tmp_path, paragraphs, name="test.abw"):
    model = create_abw(paragraphs)
    p = tmp_path / name
    write_abw(model, str(p))
    return str(p)


class TestAbwAverageWordLength:
    def test_single_word(self, tmp_path):
        path = _make_abw(tmp_path, ["hello"])
        assert abw_average_word_length(path) == pytest.approx(5.0)

    def test_multiple_words(self, tmp_path):
        path = _make_abw(tmp_path, ["hi there"])
        # "hi" = 2, "there" = 5 => avg = 3.5
        assert abw_average_word_length(path) == pytest.approx(3.5)

    def test_empty_document(self, tmp_path):
        path = _make_abw(tmp_path, [])
        assert abw_average_word_length(path) == pytest.approx(0.0)

    def test_empty_paragraphs(self, tmp_path):
        path = _make_abw(tmp_path, ["", "  ", ""])
        assert abw_average_word_length(path) == pytest.approx(0.0)

    def test_multiple_paragraphs(self, tmp_path):
        path = _make_abw(tmp_path, ["a bb", "ccc"])
        # "a"=1, "bb"=2, "ccc"=3 => 6/3 = 2.0
        assert abw_average_word_length(path) == pytest.approx(2.0)

    def test_real_sample(self):
        path = str(_SAMPLES / "two-paragraphs.abw")
        result = abw_average_word_length(path)
        assert isinstance(result, float)
        assert result > 0

    def test_return_type(self, tmp_path):
        path = _make_abw(tmp_path, ["test"])
        assert isinstance(abw_average_word_length(path), float)

    def test_importable_from_package(self):
        from abw import abw_average_word_length as fn
        assert callable(fn)
