"""
compress_decompress_file.py — ZST FOSS codec example.

ALPHA FOSS PREVIEW — NOT FOR COMMERCIAL USE
capability_level: alpha-foss-preview
commercial_product_ready: false

No network access required.
Demonstrates: compress_bytes, decompress_bytes, probe_frame, validate_file.

Run from repo root:
  PYTHONPATH=src/python python examples/python/zst/compress_decompress_file.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Locate repo root and src/python
_SCRIPT = Path(__file__).resolve()
_REPO_ROOT = _SCRIPT.parent.parent.parent.parent
_SRC_PYTHON = _REPO_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

import zst

print("ZST FOSS Example — alpha-foss-preview")
print(f"Package version: {zst.__version__}")
print(f"Commercial ready: {zst.__commercial_ready__}")
print(f"Capability level: {zst.__capability_level__}")
print()

# --- compress_bytes / decompress_bytes ---
original = b"Hello, Zstandard! " * 20
print(f"compress_bytes: {len(original)} bytes input")

try:
    compressed = zst.compress_bytes(original)
    print(f"  → {len(compressed)} bytes compressed")

    decompressed = zst.decompress_bytes(compressed)
    assert decompressed == original, "Round-trip mismatch!"
    print(f"  → {len(decompressed)} bytes decompressed (round-trip OK)")
except zst.ZstError as e:
    print(f"  ZST not available: {e}")
    print("  Install zstandard: pip install zstandard")

print()

# --- probe_frame ---
print("probe_frame: checking magic bytes only (no zstandard required)")
ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"
sample_data = ZSTD_MAGIC + b"\x00" * 4  # minimal frame header stub
result = zst.probe_frame(sample_data)
print(f"  probe_frame result: {result}")

print()

# --- validate_file from samples ---
samples_dir = _REPO_ROOT / "samples" / "by-format" / "zst"
zst_files = list(samples_dir.glob("*.zst")) if samples_dir.exists() else []

if zst_files:
    sample = zst_files[0]
    print(f"validate_file: {sample.name}")
    try:
        valid = zst.validate_file(sample)
        print(f"  → VALID: {valid}")
    except zst.ZstError as e:
        print(f"  → Error: {e}")
else:
    print("validate_file: SKIPPED (no .zst sample files found)")
    print(f"  Expected: {samples_dir}")

print()
print("Example complete.")
print("NOTE: This is alpha-foss-preview. Do not use in production or commercial products.")
