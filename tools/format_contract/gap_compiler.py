"""Contract gap compiler — converts reconciliation gaps into canonical
gap-ledger entries (L30 -> L03 -> L14 consumption chain, HO-010/HO-011).

Gap records conform to schemas/capability/capability_gap.schema.json and are
appended to reports/capability-layer/gap-ledger.json, where the ACTIVE
supervisor chain (capability_feature_compiler.py, called from
autonomous_cycle.py) already converts open gaps into next-work-items. Contract
origin travels in `related_capability_id` (the contract capability ID) and
`notes` (contract path + depth delta) — no schema change, no bypass.

Idempotent: rerunning updates existing GAP-FCL-* entries in place by gap_id;
closed capabilities (no depth gap) retire their ledger entries.

Exit codes: 0 ok · 1 error.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import stores

GAP_LEDGER = stores.REPO_ROOT / "reports" / "capability-layer" / "gap-ledger.json"
RECON_DIR = stores.REPO_ROOT / "reports" / "format-contract-layer"

_LEVEL_PRIORITY = {"MUST": "P1", "SHOULD": "P2", "MAY": "P3"}


def _gap_record(format_id: str, obs: dict, seq: int) -> dict:
    fmt_uc = format_id.upper()
    cap_id = obs["capability_id"]
    return {
        "gap_id": f"GAP-FCL-{fmt_uc}-{seq:03d}",
        "format": fmt_uc,
        "product_type": "foss_reduced",
        "capability_name": f"contract:{cap_id}",
        "current_state": obs["observed_status"].lower(),
        "gap_type": "missing_tests" if obs["observed_status"] == "IMPLEMENTED_UNPROVEN"
                    else "missing_implementation",
        "status": "open",
        "blocks_poc": False,
        "blocks_readiness": obs.get("level") == "MUST",
        "commercial_impact": "medium" if obs.get("level") == "MUST" else "low",
        "foss_impact": "high" if obs.get("level") == "MUST" else "medium",
        "priority": _LEVEL_PRIORITY.get(obs.get("level"), "P3"),
        "owning_lane": "product_deepening",
        "suggested_taskcard": f"TC-FCLGAP-{fmt_uc}-{seq:03d}",
        "suggested_verification": (
            f"Raise observed depth from {obs['observed_depth']} to required "
            f"{obs['depth_required']} with executed tests; rerun contract_reconciler"
        ),
        "related_capability_id": cap_id,
        "notes": (
            f"L30 contract gap: shared/format-contracts/{format_id}.yaml capability {cap_id} "
            f"requires depth {obs['depth_required']}, observed {obs['observed_depth']} "
            f"({obs['observed_status']}). Origin: contract_reconciler."
        ),
    }


def compile_gaps(format_id: str) -> dict:
    recon_path = RECON_DIR / f"{format_id}-reconciliation.json"
    if not recon_path.is_file():
        raise stores.StoreError(f"no reconciliation report: {recon_path} (run contract_reconciler first)")
    recon = json.loads(recon_path.read_text(encoding="utf-8"))

    gap_caps = sorted(
        (o for o in recon["capabilities"] if o["gap_depth"] > 0 or o["observed_status"] == "NOT_STARTED"),
        key=lambda o: o["capability_id"],
    )
    fresh = [_gap_record(format_id, obs, i + 1) for i, obs in enumerate(gap_caps)]

    ledger = json.loads(GAP_LEDGER.read_text(encoding="utf-8"))
    prefix = f"GAP-FCL-{format_id.upper()}-"
    kept = [g for g in ledger["gaps"] if not str(g.get("gap_id", "")).startswith(prefix)]
    replaced = len(ledger["gaps"]) - len(kept)
    ledger["gaps"] = kept + fresh
    ledger["total_gaps"] = len(ledger["gaps"])
    ledger["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    GAP_LEDGER.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")

    out = RECON_DIR / f"{format_id}-contract-gaps.json"
    out.write_text(json.dumps({"format_id": format_id, "gaps": fresh}, indent=2) + "\n",
                   encoding="utf-8")
    return {"emitted": len(fresh), "replaced_previous": replaced,
            "ledger_total": ledger["total_gaps"], "report": str(out)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format-id", required=True)
    args = parser.parse_args(argv)
    try:
        result = compile_gaps(args.format_id.lower())
    except (stores.StoreError, FileNotFoundError) as exc:
        print(f"[fcl-gaps] ERROR {exc}", file=sys.stderr)
        return 1
    print(f"[fcl-gaps] {args.format_id}: {result['emitted']} contract gaps in canonical ledger "
          f"(replaced {result['replaced_previous']}; ledger total {result['ledger_total']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
