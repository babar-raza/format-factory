"""
tests/python/abw/test_r122_abw_edit_and_json.py

Sprint: FORMAT-FACTORY-STANDING-MULTI-LANE-PRODUCT-FIRST-MEGA-TRAIN-001
TC-ABW-EDIT: edit_paragraph()
TC-ABW-JSON-WIRE: export_to_json() via __init__
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import create_abw, edit_paragraph, export_to_json


class TestEditParagraph:
    """Tests for edit_paragraph()."""

    def test_returns_new_model(self):
        model = create_abw(["Hello", "World"])
        result = edit_paragraph(model, 0, "Hi")
        assert result is not model

    def test_original_unchanged(self):
        model = create_abw(["Hello", "World"])
        edit_paragraph(model, 0, "Hi")
        assert model["paragraphs"][0] == "Hello"

    def test_first_paragraph_replaced(self):
        model = create_abw(["Hello", "World"])
        result = edit_paragraph(model, 0, "Hi")
        assert result["paragraphs"][0] == "Hi"

    def test_second_paragraph_replaced(self):
        model = create_abw(["Hello", "World"])
        result = edit_paragraph(model, 1, "Earth")
        assert result["paragraphs"][1] == "Earth"

    def test_other_paragraphs_unchanged(self):
        model = create_abw(["A", "B", "C"])
        result = edit_paragraph(model, 1, "X")
        assert result["paragraphs"][0] == "A"
        assert result["paragraphs"][2] == "C"

    def test_paragraph_count_unchanged(self):
        model = create_abw(["A", "B", "C"])
        result = edit_paragraph(model, 0, "Z")
        assert result["paragraph_count"] == 3

    def test_empty_replacement_allowed(self):
        model = create_abw(["Hello"])
        result = edit_paragraph(model, 0, "")
        assert result["paragraphs"][0] == ""

    def test_out_of_range_raises_index_error(self):
        model = create_abw(["Hello"])
        try:
            edit_paragraph(model, 5, "X")
            assert 1 == 0, "Expected IndexError"

        except IndexError:
            pass

    def test_negative_out_of_range_raises(self):
        model = create_abw(["Hello"])
        try:
            edit_paragraph(model, -1, "X")
            assert 1 == 0, "Expected IndexError"

        except IndexError:
            pass

    def test_non_string_new_text_raises_type_error(self):
        model = create_abw(["Hello"])
        try:
            edit_paragraph(model, 0, 42)
            assert 1 == 0, "Expected TypeError"

        except TypeError:
            pass

    def test_non_dict_model_raises_type_error(self):
        try:
            edit_paragraph("not a dict", 0, "X")
            assert 1 == 0, "Expected TypeError"

        except TypeError:
            pass

    def test_chained_edits(self):
        model = create_abw(["A", "B", "C"])
        model2 = edit_paragraph(model, 0, "Alpha")
        model3 = edit_paragraph(model2, 2, "Gamma")
        assert model3["paragraphs"] == ["Alpha", "B", "Gamma"]

    def test_model_is_abw_preserved(self):
        model = create_abw(["Hello"])
        result = edit_paragraph(model, 0, "Hi")
        assert result.get("is_abw") is True

    def test_write_after_edit(self):
        """edit_paragraph result can be written to a file."""
        import tempfile
        from abw.abw_codec import write_abw, load
        model = create_abw(["Original", "Keep"])
        edited = edit_paragraph(model, 0, "Replaced")
        with tempfile.NamedTemporaryFile(suffix=".abw", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_abw(edited, tmp)
            loaded = load(tmp)
            assert loaded["paragraphs"][0] == "Replaced"
            assert loaded["paragraphs"][1] == "Keep"
        finally:
            tmp.unlink()


class TestExportToJsonWired:
    """Tests that export_to_json is accessible from abw package __init__."""

    def test_import_from_package(self):
        import abw
        assert hasattr(abw, "export_to_json")

    def test_export_to_json_in_all(self):
        import abw
        assert "export_to_json" in abw.__all__

    def test_returns_valid_json(self):
        import tempfile
        from abw.abw_codec import write_abw
        model = create_abw(["Hello", "World"])
        tmp = Path(tempfile.mktemp(suffix=".abw"))
        try:
            write_abw(model, tmp)
            result = export_to_json(tmp)
            parsed = json.loads(result)
            assert isinstance(parsed, dict)
        finally:
            tmp.unlink(missing_ok=True)

    def test_paragraphs_in_output(self):
        import tempfile
        from abw.abw_codec import write_abw
        model = create_abw(["Hello", "World"])
        tmp = Path(tempfile.mktemp(suffix=".abw"))
        try:
            write_abw(model, tmp)
            parsed = json.loads(export_to_json(tmp))
            assert "paragraphs" in parsed
        finally:
            tmp.unlink(missing_ok=True)

    def test_paragraph_values_preserved(self):
        import tempfile
        from abw.abw_codec import write_abw
        model = create_abw(["Alpha", "Beta"])
        tmp = Path(tempfile.mktemp(suffix=".abw"))
        try:
            write_abw(model, tmp)
            parsed = json.loads(export_to_json(tmp))
            assert "Alpha" in parsed["paragraphs"]
            assert "Beta" in parsed["paragraphs"]
        finally:
            tmp.unlink(missing_ok=True)
