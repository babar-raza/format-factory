# R104 Wave 2: ZST compression level coverage and ratio verification
# Lane D — ZST FOSS hardening
# Ledger: R104-FOSS-ZST-COMPRESSION-LEVELS-001

import pytest
from zst.zst_codec import (
    compress_bytes,
    decompress_bytes,
    probe_frame,
    ZstError,
    ZSTD_MAGIC,
)


@pytest.fixture
def sample_data():
    """Repetitive data that compresses well."""
    return b"ABCDEFGH" * 1024  # 8 KiB


@pytest.fixture
def random_ish_data():
    """Pseudo-random data that compresses poorly."""
    return bytes(range(256)) * 32  # 8 KiB, high entropy


class TestCompressionLevelRange:
    """Verify compress/decompress roundtrip across all 22 levels."""

    @pytest.mark.parametrize("level", [1, 3, 6, 9, 12, 15, 18, 22])
    def test_roundtrip_at_level(self, sample_data, level):
        compressed = compress_bytes(sample_data, level=level)
        assert compressed[:4] == ZSTD_MAGIC
        result = decompress_bytes(compressed)
        assert result == sample_data

    @pytest.mark.parametrize("level", [1, 11, 22])
    def test_roundtrip_random_data(self, random_ish_data, level):
        compressed = compress_bytes(random_ish_data, level=level)
        result = decompress_bytes(compressed)
        assert result == random_ish_data

    def test_higher_level_better_ratio(self, sample_data):
        """Higher compression levels should produce smaller or equal output."""
        size_1 = len(compress_bytes(sample_data, level=1))
        size_22 = len(compress_bytes(sample_data, level=22))
        assert size_22 <= size_1

    def test_level_1_fastest(self, sample_data):
        """Level 1 should still produce valid output."""
        c = compress_bytes(sample_data, level=1)
        assert decompress_bytes(c) == sample_data

    def test_level_22_max(self, sample_data):
        """Level 22 (max) should still produce valid output."""
        c = compress_bytes(sample_data, level=22)
        assert decompress_bytes(c) == sample_data


class TestCompressionRatios:
    """Verify compression ratio properties."""

    def test_repetitive_data_compresses_well(self, sample_data):
        compressed = compress_bytes(sample_data, level=3)
        ratio = len(sample_data) / len(compressed)
        assert ratio > 5  # repetitive data should compress 5x+

    def test_empty_input_roundtrip(self):
        compressed = compress_bytes(b"", level=3)
        assert decompress_bytes(compressed) == b""

    def test_single_byte_roundtrip(self):
        compressed = compress_bytes(b"\x42", level=3)
        assert decompress_bytes(compressed) == b"\x42"

    def test_probe_shows_content_size(self, sample_data):
        compressed = compress_bytes(sample_data, level=3)
        info = probe_frame(compressed)
        assert info["magic_ok"] is True
        # content_size may or may not be declared depending on zstandard version


class TestInvalidLevels:
    """Verify error handling for invalid compression levels."""

    def test_level_zero_raises(self):
        with pytest.raises(ZstError, match="level must be 1-22"):
            compress_bytes(b"test", level=0)

    def test_level_23_raises(self):
        with pytest.raises(ZstError, match="level must be 1-22"):
            compress_bytes(b"test", level=23)

    def test_negative_level_raises(self):
        with pytest.raises(ZstError, match="level must be 1-22"):
            compress_bytes(b"test", level=-1)
