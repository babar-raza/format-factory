"""
mtlx_to_csv.py — Dogfood export: mtlx → CSV using Format Factory libraries.

Reads a MaterialX document using Format Factory's mtlx codec and writes a
material inventory as CSV rows using Format Factory's CSV writer: one row
per material (name, type, shader nodename) — the "bill of materials" shape
a technical director or asset-pipeline tool would want.

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from mtlx.mtlx_codec import load_mtlx
from ff_csv.csv_writer import write_csv_to_file


def _shader_nodename(material: dict) -> str:
    for inp in material.get("inputs", []):
        if inp.get("nodename"):
            return str(inp["nodename"])
    return ""


def mtlx_to_csv(
    mtlx_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
) -> int:
    """Convert a material inventory to CSV rows, one row per material.

    Args:
        mtlx_path: Path to the source .mtlx file.
        dest_path: Path for the output .csv file (parent dirs created).
        include_header: When True, emits a header row.

    Returns:
        Number of data rows written (not counting the header).
    """
    mtlx_path = Path(mtlx_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load_mtlx(mtlx_path)
    materials = model.get("materials", [])

    rows: list[list[str]] = []
    header = ["name", "type", "shader_nodename"]

    for mat in materials:
        rows.append([
            str(mat.get("name", "")),
            str(mat.get("type", "")),
            _shader_nodename(mat),
        ])

    write_csv_to_file(rows, dest_path, headers=header if include_header else None)
    return len(rows)
