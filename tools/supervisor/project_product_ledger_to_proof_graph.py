"""
project_product_ledger_to_proof_graph.py — Deterministic Proof Graph Projection

Reads reports/r90/product-code-change-ledger.json and emits a proof graph
as stable JSONL nodes and edges.

This implements Option B from the autonomous execution contract:
  - Product code change ledger is the canonical operational record
  - A deterministic proof graph projection MUST be generated from the ledger
  - "Ledger only" without projection is NOT accepted as POC proof

Output:
  reports/autonomous-system-audit/projected-proof-graph/nodes.jsonl
  reports/autonomous-system-audit/projected-proof-graph/edges.jsonl
  reports/autonomous-system-audit/projected-proof-graph/projection-report.json
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent

LEDGER_PATH = REPO_ROOT / "reports" / "r90" / "product-code-change-ledger.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "reports" / "autonomous-system-audit" / "projected-proof-graph"


# Product name normalization map
PRODUCT_NORMALIZE = {
    "fods .net": "fods",
    "fodt .net": "fodt",
    "netpbm .net": "netpbm",
    "netpbm": "netpbm",
    "netpbm python foss": "netpbm_python",
    "zst": "zst",
    "zst python foss": "zst",
    "sylk python foss": "sylk",
    "sylk": "sylk",
    "dif python foss": "dif",
    "dif": "dif",
    "ppm python foss": "netpbm_python",
    "pbm python foss": "netpbm_python",
    "pgm python foss": "netpbm_python",
}


def _normalize_product(raw: str) -> str:
    """Normalize product name to canonical key."""
    return PRODUCT_NORMALIZE.get(raw.lower().strip(), raw.lower().replace(" ", "_"))


def _stable_node_id(node_type: str, label: str) -> str:
    """Produce a deterministic stable ID for a node."""
    raw = f"{node_type}::{label}"
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def _load_ledger(ledger_path: Path) -> list[dict]:
    """Load and validate the product code change ledger."""
    if not ledger_path.exists():
        raise FileNotFoundError(f"Ledger not found: {ledger_path}")
    data = json.loads(ledger_path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict):
        entries = data.get("entries", data.get("records", []))
    else:
        raise ValueError(f"Unexpected ledger format: {type(data)}")
    if not entries:
        raise ValueError("Ledger is empty")
    return entries


def project_ledger(
    ledger_path: Path = LEDGER_PATH,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    """Project the product code change ledger into a proof graph.

    Returns:
      report dict with node_count, edge_count, products, status
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    entries = _load_ledger(ledger_path)

    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    errors: list[str] = []
    product_counts: dict[str, int] = {}

    def add_node(node_type: str, label: str, **attrs) -> str:
        nid = _stable_node_id(node_type, label)
        if nid not in nodes:
            nodes[nid] = {"node_id": nid, "type": node_type, "label": label, **attrs}
        return nid

    def add_edge(src_id: str, dst_id: str, rel: str, entry_id: str) -> None:
        edges.append({
            "src_node_id": src_id,
            "dst_node_id": dst_id,
            "relationship": rel,
            "entry_id": entry_id,
        })

    for entry in entries:
        entry_id = entry.get("entry_id", "UNKNOWN")
        product_raw = entry.get("product", "")
        if not product_raw:
            errors.append(f"{entry_id}: missing 'product' field")
            continue

        product_key = _normalize_product(product_raw)

        # --- Product node ---
        product_nid = add_node("product", product_key, raw_name=product_raw)
        product_counts[product_key] = product_counts.get(product_key, 0) + 1

        # --- Capability nodes ---
        for cap_ref in entry.get("capability_refs", []):
            cap_nid = add_node("capability", cap_ref)
            add_edge(product_nid, cap_nid, "HAS_CAPABILITY", entry_id)

        # --- API symbol nodes ---
        for sym in entry.get("api_symbols", []):
            sym_nid = add_node("api_symbol", f"{product_key}::{sym}")
            add_edge(product_nid, sym_nid, "EXPOSES_API", entry_id)

        # --- Source file nodes ---
        for sf in entry.get("source_files", []):
            sf_path = sf.get("path", "") if isinstance(sf, dict) else str(sf)
            if sf_path:
                sf_nid = add_node("source_file", sf_path)
                add_edge(product_nid, sf_nid, "HAS_SOURCE", entry_id)

        # --- Test file nodes ---
        for tf in entry.get("test_files", []):
            tf_path = tf.get("path", "") if isinstance(tf, dict) else str(tf)
            if tf_path:
                tf_nid = add_node("test_file", tf_path)
                add_edge(product_nid, tf_nid, "HAS_TEST", entry_id)

        # --- Raw log nodes ---
        raw_log = entry.get("raw_log", "")
        if raw_log:
            log_nid = add_node("raw_log", raw_log)
            add_edge(product_nid, log_nid, "HAS_LOG", entry_id)

        # --- Changed file nodes ---
        for cf in entry.get("changed_files", []):
            cf_path = cf.get("path", "") if isinstance(cf, dict) else str(cf)
            if cf_path:
                cf_nid = add_node("changed_file", cf_path)
                add_edge(product_nid, cf_nid, "CHANGED", entry_id)

        # --- Delta / capability delta ---
        result = entry.get("result", entry.get("validation_result", ""))
        if result:
            delta_label = f"{product_key}::{entry_id}::delta"
            delta_nid = add_node("capability_delta", delta_label, result=result)
            add_edge(product_nid, delta_nid, "HAS_DELTA", entry_id)

    # Write nodes.jsonl
    nodes_path = output_dir / "nodes.jsonl"
    nodes_path.write_text(
        "\n".join(json.dumps(n) for n in nodes.values()) + "\n",
        encoding="utf-8",
    )

    # Write edges.jsonl
    edges_path = output_dir / "edges.jsonl"
    edges_path.write_text(
        "\n".join(json.dumps(e) for e in edges) + "\n",
        encoding="utf-8",
    )

    # Pre-index edges by source node ID for O(1) lookup (avoids O(P×N×E) scan)
    from collections import defaultdict
    _edges_by_src: dict[str, set[str]] = defaultdict(set)
    for e in edges:
        _edges_by_src[e["src_node_id"]].add(e["dst_node_id"])

    # Per-product coverage summary
    per_product_coverage: dict[str, dict] = {}
    for product_key in product_counts:
        product_nid = _stable_node_id("product", product_key)
        dst_ids = _edges_by_src.get(product_nid, set())
        product_sources = [
            n for nid, n in nodes.items()
            if n["type"] == "source_file" and nid in dst_ids
        ]
        product_tests = [
            n for nid, n in nodes.items()
            if n["type"] == "test_file" and nid in dst_ids
        ]
        product_logs = [
            n for nid, n in nodes.items()
            if n["type"] == "raw_log" and nid in dst_ids
        ]
        per_product_coverage[product_key] = {
            "ledger_entries": product_counts[product_key],
            "source_nodes": len(product_sources),
            "test_nodes": len(product_tests),
            "log_nodes": len(product_logs),
        }

    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "ledger_path": str(ledger_path),
        "ledger_entry_count": len(entries),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "error_count": len(errors),
        "errors": errors[:10],
        "products": list(product_counts.keys()),
        "per_product_coverage": per_product_coverage,
        "product_counts": product_counts,
        "nodes_path": str(nodes_path),
        "edges_path": str(edges_path),
        "status": "SUCCESS" if not errors else "SUCCESS_WITH_WARNINGS",
    }

    report_path = output_dir / "projection-report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return report


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Project product ledger to proof graph")
    parser.add_argument("--ledger", default=str(LEDGER_PATH), help="Ledger path")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory")
    args = parser.parse_args()

    report = project_ledger(
        ledger_path=Path(args.ledger),
        output_dir=Path(args.output_dir),
    )
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["status"].startswith("SUCCESS") else 1)


if __name__ == "__main__":
    main()
