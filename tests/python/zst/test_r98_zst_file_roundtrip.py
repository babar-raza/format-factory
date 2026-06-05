# R98 Train O: ZST file-level roundtrip tests
# Governed skill: /add-roundtrip-test
# Ledger: R98-GOVERNED-PYTHON-ZST-FILE-ROUNDTRIP-001
# Priority: 3 (load/edit/save/export completeness)

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


def test_file_roundtrip_write_validate():
    """Compress bytes, write to file, validate_file returns valid."""
    original = b"format factory zst file roundtrip test data" * 50
    compressed = compress_bytes(original)
    with tempfile.NamedTemporaryFile(suffix=".zst", delete=False) as f:
        f.write(compressed)
        tmp_path = f.name
    try:
        result = validate_file(tmp_path)
        assert result["valid"] is True
        assert result["exists"] is True
        assert result["size_bytes"] == len(compressed)
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_file_roundtrip_write_read_decompress():
    """Write compressed file, read it back, decompress matches original."""
    original = b"roundtrip file test " * 100
    compressed = compress_bytes(original)
    with tempfile.NamedTemporaryFile(suffix=".zst", delete=False) as f:
        f.write(compressed)
        tmp_path = f.name
    try:
        data = Path(tmp_path).read_bytes()
        result = decompress_bytes(data)
        assert result == original
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_file_roundtrip_binary_payload():
    """Binary payload survives file write/read cycle."""
    original = bytes(range(256)) * 40
    compressed = compress_bytes(original, level=9)
    with tempfile.NamedTemporaryFile(suffix=".zst", delete=False) as f:
        f.write(compressed)
        tmp_path = f.name
    try:
        data = Path(tmp_path).read_bytes()
        assert data[:4] == ZSTD_MAGIC
        result = decompress_bytes(data)
        assert result == original
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_file_roundtrip_empty_payload():
    """Empty payload compressed file validates and decompresses."""
    original = b""
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


def test_validate_file_nonexistent():
    """validate_file returns valid=False for nonexistent file."""
    result = validate_file("/nonexistent/path/to/test.zst")
    assert result["valid"] is False
    assert result["exists"] is False


def test_validate_file_invalid_magic():
    """validate_file rejects file without Zstandard magic."""
    with tempfile.NamedTemporaryFile(suffix=".zst", delete=False) as f:
        f.write(b"not a zst file at all")
        tmp_path = f.name
    try:
        result = validate_file(tmp_path)
        assert result["valid"] is False
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_probe_frame_on_file_data():
    """probe_frame on file data returns magic_ok and valid."""
    original = b"probe test data for file roundtrip"
    compressed = compress_bytes(original)
    with tempfile.NamedTemporaryFile(suffix=".zst", delete=False) as f:
        f.write(compressed)
        tmp_path = f.name
    try:
        data = Path(tmp_path).read_bytes()
        probe = probe_frame(data)
        assert probe["magic_ok"] is True
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_file_roundtrip_multiple_levels():
    """Different compression levels all produce valid files."""
    original = b"level test for file roundtrip " * 30
    for level in (1, 5, 15, 22):
        compressed = compress_bytes(original, level=level)
        with tempfile.NamedTemporaryFile(suffix=".zst", delete=False) as f:
            f.write(compressed)
            tmp_path = f.name
        try:
            result = validate_file(tmp_path)
            assert result["valid"] is True, f"Level {level} produced invalid file"
            data = Path(tmp_path).read_bytes()
            assert decompress_bytes(data) == original
        finally:
            Path(tmp_path).unlink(missing_ok=True)
