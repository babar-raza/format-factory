"""
fodg_to_toml.py — Dogfood export: FODG → TOML using Format Factory libraries.

Reads a Flat OpenDocument Drawing (.fodg) file using Format Factory's FODG codec
and writes each page as a TOML array table entry using Format Factory's TOML writer.

Each drawing page becomes a [[pages]] entry with page_name, text_content, and
shape_count fields.

Sprint: FODG-TO-TOML-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODG-TO-TOML-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from fodg.fodg_codec import load as load_fodg  # FF source reader
from toml.toml_codec import write_toml  # FF target writer


def fodg_to_toml(
    fodg_path: str | Path,
    dest_path: str | Path,
    *,
    table_key: str = "pages",
) -> int:
    """Convert a FODG drawing file to a TOML file, one [[pages]] entry per page.

    Each page has keys: page_name, text_content (joined with ' '), and shape_count.

    Args:
        fodg_path: Path to the source .fodg file.
        dest_path: Path for the output .toml file (parent dirs created).
        table_key: Name for the TOML array table (default "pages").

    Returns:
        Number of pages written.
    """
    fodg_path = Path(fodg_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodg(fodg_path)  # Format Factory fodg reader
    pages = doc.get("pages", [])

    toml_pages: list[dict] = []
    for page in pages:
        page_name = page.get("name", "") or ""
        text_parts = page.get("text_content", []) or []
        text_content = " ".join(str(t) for t in text_parts if t)
        shape_count = str(page.get("shape_count", 0))
        toml_pages.append({
            "page_name": page_name,
            "text_content": text_content,
            "shape_count": shape_count,
        })

    write_toml({table_key: toml_pages}, dest_path)  # Format Factory toml writer
    return len(toml_pages)


__all__ = ["fodg_to_toml"]
