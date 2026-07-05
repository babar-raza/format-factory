"""
extract_cells.py — Gnumeric FOSS codec example.

ALPHA FOSS PREVIEW — NOT FOR COMMERCIAL USE
capability_level: alpha-foss-preview
commercial_product_ready: false

No network access required.
Demonstrates: load, get_sheet_count, get_cell_count, extract_values, get_sheet_metadata.

Run from repo root:
  PYTHONPATH=src/python python examples/python/gnumeric/extract_cells.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT = Path(__file__).resolve()
_REPO_ROOT = _SCRIPT.parent.parent.parent.parent
_SRC_PYTHON = _REPO_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

import gnumeric

print("Gnumeric FOSS Example — alpha-foss-preview")
print(f"Package version: {gnumeric.__version__}")
print(f"Commercial ready: {gnumeric.__commercial_ready__}")
print(f"Capability level: {gnumeric.__capability_level__}")
print()

samples_dir = _REPO_ROOT / "samples" / "by-format" / "gnumeric"
gnumeric_files = sorted(samples_dir.glob("*.gnumeric")) if samples_dir.exists() else []

if not gnumeric_files:
    print("SKIPPED: No .gnumeric sample files found.")
    print(f"  Expected: {samples_dir}")
    sys.exit(0)

for sample in gnumeric_files:
    print(f"File: {sample.name}")
    try:
        model = gnumeric.load(sample)
        sheet_count = gnumeric.get_sheet_count(sample)
        cell_count = gnumeric.get_cell_count(sample)
        values = gnumeric.extract_values(sample)
        metadata = gnumeric.get_sheet_metadata(sample)
        print(f"  Sheets: {sheet_count}")
        print(f"  Cells: {cell_count}")
        print(f"  Values (first 5): {values[:5]}{'...' if len(values) > 5 else ''}")
        print(f"  Sheet metadata (first): {metadata[0] if metadata else 'none'}")
    except gnumeric.GnumericError as e:
        print(f"  Error: {e}")
    print()

print("Example complete.")
print("NOTE: This is alpha-foss-preview. Do not use in production or commercial products.")
