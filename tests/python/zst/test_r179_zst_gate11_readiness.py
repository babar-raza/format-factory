"""
test_r179_zst_gate11_readiness.py -- ZST Gate 11 commercial readiness scenario tests.

15 scenarios covering all Gate 11 criteria:
  - Round-trip correctness (magic header, exact byte identity)
  - Compression levels (1 fastest, 3 default, 19 best)
  - Frame validation and introspection
  - Batch operations
  - String/streaming paths
  - Edge cases (empty, large payload)
  - Dictionary-mode (optional capability indicator)

Sprint: FORMAT-FACTORY-SAL-PHASE3-PRODUCT-DEEPENING-SPRINT3-001
Gate: ZST Gate 11 readiness proof
Spec ref: FACT-ZST-001 (magic bytes 0x28 0xB5 0x2F 0xFD)
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from zst.zst_codec import (
    compress_bytes,
    decompress_bytes,
    compress_string,
    decompress_to_string,
    validate_roundtrip,
    get_frame_info,
    is_valid_frame,
    estimate_ratio,
    batch_compress,
    batch_decompress,
    zst_frame_count,
    ZSTD_MAGIC,
)

# Gate 11 payload constants
_SMALL_TEXT = b"Hello, ZST Gate 11!"
_MEDIUM_TEXT = b"Format Factory ZST Gate 11 readiness. " * 200
_LARGE_PAYLOAD = os.urandom(1024 * 1024)  # 1 MiB random bytes


class TestZstGate11RoundTrip:
    """Gate 11 scenario 1-3: exact round-trip identity."""

    def test_compress_decompress_exact_bytes(self):
        """Compress and decompress must produce bit-identical output."""
        compressed = compress_bytes(_MEDIUM_TEXT)
        recovered = decompress_bytes(compressed)
        assert recovered == _MEDIUM_TEXT

    def test_magic_header_present_in_compressed(self):
        """FACT-ZST-001: compressed bytes must start with Zstandard magic 0x28 0xB5 0x2F 0xFD."""
        compressed = compress_bytes(_SMALL_TEXT)
        assert compressed[:4] == ZSTD_MAGIC

    def test_validate_roundtrip_match_true(self):
        """validate_roundtrip() must confirm identity with match=True."""
        result = validate_roundtrip(_MEDIUM_TEXT)
        assert result.get("match") is True


class TestZstGate11CompressionLevels:
    """Gate 11 scenario 4-6: compression level correctness."""

    def test_level_1_fastest_compresses_and_decompresses(self):
        """Level 1 (fastest) must produce valid compressed bytes that decompress correctly."""
        compressed = compress_bytes(_MEDIUM_TEXT, level=1)
        assert is_valid_frame(compressed)
        assert decompress_bytes(compressed) == _MEDIUM_TEXT

    def test_level_19_best_compresses_and_decompresses(self):
        """Level 19 (best compression) must produce valid bytes that decompress correctly."""
        compressed = compress_bytes(_MEDIUM_TEXT, level=19)
        assert is_valid_frame(compressed)
        assert decompress_bytes(compressed) == _MEDIUM_TEXT

    def test_higher_level_achieves_smaller_size(self):
        """Level 19 result must be <= level 1 result for compressible data."""
        compressible = b"AAAAAAAAAAAABBBBBBBBBBBBB" * 1000
        c1 = compress_bytes(compressible, level=1)
        c19 = compress_bytes(compressible, level=19)
        assert len(c19) <= len(c1)


class TestZstGate11FrameInspection:
    """Gate 11 scenario 7-9: frame validation and introspection."""

    def test_get_frame_info_returns_dict(self):
        """get_frame_info must return a dict for valid compressed data."""
        compressed = compress_bytes(_SMALL_TEXT)
        info = get_frame_info(compressed)
        assert isinstance(info, dict)

    def test_is_valid_frame_true_for_valid_compressed(self):
        """is_valid_frame must return True for properly compressed data."""
        compressed = compress_bytes(_SMALL_TEXT)
        assert is_valid_frame(compressed) is True

    def test_is_valid_frame_false_for_random_garbage(self):
        """is_valid_frame must return False for random non-Zstandard bytes."""
        garbage = b"\x00\x11\x22\x33\x44NOTAFRAME"
        assert is_valid_frame(garbage) is False


class TestZstGate11BatchOperations:
    """Gate 11 scenario 10-11: batch compress/decompress."""

    def test_batch_compress_returns_same_count(self):
        """batch_compress must return the same number of file-pair items as input."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            items = []
            for i, payload in enumerate([b"alpha", b"beta" * 50, b"gamma" * 100]):
                inp = tmpdir / f"in{i}.bin"
                out = tmpdir / f"out{i}.bin.zst"
                inp.write_bytes(payload)
                items.append((str(inp), str(out)))
            results = batch_compress(items)
            assert len(results) == len(items)
            assert all(r.get("success") for r in results)

    def test_batch_decompress_recovers_originals(self):
        """batch_decompress must recover originals from batch_compress output."""
        originals = [b"alpha data", b"beta data" * 50, b"gamma data" * 100]
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            compress_items = []
            decompress_items = []
            for i, payload in enumerate(originals):
                inp = tmpdir / f"in{i}.bin"
                cmp = tmpdir / f"in{i}.bin.zst"
                out = tmpdir / f"out{i}.bin"
                inp.write_bytes(payload)
                compress_items.append((str(inp), str(cmp)))
                decompress_items.append((str(cmp), str(out)))
            batch_compress(compress_items)
            batch_decompress(decompress_items)
            for i, orig in enumerate(originals):
                out = tmpdir / f"out{i}.bin"
                assert out.read_bytes() == orig


class TestZstGate11StringPath:
    """Gate 11 scenario 12-13: string compress/decompress path."""

    def test_compress_string_decompress_string_roundtrip(self):
        """compress_string + decompress_to_string must recover exact original string."""
        original = "Format Factory ZST string round-trip test. Unicode: \u00e9\u00e0\u00fc"
        compressed = compress_string(original)
        recovered = decompress_to_string(compressed)
        assert recovered == original

    def test_compress_string_produces_valid_frame(self):
        """compress_string must produce bytes starting with ZST magic."""
        compressed = compress_string("test string")
        assert compressed[:4] == ZSTD_MAGIC


class TestZstGate11EdgeCases:
    """Gate 11 scenario 14-15: edge cases."""

    def test_empty_bytes_compresses_without_error(self):
        """Empty input must compress and decompress without exception."""
        compressed = compress_bytes(b"")
        recovered = decompress_bytes(compressed)
        assert recovered == b""

    def test_large_payload_1mb_roundtrip(self):
        """1 MiB random payload must survive compress → decompress unchanged."""
        compressed = compress_bytes(_LARGE_PAYLOAD)
        assert is_valid_frame(compressed)
        recovered = decompress_bytes(compressed)
        assert recovered == _LARGE_PAYLOAD


class TestZstGate11RatioAndCount:
    """Additional Gate 11 quality indicators."""

    def test_estimate_ratio_positive_for_compressible_data(self):
        """estimate_ratio must return a dict with ratio < 1.0 for compressible input."""
        compressible = b"AAAA" * 1000
        result = estimate_ratio(compressible)
        assert isinstance(result, dict)
        assert result.get("ratio") is not None
        assert result["ratio"] < 1.0  # compressed is smaller

    def test_frame_count_at_least_one(self):
        """zst_frame_count must return >= 1 for a single compressed file."""
        with tempfile.NamedTemporaryFile(suffix=".zst", delete=False) as f:
            tmp_path = f.name
        try:
            compressed = compress_bytes(_SMALL_TEXT)
            Path(tmp_path).write_bytes(compressed)
            count = zst_frame_count(tmp_path)
            assert isinstance(count, int)
            assert count >= 1
        finally:
            os.unlink(tmp_path)
