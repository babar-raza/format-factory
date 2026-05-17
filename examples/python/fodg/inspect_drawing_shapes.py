"""
inspect_drawing_shapes.py — FODG FOSS codec example.

ALPHA FOSS PREVIEW — NOT FOR COMMERCIAL USE
capability_level: alpha-foss-preview
commercial_product_ready: false

No network access required.
Demonstrates: load, get_page_count, get_shape_count, extract_text, get_page_metadata.

Run from repo root:
  PYTHONPATH=src/python python examples/python/fodg/inspect_drawing_shapes.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT = Path(__file__).resolve()
_REPO_ROOT = _SCRIPT.parent.parent.parent.parent
_SRC_PYTHON = _REPO_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

import fodg

print("FODG FOSS Example — alpha-foss-preview")
print(f"Package version: {fodg.__version__}")
print(f"Commercial ready: {fodg.__commercial_ready__}")
print(f"Capability level: {fodg.__capability_level__}")
print()

samples_dir = _REPO_ROOT / "samples" / "by-format" / "fodg"
fodg_files = sorted(samples_dir.glob("*.fodg")) if samples_dir.exists() else []

if not fodg_files:
    print("SKIPPED: No .fodg sample files found.")
    print(f"  Expected: {samples_dir}")
    sys.exit(0)

for sample in fodg_files:
    print(f"File: {sample.name}")
    try:
        model = fodg.load(sample)
        page_count = fodg.get_page_count(model)
        shape_count = fodg.get_shape_count(model)
        text = fodg.extract_text(model)
        metadata = fodg.get_page_metadata(model)
        print(f"  Pages: {page_count}")
        print(f"  Shapes: {shape_count}")
        print(f"  Text: {text[:5]}{'...' if len(text) > 5 else ''}")
        print(f"  Page metadata (first): {metadata[0] if metadata else 'none'}")
    except fodg.FodgError as e:
        print(f"  Error: {e}")
    print()

print("Example complete.")
print("NOTE: This is alpha-foss-preview. Do not use in production or commercial products.")
