"""scan_fact_refs.py — Scan src/python/**/*.py for FACT-* canonical ID references.

Outputs a JSON dict: {fact_id: [list of source file paths (relative to repo root)]}

Usage:
    python scan_fact_refs.py --format fods [--out path.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_FACT_PATTERN = re.compile(r"\bFACT-([A-Z]+)-(?:EX-)?(\d+)\b")


def scan_source_refs(format_id: str, src_root: Path | None = None) -> dict[str, list[str]]:
    """Scan src/python/{format_id}/**/*.py for FACT-{FORMAT}-* references.

    Returns {fact_id: [relative_path, ...]} for all files containing a match.
    """
    src_root = src_root or (_REPO_ROOT / "src" / "python")
    fmt_dir = src_root / format_id.lower()
    if not fmt_dir.is_dir():
        return {}

    results: dict[str, list[str]] = {}
    prefix = f"FACT-{format_id.upper()}-"

    for py_file in fmt_dir.rglob("*.py"):
        if "build" in py_file.parts or "__pycache__" in py_file.parts:
            continue
        try:
            text = py_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        found = set()
        for m in _FACT_PATTERN.finditer(text):
            fid = f"FACT-{m.group(1)}-{m.group(2)}"
            if fid.startswith(prefix.rstrip("-")):
                full_id = m.group(0)
                found.add(full_id)
        for fid in found:
            rel = str(py_file.relative_to(_REPO_ROOT)).replace("\\", "/")
            results.setdefault(fid, [])
            if rel not in results[fid]:
                results[fid].append(rel)

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan source files for FACT-* refs")
    parser.add_argument("--format", required=True, dest="format_id", help="Format ID (e.g. fods)")
    parser.add_argument("--out", help="Output JSON path (default: stdout)")
    args = parser.parse_args()

    refs = scan_source_refs(args.format_id)
    output = json.dumps(refs, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(output + "\n", encoding="utf-8")
        print(f"Written: {args.out}", file=sys.stderr)
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
