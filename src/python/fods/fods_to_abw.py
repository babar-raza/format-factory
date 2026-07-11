from __future__ import annotations
import sys
from pathlib import Path
_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "src" / "python" / "fods"))
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))
from fods.parser import parse_fods_strict
from abw.abw_codec import write_abw
def fods_to_abw(fods_path, dest_path, *, sheet_index=0, separator=" | "):
    """Convert FODS to ABW, one paragraph per row."""
    fods_path = Path(fods_path); dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    doc = parse_fods_strict(fods_path)
    sheets = doc.get("sheets", []) if isinstance(doc, dict) else []
    paragraphs = []
    if sheets and sheet_index < len(sheets):
        sheet = sheets[sheet_index]
        for row in sheet.get("rows", []):
            parts = []
            for cell in row.get("cells", []):
                val = str(cell.get("value", "")) if cell.get("value") is not None else ""
                parts.append(val)
            paragraphs.append(separator.join(parts))
    write_abw({"is_abw": True, "paragraphs": paragraphs}, dest_path)
    return len(paragraphs)
__all__ = ["fods_to_abw"]