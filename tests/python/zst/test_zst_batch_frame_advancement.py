"""
test_zst_batch_frame_advancement.py -- ZST batch operations and frame info tests.

Sprint: REWORK-MEGATRAIN-FINAL-001
Added: 2026-06-10

Tests batch_compress, batch_decompress, get_frame_info, estimate_ratio,
validate_file, validate_roundtrip, and probe_frame.
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
    reason="zstandard not installed",
)

if ZSTD_AVAILABLE:
    from zst.zst_codec import (
        compress_bytes,
        decompress_bytes,
        compress_file,
        decompress_file,
        probe_frame,
        get_frame_info,
        estimate_ratio,
        validate_file,
        validate_roundtrip,
        batch_compress,
        batch_decompress,
    )


@skip_if_no_zstd
def test_compress_decompress_roundtrip():
    """Basic compress -> decompress roundtrip."""
    data = b"Hello Format Factory! " * 100
    compressed = compress_bytes(data)
    assert len(compressed) < len(data)
    restored = decompress_bytes(compressed)
    assert restored == data


@skip_if_no_zstd
def test_probe_frame_magic():
    """probe_frame detects valid Zstandard frame."""
    data = b"probe test data " * 50
    compressed = compress_bytes(data)
    info = probe_frame(compressed)
    assert info is not None
    assert isinstance(info, dict)


@skip_if_no_zstd
def test_get_frame_info():
    """get_frame_info returns detailed frame metadata."""
    data = b"frame info test " * 100
    compressed = compress_bytes(data)
    info = get_frame_info(compressed)
    assert isinstance(info, dict)


@skip_if_no_zstd
def test_estimate_ratio():
    """estimate_ratio returns a compression ratio."""
    data = b"AAAA" * 1000  # highly compressible
    result = estimate_ratio(data)
    assert isinstance(result, dict)
    assert result.get("ratio", 0) > 1.0 or result.get("compressed_size", 0) < len(data)


@skip_if_no_zstd
def test_validate_roundtrip_passes():
    """validate_roundtrip confirms data integrity."""
    data = b"roundtrip validation " * 50
    result = validate_roundtrip(data)
    assert result is True or (isinstance(result, dict) and result.get("valid", True))


@skip_if_no_zstd
def test_compress_file_roundtrip():
    """compress_file + decompress_file roundtrip."""
    data = b"file roundtrip content " * 100
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "input.bin"
        src.write_bytes(data)
        zst = Path(tmp) / "output.zst"
        compress_file(src, zst)
        assert zst.exists()
        assert zst.stat().st_size > 0
        out = Path(tmp) / "restored.bin"
        decompress_file(zst, out)
        assert out.read_bytes() == data


@skip_if_no_zstd
def test_validate_file():
    """validate_file confirms a .zst file is valid."""
    data = b"validate file test " * 50
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "data.bin"
        src.write_bytes(data)
        zst = Path(tmp) / "data.zst"
        compress_file(src, zst)
        result = validate_file(zst)
        assert result is True or (isinstance(result, dict) and result.get("valid", True))


@skip_if_no_zstd
def test_batch_compress():
    """batch_compress compresses multiple files."""
    with tempfile.TemporaryDirectory() as tmp:
        items = []
        for i in range(3):
            src = Path(tmp) / f"file{i}.txt"
            src.write_bytes(f"content {i} ".encode() * 50)
            dst = Path(tmp) / f"file{i}.txt.zst"
            items.append((src, dst))
        results = batch_compress(items)
        assert len(results) == 3


@skip_if_no_zstd
def test_batch_decompress():
    """batch_decompress decompresses multiple .zst files."""
    with tempfile.TemporaryDirectory() as tmp:
        # First compress
        compress_items = []
        for i in range(3):
            src = Path(tmp) / f"src{i}.bin"
            src.write_bytes(f"batch {i} ".encode() * 50)
            zst = Path(tmp) / f"src{i}.bin.zst"
            compress_items.append((src, zst))
        batch_compress(compress_items)
        # Now decompress
        out_dir = Path(tmp) / "out"
        out_dir.mkdir()
        decompress_items = []
        for i in range(3):
            zst = Path(tmp) / f"src{i}.bin.zst"
            out = out_dir / f"src{i}.bin"
            decompress_items.append((zst, out))
        results = batch_decompress(decompress_items)
        assert len(results) == 3


@skip_if_no_zstd
def test_empty_input_compress():
    """Compressing empty bytes produces valid output."""
    compressed = compress_bytes(b"")
    assert len(compressed) > 0
    restored = decompress_bytes(compressed)
    assert restored == b""
