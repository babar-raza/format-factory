"""Tests for FodgDocument mutation API: add_page() and save_to_file().

Sprint: FODG-PYTHON-MUTATION-001
"""
import tempfile
from pathlib import Path

import pytest

from fodg.fodg_codec import create_fodg
from fodg.models import FodgDocument


def _make_doc() -> FodgDocument:
    """Create a single-page FodgDocument with 2 text shapes."""
    model = create_fodg([{"name": "Page1", "texts": ["Hello", "World"]}])
    return FodgDocument(model)


class TestAddPage:
    def test_add_page_increments_page_count(self):
        doc = _make_doc()
        assert doc.page_count == 1
        doc.add_page(name="Page2")
        assert doc.page_count == 2

    def test_add_page_with_texts_updates_shapes_total(self):
        doc = _make_doc()
        before = doc.shapes_total
        doc.add_page(name="Extra", texts=["A", "B", "C"])
        assert doc.shapes_total == before + 3

    def test_add_page_auto_name(self):
        doc = _make_doc()
        doc.add_page()
        assert doc.page_count == 2

    def test_add_page_non_str_name_raises(self):
        from fodg.fodg_codec import FodgError
        doc = _make_doc()
        with pytest.raises(FodgError):
            doc.add_page(name=42)  # type: ignore[arg-type]

    def test_add_multiple_pages(self):
        doc = _make_doc()
        doc.add_page(name="P2")
        doc.add_page(name="P3")
        assert doc.page_count == 3

    def test_existing_page_intact_after_add(self):
        doc = _make_doc()
        doc.add_page(name="NewPage")
        assert doc.pages[0]["name"] == "Page1"


class TestSaveToFile:
    def test_save_creates_file(self):
        doc = _make_doc()
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.fodg"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_empty_path_raises(self):
        from fodg.fodg_codec import FodgError
        doc = _make_doc()
        with pytest.raises(FodgError):
            doc.save_to_file("")

    def test_save_creates_parent_dirs(self):
        doc = _make_doc()
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "sub" / "dir" / "out.fodg"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_file_is_nonzero(self):
        doc = _make_doc()
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.fodg"
            doc.save_to_file(dest)
            assert dest.stat().st_size > 0


class TestMutationRoundtrip:
    def test_add_page_roundtrip(self):
        """add_page → save_to_file → from_file: new page count preserved."""
        doc = _make_doc()
        doc.add_page(name="NewPage", texts=["Added"])
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt.fodg"
            doc.save_to_file(dest)
            reloaded = FodgDocument.from_file(dest)
            assert reloaded.page_count == 2

    def test_add_page_roundtrip_shapes_preserved(self):
        doc = _make_doc()
        doc.add_page(name="P2", texts=["X", "Y"])
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt2.fodg"
            doc.save_to_file(dest)
            reloaded = FodgDocument.from_file(dest)
            assert reloaded.shapes_total >= 2  # original 2 + new 2

    def test_save_and_reload_is_fodg(self):
        doc = _make_doc()
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt3.fodg"
            doc.save_to_file(dest)
            reloaded = FodgDocument.from_file(dest)
            assert reloaded.is_fodg
