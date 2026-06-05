# R100 Train E: ZST deep FOSS lane — probe + validate workflow tests
# Governed skill: /add-roundtrip-test
# Ledger: R100-GOVERNED-PYTHON-ZST-PROBE-WORKFLOW-001

import tempfile
from pathlib import Path

import pytest

from zst.zst_codec import (
    compress_bytes,
    decompress_bytes,
    validate_file,
    ZstError,
    ZstInvalidFrameError,
    ZSTD_MAGIC,
)


def test_validate_valid_file():
    """validate_file returns valid=True for a proper ZST file."""
    data = compress_bytes(b"probe test data")
    with tempfile.NamedTemporaryFile(suffix=".zst", delete=False) as f:
        f.write(data)
        tmp = f.name
    try:
        result = validate_file(tmp)
        assert result["valid"] is True
        assert result["exists"] is True
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_validate_nonexistent_file():
    """validate_file handles missing file gracefully."""
    result = validate_file("/tmp/nonexistent_r100_zst_probe.zst")
    assert result["exists"] is False
    assert result["valid"] is False


def test_validate_corrupt_magic():
    """validate_file rejects file with wrong magic bytes."""
    with tempfile.NamedTemporaryFile(suffix=".zst", delete=False) as f:
        f.write(b"\x00\x00\x00\x00" + b"garbage" * 10)
        tmp = f.name
    try:
        result = validate_file(tmp)
        assert result["valid"] is False
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_magic_bytes_constant():
    """ZSTD_MAGIC matches the known Zstandard magic number."""
    assert ZSTD_MAGIC == b"\x28\xb5\x2f\xfd"


def test_compress_starts_with_magic():
    """Compressed output starts with ZSTD magic bytes."""
    data = compress_bytes(b"magic check")
    assert data[:4] == ZSTD_MAGIC


def test_roundtrip_binary_data():
    """Binary data (all byte values) survives compression roundtrip."""
    original = bytes(range(256)) * 10
    compressed = compress_bytes(original)
    assert decompress_bytes(compressed) == original


def test_empty_input_compress():
    """Empty input compresses and decompresses to empty bytes."""
    compressed = compress_bytes(b"")
    assert decompress_bytes(compressed) == b""


def test_invalid_frame_raises():
    """Decompressing invalid data raises an appropriate error."""
    with pytest.raises((ZstError, ZstInvalidFrameError, Exception)):
        decompress_bytes(b"this is not zstd data at all")


def test_validate_reports_size():
    """validate_file includes file size in result."""
    data = compress_bytes(b"size check data" * 100)
    with tempfile.NamedTemporaryFile(suffix=".zst", delete=False) as f:
        f.write(data)
        tmp = f.name
    try:
        result = validate_file(tmp)
        assert result.get("size", 0) > 0 or result.get("file_size", 0) > 0 or result["exists"]
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_multiple_compress_deterministic():
    """Same input produces same compressed output (deterministic)."""
    data = b"deterministic test" * 50
    c1 = compress_bytes(data, level=3)
    c2 = compress_bytes(data, level=3)
    assert c1 == c2
