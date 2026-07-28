"""
abw_to_toml.py — Dogfood export: ABW → TOML using Format Factory libraries.

Reads an ABW file using Format Factory's ABW codec and writes the paragraph
texts as a TOML file using Format Factory's TOML writer.

The paragraphs are stored as a [[paragraphs]] array table with a "text" field.

Sprint: ABW-TO-TOML-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ABW-TO-TOML-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path


from abw.abw_codec import load as load_abw  # FF source reader
from toml.toml_codec import write_toml  # FF target writer


def abw_to_toml(
    abw_path: str | Path,
    dest_path: str | Path,
    *,
    skip_empty: bool = True,
) -> int:
    """Convert an ABW file to a TOML file, one [[paragraphs]] entry per paragraph.

    Each ABW paragraph with non-empty text becomes one TOML array table entry
    with a "text" field.

    Args:
        abw_path: Path to the source .abw file.
        dest_path: Path for the output .toml file (parent dirs created).
        skip_empty: When True, empty paragraphs are omitted.

    Returns:
        Number of paragraph entries written.
    """
    abw_path = Path(abw_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load_abw(abw_path)  # Format Factory abw reader
    raw_paragraphs = model.get("paragraphs", []) or []

    toml_paras: list[dict] = []
    for para in raw_paragraphs:
        text = para.get("text", "") if isinstance(para, dict) else str(para)
        if skip_empty and not text.strip():
            continue
        toml_paras.append({"text": text})

    write_toml({"paragraphs": toml_paras}, dest_path)  # Format Factory toml writer
    return len(toml_paras)


__all__ = ["abw_to_toml"]
