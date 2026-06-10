"""Tests for merge_abw() — ABW document model merge.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-4-001
TC-PRODUCT-ABW-MERGE
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import create_abw, merge_abw


class TestMergeAbw:
    def test_merge_concatenates_paragraphs(self):
        a = create_abw(["Hello", "World"])
        b = create_abw(["Foo", "Bar"])
        merged = merge_abw(a, b)
        assert merged["paragraphs"] == ["Hello", "World", "Foo", "Bar"]

    def test_merge_paragraph_count(self):
        a = create_abw(["A", "B"])
        b = create_abw(["C"])
        merged = merge_abw(a, b)
        assert merged["paragraph_count"] == 3

    def test_merge_is_abw_flag(self):
        a = create_abw(["p1"])
        b = create_abw(["p2"])
        merged = merge_abw(a, b)
        assert merged.get("is_abw") is True

    def test_merge_empty_first(self):
        a = create_abw([])
        b = create_abw(["only"])
        merged = merge_abw(a, b)
        assert merged["paragraphs"] == ["only"]

    def test_merge_empty_second(self):
        a = create_abw(["only"])
        b = create_abw([])
        merged = merge_abw(a, b)
        assert merged["paragraphs"] == ["only"]

    def test_merge_both_empty(self):
        a = create_abw([])
        b = create_abw([])
        merged = merge_abw(a, b)
        assert merged["paragraphs"] == []
        assert merged["paragraph_count"] == 0

    def test_merge_does_not_mutate_a(self):
        a = create_abw(["original"])
        b = create_abw(["new"])
        merge_abw(a, b)
        assert a["paragraphs"] == ["original"]

    def test_merge_does_not_mutate_b(self):
        a = create_abw(["new"])
        b = create_abw(["original"])
        merge_abw(a, b)
        assert b["paragraphs"] == ["original"]

    def test_merge_preserves_order(self):
        a = create_abw(["1", "2", "3"])
        b = create_abw(["4", "5"])
        merged = merge_abw(a, b)
        assert merged["paragraphs"] == ["1", "2", "3", "4", "5"]

    def test_merge_type_error_on_non_dict_a(self):
        with pytest.raises(TypeError):
            merge_abw("not a dict", create_abw([]))

    def test_merge_type_error_on_non_dict_b(self):
        with pytest.raises(TypeError):
            merge_abw(create_abw([]), 42)

    def test_merge_unicode_paragraphs(self):
        a = create_abw(["日本語"])
        b = create_abw(["Αβγδ"])
        merged = merge_abw(a, b)
        assert merged["paragraphs"] == ["日本語", "Αβγδ"]
