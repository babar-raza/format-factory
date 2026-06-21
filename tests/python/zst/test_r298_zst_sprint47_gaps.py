"""Tests for ZST Sprint 47 gap closure.

Closes:
  GAP-ZST-FOSS-ZST_DENSITY-001       (Zst Density)
  GAP-ZST-FOSS-ZST_UNIQUE_F-001      (Zst Unique Frame Size Count)
  GAP-ZST-FOSS-ZST_IS_UNIFO-001      (Zst Is Uniform Frames)
  GAP-ZST-FOSS-ZST_CONTENT_-001      (Zst Content Type Hint)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_density,
    zst_unique_frame_size_count,
    zst_is_uniform_frames,
    zst_content_type_hint,
)

_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"
_EMPTY = str(_DIR / "empty-block.zst")
_MINIMAL = str(_DIR / "minimal-synthetic.zst")
_TEXT = str(_DIR / "text-compressed.zst")


class TestZstDensity:
    def test_return_type(self):
        assert isinstance(zst_density(_MINIMAL), (int, float))

    def test_exact_10_for_minimal(self):
        assert zst_density(_MINIMAL) == 10.0

    def test_zero_for_empty(self):
        assert zst_density(_EMPTY) == 0.0

    def test_nonnegative(self):
        assert zst_density(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert zst_density(_MINIMAL) == zst_density(_MINIMAL)


class TestZstUniqueFrameSizeCount:
    def test_return_type(self):
        assert isinstance(zst_unique_frame_size_count(_MINIMAL), int)

    def test_exact_1_for_minimal(self):
        assert zst_unique_frame_size_count(_MINIMAL) == 1

    def test_exact_1_for_empty(self):
        assert zst_unique_frame_size_count(_EMPTY) == 1

    def test_positive(self):
        assert zst_unique_frame_size_count(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert zst_unique_frame_size_count(_MINIMAL) == zst_unique_frame_size_count(_MINIMAL)


class TestZstIsUniformFrames:
    def test_return_type(self):
        assert isinstance(zst_is_uniform_frames(_MINIMAL), bool)

    def test_true_for_minimal(self):
        assert zst_is_uniform_frames(_MINIMAL) is True

    def test_true_for_empty(self):
        assert zst_is_uniform_frames(_EMPTY) is True

    def test_true_for_text(self):
        assert zst_is_uniform_frames(_TEXT) is True

    def test_consistent_across_calls(self):
        assert zst_is_uniform_frames(_MINIMAL) == zst_is_uniform_frames(_MINIMAL)


class TestZstContentTypeHint:
    def test_return_type(self):
        assert isinstance(zst_content_type_hint(_MINIMAL), str)

    def test_exact_highly_compressible_for_minimal(self):
        assert zst_content_type_hint(_MINIMAL) == "highly_compressible"

    def test_exact_empty_for_empty_block(self):
        assert zst_content_type_hint(_EMPTY) == "empty"

    def test_nonempty_string(self):
        assert len(zst_content_type_hint(_MINIMAL)) > 0

    def test_consistent_across_calls(self):
        assert zst_content_type_hint(_MINIMAL) == zst_content_type_hint(_MINIMAL)
