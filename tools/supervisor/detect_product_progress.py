"""Detect stalled product-factory capability progress from local snapshots.

v2 improvements (R100):
- Per-category breakdown: load, edit, save, export, dogfood, package
- category_progress() returns per-category done/total counts

v3 improvements (R101):
- classify_progress_type(): returns TOOLING_PROGRESS, EVIDENCE_ONLY, PRODUCT_PROGRESS, BLOCKED_WITH_REASON, or NO_PROGRESS
- Examines both capability matrix and lane ledger to distinguish tooling-only from product progress
"""

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


CAPABILITY_CATEGORIES = {
    "load": ("load", "parse", "read", "open"),
    "edit": ("edit", "set", "add", "remove", "update"),
    "save": ("save", "write"),
    "export": ("export", "to_csv", "to_html", "to_json", "to_text"),
    "dogfood": ("dogfood",),
    "package": ("package", "wheel", "install", "pip"),
}

DONE_STATUSES = {"DONE", "true", "PASS", "IMPLEMENTED"}


def category_progress(matrix: dict) -> dict[str, dict[str, int]]:
    """Return per-category done/total counts from the capability matrix."""
    counts: dict[str, dict[str, int]] = {
        cat: {"done": 0, "total": 0} for cat in CAPABILITY_CATEGORIES
    }
    counts["other"] = {"done": 0, "total": 0}

    for group in ("commercial_net_products", "foss_reduced_products"):
        for product in matrix.get(group, []):
            for status_key in ("dotnet_status", "python_status", "python_foss_status", "dogfood_status"):
                statuses = product.get(status_key, {})
                if not isinstance(statuses, dict):
                    continue
                for cap_name, cap_value in statuses.items():
                    val = str(cap_value)
                    matched = False
                    for cat, keywords in CAPABILITY_CATEGORIES.items():
                        if any(kw in cap_name.lower() for kw in keywords):
                            counts[cat]["total"] += 1
                            if val in DONE_STATUSES:
                                counts[cat]["done"] += 1
                            matched = True
                            break
                    if not matched:
                        counts["other"]["total"] += 1
                        if val in DONE_STATUSES:
                            counts["other"]["done"] += 1

    return counts


def classify_progress_type(
    category_counts: dict[str, dict[str, int]],
    lane_ledger: dict[str, Any] | None = None,
    blockers: list[str] | None = None,
) -> dict[str, Any]:
    """Classify the type of progress made in a sprint.

    Returns one of:
    - PRODUCT_PROGRESS: at least one product capability moved to DONE
    - TOOLING_PROGRESS: only tooling/acceleration lanes, no product caps changed
    - EVIDENCE_ONLY: lanes completed but no capability or tooling changes
    - BLOCKED_WITH_REASON: explicit blockers prevent progress
    - NO_PROGRESS: nothing happened
    """
    if blockers:
        return {
            "progress_type": "BLOCKED_WITH_REASON",
            "reason": "; ".join(blockers),
        }

    total_done = sum(c["done"] for c in category_counts.values())
    total_caps = sum(c["total"] for c in category_counts.values())

    lanes = (lane_ledger or {}).get("lanes", [])
    completed_lanes = [l for l in lanes if l.get("status") == "completed"]
    tooling_lanes = [l for l in completed_lanes if l.get("stream_id") in ("acceleration", "supervisor")]
    product_lanes = [l for l in completed_lanes if l.get("stream_id") not in ("acceleration", "supervisor")]

    if total_done > 0 and product_lanes:
        return {
            "progress_type": "PRODUCT_PROGRESS",
            "capabilities_done": total_done,
            "capabilities_total": total_caps,
            "product_lanes": len(product_lanes),
        }

    if tooling_lanes and not product_lanes:
        return {
            "progress_type": "TOOLING_PROGRESS",
            "tooling_lanes": len(tooling_lanes),
        }

    if completed_lanes:
        return {
            "progress_type": "EVIDENCE_ONLY",
            "completed_lanes": len(completed_lanes),
        }

    return {
        "progress_type": "NO_PROGRESS",
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
