"""
tests/python/abw/test_r166_abw_is_empty.py

Tests for ABW is_empty function.

Sprint: FORMAT-FACTORY-BROAD-SELF-HEALING-PRODUCT-ACCELERATION-RNEXT-001
Queue: broad-accel-q-004
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw.abw_codec import is_empty


class TestIsEmpty:
    def test_empty_paragraphs_list(self) -> None:
        assert is_empty({"paragraphs": []}) is True

    def test_no_paragraphs_key(self) -> None:
        assert is_empty({}) is True

    def test_non_dict_returns_true(self) -> None:
        assert is_empty(None) is True  # type: ignore[arg-type]
        assert is_empty("hello") is True  # type: ignore[arg-type]

    def test_single_content_paragraph(self) -> None:
        assert is_empty({"paragraphs": ["Hello world"]}) is False

    def test_all_whitespace_paragraphs(self) -> None:
        assert is_empty({"paragraphs": ["  ", "\t", ""]}) is True

    def test_mixed_empty_and_content(self) -> None:
        assert is_empty({"paragraphs": ["", "not empty"]}) is False

    def test_single_whitespace_paragraph(self) -> None:
        assert is_empty({"paragraphs": [" "]}) is True

    def test_single_nonempty_word(self) -> None:
        assert is_empty({"paragraphs": ["x"]}) is False

    def test_multiple_content_paragraphs(self) -> None:
        model = {"paragraphs": ["para one", "para two", "para three"]}
        assert is_empty(model) is False
