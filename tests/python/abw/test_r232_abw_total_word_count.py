"""Tests for abw_total_word_count (Sprint 22)."""
import pytest
from src.python.abw import abw_total_word_count


@pytest.fixture
def abw_file(tmp_path):
    def _make(paragraphs):
        p = tmp_path / "test.abw"
        paras = "".join(f"<p>{t}</p>" for t in paragraphs)
        content = f"""<?xml version="1.0" encoding="UTF-8"?>
<abiword xmlns:awml="http://www.abisource.com/awml.dtd" version="0.99">
{paras}
</abiword>"""
        p.write_text(content, encoding="utf-8")
        return str(p)
    return _make


class TestAbwTotalWordCount:
    def test_simple(self, abw_file):
        path = abw_file(["hello world"])
        assert abw_total_word_count(path) == 2

    def test_multiple_paragraphs(self, abw_file):
        path = abw_file(["one two", "three"])
        assert abw_total_word_count(path) == 3

    def test_empty(self, abw_file):
        path = abw_file([])
        assert abw_total_word_count(path) == 0

    def test_return_type(self, abw_file):
        path = abw_file(["test"])
        assert isinstance(abw_total_word_count(path), int)

    def test_non_negative(self, abw_file):
        path = abw_file(["x"])
        assert abw_total_word_count(path) >= 0
