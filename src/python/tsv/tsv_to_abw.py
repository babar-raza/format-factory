from __future__ import annotations
from pathlib import Path
from tsv.tsv_parser import parse_tsv_strict
from abw.abw_codec import write_abw
def tsv_to_abw(tsv_path, dest_path, *, separator=" | ", include_header=True):
    """Convert TSV to ABW, one paragraph per row."""
    tsv_path = Path(tsv_path); dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    result = parse_tsv_strict(tsv_path)
    headers = result.get("headers") or []
    data_rows = result.get("rows") or []
    paragraphs = []
    if include_header and headers:
        paragraphs.append(separator.join(str(h) for h in headers))
    for row in data_rows:
        paragraphs.append(separator.join(str(v) for v in row))
    write_abw({"is_abw": True, "paragraphs": paragraphs}, dest_path)
    return len(paragraphs)
__all__ = ["tsv_to_abw"]