"""
FODT example: Read and inspect a Flat OpenDocument Text document.

Usage:
    python read_and_inspect.py [path/to/file.fodt]

If no path is given, uses the built-in minimal sample.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

try:
    from fodt import parse_fodt_strict, document_text_content
except ImportError:
    sys.path.insert(0, str(_REPO / "src" / "python"))
    from fodt import parse_fodt_strict, document_text_content  # type: ignore

# --- Locate sample ---
if len(sys.argv) > 1:
    sample_path = sys.argv[1]
else:
    sample_path = str(_REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt")

if not Path(sample_path).exists():
    print(f"File not found: {sample_path}")
    sys.exit(1)

# --- Parse the document ---
document = parse_fodt_strict(sample_path)

# --- Inspect top-level structure ---
print(f"Document: {sample_path}")
blocks = document.get("blocks", [])
print(f"  Block count: {len(blocks)}")

# --- Inspect each block ---
for i, block in enumerate(blocks):
    btype = block.get("type", "unknown")
    text = block.get("text", "")
    level = block.get("heading_level")
    level_str = f" (level {level})" if level else ""
    print(f"  Block {i}: [{btype}{level_str}] {text!r}")

# --- Full text content ---
full_text = document_text_content(document)
print(f"\nFull text content ({len(full_text)} chars):")
print(full_text[:300] + ("..." if len(full_text) > 300 else ""))
