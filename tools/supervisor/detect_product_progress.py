"""Detect stalled product-factory capability progress from local snapshots."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DEFAULT_LEDGER = REPO_ROOT / "reports" / "r90" / "product-code-change-ledger.json"
DEFAULT_MATRIX = REPO_ROOT / "product-capability-matrix" / "poc-targets.yaml"
DEFAULT_POLICIES = REPO_ROOT / ".supervisor" / "policies.yaml"


def _load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)


def _capability_state(matrix: dict) -> dict[str, Any]:
    state: dict[str, Any] = {}
    for group in ("commercial_net_products", "foss_reduced_products"):
        for product in matrix.get(group, []):
            name = str(product.get("format", "unknown"))
            key = f"{group}:{name}"
            state[key] = {
                "dotnet_status": product.get("dotnet_status", {}),
                "python_status": product.get("python_status", product.get("python_foss_status", {})),
                "dogfood_status": product.get("dogfood_status", {}),
                "next_action": product.get("next_action"),
            }
    return state


def build_snapshot(ledger: dict, matrix: dict, captured_at: str | None = None) -> dict:
    payload = {
        "ledger_entry_ids": [entry.get("entry_id") for entry in ledger.get("entries", [])],
        "capabilities": _capability_state(matrix),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "captured_at": captured_at or datetime.now(timezone.utc).isoformat(),
        "fingerprint": hashlib.sha256(encoded).hexdigest(),
        **payload,
    }


def detect_no_progress(snapshots: list[dict], threshold: int) -> dict:
    if threshold < 1:
        raise ValueError("threshold must be at least 1")
    fingerprints = [snapshot.get("fingerprint") for snapshot in snapshots]
    stagnant_intervals = 0
    for previous, current in zip(reversed(fingerprints[:-1]), reversed(fingerprints[1:])):
        if previous != current:
            break
        stagnant_intervals += 1
    return {
        "no_progress": stagnant_intervals >= threshold,
        "threshold": threshold,
        "snapshot_count": len(snapshots),
        "stagnant_intervals": stagnant_intervals,
        "latest_fingerprint": fingerprints[-1] if fingerprints else None,
        "status": "NO_PROGRESS" if stagnant_intervals >= threshold else "PROGRESS_OR_BELOW_THRESHOLD",
    }


def threshold_from_policies(path: Path) -> int:
    policies = _load(path) or {}
    return int(policies.get("autonomous_continuation", {}).get("no_progress_max_consecutive", 2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", action="append", type=Path, default=[])
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--previous-ledger", type=Path)
    parser.add_argument("--previous-matrix", type=Path)
    parser.add_argument("--policies", type=Path, default=DEFAULT_POLICIES)
    parser.add_argument("--threshold", type=int)
    parser.add_argument("--write-snapshot", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    threshold = args.threshold or threshold_from_policies(args.policies)
    snapshots = [_load(path) for path in args.snapshot]
    if args.previous_ledger or args.previous_matrix:
        if not args.previous_ledger or not args.previous_matrix:
            parser.error("--previous-ledger and --previous-matrix must be supplied together")
        snapshots.append(build_snapshot(_load(args.previous_ledger), _load(args.previous_matrix)))
    current = build_snapshot(_load(args.ledger), _load(args.matrix))
    snapshots.append(current)
    if args.write_snapshot:
        args.write_snapshot.parent.mkdir(parents=True, exist_ok=True)
        args.write_snapshot.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")

    result = detect_no_progress(snapshots, threshold)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"PRODUCT_PROGRESS: {result['status']}")
        print(f"  stagnant_intervals: {result['stagnant_intervals']}/{result['threshold']}")
    return 2 if result["no_progress"] else 0


if __name__ == "__main__":
    sys.exit(main())
