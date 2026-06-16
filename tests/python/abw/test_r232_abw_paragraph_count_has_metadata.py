"""Tests for abw_paragraph_count and abw_has_metadata.

Product deepening: ABW analytics — TC-H3-002-ABW / PDC-ABW-PARA-META-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import create_abw, write_abw, abw_paragraph_count, abw_has_metadata


def _make_abw(tmp_path, name, paragraphs, metadata=None):
    model = create_abw(paragraphs=paragraphs)
    if metadata:
        model["metadata"] = metadata
    p = tmp_path / f"{name}.abw"
    write_abw(model, str(p))
    return p


class TestAbwParagraphCount:
    def test_single_paragraph(self, tmp_path):
        p = _make_abw(tmp_path, "one", ["hello world"])
        result = abw_paragraph_count(p)
        assert isinstance(result, int)
        assert result >= 1

    def test_multiple_paragraphs(self, tmp_path):
        p = _make_abw(tmp_path, "multi", ["first", "second", "third"])
        result = abw_paragraph_count(p)
        assert result >= 3

    def test_empty(self, tmp_path):
        p = _make_abw(tmp_path, "empty", [])
        result = abw_paragraph_count(p)
        assert result == 0

    def test_returns_int(self, tmp_path):
        p = _make_abw(tmp_path, "type", ["test"])
        assert isinstance(abw_paragraph_count(p), int)

    def test_non_negative(self, tmp_path):
        p = _make_abw(tmp_path, "nn", ["x"])
        assert abw_paragraph_count(p) >= 0


class TestAbwHasMetadata:
    def test_no_metadata(self, tmp_path):
        p = _make_abw(tmp_path, "no_meta", ["hello"])
        result = abw_has_metadata(p)
        assert isinstance(result, bool)

    def test_returns_bool(self, tmp_path):
        p = _make_abw(tmp_path, "bool_type", ["test"])
        assert isinstance(abw_has_metadata(p), bool)

    def test_with_metadata_dict(self, tmp_path):
        p = _make_abw(tmp_path, "with_meta", ["hello"], metadata={"title": "Test"})
        result = abw_has_metadata(p)
        assert isinstance(result, bool)

    def test_empty_paragraphs(self, tmp_path):
        p = _make_abw(tmp_path, "empty_p", [])
        result = abw_has_metadata(p)
        assert isinstance(result, bool)

    def test_consistent_type(self, tmp_path):
        p = _make_abw(tmp_path, "consist", ["a", "b"])
        r1 = abw_has_metadata(p)
        r2 = abw_has_metadata(p)
        assert r1 == r2
