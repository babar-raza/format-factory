"""
FODT example: Load a document and export to plain text and HTML.

Usage:
    python edit_and_export.py [path/to/file.fodt]

If no path is given, builds a document from scratch.
"""
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

try:
    from fodt import parse_fodt_strict, write_fodt, document_text_content, document_to_html
except ImportError:
    import sys
    from pathlib import Path as _Path
    sys.path.insert(0, str(_Path(__file__).resolve().parents[3]))
    from src.python.fodt import parse_fodt_strict, write_fodt, document_text_content, document_to_html

# --- Build or load document ---
sample_path = str(_REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt")

if Path(sample_path).exists():
    document = parse_fodt_strict(sample_path)
    print(f"Loaded: {sample_path}")
else:
    # Build a minimal document inline
    document = {
        "blocks": [
            {"type": "heading", "text": "My Document", "heading_level": 1},
            {"type": "paragraph", "text": "This is a sample paragraph."},
            {"type": "paragraph", "text": "Another paragraph with more content."},
        ]
    }
    print("Built document inline.")

# --- Export to plain text ---
plain_text = document_text_content(document)
print("\nPlain text export:")
print(plain_text[:400])

# --- Export to HTML ---
html = document_to_html(document)
print(f"\nHTML export ({len(html)} chars):")
print(html[:300] + ("..." if len(html) > 300 else ""))

# --- Save modified document ---
with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False) as f:
    out_path = f.name

write_fodt(document, out_path)
print(f"\nSaved document to: {out_path}")
print(f"File size: {Path(out_path).stat().st_size} bytes")
