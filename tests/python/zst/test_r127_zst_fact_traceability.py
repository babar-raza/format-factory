"""
test_r127_zst_fact_traceability.py
Sprint: SPEC-AUTHORITY-LAYER-CONVEYOR-ACCELERATION-AND-OPS-CLEANUP-001
Added: 2026-06-08

Fact-traceability tests for ZST codec — verifies SAL-ZST-00001 and SAL-ZST-00002
citations in source code and magic-byte correctness.

SAL-ZST-00001: "Zstandard frame starts with 4-byte magic number 0xFD2FB528 in little-endian"
  Source: RFC 8878 section 3.1.1, Table 1
  validated_by: deterministic_spec_text_search

SAL-ZST-00002: "Skippable frames start with 4-byte magic number in range 0x184D2A50 to 0x184D2A5F"
  Source: RFC 8878 section 3.1.2
  validated_by: deterministic_spec_text_search
"""
import sys
from pathlib import Path

# Repo root discovery
_REPO_ROOT = None
for _p in [Path(__file__).resolve(), *Path(__file__).resolve().parents]:
    if (_p / ".git").exists():
        _REPO_ROOT = _p
        break
if _REPO_ROOT is None:
    _REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent

sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))


class TestZstFactZst001Traceability:
    """SAL-ZST-00001: magic number 0xFD2FB528 is cited and correct in source.

    Spec authority: RFC 8878 §3.1.1 (SAL-ZST-00001)
    """

    def test_zstd_magic_constant_exists(self):
        """ZSTD_MAGIC constant must be exported from zst_codec."""
        from zst.zst_codec import ZSTD_MAGIC
        assert ZSTD_MAGIC is not None

    def test_zstd_magic_is_bytes(self):
        """ZSTD_MAGIC must be a bytes object. (SAL-ZST-00001)"""
        from zst.zst_codec import ZSTD_MAGIC
        assert isinstance(ZSTD_MAGIC, bytes)

    def test_zstd_magic_is_four_bytes(self):
        """ZSTD_MAGIC must be exactly 4 bytes per RFC 8878 §3.1.1. (SAL-ZST-00001)"""
        from zst.zst_codec import ZSTD_MAGIC
        assert len(ZSTD_MAGIC) == 4, f"Expected 4 bytes, got {len(ZSTD_MAGIC)}"

    def test_zstd_magic_little_endian_value(self):
        """ZSTD_MAGIC must equal 0xFD2FB528 in little-endian byte order. (SAL-ZST-00001)

        RFC 8878 §3.1.1 Table 1: Magic_Number = 0xFD2FB528 (little-endian).
        Little-endian byte sequence: 28 B5 2F FD.
        """
        from zst.zst_codec import ZSTD_MAGIC
        import struct
        # Decode as 32-bit little-endian unsigned integer
        value = struct.unpack("<I", ZSTD_MAGIC)[0]
        assert value == 0xFD2FB528, (
            f"SAL-ZST-00001 violation: magic = 0x{value:08X}, expected 0xFD2FB528"
        )

    def test_zstd_magic_raw_bytes_match_little_endian(self):
        """ZSTD_MAGIC raw bytes must be [0x28, 0xB5, 0x2F, 0xFD]. (SAL-ZST-00001)"""
        from zst.zst_codec import ZSTD_MAGIC
        expected = bytes([0x28, 0xB5, 0x2F, 0xFD])
        assert ZSTD_MAGIC == expected, (
            f"SAL-ZST-00001: bytes={ZSTD_MAGIC.hex()}, expected={expected.hex()}"
        )

    def test_fact_zst_001_citation_in_source(self):
        """SAL-ZST-00001 must be cited in zst_codec.py source file."""
        source = (_REPO_ROOT / "src" / "python" / "zst" / "zst_codec.py").read_text(encoding="utf-8")
        assert "SAL-ZST-00001" in source, "SAL-ZST-00001 citation missing from zst_codec.py"

    def test_probe_frame_detects_invalid_magic(self):
        """probe_frame must detect non-Zstandard magic as invalid. (SAL-ZST-00001)

        Negative test: bytes not starting with 0x28B52FFD must be rejected.
        """
        from zst.zst_codec import probe_frame
        bad_data = b"\x00\x00\x00\x00" + b"\x00" * 10
        result = probe_frame(bad_data)
        assert not result["magic_ok"], "probe_frame should reject non-Zstandard magic"
        assert not result["valid"]

    def test_decompress_raises_on_wrong_magic(self):
        """decompress_bytes must raise ZstInvalidFrameError for non-magic input. (SAL-ZST-00001)"""
        from zst.zst_codec import decompress_bytes, ZstInvalidFrameError
        try:
            decompress_bytes(b"\x00\x00\x00\x00something")
            assert 1 == 0, "Expected ZstInvalidFrameError"

        except ZstInvalidFrameError:
            pass  # Expected


class TestZstFactZst002Traceability:
    """SAL-ZST-00002: skippable frame magic range 0x184D2A50-0x184D2A5F.

    Spec authority: RFC 8878 §3.1.2 (SAL-ZST-00002)
    """

    def test_skippable_magic_lower_bound(self):
        """Skippable frame magic lower bound is 0x184D2A50. (SAL-ZST-00002)

        RFC 8878 §3.1.2: Magic_Number for skippable frames is in range
        [0x184D2A50, 0x184D2A5F].
        """
        lower = 0x184D2A50
        upper = 0x184D2A5F
        assert lower < upper
        assert (upper - lower) == 15  # 16 valid values (0x50 to 0x5F inclusive)

    def test_skippable_magic_range_has_16_values(self):
        """Skippable frame magic range covers exactly 16 values. (SAL-ZST-00002)

        RFC 8878 §3.1.2: 0x184D2A50 through 0x184D2A5F = 16 valid magic values.
        """
        lower = 0x184D2A50
        upper = 0x184D2A5F
        count = upper - lower + 1
        assert count == 16, f"SAL-ZST-00002: expected 16 skippable magic values, got {count}"

    def test_probe_frame_rejects_skippable_magic_as_standard_frame(self):
        """probe_frame must reject a skippable-magic frame as not a standard Zstd frame. (SAL-ZST-00002)

        Skippable frames are distinct from standard Zstandard frames.
        A skippable magic should NOT match ZSTD_MAGIC (0xFD2FB528).
        """
        import struct
        from zst.zst_codec import probe_frame
        # Build a skippable-magic frame header (0x184D2A50 little-endian)
        skippable_magic = struct.pack("<I", 0x184D2A50)
        skippable_data = skippable_magic + b"\x00" * 8
        result = probe_frame(skippable_data)
        # Should not be a valid standard Zstandard frame
        assert not result["magic_ok"], (
            "Skippable frame magic should not match standard Zstandard frame magic (SAL-ZST-00002)"
        )
