"""
Tests for src/python/zst/zst_codec.py

FOSS track. Requires python-zstandard.
Skips gracefully if zstandard is not installed.

Run from repo root:
    PYTHONPATH=C:/Users/prora/AppData/Roaming/Python/Python313/site-packages \
        python -m pytest tests/python/zst/ -v
"""

import sys
import os
import tempfile
from pathlib import Path

import pytest

# Add src/python to path
REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

try:
    import zstandard  # noqa: F401
    ZSTD_AVAILABLE = True
except ImportError:
    ZSTD_AVAILABLE = False

skip_if_no_zstd = pytest.mark.skipif(
    not ZSTD_AVAILABLE,
    reason="zstandard not installed — install with: pip install zstandard"
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
# Constants / helpers
# ---------------------------------------------------------------------------

SAMPLE_TEXT = b"Hello, Zstandard! " * 100  # 1800 bytes, compresses well


@skip_if_no_zstd
def _make_zst(data: bytes = SAMPLE_TEXT, level: int = 3) -> bytes:
    """Helper: compress data and return ZST bytes."""
    return compress_bytes(data, level=level)


# ---------------------------------------------------------------------------
# 1. compress_bytes
# ---------------------------------------------------------------------------

@skip_if_no_zstd
def test_compress_bytes_returns_zstd_frame():
    """compress_bytes output starts with Zstandard magic."""
    compressed = compress_bytes(SAMPLE_TEXT)
    assert compressed[:4] == ZSTD_MAGIC


@skip_if_no_zstd
def test_compress_bytes_smaller_than_input():
    """Compression should reduce size for repetitive data."""
    compressed = compress_bytes(SAMPLE_TEXT)
    assert len(compressed) < len(SAMPLE_TEXT)


@skip_if_no_zstd
def test_compress_bytes_all_levels():
    """All valid compression levels produce valid Zstd frames."""
    for level in [1, 3, 9, 22]:
        result = compress_bytes(b"test data " * 50, level=level)
        assert result[:4] == ZSTD_MAGIC, f"Level {level} failed"


def test_compress_bytes_invalid_input_type():
    """compress_bytes raises ZstError for non-bytes input."""
    with pytest.raises(ZstError):
        compress_bytes("not bytes")  # type: ignore[arg-type]


@skip_if_no_zstd
def test_compress_bytes_invalid_level():
    """compress_bytes raises ZstError for out-of-range level."""
    with pytest.raises(ZstError):
        compress_bytes(b"test", level=0)
    with pytest.raises(ZstError):
        compress_bytes(b"test", level=23)


# ---------------------------------------------------------------------------
# 2. decompress_bytes — round-trip
# ---------------------------------------------------------------------------

@skip_if_no_zstd
def test_roundtrip_basic():
    """compress then decompress returns original data."""
    compressed = compress_bytes(SAMPLE_TEXT)
    recovered = decompress_bytes(compressed)
    assert recovered == SAMPLE_TEXT


@skip_if_no_zstd
def test_roundtrip_empty_bytes():
    """Empty bytes compresses and decompresses correctly."""
    compressed = compress_bytes(b"")
    recovered = decompress_bytes(compressed)
    assert recovered == b""


@skip_if_no_zstd
def test_roundtrip_binary_data():
    """Binary data (bytes 0-255) round-trips correctly."""
    data = bytes(range(256)) * 100
    compressed = compress_bytes(data)
    recovered = decompress_bytes(compressed)
    assert recovered == data


# ---------------------------------------------------------------------------
# 3. decompress_bytes — invalid input
# ---------------------------------------------------------------------------

def test_decompress_wrong_magic():
    """decompress_bytes raises ZstInvalidFrameError for wrong magic."""
    with pytest.raises(ZstInvalidFrameError):
        decompress_bytes(b"\x00\x00\x00\x00" + b"garbage data")


def test_decompress_truncated_magic():
    """decompress_bytes raises ZstInvalidFrameError for too-short input."""
    with pytest.raises(ZstInvalidFrameError):
        decompress_bytes(b"\x28\xb5")  # magic truncated


def test_decompress_non_bytes_input():
    """decompress_bytes raises ZstError for non-bytes input."""
    with pytest.raises(ZstError):
        decompress_bytes("string input")  # type: ignore[arg-type]


@skip_if_no_zstd
def test_decompress_truncated_frame():
    """decompress_bytes raises ZstDecompressionError for a truncated frame.

    Uses a manually constructed truncated frame: valid magic + header bytes
    but body is cut off. The 'claimed-large-truncated.zst' sample demonstrates
    this pattern — valid magic, declared content_size, no actual block data.
    """
    invalid_dir = REPO_ROOT / "samples" / "by-format" / "zst" / "invalid" / "generated"
    truncated_path = invalid_dir / "claimed-large-truncated.zst"
    if not truncated_path.exists():
        pytest.skip("claimed-large-truncated.zst not found")
    truncated = truncated_path.read_bytes()
    with pytest.raises((ZstDecompressionError, ZstInvalidFrameError)):
        decompress_bytes(truncated)


# ---------------------------------------------------------------------------
# 4. Output size guard
# ---------------------------------------------------------------------------

@skip_if_no_zstd
def test_output_guard_triggers():
    """decompress_bytes raises ZstOutputLimitExceeded when output exceeds limit."""
    data = b"A" * 10000
    compressed = compress_bytes(data)
    with pytest.raises(ZstOutputLimitExceeded):
        decompress_bytes(compressed, max_output_size=100)


@skip_if_no_zstd
def test_output_guard_passes_within_limit():
    """decompress_bytes succeeds when output is within limit."""
    data = b"small data"
    compressed = compress_bytes(data)
    recovered = decompress_bytes(compressed, max_output_size=100)
    assert recovered == data


@skip_if_no_zstd
def test_output_guard_disabled():
    """decompress_bytes with max_output_size=0 disables the guard."""
    data = b"A" * 1000
    compressed = compress_bytes(data)
    recovered = decompress_bytes(compressed, max_output_size=0)
    assert recovered == data


# ---------------------------------------------------------------------------
# 5. probe_frame
# ---------------------------------------------------------------------------

@skip_if_no_zstd
def test_probe_valid_frame():
    """probe_frame returns magic_ok=True for a valid Zstd frame."""
    compressed = compress_bytes(SAMPLE_TEXT)
    result = probe_frame(compressed)
    assert result["magic_ok"] is True
    assert result["error"] is None or "unavailable" in result.get("error", "")


def test_probe_wrong_magic():
    """probe_frame returns magic_ok=False for wrong magic."""
    result = probe_frame(b"\x00\x01\x02\x03" + b"garbage")
    assert result["magic_ok"] is False
    assert result["valid"] is False
    assert result["error"] is not None


def test_probe_too_short():
    """probe_frame returns error for input shorter than 4 bytes."""
    result = probe_frame(b"\x28\xb5")
    assert result["valid"] is False
    assert result["error"] is not None


def test_probe_non_bytes():
    """probe_frame returns error for non-bytes input."""
    result = probe_frame("not bytes")  # type: ignore[arg-type]
    assert result["valid"] is False
    assert result["error"] is not None


def test_probe_never_raises():
    """probe_frame must never raise — always returns dict."""
    for bad_input in [b"", b"\x00", b"\x28\xb5\x2f\xfd", b"x" * 3, None, 42]:
        try:
            result = probe_frame(bad_input)  # type: ignore[arg-type]
            assert isinstance(result, dict)
            assert "valid" in result
        except Exception as exc:
            pytest.fail(f"probe_frame raised {type(exc).__name__} for {bad_input!r}: {exc}")


# ---------------------------------------------------------------------------
# 6. validate_file
# ---------------------------------------------------------------------------

@skip_if_no_zstd
def test_validate_file_valid():
    """validate_file returns valid=True for a valid .zst file."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "test.zst"
        path.write_bytes(compress_bytes(SAMPLE_TEXT))
        result = validate_file(path)
        assert result["exists"] is True
        assert result["valid"] is True
        assert result["error"] is None


def test_validate_file_not_found():
    """validate_file returns valid=False for non-existent file."""
    result = validate_file("/nonexistent/path/test.zst")
    assert result["exists"] is False
    assert result["valid"] is False
    assert result["error"] is not None


@skip_if_no_zstd
def test_validate_file_wrong_magic():
    """validate_file returns valid=False for file with wrong magic."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bad.zst"
        path.write_bytes(b"\x00\x00\x00\x00" + b"garbage")
        result = validate_file(path)
        assert result["valid"] is False
        assert result["error"] is not None


@skip_if_no_zstd
def test_validate_corpus_valid_samples():
    """validate_file passes for all valid ZST corpus samples."""
    corpus_dir = REPO_ROOT / "samples" / "by-format" / "zst" / "valid"
    if not corpus_dir.exists():
        pytest.skip(f"Corpus directory not found: {corpus_dir}")

    zst_files = list(corpus_dir.glob("*.zst"))
    if not zst_files:
        pytest.skip("No .zst files in corpus")

    for zst_path in zst_files:
        result = validate_file(zst_path)
        assert result["valid"] is True, (
            f"Corpus sample {zst_path.name} failed validation: {result['error']}"
        )


@skip_if_no_zstd
def test_validate_corpus_invalid_samples():
    """validate_file returns valid=False for all invalid ZST corpus samples."""
    invalid_dir = REPO_ROOT / "samples" / "by-format" / "zst" / "invalid" / "generated"
    if not invalid_dir.exists():
        pytest.skip(f"Invalid corpus directory not found: {invalid_dir}")

    zst_files = list(invalid_dir.glob("*.zst"))
    if not zst_files:
        pytest.skip("No .zst files in invalid corpus")

    for zst_path in zst_files:
        result = validate_file(zst_path)
        # All invalid samples should fail validation
        assert result["valid"] is False, (
            f"Invalid sample {zst_path.name} unexpectedly passed validation"
        )
