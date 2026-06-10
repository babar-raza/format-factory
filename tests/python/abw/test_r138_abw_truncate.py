"""Tests for truncate_paragraphs() — ABW paragraph truncation.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-5-001
TC-PRODUCT-ABW-TRUNCATE
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import create_abw, truncate_paragraphs


class TestTruncateParagraphs:
    def test_truncate_to_fewer(self):
        model = create_abw(["a", "b", "c", "d", "e"])
        result = truncate_paragraphs(model, 3)
        assert result["paragraphs"] == ["a", "b", "c"]

    def test_truncate_to_zero(self):
        model = create_abw(["a", "b"])
        result = truncate_paragraphs(model, 0)
        assert result["paragraphs"] == []
        assert result["paragraph_count"] == 0

    def test_truncate_larger_than_length(self):
        model = create_abw(["a", "b"])
        result = truncate_paragraphs(model, 10)
        assert result["paragraphs"] == ["a", "b"]

    def test_does_not_mutate_input(self):
        model = create_abw(["a", "b", "c"])
        truncate_paragraphs(model, 1)
        assert len(model["paragraphs"]) == 3

    def test_paragraph_count_updated(self):
        model = create_abw(["a", "b", "c"])
        result = truncate_paragraphs(model, 2)
        assert result["paragraph_count"] == 2

    def test_is_abw_preserved(self):
        model = create_abw(["a"])
        result = truncate_paragraphs(model, 1)
        assert result["is_abw"] is True

    def test_negative_raises(self):
        model = create_abw(["a"])
        with pytest.raises(ValueError):
            truncate_paragraphs(model, -1)

    def test_type_error_on_non_dict(self):
        with pytest.raises(TypeError):
            truncate_paragraphs("not a dict", 2)

    def test_exact_count(self):
        model = create_abw(["x", "y", "z"])
        result = truncate_paragraphs(model, 3)
        assert result["paragraphs"] == ["x", "y", "z"]

    def test_returns_dict(self):
        model = create_abw(["a"])
        assert isinstance(truncate_paragraphs(model, 1), dict)
