# R104 Wave 2: ZST output guard and decompression edge cases
# Lane D — ZST FOSS hardening
# Ledger: R104-FOSS-ZST-GUARD-LIMITS-001

import pytest
from zst.zst_codec import (
    compress_bytes,
    decompress_bytes,
    probe_frame,
    validate_file,
    ZstError,
    ZstInvalidFrameError,
    ZstDecompressionError,
    ZstOutputLimitExceeded,
    DEFAULT_MAX_OUTPUT_BYTES,
)


class TestOutputGuard:
    """Verify max_output_size guard behavior."""

    def test_small_limit_triggers_on_large_data(self):
        data = b"X" * 10000
        compressed = compress_bytes(data)
        with pytest.raises(ZstOutputLimitExceeded):
            decompress_bytes(compressed, max_output_size=100)

    def test_exact_limit_passes(self):
        data = b"Y" * 500
        compressed = compress_bytes(data)
        result = decompress_bytes(compressed, max_output_size=500)
        assert result == data

    def test_limit_zero_disables_guard(self):
        data = b"Z" * 5000
        compressed = compress_bytes(data)
        result = decompress_bytes(compressed, max_output_size=0)
        assert result == data

    def test_default_limit_is_256mib(self):
        assert DEFAULT_MAX_OUTPUT_BYTES == 256 * 1024 * 1024

    def test_none_limit_uses_default(self):
        data = b"A" * 100
        compressed = compress_bytes(data)
        result = decompress_bytes(compressed, max_output_size=None)
        assert result == data


class TestInvalidInput:
    """Verify error handling for invalid decompression input."""

    def test_empty_bytes_raises(self):
        with pytest.raises(ZstInvalidFrameError):
            decompress_bytes(b"")

    def test_wrong_magic_raises(self):
        with pytest.raises(ZstInvalidFrameError, match="magic"):
            decompress_bytes(b"\x00\x00\x00\x00" + b"\x00" * 100)

    def test_truncated_frame_raises(self):
        data = b"Hello World"
        compressed = compress_bytes(data)
        truncated = compressed[:8]
        with pytest.raises((ZstDecompressionError, ZstInvalidFrameError)):
            decompress_bytes(truncated)

    def test_non_bytes_raises(self):
        with pytest.raises(ZstError, match="bytes"):
            decompress_bytes("not bytes")  # type: ignore

    def test_compress_non_bytes_raises(self):
        with pytest.raises(ZstError, match="bytes"):
            compress_bytes("not bytes")  # type: ignore


class TestProbeFrame:
    """Verify probe_frame metadata extraction."""

    def test_valid_frame(self):
        compressed = compress_bytes(b"test data")
        info = probe_frame(compressed)
        assert info["magic_ok"] is True

    def test_invalid_magic(self):
        info = probe_frame(b"\x00\x01\x02\x03")
        assert info["magic_ok"] is False
        assert info["error"] is not None

    def test_too_short(self):
        info = probe_frame(b"\x28\xb5")
        assert info["valid"] is False
        assert "short" in info["error"].lower()

    def test_non_bytes_input(self):
        info = probe_frame("string")  # type: ignore
        assert info["valid"] is False
        assert info["error"] is not None


class TestValidateFile:
    """Verify validate_file on disk."""

    def test_valid_file(self, tmp_path):
        data = compress_bytes(b"file content test")
        p = tmp_path / "test.zst"
        p.write_bytes(data)
        result = validate_file(str(p))
        assert result["valid"] is True
        assert result["exists"] is True

    def test_nonexistent_file(self, tmp_path):
        result = validate_file(str(tmp_path / "nope.zst"))
        assert result["valid"] is False
        assert result["exists"] is False

    def test_corrupt_file(self, tmp_path):
        p = tmp_path / "bad.zst"
        p.write_bytes(b"not a zst file")
        result = validate_file(str(p))
        assert result["valid"] is False

    def test_file_size_reported(self, tmp_path):
        data = compress_bytes(b"size test")
        p = tmp_path / "sized.zst"
        p.write_bytes(data)
        result = validate_file(str(p))
        assert result["size_bytes"] == len(data)
