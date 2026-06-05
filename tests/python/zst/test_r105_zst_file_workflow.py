# R105 Wave 3: ZST file-based workflow hardening
# Lane D — ZST FOSS
# Ledger: R105-FOSS-ZST-FILE-WORKFLOW-001

import pytest
from pathlib import Path
from zst.zst_codec import (
    compress_bytes,
    decompress_bytes,
    probe_frame,
    validate_file,
    ZstError,
    ZstOutputLimitExceeded,
    ZSTD_MAGIC,
)


class TestFileWorkflow:
    """Complete file-based compress→write→validate→read→decompress workflow."""

    def test_full_file_roundtrip(self, tmp_path):
        original = b"File roundtrip content " * 100
        compressed = compress_bytes(original, level=3)
        p = tmp_path / "test.zst"
        p.write_bytes(compressed)
        result = validate_file(str(p))
        assert result["valid"] is True
        loaded = p.read_bytes()
        assert decompress_bytes(loaded) == original

    def test_multiple_files_workflow(self, tmp_path):
        for i in range(5):
            data = f"File {i} content".encode() * 50
            c = compress_bytes(data, level=3)
            p = tmp_path / f"file_{i}.zst"
            p.write_bytes(c)
            assert validate_file(str(p))["valid"] is True
            assert decompress_bytes(p.read_bytes()) == data

    def test_large_file_roundtrip(self, tmp_path):
        data = bytes(range(256)) * 4096  # 1 MiB
        c = compress_bytes(data, level=1)
        p = tmp_path / "large.zst"
        p.write_bytes(c)
        assert validate_file(str(p))["valid"] is True
        assert decompress_bytes(p.read_bytes()) == data

    def test_empty_data_file(self, tmp_path):
        c = compress_bytes(b"")
        p = tmp_path / "empty.zst"
        p.write_bytes(c)
        assert validate_file(str(p))["valid"] is True
        assert decompress_bytes(p.read_bytes()) == b""

    def test_validate_non_zst_file(self, tmp_path):
        p = tmp_path / "text.txt"
        p.write_text("not compressed")
        result = validate_file(str(p))
        assert result["valid"] is False

    def test_probe_from_file(self, tmp_path):
        data = b"Probe test" * 10
        c = compress_bytes(data)
        p = tmp_path / "probe.zst"
        p.write_bytes(c)
        info = probe_frame(p.read_bytes())
        assert info["magic_ok"] is True

    def test_compressed_smaller_than_original(self, tmp_path):
        data = b"Repetitive " * 1000
        c = compress_bytes(data, level=3)
        assert len(c) < len(data)

    def test_different_levels_same_decompression(self, tmp_path):
        data = b"Level test " * 200
        for level in [1, 10, 22]:
            c = compress_bytes(data, level=level)
            assert decompress_bytes(c) == data

    def test_binary_data_roundtrip(self, tmp_path):
        data = bytes(range(256))
        c = compress_bytes(data)
        p = tmp_path / "binary.zst"
        p.write_bytes(c)
        assert decompress_bytes(p.read_bytes()) == data
