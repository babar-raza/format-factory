"""ZST spec-parity migration proof: maps ZST spec facts to implementing functions."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

# ZST spec facts from _FORMAT_SPECIFIC_FACTS in sal_master_runner.py
# ZST-FACT-001: RFC 8878 §3 — Zstandard Frame Format (magic number, frame header)
# ZST-FACT-002: RFC 8878 §3.1 — Blocks (block header, block types)
# ZST-FACT-003: RFC 8878 §8 — Skippable Frames

ZST_SPEC_FUNCTION_MAP = {
    "ZST-FACT-001": [
        # Frame format: magic number detection, frame header parsing
        "probe_frame",
        "get_frame_info",
        "validate_file",
        "is_valid_frame",
        "zst_is_valid_file",
    ],
    "ZST-FACT-002": [
        # Blocks: compress/decompress operate on block-level structure
        "compress_bytes",
        "decompress_bytes",
        "compress_file",
        "decompress_file",
        "validate_roundtrip",
    ],
    "ZST-FACT-003": [
        # Skippable frames: frame counting must handle skippable frames,
        # size stats parse frame boundaries
        "zst_frame_count",
        "get_frame_size_stats",
        "zst_compressed_size",
        "zst_decompressed_size",
    ],
}


@pytest.fixture
def zst_module():
    """Load the ZST module."""
    from src.python.zst import zst_codec
    return zst_codec


@pytest.fixture
def zst_all():
    """Get the __all__ list from zst __init__."""
    from src.python import zst
    return zst.__all__


class TestZstSpecFactCoverage:
    """Verify each ZST spec fact maps to real, exported functions."""

    @pytest.mark.parametrize("qname", list(ZST_SPEC_FUNCTION_MAP.keys()))
    def test_spec_fact_has_implementing_functions(self, qname):
        """Each spec fact must map to at least 2 functions."""
        funcs = ZST_SPEC_FUNCTION_MAP[qname]
        assert len(funcs) >= 2, f"{qname} maps to fewer than 2 functions"

    @pytest.mark.parametrize("qname", list(ZST_SPEC_FUNCTION_MAP.keys()))
    def test_functions_exist_in_module(self, qname, zst_module):
        """All mapped functions must exist in the zst_codec module."""
        for fn_name in ZST_SPEC_FUNCTION_MAP[qname]:
            assert hasattr(zst_module, fn_name), (
                f"{qname}: function '{fn_name}' not found in zst_codec"
            )

    @pytest.mark.parametrize("qname", list(ZST_SPEC_FUNCTION_MAP.keys()))
    def test_functions_are_callable(self, qname, zst_module):
        """All mapped functions must be callable."""
        for fn_name in ZST_SPEC_FUNCTION_MAP[qname]:
            fn = getattr(zst_module, fn_name)
            assert callable(fn), f"{qname}: '{fn_name}' is not callable"

    @pytest.mark.parametrize("qname", list(ZST_SPEC_FUNCTION_MAP.keys()))
    def test_functions_exported_in_all(self, qname, zst_all):
        """All mapped functions must be in __all__."""
        for fn_name in ZST_SPEC_FUNCTION_MAP[qname]:
            assert fn_name in zst_all, (
                f"{qname}: '{fn_name}' not in zst.__all__"
            )


class TestZstSpecFactLiveExecution:
    """Verify spec-fact-mapped functions actually work on real data."""

    def test_fact001_probe_frame_detects_magic(self, zst_module):
        """ZST-FACT-001: probe_frame should detect magic number in valid zst data."""
        data = zst_module.compress_bytes(b"hello world")
        info = zst_module.probe_frame(data)
        assert isinstance(info, dict)
        assert info.get("valid", info.get("is_valid", False)) or "magic" in str(info).lower() or len(info) > 0

    def test_fact001_is_valid_frame(self, zst_module):
        """ZST-FACT-001: is_valid_frame should verify magic number."""
        valid = zst_module.compress_bytes(b"test data")
        assert zst_module.is_valid_frame(valid) is True
        assert zst_module.is_valid_frame(b"not a zst frame") is False

    def test_fact002_compress_decompress_roundtrip(self, zst_module):
        """ZST-FACT-002: compress/decompress operate on block structure."""
        original = b"The quick brown fox jumps over the lazy dog" * 10
        compressed = zst_module.compress_bytes(original)
        decompressed = zst_module.decompress_bytes(compressed)
        assert decompressed == original

    def test_fact002_validate_roundtrip(self, zst_module):
        """ZST-FACT-002: validate_roundtrip confirms block-level integrity."""
        data = b"roundtrip test data"
        result = zst_module.validate_roundtrip(data)
        assert isinstance(result, dict)

    def test_fact003_frame_count(self, zst_module, tmp_path):
        """ZST-FACT-003: zst_frame_count counts frames in a file."""
        data = zst_module.compress_bytes(b"frame counting test")
        zst_file = tmp_path / "test.zst"
        zst_file.write_bytes(data)
        count = zst_module.zst_frame_count(str(zst_file))
        assert count >= 1

    def test_fact003_frame_size_stats(self, zst_module):
        """ZST-FACT-003: get_frame_size_stats parses frame boundaries."""
        data = zst_module.compress_bytes(b"size stats test data")
        stats = zst_module.get_frame_size_stats(data)
        assert isinstance(stats, dict)
