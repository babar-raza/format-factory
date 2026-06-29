"""
tests/python/zst/test_r267_zst_compression_summary.py

Sprint: ff-sprint-s267-zst-compression-summary-20260626
Authority: FACT-ZST-001 (RFC 8878 §3.1 — Zstandard frame structure)

Tests for get_compression_summary() in zst_codec.py.
"""
from __future__ import annotations

import pytest

zstandard = pytest.importorskip("zstandard", reason="zstandard library not installed")


class TestGetCompressionSummaryImport:
    """get_compression_summary is importable and callable."""

    def test_importable_from_zst_codec(self):
        from zst.zst_codec import get_compression_summary
        assert callable(get_compression_summary)

    def test_importable_from_package(self):
        import zst
        assert hasattr(zst, "get_compression_summary")


class TestGetCompressionSummaryStructure:
    """get_compression_summary returns correct output structure."""

    _DATA = b"compression test payload " * 50

    def test_returns_dict(self):
        from zst.zst_codec import get_compression_summary
        result = get_compression_summary(self._DATA)
        assert isinstance(result, dict)

    def test_format_field(self):
        from zst.zst_codec import get_compression_summary
        result = get_compression_summary(self._DATA)
        assert result["format"] == "zstd"

    def test_level_field_matches_input(self):
        from zst.zst_codec import get_compression_summary
        result = get_compression_summary(self._DATA, level=5)
        assert result["level"] == 5

    def test_original_size_matches_input(self):
        from zst.zst_codec import get_compression_summary
        result = get_compression_summary(self._DATA)
        assert result["original_size"] == len(self._DATA)

    def test_compressed_size_positive(self):
        from zst.zst_codec import get_compression_summary
        result = get_compression_summary(self._DATA)
        assert result["compressed_size"] > 0

    def test_ratio_greater_than_one(self):
        from zst.zst_codec import get_compression_summary
        result = get_compression_summary(self._DATA)
        assert result["ratio"] > 1.0

    def test_frame_count_positive(self):
        from zst.zst_codec import get_compression_summary
        result = get_compression_summary(self._DATA)
        assert result["frame_count"] >= 1

    def test_valid_field_true(self):
        from zst.zst_codec import get_compression_summary
        result = get_compression_summary(self._DATA)
        assert result["valid"] is True

    def test_magic_ok_true(self):
        from zst.zst_codec import get_compression_summary
        result = get_compression_summary(self._DATA)
        assert result["magic_ok"] is True

    def test_has_all_required_keys(self):
        from zst.zst_codec import get_compression_summary
        result = get_compression_summary(self._DATA)
        required = {"format", "level", "original_size", "compressed_size", "ratio", "frame_count", "valid", "magic_ok"}
        assert required.issubset(result.keys())


class TestGetCompressionSummaryLevels:
    """get_compression_summary works at various compression levels."""

    _DATA = b"level test data with repeating patterns " * 30

    def test_level_1_works(self):
        from zst.zst_codec import get_compression_summary
        result = get_compression_summary(self._DATA, level=1)
        assert result["valid"] is True
        assert result["level"] == 1

    def test_level_3_default(self):
        from zst.zst_codec import get_compression_summary
        result = get_compression_summary(self._DATA)
        assert result["level"] == 3

    def test_level_6_works(self):
        from zst.zst_codec import get_compression_summary
        result = get_compression_summary(self._DATA, level=6)
        assert result["valid"] is True
        assert result["magic_ok"] is True
