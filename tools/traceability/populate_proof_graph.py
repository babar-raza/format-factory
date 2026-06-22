"""populate_proof_graph.py — Build bidirectional FACT-ID proof graph for a format.

Combines scan_fact_refs + map_facts_to_tests output into a traceability JSON:
    .local/capability-proof-graph/{format}-traceability.json

Each entry: {fact_id: {product_files: [...], test_files: [...]}}

Usage:
    python populate_proof_graph.py --format fods
    python populate_proof_graph.py --format fods --format zst
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_OUT_DIR = _REPO_ROOT / ".local" / "capability-proof-graph"

# Add tools/traceability to sys.path for sibling imports
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from scan_fact_refs import scan_source_refs  # noqa: E402
from map_facts_to_tests import scan_test_refs  # noqa: E402


def build_proof_graph(format_id: str) -> dict:
    """Scan src + tests for FACT-* refs, merge into a traceability dict."""
    product_refs = scan_source_refs(format_id)
    test_refs = scan_test_refs(format_id)

    all_fact_ids = sorted(set(product_refs) | set(test_refs))
    graph: dict[str, dict] = {}
    for fid in all_fact_ids:
        graph[fid] = {
            "product_files": sorted(product_refs.get(fid, [])),
            "test_files": sorted(test_refs.get(fid, [])),
        }

    return {
        "format_id": format_id,
        "generated_at": date.today().isoformat(),
        "fact_count": len(graph),
        "facts": graph,
    }


def populate(format_id: str) -> Path:
    """Build and write the proof graph. Returns output path."""
    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = _OUT_DIR / f"{format_id.lower()}-traceability.json"
    data = build_proof_graph(format_id)
    out_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build FACT-ID proof graph")
    parser.add_argument("--format", action="append", dest="formats",
                        metavar="FORMAT_ID", required=True,
                        help="Format to process (repeatable: --format fods --format zst)")
    args = parser.parse_args()

    ok = True
    for fmt in args.formats:
        out = populate(fmt)
        data = json.loads(out.read_text(encoding="utf-8"))
        n = data["fact_count"]
        sample = list(data["facts"].items())[:3]
        coverage_ok = any(
            v["product_files"] and v["test_files"] for v in data["facts"].values()
        )
        print(f"[{fmt}] {n} facts traced → {out}", file=sys.stderr)
        for fid, v in sample:
            print(f"  {fid}: {len(v['product_files'])} src, {len(v['test_files'])} tests", file=sys.stderr)
        if not coverage_ok:
            print(f"  WARN: no fact has both product_file and test_file for {fmt}", file=sys.stderr)
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
