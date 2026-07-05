"""
extract_text.py — ABW FOSS codec example.

ALPHA FOSS PREVIEW — NOT FOR COMMERCIAL USE
capability_level: alpha-foss-preview
commercial_product_ready: false

No network access required.
Demonstrates: load, get_section_count, get_paragraph_count, extract_text.

Run from repo root:
  PYTHONPATH=src/python python examples/python/abw/extract_text.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT = Path(__file__).resolve()
_REPO_ROOT = _SCRIPT.parent.parent.parent.parent
_SRC_PYTHON = _REPO_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

import abw

print("ABW FOSS Example — alpha-foss-preview")
print(f"Package version: {abw.__version__}")
print(f"Commercial ready: {abw.__commercial_ready__}")
print(f"Capability level: {abw.__capability_level__}")
print()

samples_dir = _REPO_ROOT / "samples" / "by-format" / "abw"
abw_files = sorted(samples_dir.glob("*.abw")) if samples_dir.exists() else []

if not abw_files:
    print("SKIPPED: No .abw sample files found.")
    print(f"  Expected: {samples_dir}")
    sys.exit(0)

for sample in abw_files:
    print(f"File: {sample.name}")
    try:
        model = abw.load(sample)
        section_count = abw.get_section_count(sample)
        paragraph_count = abw.get_paragraph_count(sample)
        text = abw.extract_text(sample)
        print(f"  Sections: {section_count}")
        print(f"  Paragraphs: {paragraph_count}")
        print(f"  Text: {text[:5]}{'...' if len(text) > 5 else ''}")
    except abw.AbwError as e:
        print(f"  Error: {e}")
    print()

print("Example complete.")
print("NOTE: This is alpha-foss-preview. Do not use in production or commercial products.")
