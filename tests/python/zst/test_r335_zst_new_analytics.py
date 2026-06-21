"""
test_r335_zst_new_analytics.py
Sprint 71 — 5 new ZST analytics functions.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import (
    zst_magic_valid,
    zst_ratio_vs_uncompressed,
    zst_bytes_saved,
    zst_is_large_file,
    zst_header_size,
)

_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"
_MINIMAL = str(_SAMPLES / "minimal-synthetic.zst")
_TEXT = str(_SAMPLES / "text-compressed.zst")
_BLOCK = str(_SAMPLES / "block-128k.zst")


# --- zst_magic_valid ---

class TestZstMagicValid:
    def test_returns_bool(self):
        assert isinstance(zst_magic_valid(_MINIMAL), bool)

    def test_minimal_valid(self):
        assert zst_magic_valid(_MINIMAL) is True

    def test_text_valid(self):
        assert zst_magic_valid(_TEXT) is True

    def test_block_valid(self):
        assert zst_magic_valid(_BLOCK) is True

    def test_all_valid_samples(self):
        for f in _SAMPLES.glob("*.zst"):
            assert zst_magic_valid(str(f)) is True


# --- zst_ratio_vs_uncompressed ---

class TestZstRatioVsUncompressed:
    def test_returns_float(self):
        assert isinstance(zst_ratio_vs_uncompressed(_TEXT), float)

    def test_non_negative(self):
        assert zst_ratio_vs_uncompressed(_TEXT) >= 0.0

    def test_minimal_non_negative(self):
        assert zst_ratio_vs_uncompressed(_MINIMAL) >= 0.0

    def test_block_non_negative(self):
        assert zst_ratio_vs_uncompressed(_BLOCK) >= 0.0

    def test_text_non_negative(self):
        assert zst_ratio_vs_uncompressed(_TEXT) >= 0.0


# --- zst_bytes_saved ---

class TestZstBytesSaved:
    def test_returns_int(self):
        assert isinstance(zst_bytes_saved(_TEXT), int)

    def test_non_negative(self):
        assert zst_bytes_saved(_TEXT) >= 0

    def test_minimal_non_negative(self):
        assert zst_bytes_saved(_MINIMAL) >= 0

    def test_block_non_negative(self):
        assert zst_bytes_saved(_BLOCK) >= 0

    def test_text_non_negative(self):
        assert zst_bytes_saved(_TEXT) >= 0


# --- zst_is_large_file ---

class TestZstIsLargeFile:
    def test_returns_bool(self):
        assert isinstance(zst_is_large_file(_MINIMAL), bool)

    def test_minimal_not_large(self):
        assert zst_is_large_file(_MINIMAL) is False

    def test_block_not_large(self):
        # 131KB < 1MB threshold → not considered large
        assert zst_is_large_file(_BLOCK) is False

    def test_text_is_bool(self):
        assert isinstance(zst_is_large_file(_TEXT), bool)

    def test_all_samples_bool(self):
        for f in _SAMPLES.glob("*.zst"):
            assert isinstance(zst_is_large_file(str(f)), bool)


# --- zst_header_size ---

class TestZstHeaderSize:
    def test_returns_int(self):
        assert isinstance(zst_header_size(_MINIMAL), int)

    def test_non_negative(self):
        assert zst_header_size(_MINIMAL) >= 0

    def test_minimal_is_six(self):
        # minimal ZST file has at least 6 bytes
        assert zst_header_size(_MINIMAL) == 6

    def test_text_is_six(self):
        assert zst_header_size(_TEXT) == 6

    def test_block_is_six(self):
        assert zst_header_size(_BLOCK) == 6
