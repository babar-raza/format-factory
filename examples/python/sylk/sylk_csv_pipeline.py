"""SYLK CSV Export Pipeline Example.

Demonstrates: Parse a SYLK file and export its data as CSV text.
Requires: pip install format-factory-sylk (or run from source with PYTHONPATH).
"""
import os
import tempfile

import sylk


def main():
    # 1. Create a sample SYLK file with numeric and string data
    content = (
        "ID;P\n"
        'C;X1;Y1;K"Name"\n'
        'C;X2;Y1;K"Score"\n'
        'C;X1;Y2;K"Alice"\n'
        "C;X2;Y2;K95\n"
        'C;X1;Y3;K"Bob"\n'
        "C;X2;Y3;K87\n"
        'C;X1;Y4;K"Charlie"\n'
        "C;X2;Y4;K-3\n"
        "E"
    )
    with tempfile.NamedTemporaryFile(suffix=".slk", delete=False, mode="w", encoding="utf-8") as f:
        f.write(content)
        path = f.name

    try:
        # 2. Parse the SYLK file to verify structure
        parsed = sylk.parse_sylk(path)
        print(f"Parse OK: {parsed.get('ok')}")
        print(f"Cells:    {parsed.get('cell_count', 'N/A')}")

        # 3. Export to CSV text
        csv_text = sylk.sylk_to_csv(path)
        print("\n--- CSV Output ---")
        print(csv_text)

        # 4. Verify negative numbers survive the pipeline
        assert "-3" in csv_text, "Negative number should survive CSV export"
        print("Negative number preserved in CSV.")
    finally:
        os.unlink(path)


if __name__ == "__main__":
    main()
