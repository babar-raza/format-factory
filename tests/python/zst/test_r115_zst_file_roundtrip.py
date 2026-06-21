"""R115 Train D: ZST file roundtrip + probe workflow deepening.

Tests compress_bytes → write to file → read → decompress_bytes roundtrip,
probe_frame metadata, validate_file, and dogfood pipeline.
"""


import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python" / "zst"))

from zst_codec import (
    compress_bytes,
    decompress_bytes,
    probe_frame,
    validate_file,
    ZSTD_MAGIC,
)


class TestZstFileRoundtrip:
    def test_roundtrip_text_data(self, tmp_path):
        data = b"Hello, Zstandard file roundtrip!"
        compressed = compress_bytes(data)
        out = tmp_path / "test.zst"
        out.write_bytes(compressed)
        recovered = decompress_bytes(out.read_bytes())
        assert recovered == data

    def test_roundtrip_binary_data(self, tmp_path):
        data = bytes(range(256)) * 64
        compressed = compress_bytes(data)
        out = tmp_path / "binary.zst"
        out.write_bytes(compressed)
        recovered = decompress_bytes(out.read_bytes())
        assert recovered == data

    def test_roundtrip_empty_data(self, tmp_path):
        data = b""
        compressed = compress_bytes(data)
        out = tmp_path / "empty.zst"
        out.write_bytes(compressed)
        recovered = decompress_bytes(out.read_bytes())
        assert recovered == data

    def test_roundtrip_large_repetitive_data(self, tmp_path):
        data = b"ABCDEFGH" * 10000
        compressed = compress_bytes(data)
        # Compressed should be significantly smaller
        assert len(compressed) < len(data)
        out = tmp_path / "large.zst"
        out.write_bytes(compressed)
        recovered = decompress_bytes(out.read_bytes())
        assert recovered == data

    def test_compressed_file_starts_with_magic(self, tmp_path):
        data = b"magic check test"
        compressed = compress_bytes(data)
        out = tmp_path / "magic.zst"
        out.write_bytes(compressed)
        assert out.read_bytes()[:4] == ZSTD_MAGIC

    def test_roundtrip_level_variations(self, tmp_path):
        data = b"Level variation test data. " * 100
        for level in (1, 3, 9, 19):
            compressed = compress_bytes(data, level=level)
            out = tmp_path / f"level{level}.zst"
            out.write_bytes(compressed)
            recovered = decompress_bytes(out.read_bytes())
            assert recovered == data, f"Failed at level {level}"


class TestZstProbeWorkflow:
    def test_probe_valid_frame(self):
        data = b"probe test payload"
        compressed = compress_bytes(data)
        result = probe_frame(compressed)
        assert result["valid"] is True
        assert result["magic_ok"] is True
        assert result["error"] is None

    def test_probe_invalid_bytes(self):
        result = probe_frame(b"\x00\x01\x02\x03garbage")
        assert result["valid"] is False
        assert result["magic_ok"] is False
        assert result["error"] is not None

    def test_validate_file_on_valid_zst(self, tmp_path):
        data = b"validate_file test"
        compressed = compress_bytes(data)
        out = tmp_path / "valid.zst"
        out.write_bytes(compressed)
        result = validate_file(out)
        assert result["valid"] is True

    def test_validate_file_on_invalid_file(self, tmp_path):
        bad = tmp_path / "bad.zst"
        bad.write_bytes(b"not a zstd frame at all")
        result = validate_file(bad)
        assert result["valid"] is False

    def test_dogfood_pipeline(self, tmp_path):
        # Full pipeline: create data → compress → write → read → probe → decompress → verify
        original = b"Dogfood pipeline: compress, write, probe, decompress." * 20
        compressed = compress_bytes(original)
        path = tmp_path / "dogfood.zst"
        path.write_bytes(compressed)

        # Probe — must be valid
        probe = probe_frame(path.read_bytes())
        assert probe["valid"] is True

        # Validate file
        val = validate_file(path)
        assert val["valid"] is True

        # Decompress and verify fidelity
        recovered = decompress_bytes(path.read_bytes())
        assert recovered == original
