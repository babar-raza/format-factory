"""
ABW HTML + Metadata Export Example
===================================
Demonstrates export_to_html() and get_metadata() added in R120.

Usage:
    python examples/python/abw/html_metadata_export_example.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from abw.abw_codec import create_abw, write_abw, export_to_html, get_metadata, probe_abw

# --- Create a simple document ---
paragraphs = [
    "Project Status Update",
    "The migration is 80% complete.",
    "Next milestone: integration testing by end of month.",
]
model = create_abw(paragraphs)

output_path = Path(__file__).parent / "example_output.abw"
write_abw(model, output_path)
print(f"Written: {output_path}")

# --- Probe ---
print(f"Is ABW: {probe_abw(output_path)}")

# --- Export to HTML ---
html = export_to_html(output_path)
html_path = Path(__file__).parent / "example_output.html"
html_path.write_text(html, encoding="utf-8")
print(f"HTML export ({len(html)} chars): {html_path}")
print(html)

# --- Extract metadata ---
meta = get_metadata(output_path)
print(f"Metadata: {meta!r}")
# Note: documents created by create_abw() have no metadata block.
# Real AbiWord documents may include dc.title, dc.creator, etc.

# --- Cleanup ---
output_path.unlink(missing_ok=True)
html_path.unlink(missing_ok=True)
