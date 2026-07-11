"""
fodp_to_toml.py — Dogfood export: FODP → TOML using Format Factory libraries.

Reads a Flat OpenDocument Presentation (.fodp) file using Format Factory's FODP
codec and writes each slide as a TOML array table entry using Format Factory's
TOML writer.

Each slide becomes a [[slides]] entry with slide_name, title, and text_content fields.

Sprint: FODP-TO-TOML-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODP-TO-TOML-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "fodp"))
sys.path.insert(0, str(_REPO))

from fodp.fodp_codec import load as load_fodp  # FF source reader
from toml.toml_codec import write_toml  # FF target writer


def fodp_to_toml(
    fodp_path: str | Path,
    dest_path: str | Path,
    *,
    table_key: str = "slides",
) -> int:
    """Convert a FODP presentation to a TOML file, one [[slides]] entry per slide.

    Each slide has keys: slide_name, title, and text_content (joined with '; ').

    Args:
        fodp_path: Path to the source .fodp file.
        dest_path: Path for the output .toml file (parent dirs created).
        table_key: Name for the TOML array table (default "slides").

    Returns:
        Number of slides written.
    """
    fodp_path = Path(fodp_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodp(fodp_path)  # Format Factory fodp reader
    pages = doc.get("pages", [])

    toml_slides: list[dict] = []
    for page in pages:
        slide_name = page.get("name", "") or ""
        title = page.get("title", "") or ""
        text_parts = page.get("text_content", []) or []
        text_content = "; ".join(str(t) for t in text_parts if t)
        toml_slides.append({
            "slide_name": slide_name,
            "title": title,
            "text_content": text_content,
        })

    write_toml({table_key: toml_slides}, dest_path)  # Format Factory toml writer
    return len(toml_slides)


__all__ = ["fodp_to_toml"]
