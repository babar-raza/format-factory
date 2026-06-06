"""
ABW create and write example — format-factory python-foss track.

Demonstrates:
  - create_abw(): build a document model from paragraph strings
  - write_abw(): serialize model to .abw XML file
  - load(): reload the file and verify content

Usage:
    python examples/python/abw/create_document_example.py

No external dependencies required (stdlib only).
"""

from pathlib import Path
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "src" / "python"))

from abw.abw_codec import create_abw, write_abw, load

def main():
    # Step 1: Create a document model
    paragraphs = [
        "Hello from Format Factory!",
        "This document was created programmatically.",
        "ABW format uses plain XML — no external dependencies required.",
    ]
    model = create_abw(paragraphs)
    print(f"Created model: {model['paragraph_count']} paragraphs, section_count={model['section_count']}")

    # Step 2: Write to file
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "example.abw"
        write_abw(model, dest)
        print(f"Written to: {dest}")
        print(f"File size: {dest.stat().st_size} bytes")

        # Step 3: Reload and verify
        loaded = load(dest)
        print(f"Reloaded: is_abw={loaded['is_abw']}, paragraphs={loaded['paragraphs']}")
        assert loaded["paragraph_count"] == 3
        assert "Hello from Format Factory!" in loaded["paragraphs"]
        print("Roundtrip verification: PASS")

if __name__ == "__main__":
    main()
