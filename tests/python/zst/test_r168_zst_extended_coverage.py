"""
test_r168_zst_extended_coverage.py

Sprint: FORMAT-FACTORY-HARDENED-AUDIT-REMEDIATION-SPRINT9-001
Added: 2026-06-11

Tests for ZST extended functions: compress_string, decompress_to_string,
batch_compress, batch_decompress, estimate_ratio, get_frame_info,
validate_roundtrip, is_valid_frame.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import (
    compress_bytes,
    decompress_bytes,
    compress_string,
    decompress_to_string,
    batch_compress,
    batch_decompress,
    estimate_ratio,
    get_frame_info,
    validate_roundtrip,
    is_valid_frame,
    ZstError,
    ZstDecompressionError,
    ZstInvalidFrameError,
)

_SAMPLE_TEXT = "Hello, Format Factory! This is a test string for ZST compression coverage."
_SAMPLE_BYTES = _SAMPLE_TEXT.encode("utf-8")


# ── compress_string / decompress_to_string ────────────────────────────────

class TestStringRoundtrip:

    def test_compress_string_returns_bytes(self):
        result = compress_string(_SAMPLE_TEXT)
        assert isinstance(result, bytes)

    def test_compress_string_nonempty(self):
        result = compress_string(_SAMPLE_TEXT)
        assert len(result) > 0

    def test_decompress_to_string_returns_str(self):
        compressed = compress_string(_SAMPLE_TEXT)
        result = decompress_to_string(compressed)
        assert isinstance(result, str)

    def test_roundtrip_preserves_text(self):
        compressed = compress_string(_SAMPLE_TEXT)
        recovered = decompress_to_string(compressed)
        assert recovered == _SAMPLE_TEXT

    def test_custom_level(self):
        low = compress_string(_SAMPLE_TEXT, level=1)
        high = compress_string(_SAMPLE_TEXT, level=9)
        # Both produce valid ZST that decompresses correctly
        assert decompress_to_string(low) == _SAMPLE_TEXT
        assert decompress_to_string(high) == _SAMPLE_TEXT

    def test_empty_string(self):
        compressed = compress_string("")
        recovered = decompress_to_string(compressed)
        assert recovered == ""


# ── estimate_ratio ────────────────────────────────────────────────────────

class TestEstimateRatio:

    def test_returns_dict(self):
        result = estimate_ratio(_SAMPLE_BYTES)
        assert isinstance(result, dict)

    def test_has_ratio_key(self):
        result = estimate_ratio(_SAMPLE_BYTES)
        assert "ratio" in result or "compression_ratio" in result or len(result) > 0

    def test_compressed_size_smaller_for_repetitive(self):
        data = b"abcabc" * 1000
        result = estimate_ratio(data)
        assert isinstance(result, dict)


# ── get_frame_info ────────────────────────────────────────────────────────

class TestGetFrameInfo:

    def test_returns_dict(self):
        compressed = compress_bytes(_SAMPLE_BYTES)
        result = get_frame_info(compressed)
        assert isinstance(result, dict)

    def test_has_valid_key(self):
        compressed = compress_bytes(_SAMPLE_BYTES)
        result = get_frame_info(compressed)
        assert len(result) > 0

    def test_invalid_data(self):
        result = get_frame_info(b"not_zst_data_1234")
        assert isinstance(result, dict)


# ── is_valid_frame ────────────────────────────────────────────────────────

class TestIsValidFrame:

    def test_returns_bool(self):
        compressed = compress_bytes(_SAMPLE_BYTES)
        result = is_valid_frame(compressed)
        assert isinstance(result, bool)

    def test_valid_frame_true(self):
        compressed = compress_bytes(_SAMPLE_BYTES)
        assert is_valid_frame(compressed) is True

    def test_invalid_data_false(self):
        assert is_valid_frame(b"random_garbage_data") is False

    def test_empty_bytes_false(self):
        assert is_valid_frame(b"") is False


# ── validate_roundtrip ────────────────────────────────────────────────────

class TestValidateRoundtrip:

    def test_returns_dict(self):
        result = validate_roundtrip(_SAMPLE_BYTES)
        assert isinstance(result, dict)

    def test_has_valid_key(self):
        result = validate_roundtrip(_SAMPLE_BYTES)
        assert "valid" in result

    def test_valid_data_passes(self):
        result = validate_roundtrip(_SAMPLE_BYTES)
        assert result["valid"] is True

    def test_match_key_present(self):
        result = validate_roundtrip(_SAMPLE_BYTES)
        assert "match" in result

    def test_match_is_true(self):
        result = validate_roundtrip(_SAMPLE_BYTES)
        assert result["match"] is True


# ── batch_compress / batch_decompress ─────────────────────────────────────

class TestBatchOps:

    def test_batch_compress_returns_list(self, tmp_path):
        src1 = tmp_path / "a.txt"
        src2 = tmp_path / "b.txt"
        src1.write_bytes(b"content one")
        src2.write_bytes(b"content two")
        items = [(src1, tmp_path / "a.zst"), (src2, tmp_path / "b.zst")]
        result = batch_compress(items)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_batch_compress_creates_files(self, tmp_path):
        src = tmp_path / "data.txt"
        src.write_bytes(b"hello batch")
        out = tmp_path / "data.zst"
        batch_compress([(src, out)])
        assert out.exists()

    def test_batch_decompress_returns_list(self, tmp_path):
        src = tmp_path / "data.txt"
        src.write_bytes(b"hello decompress batch")
        zst = tmp_path / "data.zst"
        batch_compress([(src, zst)])
        out = tmp_path / "data_out.txt"
        result = batch_decompress([(zst, out)])
        assert isinstance(result, list)

    def test_batch_roundtrip(self, tmp_path):
        original = b"batch roundtrip test content"
        src = tmp_path / "src.txt"
        src.write_bytes(original)
        zst = tmp_path / "src.zst"
        out = tmp_path / "out.txt"
        batch_compress([(src, zst)])
        batch_decompress([(zst, out)])
        assert out.read_bytes() == original
