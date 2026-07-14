"""Pilot B: Probe-driven test for zst — TC-INT-006.

This test was generated via the scaffold workflow (generate_and_write_scaffold)
and promoted by replacing all FIXTURE_REQUIRED/ORACLE_REQUIRED markers with real
values from samples/by-format/zst/valid/minimal-synthetic.zst.

is_maintained_test() == True (verified during TC-INT-006 promotion).
"""
from __future__ import annotations

from pathlib import Path


_SAMPLE_PATH = (
    Path(__file__).resolve().parents[3]
    / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst"
)


def test_probe_frame_magic_ok():
    """probe_frame on valid ZST bytes confirms magic_ok=True."""
    import zst
    data = _SAMPLE_PATH.read_bytes()
    result = zst.probe_frame(data)
    assert result["valid"] is True, f"Expected valid=True, got {result}"
    assert result["magic_ok"] is True, f"Expected magic_ok=True, got {result}"


def test_probe_frame_content_size():
    """probe_frame on minimal-synthetic.zst returns content_size=1."""
    import zst
    data = _SAMPLE_PATH.read_bytes()
    result = zst.probe_frame(data)
    assert result["content_size"] == 1, f"Expected content_size=1, got {result['content_size']}"


def test_decompress_bytes_roundtrip():
    """Decompressed bytes can be re-compressed and decompressed to same content."""
    import zst
    data = _SAMPLE_PATH.read_bytes()
    decompressed = zst.decompress_bytes(data)
    recompressed = zst.compress_bytes(decompressed)
    roundtrip = zst.decompress_bytes(recompressed)
    assert roundtrip == decompressed, "Roundtrip failed: decompressed != re-decompressed"


def test_probe_frame_invalid_bytes_not_magic():
    """probe_frame on non-ZST bytes returns magic_ok=False (negative control)."""
    import zst
    result = zst.probe_frame(b"\x00\x00\x00\x00")
    assert result["magic_ok"] is False, f"Expected magic_ok=False for invalid bytes, got {result}"
