"""Sprint R290I: ZST analytics deepening — frame_count_ratio, overhead_bytes, avg_compression_per_byte."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from zst.zst_codec import (
    zst_frame_count_ratio,
    zst_overhead_bytes,
    zst_avg_compression_per_byte,
)

SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"
BLOCK = SAMPLES / "block-128k.zst"


@pytest.fixture
def sample():
    if not BLOCK.exists():
        pytest.skip("ZST block-128k sample not available")
    return BLOCK


class TestZstFrameCountRatio:
    def test_returns_float(self, sample):
        assert isinstance(zst_frame_count_ratio(sample), float)

    def test_nonnegative(self, sample):
        assert zst_frame_count_ratio(sample) >= 0.0


class TestZstOverheadBytes:
    def test_returns_int(self, sample):
        assert isinstance(zst_overhead_bytes(sample), int)

    def test_nonnegative(self, sample):
        assert zst_overhead_bytes(sample) >= 0


class TestZstAvgCompressionPerByte:
    def test_returns_float(self, sample):
        assert isinstance(zst_avg_compression_per_byte(sample), float)

    def test_nonnegative(self, sample):
        assert zst_avg_compression_per_byte(sample) >= 0.0
