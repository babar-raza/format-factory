"""Tests for abw_nonempty_paragraph_count and abw_char_count (Sprint 27)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import create_abw, write_abw, abw_nonempty_paragraph_count, abw_char_count


def _make_abw(tmp_path, name, paragraphs):
    model = create_abw(paragraphs=paragraphs)
    p = tmp_path / f"{name}.abw"
    write_abw(model, str(p))
    return str(p)


class TestAbwNonemptyParagraphCount:
    def test_return_type(self, tmp_path):
        p = _make_abw(tmp_path, "rt", ["hello"])
        assert isinstance(abw_nonempty_paragraph_count(p), int)

    def test_all_nonempty(self, tmp_path):
        # "hello" and "world" are both non-empty => 2
        p = _make_abw(tmp_path, "all", ["hello", "world"])
        assert abw_nonempty_paragraph_count(p) == 2

    def test_empty_excluded(self, tmp_path):
        # "" is empty, "hello" and "world" are not => 2
        p = _make_abw(tmp_path, "ex", ["hello", "", "world"])
        assert abw_nonempty_paragraph_count(p) == 2

    def test_all_empty(self, tmp_path):
        p = _make_abw(tmp_path, "ae", ["", "", ""])
        assert abw_nonempty_paragraph_count(p) == 0

    def test_no_paragraphs(self, tmp_path):
        p = _make_abw(tmp_path, "np", [])
        assert abw_nonempty_paragraph_count(p) == 0


class TestAbwCharCount:
    def test_return_type(self, tmp_path):
        p = _make_abw(tmp_path, "rt2", ["hello"])
        assert isinstance(abw_char_count(p), int)

    def test_exact_single(self, tmp_path):
        # "hello" = 5 chars
        p = _make_abw(tmp_path, "es", ["hello"])
        assert abw_char_count(p) == 5

    def test_exact_two_paragraphs(self, tmp_path):
        # "hello" + "world" = 5 + 5 = 10 chars
        p = _make_abw(tmp_path, "tp", ["hello", "world"])
        assert abw_char_count(p) == 10

    def test_empty_paragraphs_zero(self, tmp_path):
        p = _make_abw(tmp_path, "ez", [])
        assert abw_char_count(p) == 0

    def test_nonnegative(self, tmp_path):
        p = _make_abw(tmp_path, "nn", ["test"])
        assert abw_char_count(p) >= 0
