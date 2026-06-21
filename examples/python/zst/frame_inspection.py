"""
ZST example: Inspect Zstandard compressed frames — frame metadata, compression ratio,
validity checks, and size statistics.

Usage:
    python frame_inspection.py [path/to/file.zst]

If no path is given, compresses an in-memory payload for demonstration.
"""
import sys
import tempfile
import os
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "zst"))

import zst_codec as zst

# --- Create or use compressed sample ---
if len(sys.argv) > 1:
    sample_path = sys.argv[1]
    with open(sample_path, "rb") as f:
        compressed = f.read()
    raw_size = None
    cleanup = False
else:
    # Compress structured text payload in memory
    payload = (
        "Region,Q1,Q2,Q3,Q4\n"
        "North,120000,135000,148000,162000\n"
        "South,98000,102000,110000,125000\n"
        "East,87000,91000,99000,108000\n"
        "West,145000,158000,172000,189000\n"
    ) * 20  # repeat for compressible data
    raw_bytes = payload.encode("utf-8")
    raw_size = len(raw_bytes)
    compressed = zst.compress_bytes(raw_bytes, level=3)
    sample_path = None
    cleanup = False

print("=== ZST Frame Inspection ===")
if sample_path:
    print(f"Source: {sample_path}")
else:
    print(f"Source: in-memory payload ({raw_size} bytes uncompressed)")

# --- Validity check ---
valid = zst.is_valid_frame(compressed)
print(f"\n  Valid ZST frame: {valid}")

# --- Frame metadata ---
frame_info = zst.get_frame_info(compressed)
print(f"\n  Frame info:")
print(f"    magic_ok:         {frame_info.get('magic_ok')}")
print(f"    compressed_size:  {frame_info.get('compressed_size')} bytes")
print(f"    content_size:     {frame_info.get('content_size')} bytes")
print(f"    compression_ratio: {frame_info.get('compression_ratio'):.6f}")
if frame_info.get("error"):
    print(f"    error: {frame_info['error']}")

# --- Size statistics ---
size_stats = zst.get_frame_size_stats(compressed)
print(f"\n  Frame size stats:")
print(f"    compressed_bytes:   {size_stats.get('compressed_bytes')}")
print(f"    decompressed_bytes: {size_stats.get('decompressed_bytes')}")
saved = size_stats.get("space_saved_bytes", 0)
saved_pct = size_stats.get("space_saved_pct", 0.0)
print(f"    space_saved:        {saved} bytes ({saved_pct:.1f}%)")

# --- Compression ratio estimate ---
if raw_size:
    estimate = zst.estimate_ratio(raw_bytes, level=3)
    print(f"\n  Compression estimate (level 3):")
    print(f"    input_bytes:    {estimate.get('input_bytes')}")
    print(f"    compressed_bytes: {estimate.get('compressed_bytes')}")
    print(f"    ratio:          {estimate.get('ratio'):.6f}")
    print(f"    savings_pct:    {estimate.get('savings_pct'):.1f}%")

# --- Probe frame (header check) ---
probe = zst.probe_frame(compressed)
print(f"\n  Probe result: {probe}")
