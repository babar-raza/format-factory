# R101 Train E: ZST installed package smoke tests
# Governed skill: /add-roundtrip-test
# Ledger: R101-GOVERNED-PYTHON-ZST-INSTALLED-SMOKE-001
# Gap: GAP-ZST-INSTALLED-SMOKE-001

import tempfile
from pathlib import Path

import pytest

from zst.zst_codec import (
    compress_bytes,
    decompress_bytes,
    validate_file,
    probe_frame,
    ZSTD_MAGIC,
)


def test_compress_decompress_basic():
    """Basic compress/decompress roundtrip."""
    data = b"ZST installed smoke test data" * 20
    compressed = compress_bytes(data)
    assert len(compressed) < len(data)
    result = decompress_bytes(compressed)
    assert result == data


def test_compress_decompress_empty():
    """Empty data roundtrip."""
    compressed = compress_bytes(b"")
    result = decompress_bytes(compressed)
    assert result == b""


def test_validate_compressed_output():
    """Compressed output starts with magic bytes."""
    data = b"validate magic test"
    compressed = compress_bytes(data)
    assert compressed[:4] == ZSTD_MAGIC


def test_probe_frame_compressed():
    """probe_frame on compressed data returns magic_ok."""
    data = b"probe frame installed test" * 10
    compressed = compress_bytes(data)
    probe = probe_frame(compressed)
    assert probe["magic_ok"] is True


def test_file_write_validate_decompress():
    """Full workflow: compress → write file → validate → read → decompress."""
    original = b"full workflow installed smoke test" * 50
    compressed = compress_bytes(original)
    with tempfile.NamedTemporaryFile(suffix=".zst", delete=False) as f:
        f.write(compressed)
        tmp_path = f.name
    try:
        result = validate_file(tmp_path)
        assert result["valid"] is True
        data = Path(tmp_path).read_bytes()
        assert decompress_bytes(data) == original
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_multiple_levels_produce_valid_output():
    """Various compression levels all produce valid decompressible output."""
    original = b"level variation test data" * 30
    for level in (1, 3, 9, 19):
        compressed = compress_bytes(original, level=level)
        assert decompress_bytes(compressed) == original


def test_large_payload_roundtrip():
    """Larger payload (100KB) roundtrips correctly."""
    original = bytes(range(256)) * 400  # 102400 bytes
    compressed = compress_bytes(original)
    assert len(compressed) < len(original)
    assert decompress_bytes(compressed) == original


def test_validate_file_rejects_garbage():
    """validate_file rejects non-ZST file."""
    with tempfile.NamedTemporaryFile(suffix=".zst", delete=False) as f:
        f.write(b"this is not zstandard data")
        tmp_path = f.name
    try:
        result = validate_file(tmp_path)
        assert result["valid"] is False
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_probe_frame_rejects_garbage():
    """probe_frame on non-ZST data returns magic_ok=False."""
    probe = probe_frame(b"not zstandard at all")
    assert probe["magic_ok"] is False


def test_decompress_invalid_raises():
    """Decompressing invalid data raises an error."""
    with pytest.raises(Exception):
        decompress_bytes(b"not valid zstd compressed data")
