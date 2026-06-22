"""map_facts_to_tests.py — Cross-reference FACT-* ids with test files.

Scans tests/python/{format_id}/**/*.py for FACT-* references.

Usage:
    python map_facts_to_tests.py --format fods [--out path.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_FACT_PATTERN = re.compile(r"\bFACT-([A-Z]+)-(?:EX-)?(\d+)\b")


def scan_test_refs(format_id: str, tests_root: Path | None = None) -> dict[str, list[str]]:
    """Scan tests/python/{format_id}/**/*.py for FACT-{FORMAT}-* references.

    Returns {fact_id: [relative_path, ...]} for all files containing a match.
    """
    tests_root = tests_root or (_REPO_ROOT / "tests" / "python")
    fmt_dir = tests_root / format_id.lower()
    if not fmt_dir.is_dir():
        return {}

    results: dict[str, list[str]] = {}
    prefix_upper = f"FACT-{format_id.upper()}-"

    for py_file in fmt_dir.rglob("*.py"):
        if "__pycache__" in py_file.parts:
            continue
        try:
            text = py_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        found = set()
        for m in _FACT_PATTERN.finditer(text):
            full_id = m.group(0)
            if full_id.startswith(prefix_upper.rstrip("-")):
                found.add(full_id)
        for fid in found:
            rel = str(py_file.relative_to(_REPO_ROOT)).replace("\\", "/")
            results.setdefault(fid, [])
            if rel not in results[fid]:
                results[fid].append(rel)

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Map FACT-* ids to test files")
    parser.add_argument("--format", required=True, dest="format_id")
    parser.add_argument("--out", help="Output JSON path (default: stdout)")
    args = parser.parse_args()

    refs = scan_test_refs(args.format_id)
    output = json.dumps(refs, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(output + "\n", encoding="utf-8")
        print(f"Written: {args.out}", file=sys.stderr)
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
