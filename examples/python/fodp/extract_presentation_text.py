"""
extract_presentation_text.py — FODP FOSS codec example.

ALPHA FOSS PREVIEW — NOT FOR COMMERCIAL USE
capability_level: alpha-foss-preview
commercial_product_ready: false

No network access required.
Demonstrates: load, get_page_count, extract_text, get_page_metadata.

Run from repo root:
  PYTHONPATH=src/python python examples/python/fodp/extract_presentation_text.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT = Path(__file__).resolve()
_REPO_ROOT = _SCRIPT.parent.parent.parent.parent
_SRC_PYTHON = _REPO_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

import fodp

print("FODP FOSS Example — alpha-foss-preview")
print(f"Package version: {fodp.__version__}")
print(f"Commercial ready: {fodp.__commercial_ready__}")
print(f"Capability level: {fodp.__capability_level__}")
print()

samples_dir = _REPO_ROOT / "samples" / "by-format" / "fodp"
fodp_files = sorted(samples_dir.glob("*.fodp")) if samples_dir.exists() else []

if not fodp_files:
    print("SKIPPED: No .fodp sample files found.")
    print(f"  Expected: {samples_dir}")
    sys.exit(0)

for sample in fodp_files:
    print(f"File: {sample.name}")
    try:
        model = fodp.load(sample)
        page_count = fodp.get_page_count(model)
        text = fodp.extract_text(model)
        metadata = fodp.get_page_metadata(model)
        print(f"  Pages: {page_count}")
        print(f"  Text: {text[:5]}{'...' if len(text) > 5 else ''}")
        print(f"  Page metadata (first): {metadata[0] if metadata else 'none'}")
    except fodp.FodpError as e:
        print(f"  Error: {e}")
    print()

print("Example complete.")
print("NOTE: This is alpha-foss-preview. Do not use in production or commercial products.")
