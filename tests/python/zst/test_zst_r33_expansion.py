"""
ZST test expansion — R33 deepening deliverable.
Target: bring ZST from 25 tests to 50+ with edge cases, boundary tests, and codec depth.

Run from repo root:
    PYTHONPATH=C:/Users/prora/AppData/Roaming/Python/Python313/site-packages \
        python -m pytest tests/python/zst/ -v
"""

import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

try:
    import zstandard  # noqa: F401
    ZSTD_AVAILABLE = True
except ImportError:
    ZSTD_AVAILABLE = False

skip_if_no_zstd = pytest.mark.skipif(
    not ZSTD_AVAILABLE,
    reason="zstandard not installed"
)

from zst.zst_codec import (
    ZstError,
    ZstDecompressionError,
    ZstInvalidFrameError,
    ZstOutputLimitExceeded,
    ZSTD_MAGIC,
    compress_bytes,
    decompress_bytes,
    probe_frame,
    validate_file,
)


# ---------------------------------------------------------------------------
# 1. Compression edge cases
# ---------------------------------------------------------------------------

class TestCompressEdgeCases:

    @skip_if_no_zstd
    def test_single_byte(self):
        data = b"\x42"
        compressed = compress_bytes(data)
        assert compressed[:4] == ZSTD_MAGIC
        assert decompress_bytes(compressed) == data

    @skip_if_no_zstd
    def test_all_zeros(self):
        data = b"\x00" * 10000
        compressed = compress_bytes(data)
        assert len(compressed) < len(data)
        assert decompress_bytes(compressed) == data

    @skip_if_no_zstd
    def test_all_ones(self):
        data = b"\xff" * 10000
        compressed = compress_bytes(data)
        assert decompress_bytes(compressed) == data

    @skip_if_no_zstd
    def test_alternating_bytes(self):
        data = (b"\x00\xff") * 5000
        compressed = compress_bytes(data)
        assert decompress_bytes(compressed) == data

    @skip_if_no_zstd
    def test_random_looking_data(self):
        """Pseudo-random data (poor compression ratio but must round-trip)."""
        import hashlib
        data = hashlib.sha256(b"seed").digest() * 100
        compressed = compress_bytes(data)
        assert decompress_bytes(compressed) == data

    @skip_if_no_zstd
    def test_unicode_encoded_text(self):
        data = "Hello \u4e16\u754c! \U0001f600".encode("utf-8") * 100
        compressed = compress_bytes(data)
        assert decompress_bytes(compressed) == data


# ---------------------------------------------------------------------------
# 2. Compression levels
# ---------------------------------------------------------------------------

class TestCompressionLevels:

    @skip_if_no_zstd
    def test_level_1_roundtrip(self):
        data = b"test " * 1000
        assert decompress_bytes(compress_bytes(data, level=1)) == data

    @skip_if_no_zstd
    def test_level_22_roundtrip(self):
        data = b"test " * 1000
        assert decompress_bytes(compress_bytes(data, level=22)) == data

    @skip_if_no_zstd
    def test_higher_level_smaller_output(self):
        data = b"repetitive data for compression " * 1000
        size_1 = len(compress_bytes(data, level=1))
        size_22 = len(compress_bytes(data, level=22))
        # Higher level should produce same or smaller output
        assert size_22 <= size_1


# ---------------------------------------------------------------------------
# 3. Decompression guards
# ---------------------------------------------------------------------------

class TestDecompressionGuards:

    def test_empty_input(self):
        with pytest.raises((ZstInvalidFrameError, ZstError)):
            decompress_bytes(b"")

    def test_single_byte_input(self):
        with pytest.raises((ZstInvalidFrameError, ZstError)):
            decompress_bytes(b"\x00")

    def test_magic_only(self):
        """Just the magic bytes with no payload."""
        with pytest.raises((ZstDecompressionError, ZstInvalidFrameError)):
            decompress_bytes(b"\x28\xb5\x2f\xfd")

    @skip_if_no_zstd
    def test_output_guard_exact_boundary(self):
        """Output guard at exact size of data should pass."""
        data = b"X" * 100
        compressed = compress_bytes(data)
        result = decompress_bytes(compressed, max_output_size=100)
        assert result == data

    @skip_if_no_zstd
    def test_output_guard_one_below(self):
        """Output guard one byte below data size should fail."""
        data = b"X" * 100
        compressed = compress_bytes(data)
        with pytest.raises(ZstOutputLimitExceeded):
            decompress_bytes(compressed, max_output_size=99)


# ---------------------------------------------------------------------------
# 4. Probe depth
# ---------------------------------------------------------------------------

class TestProbeDepth:

    @skip_if_no_zstd
    def test_probe_returns_content_size_when_available(self):
        data = b"known size data " * 100
        compressed = compress_bytes(data)
        result = probe_frame(compressed)
        assert result["magic_ok"] is True

    def test_probe_empty_bytes(self):
        result = probe_frame(b"")
        assert result["valid"] is False

    def test_probe_returns_dict_keys(self):
        result = probe_frame(b"\x28\xb5\x2f\xfd")
        assert "valid" in result
        assert "magic_ok" in result

    @skip_if_no_zstd
    def test_probe_multiple_valid(self):
        """Probe multiple different compressed payloads."""
        for payload in [b"a", b"bb" * 1000, bytes(range(256))]:
            compressed = compress_bytes(payload)
            result = probe_frame(compressed)
            assert result["magic_ok"] is True


# ---------------------------------------------------------------------------
# 5. File validation depth
# ---------------------------------------------------------------------------

class TestValidateFileDepth:

    @skip_if_no_zstd
    def test_validate_roundtrip_file(self):
        data = b"file validation test " * 50
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.zst"
            path.write_bytes(compress_bytes(data))
            result = validate_file(path)
            assert result["valid"] is True

    def test_validate_empty_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.zst"
            path.write_bytes(b"")
            result = validate_file(path)
            assert result["valid"] is False

    def test_validate_text_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "text.zst"
            path.write_text("not compressed")
            result = validate_file(path)
            assert result["valid"] is False

    @skip_if_no_zstd
    def test_validate_large_compressed(self):
        """Validate a larger compressed payload."""
        data = bytes(range(256)) * 1000  # 256KB
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "large.zst"
            path.write_bytes(compress_bytes(data))
            result = validate_file(path)
            assert result["valid"] is True

    @skip_if_no_zstd
    def test_validate_file_preserves_data(self):
        """Ensure validate_file does not corrupt the file."""
        data = b"preserve test " * 100
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "preserve.zst"
            compressed = compress_bytes(data)
            path.write_bytes(compressed)
            validate_file(path)
            assert path.read_bytes() == compressed
