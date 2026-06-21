"""Tests for ZST Sprint 56 gap closure.

Closes:
  GAP-ZST-FOSS-ZST_MAGIC_VA-001   (Zst Magic Valid)
  GAP-ZST-FOSS-ZST_RATIO_VS-001   (Zst Ratio Vs Uncompressed)
  GAP-ZST-FOSS-ZST_BYTES_SA-001   (Zst Bytes Saved)
  GAP-ZST-FOSS-ZST_HEADER_S-001   (Zst Header Size)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.zst import zst_magic_valid, zst_ratio_vs_uncompressed, zst_bytes_saved, zst_header_size

_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"
_MINIMAL = str(_DIR / "minimal-synthetic.zst")
_EMPTY = str(_DIR / "empty-block.zst")
_TEXT = str(_DIR / "text-compressed.zst")


class TestZstMagicValid:
    def test_return_type(self):
        assert isinstance(zst_magic_valid(_MINIMAL), bool)

    def test_true_for_minimal(self):
        assert zst_magic_valid(_MINIMAL) is True

    def test_true_for_empty(self):
        assert zst_magic_valid(_EMPTY) is True

    def test_true_for_text(self):
        assert zst_magic_valid(_TEXT) is True

    def test_consistent_across_calls(self):
        assert zst_magic_valid(_MINIMAL) == zst_magic_valid(_MINIMAL)


class TestZstRatioVsUncompressed:
    def test_return_type(self):
        assert isinstance(zst_ratio_vs_uncompressed(_MINIMAL), (int, float))

    def test_exact_10_for_minimal(self):
        assert zst_ratio_vs_uncompressed(_MINIMAL) == 10.0

    def test_zero_for_empty(self):
        assert zst_ratio_vs_uncompressed(_EMPTY) == 0.0

    def test_nonnegative(self):
        assert zst_ratio_vs_uncompressed(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert zst_ratio_vs_uncompressed(_MINIMAL) == zst_ratio_vs_uncompressed(_MINIMAL)


class TestZstBytesSaved:
    def test_return_type(self):
        assert isinstance(zst_bytes_saved(_MINIMAL), int)

    def test_zero_for_minimal(self):
        assert zst_bytes_saved(_MINIMAL) == 0

    def test_zero_for_empty(self):
        assert zst_bytes_saved(_EMPTY) == 0

    def test_exact_118_for_text(self):
        assert zst_bytes_saved(_TEXT) == 118

    def test_nonnegative(self):
        assert zst_bytes_saved(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert zst_bytes_saved(_MINIMAL) == zst_bytes_saved(_MINIMAL)


class TestZstHeaderSize:
    def test_return_type(self):
        assert isinstance(zst_header_size(_MINIMAL), int)

    def test_exact_6_for_minimal(self):
        assert zst_header_size(_MINIMAL) == 6

    def test_exact_6_for_empty(self):
        assert zst_header_size(_EMPTY) == 6

    def test_exact_6_for_text(self):
        assert zst_header_size(_TEXT) == 6

    def test_positive(self):
        assert zst_header_size(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert zst_header_size(_MINIMAL) == zst_header_size(_MINIMAL)
