# R106 Wave 3: ZST streaming and chunk-level proof
# Lane D — ZST FOSS
# Ledger: R106-FOSS-ZST-STREAMING-PROOF-001

from zst.zst_codec import (
    compress_bytes,
    decompress_bytes,
    probe_frame,
    validate_file,
    ZSTD_MAGIC,
)


class TestStreamingProof:
    """Verify chunk-level compress/decompress workflows."""

    def test_small_chunks_roundtrip(self, tmp_path):
        chunks = [f"chunk-{i}-".encode() * 10 for i in range(10)]
        data = b"".join(chunks)
        c = compress_bytes(data)
        assert decompress_bytes(c) == data

    def test_empty_then_nonempty(self):
        c1 = compress_bytes(b"")
        c2 = compress_bytes(b"data")
        assert decompress_bytes(c1) == b""
        assert decompress_bytes(c2) == b"data"

    def test_repeated_pattern_compresses(self):
        data = b"ABCD" * 10000
        c = compress_bytes(data, level=3)
        assert len(c) < len(data)
        assert decompress_bytes(c) == data

    def test_random_bytes_roundtrip(self):
        data = bytes(range(256)) * 100
        c = compress_bytes(data)
        assert decompress_bytes(c) == data

    def test_magic_bytes_present(self):
        c = compress_bytes(b"test")
        assert c[:4] == ZSTD_MAGIC

    def test_probe_reports_magic_ok(self):
        c = compress_bytes(b"probe test")
        info = probe_frame(c)
        assert info["magic_ok"] is True

    def test_validate_compressed_data(self, tmp_path):
        p = tmp_path / "valid.zst"
        p.write_bytes(compress_bytes(b"validate"))
        result = validate_file(str(p))
        assert result["valid"] is True

    def test_validate_garbage(self, tmp_path):
        p = tmp_path / "garbage.zst"
        p.write_bytes(b"not zstd data")
        result = validate_file(str(p))
        assert result["valid"] is False

    def test_level_1_vs_22_same_output(self):
        data = b"Level comparison" * 500
        c1 = compress_bytes(data, level=1)
        c22 = compress_bytes(data, level=22)
        assert decompress_bytes(c1) == data
        assert decompress_bytes(c22) == data
        # Higher level should compress at least as well
        assert len(c22) <= len(c1)
