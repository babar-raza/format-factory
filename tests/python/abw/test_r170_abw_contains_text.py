"""Tests for ABW contains_text function (rnext34)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import contains_text


class TestContainsText:
    def _model(self, paragraphs):
        return {"paragraphs": paragraphs}

    def test_found_exact(self):
        assert contains_text(self._model(["Hello world"]), "Hello world") is True

    def test_found_substring(self):
        assert contains_text(self._model(["Hello world"]), "world") is True

    def test_not_found(self):
        assert contains_text(self._model(["Hello world"]), "xyz") is False

    def test_empty_paragraphs(self):
        assert contains_text(self._model([]), "text") is False

    def test_empty_search(self):
        # Empty string is always a substring of any string
        assert contains_text(self._model(["any text"]), "") is True

    def test_case_sensitive_no_match(self):
        assert contains_text(self._model(["Hello"]), "hello", case_sensitive=True) is False

    def test_case_insensitive_match(self):
        assert contains_text(self._model(["Hello World"]), "hello world", case_sensitive=False) is True

    def test_multiple_paragraphs_found_second(self):
        assert contains_text(self._model(["First", "Second paragraph"]), "Second") is True

    def test_non_dict_returns_false(self):
        assert contains_text("not a dict", "text") is False
