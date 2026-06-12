"""
test_r167_zst_package_export.py

Lane E — ZST Package, Export, and Sample Output Proof:
Verifies that compress_string_to_file and decompress_file_to_string
are properly exported through the public package API.

Sprint: FORMAT-FACTORY-SAL-ENFORCEMENT-CLOSEOUT-AND-PRODUCT-ACCELERATION-RNEXT-001
spec_fact_refs: FACT-ZST-001
Route decision: RDEC-RNEXT-LE-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO / "src" / "python"))


class TestZstPackageExports:
    """All public ZST functions must be importable from the package."""

    def test_package_exports_compress_string_to_file(self):
        from zst import compress_string_to_file
        assert callable(compress_string_to_file)

    def test_package_exports_decompress_file_to_string(self):
        from zst import decompress_file_to_string
        assert callable(decompress_file_to_string)

    def test_package_exports_compress_string(self):
        from zst import compress_string
        assert callable(compress_string)

    def test_package_exports_decompress_to_string(self):
        from zst import decompress_to_string
        assert callable(decompress_to_string)

    def test_all_in_all(self):
        import zst
        expected = [
            "compress_string_to_file", "decompress_file_to_string",
            "compress_string", "decompress_to_string",
        ]
        for name in expected:
            assert name in zst.__all__, f"{name} must be in zst.__all__"

    def test_package_level_compress_string_to_file_works(self, tmp_path):
        from zst import compress_string_to_file, decompress_file_to_string
        text = "Package-level round-trip via RNEXT SAL enforcement sprint."
        out = tmp_path / "pkg_test.zst"
        result = compress_string_to_file(text, out)
        assert result["success"] is True
        recovered = decompress_file_to_string(out)
        assert recovered == text


class TestZstSampleOutputProof:
    """Generate sample .zst output and verify decompressed proof."""

    def test_sample_compression_produces_valid_zst(self, tmp_path):
        from zst import compress_string_to_file, decompress_file_to_string
        sample_text = (
            "Format Factory ZST sample output.\n"
            "Sprint: FORMAT-FACTORY-SAL-ENFORCEMENT-CLOSEOUT-AND-PRODUCT-ACCELERATION-RNEXT-001\n"
            "spec_fact_refs: FACT-ZST-001\n"
            "This file was produced by compress_string_to_file() and verified by decompress_file_to_string().\n"
        )
        sample_path = tmp_path / "rnext-sample.zst"
        result = compress_string_to_file(sample_text, sample_path)
        assert result["success"] is True
        assert sample_path.read_bytes()[:4] == b"\x28\xb5\x2f\xfd"
        recovered = decompress_file_to_string(sample_path)
        assert recovered == sample_text
        assert "FACT-ZST-001" in recovered

    def test_max_output_size_regression(self, tmp_path):
        from zst import compress_string_to_file, decompress_file_to_string, ZstError
        text = "B" * 10000
        out = tmp_path / "large.zst"
        compress_string_to_file(text, out)
        with pytest.raises(ZstError):
            decompress_file_to_string(out, max_output_size=100)
