"""
test_r154_zst_validate_roundtrip.py

Sprint: FORMAT-FACTORY-AUTHORITY-GATED-PRODUCT-DOGFOOD-FEATURES-AND-BACKFILL-001
Added: 2026-06-09

Tests for ZST validate_roundtrip() API:
- validate_roundtrip(data, level) -> dict

Authority: P6 (SAL-ZST-00001: Zstandard magic 0xFD2FB528, RFC 8878 §3.1.1)
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.zst.zst_codec import validate_roundtrip


class TestValidateRoundtrip:
    """validate_roundtrip: compress + decompress + verify byte equality."""

    def test_valid_bytes_roundtrip(self):
        """validate_roundtrip must return valid=True for well-formed bytes."""
        data = b"Hello ZST roundtrip!" * 100
        result = validate_roundtrip(data)
        assert result["valid"] is True
        assert result["match"] is True

    def test_result_has_required_keys(self):
        """validate_roundtrip result must contain expected keys."""
        result = validate_roundtrip(b"abc" * 50)
        for key in ("valid", "input_bytes", "compressed_bytes", "decompressed_bytes",
                    "match", "compression_ratio", "error"):
            assert key in result

    def test_input_bytes_correct(self):
        """validate_roundtrip must report correct input_bytes."""
        data = b"x" * 500
        result = validate_roundtrip(data)
        assert result["input_bytes"] == 500

    def test_decompressed_bytes_equals_input(self):
        """decompressed_bytes must equal input_bytes on successful roundtrip."""
        data = b"roundtrip size check " * 30
        result = validate_roundtrip(data)
        assert result["decompressed_bytes"] == len(data)

    def test_compression_ratio_lt_one_for_compressible(self):
        """Compression ratio must be < 1.0 for repetitive data."""
        data = b"repetitive " * 500
        result = validate_roundtrip(data)
        assert result["compression_ratio"] is not None
        assert result["compression_ratio"] < 1.0

    def test_no_error_on_success(self):
        """error field must be None on successful roundtrip."""
        result = validate_roundtrip(b"clean data" * 50)
        assert result["error"] is None

    def test_invalid_input_type_returns_error(self):
        """Non-bytes input must return valid=False with error message."""
        result = validate_roundtrip("not bytes")
        assert result["valid"] is False
        assert result["error"] is not None

    def test_custom_level_works(self):
        """validate_roundtrip must accept custom compression level."""
        data = b"level test data " * 100
        for level in (1, 9, 19):
            result = validate_roundtrip(data, level=level)
            assert result["valid"] is True

    def test_exported_from_package(self):
        """validate_roundtrip must be importable from zst package."""
        from src.python.zst import validate_roundtrip as vr
        assert callable(vr)
