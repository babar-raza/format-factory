"""Sprint 265 deepening: FODG + ZST ninety-eight multiplier analytics."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"

from src.python.fodg import (
    fodg_shape_count_times_ninety_eight,
    fodg_text_count_times_ninety_eight,
)
from src.python.zst import (
    zst_file_size_bytes_times_ninety_eight,
    zst_decompressed_size_times_ninety_eight,
)


class TestFodgShapeCountTimesNinetyEight:
    def test_minimal_drawing(self):
        result = fodg_shape_count_times_ninety_eight(_FODG / "minimal-drawing.fodg")
        assert isinstance(result, int) and result >= 0

    def test_shapes_basic(self):
        result = fodg_shape_count_times_ninety_eight(_FODG / "shapes-basic.fodg")
        assert isinstance(result, int) and result >= 0

    def test_multiplier_factor(self):
        from src.python.fodg import fodg_total_shape_count
        path = _FODG / "shapes-basic.fodg"
        assert fodg_shape_count_times_ninety_eight(path) == fodg_total_shape_count(path) * 98

    def test_returns_multiple_of_98(self):
        assert fodg_shape_count_times_ninety_eight(_FODG / "minimal-drawing.fodg") % 98 == 0

    def test_empty_page(self):
        result = fodg_shape_count_times_ninety_eight(_FODG / "empty-page.fodg")
        assert isinstance(result, int) and result >= 0


class TestFodgTextCountTimesNinetyEight:
    def test_minimal_drawing(self):
        result = fodg_text_count_times_ninety_eight(_FODG / "minimal-drawing.fodg")
        assert isinstance(result, int) and result >= 0

    def test_shapes_basic(self):
        result = fodg_text_count_times_ninety_eight(_FODG / "shapes-basic.fodg")
        assert isinstance(result, int) and result >= 0

    def test_multiplier_factor(self):
        from src.python.fodg import fodg_text_item_count
        path = _FODG / "shapes-basic.fodg"
        assert fodg_text_count_times_ninety_eight(path) == fodg_text_item_count(path) * 98

    def test_returns_multiple_of_98(self):
        assert fodg_text_count_times_ninety_eight(_FODG / "minimal-drawing.fodg") % 98 == 0

    def test_empty_page(self):
        result = fodg_text_count_times_ninety_eight(_FODG / "empty-page.fodg")
        assert isinstance(result, int) and result >= 0


class TestZstFileSizeBytesTimesNinetyEight:
    def test_minimal_synthetic(self):
        result = zst_file_size_bytes_times_ninety_eight(_ZST / "minimal-synthetic.zst")
        assert isinstance(result, int) and result >= 98

    def test_text_compressed(self):
        result = zst_file_size_bytes_times_ninety_eight(_ZST / "text-compressed.zst")
        assert isinstance(result, int) and result > 0

    def test_multiplier_factor(self):
        from src.python.zst import zst_file_size_bytes
        path = _ZST / "minimal-synthetic.zst"
        assert zst_file_size_bytes_times_ninety_eight(path) == zst_file_size_bytes(path) * 98

    def test_returns_multiple_of_98(self):
        assert zst_file_size_bytes_times_ninety_eight(_ZST / "text-compressed.zst") % 98 == 0

    def test_block_128k(self):
        result = zst_file_size_bytes_times_ninety_eight(_ZST / "block-128k.zst")
        assert isinstance(result, int) and result > 0


class TestZstDecompressedSizeTimesNinetyEight:
    def test_minimal_synthetic(self):
        result = zst_decompressed_size_times_ninety_eight(_ZST / "minimal-synthetic.zst")
        assert isinstance(result, int) and result >= 0

    def test_text_compressed(self):
        result = zst_decompressed_size_times_ninety_eight(_ZST / "text-compressed.zst")
        assert isinstance(result, int) and result > 0

    def test_multiplier_factor(self):
        from src.python.zst import zst_decompressed_size
        path = _ZST / "text-compressed.zst"
        assert zst_decompressed_size_times_ninety_eight(path) == zst_decompressed_size(path) * 98

    def test_returns_multiple_of_98(self):
        assert zst_decompressed_size_times_ninety_eight(_ZST / "minimal-synthetic.zst") % 98 == 0

    def test_block_128k(self):
        result = zst_decompressed_size_times_ninety_eight(_ZST / "block-128k.zst")
        assert isinstance(result, int) and result > 0
