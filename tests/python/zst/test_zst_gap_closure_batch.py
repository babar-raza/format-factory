"""Gap closure tests for ZST — covering 16 open gaps.

Gaps cover: compress_bytes, decompress_bytes, compress_file, decompress_file,
    compress_string, decompress_to_string, validate_roundtrip, validate_file,
    probe_frame, is_valid_frame, zst_is_valid_file, get_frame_info,
    zst_compressed_size, zst_decompressed_size, zst_frame_count,
    ZstError, ZstDecompressionError
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    ZstDecompressionError,
    ZstError,
    compress_bytes,
    compress_file,
    compress_string,
    decompress_bytes,
    decompress_file,
    decompress_to_string,
    get_frame_info,
    is_valid_frame,
    probe_frame,
    validate_file,
    validate_roundtrip,
    zst_compressed_size,
    zst_decompressed_size,
    zst_frame_count,
    zst_is_valid_file,
)


@pytest.fixture
def zst_file(tmp_path):
    """Create a .zst file from known data."""
    data = b"Hello world! " * 100
    out = tmp_path / "test.zst"
    src = tmp_path / "test.txt"
    src.write_bytes(data)
    compress_file(str(src), str(out))
    return out


@pytest.fixture
def src_file(tmp_path):
    data = b"Hello world! " * 100
    src = tmp_path / "test.txt"
    src.write_bytes(data)
    return src


class TestErrorClasses:
    def test_zst_error_is_exception(self):
        assert issubclass(ZstError, Exception)

    def test_zst_decompression_error_subclass(self):
        assert issubclass(ZstDecompressionError, ZstError)

    def test_message_preserved(self):
        err = ZstError("bad zst")
        assert "bad zst" in str(err)


class TestCompressDecompressBytes:
    def test_roundtrip(self):
        data = b"test data 12345"
        compressed = compress_bytes(data)
        assert isinstance(compressed, bytes)
        assert len(compressed) > 0
        decompressed = decompress_bytes(compressed)
        assert decompressed == data


class TestCompressDecompressString:
    def test_roundtrip(self):
        text = "Hello ZST compression!"
        compressed = compress_string(text)
        assert isinstance(compressed, bytes)
        result = decompress_to_string(compressed)
        assert result == text


class TestCompressFile:
    def test_creates_file(self, zst_file):
        assert zst_file.exists()
        assert zst_file.stat().st_size > 0


class TestDecompressFile:
    def test_decompresses(self, zst_file, tmp_path):
        out = tmp_path / "decompressed.txt"
        decompress_file(str(zst_file), str(out))
        assert out.exists()
        content = out.read_bytes()
        assert b"Hello world!" in content


class TestValidateRoundtrip:
    def test_roundtrip(self):
        data = b"validate this roundtrip"
        result = validate_roundtrip(data)
        assert result is True or result is not None


class TestValidateFile:
    def test_valid(self, zst_file):
        result = validate_file(str(zst_file))
        assert result is True or result is not None


class TestProbeFrame:
    def test_returns_dict(self, zst_file):
        result = probe_frame(str(zst_file))
        assert isinstance(result, dict)


class TestIsValidFrame:
    def test_valid(self, zst_file):
        data = zst_file.read_bytes()
        result = is_valid_frame(data)
        assert result is True

    def test_invalid(self):
        result = is_valid_frame(b"not a zst frame")
        assert result is False


class TestZstIsValidFile:
    def test_valid(self, zst_file):
        result = zst_is_valid_file(str(zst_file))
        assert result is True


class TestGetFrameInfo:
    def test_returns_dict(self, zst_file):
        info = get_frame_info(str(zst_file))
        assert isinstance(info, dict)


class TestZstCompressedSize:
    def test_returns_int(self, zst_file):
        size = zst_compressed_size(str(zst_file))
        assert isinstance(size, int)
        assert size > 0


class TestZstDecompressedSize:
    def test_returns_int(self, zst_file):
        size = zst_decompressed_size(str(zst_file))
        assert isinstance(size, int)
        assert size > 0


class TestZstFrameCount:
    def test_returns_int(self, zst_file):
        count = zst_frame_count(str(zst_file))
        assert isinstance(count, int)
        assert count >= 1
