#!/usr/bin/env python3
"""SYLK write + CSV export example.

Creates a SYLK document with sample data, writes it to a file,
then exports it to CSV format using Format Factory's SYLK library.

Usage:
    python write_export_sylk.py

Requires: format-factory-sylk (installed from wheel)
"""

from pathlib import Path
import tempfile

from sylk.sylk_parser import SylkDocument, SylkCell, write_sylk, sylk_to_csv


def main():
    # Create a document with sample data
    doc = SylkDocument()
    doc.cells = [
        SylkCell(row=1, col=1, value="Product"),
        SylkCell(row=1, col=2, value="Price"),
        SylkCell(row=1, col=3, value="Qty"),
        SylkCell(row=2, col=1, value="Widget"),
        SylkCell(row=2, col=2, value="9.99"),
        SylkCell(row=2, col=3, value="100"),
        SylkCell(row=3, col=1, value="Gadget"),
        SylkCell(row=3, col=2, value="24.50"),
        SylkCell(row=3, col=3, value="50"),
    ]
    doc.rows = 3
    doc.cols = 3

    # Write to a temporary SYLK file
    tmp_dir = Path(tempfile.mkdtemp())
    sylk_path = tmp_dir / "products.sylk"
    write_sylk(doc, str(sylk_path))
    print(f"Written SYLK file: {sylk_path}")
    print(f"File size: {sylk_path.stat().st_size} bytes")

    # Export to CSV
    csv_text = sylk_to_csv(str(sylk_path))
    print(f"\nCSV export:\n{csv_text}")

    # Cleanup
    sylk_path.unlink()
    tmp_dir.rmdir()
    print("Done.")


if __name__ == "__main__":
    main()
