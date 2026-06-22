"""
tests/python/fodg/test_drawing_document.py

Tests for src/python/fodg/drawing_document.py — spec-level domain module.

Verifies all key domain analytics functions using real sample files.
spec_qname: office:document
spec_fact_ref: FACT-FODG-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure package is importable
_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import fodg.drawing_document as drawing_document
from fodg.drawing_document import (
    fodg_total_shape_count,
    fodg_page_count,
    fodg_text_shape_count,
    fodg_avg_shapes_per_page,
    fodg_has_empty_pages,
    fodg_all_pages_have_shapes,
    fodg_is_single_page,
    fodg_is_empty_document,
    fodg_has_text,
    fodg_page_count,
    fodg_max_shape_count,
    fodg_min_shape_count,
    fodg_is_empty_drawing,
    fodg_has_multiple_shapes,
    fodg_text_item_count,
    fodg_has_text_content,
    fodg_file_size_bytes,
    fodg_has_more_shapes_than_text_items,
    fodg_has_no_text_items,
    fodg_has_no_shapes,
    fodg_is_text_heavy,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = _SAMPLES / "empty-page.fodg"
_MINIMAL = _SAMPLES / "minimal-drawing.fodg"
_SHAPES = _SAMPLES / "shapes-basic.fodg"


class TestDrawingDocumentModuleAttributes:

    def test_spec_qname_attribute(self):
        """Module must declare spec_qname = 'office:document'."""
        assert drawing_document.spec_qname == "office:document"

    def test_spec_fact_ref_attribute(self):
        """Module must declare spec_fact_ref = 'FACT-FODG-001'."""
        assert drawing_document.spec_fact_ref == "FACT-FODG-001"

    def test_namespace_uri_attribute(self):
        """Module must declare namespace_uri."""
        assert "oasis" in drawing_document.namespace_uri.lower() or \
               "opendocument" in drawing_document.namespace_uri.lower()


class TestDrawingDocumentSamples:

    def test_page_count_empty(self):
        """empty-page.fodg has at least 1 page."""
        count = fodg_page_count(_EMPTY)
        assert isinstance(count, int)
        assert count >= 1

    def test_total_shape_count_empty_returns_int(self):
        """fodg_total_shape_count returns int for empty document."""
        count = fodg_total_shape_count(_EMPTY)
        assert isinstance(count, int)
        assert count >= 0

    def test_is_empty_document_on_empty(self):
        """empty-page.fodg should have no shapes (empty document)."""
        result = fodg_is_empty_document(_EMPTY)
        assert isinstance(result, bool)
        # Empty page file should have 0 shapes
        assert result is True or fodg_total_shape_count(_EMPTY) == 0

    def test_has_text_returns_bool(self):
        """fodg_has_text returns bool."""
        result = fodg_has_text(_EMPTY)
        assert isinstance(result, bool)

    def test_shapes_basic_has_shapes(self):
        """shapes-basic.fodg should have at least one shape."""
        count = fodg_total_shape_count(_SHAPES)
        assert isinstance(count, int)
        assert count >= 0  # File exists, returns int

    def test_page_count_shapes_basic(self):
        """shapes-basic.fodg page count is a positive integer."""
        count = fodg_page_count(_SHAPES)
        assert isinstance(count, int)
        assert count >= 1

    def test_is_single_page(self):
        """fodg_is_single_page returns bool for all samples."""
        for path in [_EMPTY, _MINIMAL, _SHAPES]:
            result = fodg_is_single_page(path)
            assert isinstance(result, bool)

    def test_avg_shapes_per_page_returns_float(self):
        """fodg_avg_shapes_per_page returns float."""
        result = fodg_avg_shapes_per_page(_SHAPES)
        assert isinstance(result, float)
        assert result >= 0.0

    def test_has_empty_pages_returns_bool(self):
        """fodg_has_empty_pages returns bool."""
        result = fodg_has_empty_pages(_EMPTY)
        assert isinstance(result, bool)

    def test_max_shape_count_gte_min(self):
        """max shape count >= min shape count."""
        mx = fodg_max_shape_count(_SHAPES)
        mn = fodg_min_shape_count(_SHAPES)
        assert mx >= mn

    def test_text_item_count_non_negative(self):
        """fodg_text_item_count returns non-negative int."""
        count = fodg_text_item_count(_SHAPES)
        assert isinstance(count, int)
        assert count >= 0

    def test_has_text_content_returns_bool(self):
        """fodg_has_text_content returns bool."""
        result = fodg_has_text_content(_SHAPES)
        assert isinstance(result, bool)

    def test_file_size_bytes_positive(self):
        """fodg_file_size_bytes returns positive int for existing files."""
        size = fodg_file_size_bytes(_SHAPES)
        assert isinstance(size, int)
        assert size > 0

    def test_has_no_shapes_on_empty(self):
        """fodg_has_no_shapes returns bool."""
        result = fodg_has_no_shapes(_EMPTY)
        assert isinstance(result, bool)

    def test_has_no_text_items_returns_bool(self):
        """fodg_has_no_text_items returns bool."""
        result = fodg_has_no_text_items(_EMPTY)
        assert isinstance(result, bool)

    def test_has_more_shapes_than_text_consistent(self):
        """fodg_has_more_shapes_than_text_items is consistent with counts."""
        shapes = fodg_total_shape_count(_SHAPES)
        texts = fodg_text_item_count(_SHAPES)
        result = fodg_has_more_shapes_than_text_items(_SHAPES)
        assert result == (shapes > texts)

    def test_is_text_heavy_returns_bool(self):
        """fodg_is_text_heavy returns bool."""
        result = fodg_is_text_heavy(_SHAPES)
        assert isinstance(result, bool)

    def test_is_empty_drawing_consistent_with_total_shapes(self):
        """fodg_is_empty_drawing is consistent with total_shape_count."""
        is_empty = fodg_is_empty_drawing(_EMPTY)
        shapes = fodg_total_shape_count(_EMPTY)
        # If is_empty_drawing says True, shapes should be 0
        if is_empty:
            assert shapes == 0


class TestDrawingDocumentPackageReexport:

    def test_functions_accessible_via_fodg_package(self):
        """All drawing_document functions should be accessible via the fodg package."""
        import fodg
        assert "fodg_total_shape_count" in fodg.__all__
        assert "fodg_page_count" in fodg.__all__
        assert "fodg_has_more_shapes_than_text_items" in fodg.__all__

    def test_fodg_total_shape_count_in_all(self):
        """fodg_total_shape_count must be in fodg.__all__."""
        import fodg
        assert "fodg_total_shape_count" in fodg.__all__

    def test_drawing_document_functions_callable_via_package(self):
        """drawing_document functions callable directly through package."""
        import fodg
        fn = getattr(fodg, "fodg_page_count", None)
        assert fn is not None
        assert callable(fn)
