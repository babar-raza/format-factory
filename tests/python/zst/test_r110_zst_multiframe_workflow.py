# R110 Wave 5: ZST Multi-frame Workflow Tests
# FOSS depth: compress→decompress→verify chain (workflow)

import pytest
import zst


class TestR110ZstMultiframeWorkflow:
    """ZST compress→decompress→verify workflow tests."""

    def test_roundtrip_basic(self):
        """Compress then decompress recovers original data."""
        data = b"Hello, Format Factory R110!"
        compressed = zst.compress_bytes(data)
        decompressed = zst.decompress_bytes(compressed)
        assert decompressed == data

    def test_roundtrip_empty(self):
        """Empty input roundtrips correctly."""
        data = b""
        compressed = zst.compress_bytes(data)
        decompressed = zst.decompress_bytes(compressed)
        assert decompressed == data

    def test_roundtrip_large(self):
        """Large data roundtrips correctly."""
        data = b"ABCDEFGHIJ" * 10000  # 100KB
        compressed = zst.compress_bytes(data)
        decompressed = zst.decompress_bytes(compressed)
        assert decompressed == data
        assert len(compressed) < len(data)  # should compress well

    def test_compress_different_levels_same_decompression(self):
        """Data compressed at different levels decompresses to same output."""
        data = b"Test data for level comparison R110" * 100
        for level in [1, 3, 9]:
            compressed = zst.compress_bytes(data, level=level)
            decompressed = zst.decompress_bytes(compressed)
            assert decompressed == data, f"Failed at level {level}"

    def test_probe_after_compress(self):
        """probe_frame returns valid dict for compressed output."""
        data = b"Probe test R110"
        compressed = zst.compress_bytes(data)
        info = zst.probe_frame(compressed)
        assert isinstance(info, dict)

    def test_multiple_sequential_compressions(self):
        """Multiple compress calls produce independent valid outputs."""
        data1 = b"First payload R110"
        data2 = b"Second payload R110"
        c1 = zst.compress_bytes(data1)
        c2 = zst.compress_bytes(data2)
        assert zst.decompress_bytes(c1) == data1
        assert zst.decompress_bytes(c2) == data2
        assert c1 != c2

    def test_decompress_garbage_raises(self):
        """Decompressing garbage data raises an error."""
        with pytest.raises(Exception):
            zst.decompress_bytes(b"not-valid-zst-data-r110")

    def test_binary_data_roundtrip(self):
        """Binary data with all byte values roundtrips correctly."""
        data = bytes(range(256)) * 10
        compressed = zst.compress_bytes(data)
        decompressed = zst.decompress_bytes(compressed)
        assert decompressed == data
