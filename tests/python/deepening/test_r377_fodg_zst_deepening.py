"""Sprint 249 deepening: FODG + ZST ninety multiplier analytics."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"

from src.python.fodg import (
    fodg_shape_count_times_ninety,
    fodg_text_count_times_ninety,
)
from src.python.zst import (
    zst_file_size_bytes_times_ninety,
    zst_decompressed_size_times_ninety,
)


class TestFodgShapeCountTimesNinety:
    def test_minimal_drawing(self):
        result = fodg_shape_count_times_ninety(_FODG / "minimal-drawing.fodg")
        assert isinstance(result, int)
        assert result >= 0

    def test_shapes_basic(self):
        result = fodg_shape_count_times_ninety(_FODG / "shapes-basic.fodg")
        assert isinstance(result, int)
        assert result >= 0

    def test_multiplier_factor(self):
        from src.python.fodg import fodg_total_shape_count
        path = _FODG / "shapes-basic.fodg"
        base = fodg_total_shape_count(path)
        assert fodg_shape_count_times_ninety(path) == base * 90

    def test_returns_multiple_of_90(self):
        result = fodg_shape_count_times_ninety(_FODG / "minimal-drawing.fodg")
        assert result % 90 == 0

    def test_empty_page(self):
        result = fodg_shape_count_times_ninety(_FODG / "empty-page.fodg")
        assert isinstance(result, int)
        assert result >= 0


class TestFodgTextCountTimesNinety:
    def test_minimal_drawing(self):
        result = fodg_text_count_times_ninety(_FODG / "minimal-drawing.fodg")
        assert isinstance(result, int)
        assert result >= 0

    def test_shapes_basic(self):
        result = fodg_text_count_times_ninety(_FODG / "shapes-basic.fodg")
        assert isinstance(result, int)
        assert result >= 0

    def test_multiplier_factor(self):
        from src.python.fodg import fodg_text_item_count
        path = _FODG / "shapes-basic.fodg"
        base = fodg_text_item_count(path)
        assert fodg_text_count_times_ninety(path) == base * 90

    def test_returns_multiple_of_90(self):
        result = fodg_text_count_times_ninety(_FODG / "minimal-drawing.fodg")
        assert result % 90 == 0

    def test_empty_page(self):
        result = fodg_text_count_times_ninety(_FODG / "empty-page.fodg")
        assert isinstance(result, int)
        assert result >= 0


class TestZstFileSizeBytesTimesNinety:
    def test_minimal_synthetic(self):
        result = zst_file_size_bytes_times_ninety(_ZST / "minimal-synthetic.zst")
        assert isinstance(result, int)
        assert result >= 90

    def test_text_compressed(self):
        result = zst_file_size_bytes_times_ninety(_ZST / "text-compressed.zst")
        assert isinstance(result, int)
        assert result > 0

    def test_multiplier_factor(self):
        from src.python.zst import zst_file_size_bytes
        path = _ZST / "minimal-synthetic.zst"
        base = zst_file_size_bytes(path)
        assert zst_file_size_bytes_times_ninety(path) == base * 90

    def test_returns_multiple_of_90(self):
        result = zst_file_size_bytes_times_ninety(_ZST / "text-compressed.zst")
        assert result % 90 == 0

    def test_block_128k(self):
        result = zst_file_size_bytes_times_ninety(_ZST / "block-128k.zst")
        assert isinstance(result, int)
        assert result > 0


class TestZstDecompressedSizeTimesNinety:
    def test_minimal_synthetic(self):
        result = zst_decompressed_size_times_ninety(_ZST / "minimal-synthetic.zst")
        assert isinstance(result, int)
        assert result >= 0

    def test_text_compressed(self):
        result = zst_decompressed_size_times_ninety(_ZST / "text-compressed.zst")
        assert isinstance(result, int)
        assert result > 0

    def test_multiplier_factor(self):
        from src.python.zst import zst_decompressed_size
        path = _ZST / "text-compressed.zst"
        base = zst_decompressed_size(path)
        assert zst_decompressed_size_times_ninety(path) == base * 90

    def test_returns_multiple_of_90(self):
        result = zst_decompressed_size_times_ninety(_ZST / "minimal-synthetic.zst")
        assert result % 90 == 0

    def test_block_128k(self):
        result = zst_decompressed_size_times_ninety(_ZST / "block-128k.zst")
        assert isinstance(result, int)
        assert result > 0
