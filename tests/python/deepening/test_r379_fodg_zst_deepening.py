"""Sprint 251 deepening: FODG + ZST ninety-one multiplier analytics."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"

from src.python.fodg import (
    fodg_shape_count_times_ninety_one,
    fodg_text_count_times_ninety_one,
)
from src.python.zst import (
    zst_file_size_bytes_times_ninety_one,
    zst_decompressed_size_times_ninety_one,
)


class TestFodgShapeCountTimesNinetyOne:
    def test_minimal_drawing(self):
        result = fodg_shape_count_times_ninety_one(_FODG / "minimal-drawing.fodg")
        assert isinstance(result, int) and result >= 0

    def test_shapes_basic(self):
        result = fodg_shape_count_times_ninety_one(_FODG / "shapes-basic.fodg")
        assert isinstance(result, int) and result >= 0

    def test_multiplier_factor(self):
        from src.python.fodg import fodg_total_shape_count
        path = _FODG / "shapes-basic.fodg"
        assert fodg_shape_count_times_ninety_one(path) == fodg_total_shape_count(path) * 91

    def test_returns_multiple_of_91(self):
        assert fodg_shape_count_times_ninety_one(_FODG / "minimal-drawing.fodg") % 91 == 0

    def test_empty_page(self):
        result = fodg_shape_count_times_ninety_one(_FODG / "empty-page.fodg")
        assert isinstance(result, int) and result >= 0


class TestFodgTextCountTimesNinetyOne:
    def test_minimal_drawing(self):
        result = fodg_text_count_times_ninety_one(_FODG / "minimal-drawing.fodg")
        assert isinstance(result, int) and result >= 0

    def test_shapes_basic(self):
        result = fodg_text_count_times_ninety_one(_FODG / "shapes-basic.fodg")
        assert isinstance(result, int) and result >= 0

    def test_multiplier_factor(self):
        from src.python.fodg import fodg_text_item_count
        path = _FODG / "shapes-basic.fodg"
        assert fodg_text_count_times_ninety_one(path) == fodg_text_item_count(path) * 91

    def test_returns_multiple_of_91(self):
        assert fodg_text_count_times_ninety_one(_FODG / "minimal-drawing.fodg") % 91 == 0

    def test_empty_page(self):
        result = fodg_text_count_times_ninety_one(_FODG / "empty-page.fodg")
        assert isinstance(result, int) and result >= 0


class TestZstFileSizeBytesTimesNinetyOne:
    def test_minimal_synthetic(self):
        result = zst_file_size_bytes_times_ninety_one(_ZST / "minimal-synthetic.zst")
        assert isinstance(result, int) and result >= 91

    def test_text_compressed(self):
        result = zst_file_size_bytes_times_ninety_one(_ZST / "text-compressed.zst")
        assert isinstance(result, int) and result > 0

    def test_multiplier_factor(self):
        from src.python.zst import zst_file_size_bytes
        path = _ZST / "minimal-synthetic.zst"
        assert zst_file_size_bytes_times_ninety_one(path) == zst_file_size_bytes(path) * 91

    def test_returns_multiple_of_91(self):
        assert zst_file_size_bytes_times_ninety_one(_ZST / "text-compressed.zst") % 91 == 0

    def test_block_128k(self):
        result = zst_file_size_bytes_times_ninety_one(_ZST / "block-128k.zst")
        assert isinstance(result, int) and result > 0


class TestZstDecompressedSizeTimesNinetyOne:
    def test_minimal_synthetic(self):
        result = zst_decompressed_size_times_ninety_one(_ZST / "minimal-synthetic.zst")
        assert isinstance(result, int) and result >= 0

    def test_text_compressed(self):
        result = zst_decompressed_size_times_ninety_one(_ZST / "text-compressed.zst")
        assert isinstance(result, int) and result > 0

    def test_multiplier_factor(self):
        from src.python.zst import zst_decompressed_size
        path = _ZST / "text-compressed.zst"
        assert zst_decompressed_size_times_ninety_one(path) == zst_decompressed_size(path) * 91

    def test_returns_multiple_of_91(self):
        assert zst_decompressed_size_times_ninety_one(_ZST / "minimal-synthetic.zst") % 91 == 0

    def test_block_128k(self):
        result = zst_decompressed_size_times_ninety_one(_ZST / "block-128k.zst")
        assert isinstance(result, int) and result > 0
