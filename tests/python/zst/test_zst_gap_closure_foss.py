"""
ZST FOSS gap closure tests.

Closes:
  GAP-ZST-FOSS-ZST_COMPRESS-001   — zst_compression_saving
  GAP-ZST-FOSS-ZST_IS_HIGHL-001   — zst_is_highly_compressed
  GAP-ZST-FOSS-ZST_IS_RLE_E-001   — zst_is_rle_efficient
  GAP-ZST-FOSS-ZST_FILE_SIZ-001   — zst_file_size_bytes
  GAP-ZST-FOSS-ZST_IS_EMPTY-001   — zst_is_empty_content
  GAP-ZST-FOSS-ZST_DENSITY-001    — zst_density
  GAP-ZST-FOSS-ZST_UNIQUE_F-001   — zst_unique_frame_size_count
  GAP-ZST-FOSS-ZST_IS_UNIFO-001   — zst_is_uniform_frames
  GAP-ZST-FOSS-ZST_CONTENT_-001   — zst_content_type_hint
  GAP-ZST-FOSS-ZST_FRAME_HE-001   — zst_frame_header_descriptor
  GAP-ZST-FOSS-ZST_IS_MINIM-001   — zst_is_minimal_frame
  GAP-ZST-FOSS-ZST_MAGIC_VA-001   — zst_magic_valid
  GAP-ZST-FOSS-ZST_RATIO_VS-001   — zst_ratio_vs_uncompressed
  GAP-ZST-FOSS-ZST_BYTES_SA-001   — zst_bytes_saved
  GAP-ZST-FOSS-ZST_HEADER_S-001   — zst_header_size
  GAP-ZST-FOSS-ZST_SIZE_EXC-001   — zst_size_exceeds_100k
  GAP-ZST-FOSS-ZST_FRAME_CO-001   — zst_frame_count_ratio
  GAP-ZST-FOSS-ZST_OVERHEAD-001   — zst_overhead_bytes
  GAP-ZST-FOSS-ZST_AVG_COMP-001   — zst_avg_compression_per_byte
  GAP-ZST-FOSS-ZST_AVG_BYTE-001   — zst_avg_byte_value
  GAP-ZST-FOSS-ZST_SIZE_PER-001   — zst_size_per_frame
  GAP-ZST-FOSS-ZST_BYTE_RAT-001   — zst_byte_ratio
  GAP-ZST-FOSS-ZST_MAX_BYTE-001   — zst_max_byte_value
  GAP-ZST-FOSS-ZST_MIN_BYTE-001   — zst_min_byte_value
  GAP-ZST-FOSS-ZST_AVG_DECO-001   — zst_avg_decompressed_byte_value
  GAP-ZST-FOSS-ZST_BYTE_SUM-001   — zst_byte_sum_per_frame
  GAP-ZST-FOSS-ZST_BYTE_COU-001   — zst_byte_count_squared
  GAP-ZST-FOSS-ZST_BYTES_PE-001   — zst_bytes_per_decompressed_byte
  GAP-ZST-FOSS-ZST_IS_TRIVI-001   — zst_is_trivial_compression
  GAP-ZST-FOSS-ZST_SIZE_RAT-001   — zst_size_ratio
  GAP-ZST-FOSS-ZST_DECOMP_T-001   — zst_decomp_times_5_plus_comp_mod_100_times_7_plus_min_byte_times_50
  GAP-ZST-FOSS-ZST_BYTE_RAN-001   — zst_byte_range

Run from repo root:
    python -m pytest tests/python/zst/test_zst_gap_closure_foss.py -v
"""

import sys
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from zst.zst_codec import (
    zst_is_highly_compressed,
    zst_file_size_bytes,
    zst_unique_frame_size_count,
    zst_is_uniform_frames,
    zst_content_type_hint,
    zst_frame_header_descriptor,
    zst_is_minimal_frame,
    zst_magic_valid,
    zst_header_size,
    zst_size_exceeds_100k,
    zst_frame_count_ratio,
    zst_overhead_bytes,
    zst_avg_byte_value,
    zst_size_per_frame,
    zst_byte_ratio,
    zst_max_byte_value,
    zst_min_byte_value,
    zst_avg_decompressed_byte_value,
    zst_byte_sum_per_frame,
    zst_byte_count_squared,
    zst_byte_range,
    # These require zstandard:
    zst_compression_saving,
    zst_is_rle_efficient,
    zst_is_empty_content,
    zst_density,
    zst_ratio_vs_uncompressed,
    zst_bytes_saved,
    zst_avg_compression_per_byte,
    zst_bytes_per_decompressed_byte,
    zst_is_trivial_compression,
    zst_size_ratio,
    zst_decomp_times_5_plus_comp_mod_100_times_7_plus_min_byte_times_50,
)

SAMPLES = REPO_ROOT / "samples" / "by-format" / "zst" / "valid"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
BLOCK = SAMPLES / "block-128k.zst"

zstandard_available = True
try:
    import zstandard  # noqa: F401
except ImportError:
    zstandard_available = False

requires_zstandard = pytest.mark.skipif(
    not zstandard_available, reason="zstandard not installed"
)


class TestZstIsHighlyCompressed:
    def test_block_not_highly_compressed(self):
        assert zst_is_highly_compressed(BLOCK) is False

    def test_returns_bool(self):
        assert isinstance(zst_is_highly_compressed(MINIMAL), bool)


class TestZstFileSizeBytes:
    def test_minimal_positive(self):
        assert zst_file_size_bytes(MINIMAL) > 0

    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes(MINIMAL), int)

    def test_block_larger(self):
        assert zst_file_size_bytes(BLOCK) > zst_file_size_bytes(MINIMAL)


class TestZstUniqueFrameSizeCount:
    def test_returns_int(self):
        assert isinstance(zst_unique_frame_size_count(MINIMAL), int)

    def test_positive(self):
        assert zst_unique_frame_size_count(MINIMAL) >= 1


class TestZstIsUniformFrames:
    def test_minimal_uniform(self):
        assert zst_is_uniform_frames(MINIMAL) is True

    def test_returns_bool(self):
        assert isinstance(zst_is_uniform_frames(MINIMAL), bool)


class TestZstContentTypeHint:
    def test_returns_str(self):
        assert isinstance(zst_content_type_hint(MINIMAL), str)

    def test_non_empty(self):
        assert len(zst_content_type_hint(MINIMAL)) > 0


class TestZstFrameHeaderDescriptor:
    def test_returns_int(self):
        assert isinstance(zst_frame_header_descriptor(MINIMAL), int)

    def test_non_negative(self):
        assert zst_frame_header_descriptor(MINIMAL) >= 0


class TestZstIsMinimalFrame:
    def test_minimal_is_minimal(self):
        assert zst_is_minimal_frame(MINIMAL) is True

    def test_block_not_minimal(self):
        assert zst_is_minimal_frame(BLOCK) is False

    def test_returns_bool(self):
        assert isinstance(zst_is_minimal_frame(MINIMAL), bool)


class TestZstMagicValid:
    def test_minimal_magic_valid(self):
        assert zst_magic_valid(MINIMAL) is True

    def test_block_magic_valid(self):
        assert zst_magic_valid(BLOCK) is True

    def test_returns_bool(self):
        assert isinstance(zst_magic_valid(MINIMAL), bool)


class TestZstHeaderSize:
    def test_returns_int(self):
        assert isinstance(zst_header_size(MINIMAL), int)

    def test_positive(self):
        assert zst_header_size(MINIMAL) > 0


class TestZstSizeExceeds100k:
    def test_minimal_not_exceed(self):
        assert zst_size_exceeds_100k(MINIMAL) is False

    def test_block_exceeds(self):
        assert zst_size_exceeds_100k(BLOCK) is True

    def test_returns_bool(self):
        assert isinstance(zst_size_exceeds_100k(MINIMAL), bool)


class TestZstFrameCountRatio:
    def test_returns_numeric(self):
        assert isinstance(zst_frame_count_ratio(MINIMAL), (int, float))

    def test_positive(self):
        assert zst_frame_count_ratio(MINIMAL) > 0


class TestZstOverheadBytes:
    def test_returns_int(self):
        assert isinstance(zst_overhead_bytes(MINIMAL), int)

    def test_non_negative(self):
        assert zst_overhead_bytes(MINIMAL) >= 0


class TestZstAvgByteValue:
    def test_returns_numeric(self):
        assert isinstance(zst_avg_byte_value(MINIMAL), (int, float))

    def test_non_negative(self):
        assert zst_avg_byte_value(MINIMAL) >= 0


class TestZstSizePerFrame:
    def test_returns_numeric(self):
        assert isinstance(zst_size_per_frame(MINIMAL), (int, float))

    def test_positive(self):
        assert zst_size_per_frame(MINIMAL) > 0


class TestZstByteRatio:
    def test_returns_numeric(self):
        assert isinstance(zst_byte_ratio(MINIMAL), (int, float))

    def test_non_negative(self):
        assert zst_byte_ratio(MINIMAL) >= 0


class TestZstMaxByteValue:
    def test_returns_int(self):
        assert isinstance(zst_max_byte_value(MINIMAL), int)

    def test_non_negative(self):
        assert zst_max_byte_value(MINIMAL) >= 0


class TestZstMinByteValue:
    def test_returns_int(self):
        assert isinstance(zst_min_byte_value(MINIMAL), int)

    def test_non_negative(self):
        assert zst_min_byte_value(MINIMAL) >= 0


class TestZstAvgDecompressedByteValue:
    def test_returns_numeric(self):
        assert isinstance(zst_avg_decompressed_byte_value(MINIMAL), (int, float))

    def test_non_negative(self):
        assert zst_avg_decompressed_byte_value(MINIMAL) >= 0


class TestZstByteSumPerFrame:
    def test_returns_int(self):
        assert isinstance(zst_byte_sum_per_frame(MINIMAL), int)

    def test_non_negative(self):
        assert zst_byte_sum_per_frame(MINIMAL) >= 0


class TestZstByteCountSquared:
    def test_returns_int(self):
        assert isinstance(zst_byte_count_squared(MINIMAL), int)

    def test_non_negative(self):
        assert zst_byte_count_squared(MINIMAL) >= 0


class TestZstByteRange:
    def test_returns_int(self):
        assert isinstance(zst_byte_range(MINIMAL), int)

    def test_non_negative(self):
        assert zst_byte_range(MINIMAL) >= 0


@requires_zstandard
class TestZstCompressionSaving:
    def test_returns_numeric(self):
        assert isinstance(zst_compression_saving(MINIMAL), (int, float))


@requires_zstandard
class TestZstIsRleEfficient:
    def test_returns_bool(self):
        assert isinstance(zst_is_rle_efficient(MINIMAL), bool)


@requires_zstandard
class TestZstIsEmptyContent:
    def test_returns_bool(self):
        assert isinstance(zst_is_empty_content(MINIMAL), bool)


@requires_zstandard
class TestZstDensity:
    def test_returns_numeric(self):
        assert isinstance(zst_density(MINIMAL), (int, float))


@requires_zstandard
class TestZstRatioVsUncompressed:
    def test_returns_numeric(self):
        assert isinstance(zst_ratio_vs_uncompressed(MINIMAL), (int, float))


@requires_zstandard
class TestZstBytesSaved:
    def test_returns_numeric(self):
        assert isinstance(zst_bytes_saved(MINIMAL), (int, float))


@requires_zstandard
class TestZstAvgCompressionPerByte:
    def test_returns_numeric(self):
        assert isinstance(zst_avg_compression_per_byte(MINIMAL), (int, float))


@requires_zstandard
class TestZstBytesPerDecompressedByte:
    def test_returns_numeric(self):
        assert isinstance(zst_bytes_per_decompressed_byte(MINIMAL), (int, float))


@requires_zstandard
class TestZstIsTrivialCompression:
    def test_returns_bool(self):
        assert isinstance(zst_is_trivial_compression(MINIMAL), bool)


@requires_zstandard
class TestZstSizeRatio:
    def test_returns_numeric(self):
        assert isinstance(zst_size_ratio(MINIMAL), (int, float))


@requires_zstandard
class TestZstDecompTimes5PlusCompMod100Times7PlusMinBytesTimes50:
    def test_returns_numeric(self):
        result = zst_decomp_times_5_plus_comp_mod_100_times_7_plus_min_byte_times_50(MINIMAL)
        assert isinstance(result, (int, float))
