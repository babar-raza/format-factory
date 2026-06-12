"""
tests/python/abw/test_r126_abw_get_paragraph.py

Sprint: FORMAT-FACTORY-AUTONOMOUS-EXECUTION-SPINE-BROAD-PRODUCT-MEGA-TRAIN-001
TC-ABW-GET-PARAGRAPH: get_paragraph() — read-access to paragraph model
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import create_abw, write_abw, load, get_paragraph


def _make_model(paragraphs):
    return {"paragraphs": paragraphs, "metadata": {}}


class TestGetParagraph:
    def test_returns_string(self):
        model = _make_model(["Hello", "World"])
        result = get_paragraph(model, 0)
        assert isinstance(result, str)

    def test_first_paragraph(self):
        model = _make_model(["First", "Second", "Third"])
        assert get_paragraph(model, 0) == "First"

    def test_last_paragraph(self):
        model = _make_model(["A", "B", "C"])
        assert get_paragraph(model, 2) == "C"

    def test_middle_paragraph(self):
        model = _make_model(["X", "Y", "Z"])
        assert get_paragraph(model, 1) == "Y"

    def test_out_of_range_raises_index_error(self):
        model = _make_model(["only"])
        try:
            get_paragraph(model, 5)
            assert False, "Expected IndexError"
        except IndexError:
            pass

    def test_negative_out_of_range_raises(self):
        model = _make_model(["only"])
        try:
            get_paragraph(model, -5)
            assert False, "Expected IndexError"
        except IndexError:
            pass

    def test_non_dict_model_raises_type_error(self):
        try:
            get_paragraph("not a model", 0)
            assert False, "Expected TypeError"
        except TypeError:
            pass

    def test_empty_paragraphs_raises_index_error(self):
        model = _make_model([])
        try:
            get_paragraph(model, 0)
            assert False, "Expected IndexError"
        except IndexError:
            pass

    def test_from_written_file(self, tmp_path):
        f = tmp_path / "test.abw"
        model = create_abw(["paragraph one", "paragraph two"])
        write_abw(model, f)
        loaded = load(f)
        result = get_paragraph(loaded, 0)
        assert isinstance(result, str)

    def test_package_import(self):
        import abw
        assert hasattr(abw, "get_paragraph")

    def test_in_all(self):
        import abw
        assert "get_paragraph" in abw.__all__
