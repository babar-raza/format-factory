"""Contract staleness checker + self-healing task emitter (L30).

Detects the healing conditions the supervisor must react to and emits
machine-readable repair tasks:

  NO_CONTRACT       — format has product source + family mapping but no contract
  STALE             — contract input_digests no longer match committed stores
  BLOCKED           — registry says BLOCKED_NEEDS_AUTHORITY (seeding required)
  UNRECONCILED      — contract + product source but no reconciliation report
  SHALLOW           — quality verdict BLOCKED/NEEDS_REVIEW in registry

Registry freshness states are updated (STALE flag) — contracts are NEVER
silently regenerated; repair tasks route to the owning skill.

Output: .local/supervisor/contract-repair-tasks.json (consumed by the
autonomous cycle / work-item generation as source 'format_contract_healing').
Exit codes: 0 (always; findings are data, not failures).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import contract_registry
import contract_validator as cv
import stores
from canonical_io import load_yaml

OUT_PATH = stores.REPO_ROOT / ".local" / "supervisor" / "contract-repair-tasks.json"


def _task(kind: str, fmt: str, skill: str, detail: str) -> dict:
    return {
        "task_id": f"FCLHEAL-{fmt.upper()}-{kind}",
        "source": "format_contract_healing",
        "condition": kind,
        "format_id": fmt,
        "owning_skill": skill,
        "detail": detail,
    }


def check_all(*, refresh: bool = False) -> dict:
    family_map = stores.load_family_map()
    tasks: list[dict] = []
    refreshed: list[str] = []
    for fmt in sorted(family_map):
        has_source = (stores.REPO_ROOT / "src" / "python" / fmt).is_dir()
        contract = load_yaml(stores.contract_path(fmt))
        entry = contract_registry.get_entry(fmt) or {}

        if contract is None:
            if entry.get("state") == "BLOCKED_NEEDS_AUTHORITY":
                tasks.append(_task(
                    "BLOCKED", fmt, "research-format-contract-sources",
                    f"readiness {entry.get('readiness_score')} < {entry.get('readiness_threshold')}; "
                    f"missing {entry.get('missing_categories')}"))
            elif has_source:
                tasks.append(_task(
                    "NO_CONTRACT", fmt, "compile-format-contract",
                    "format has product source and family mapping but no contract"))
            continue

        if cv.check_freshness(contract)["result"] != "PASS":
            if refresh:
                try:
                    import contract_compiler as cc
                    status, doc = cc.compile_contract(fmt)
                    if doc:
                        from canonical_io import canonical_write
                        canonical_write(stores.contract_path(fmt), doc)
                        refreshed.append(fmt)
                        continue
                except Exception as exc:
                    tasks.append(_task(
                        "STALE", fmt, "refresh-format-contract",
                        f"auto-refresh failed ({exc}); manual refresh required"))
                    continue
            contract_registry.update_entry(fmt, state="STALE")
            tasks.append(_task(
                "STALE", fmt, "refresh-format-contract",
                "input_digests drifted from committed stores; refresh (never silent regeneration)"))

        if has_source:
            recon = stores.REPO_ROOT / "reports" / "format-contract-layer" / f"{fmt}-reconciliation.json"
            if not recon.is_file():
                tasks.append(_task(
                    "UNRECONCILED", fmt, "reconcile-contract-capabilities",
                    "contract + product source without reconciliation report"))

        if entry.get("quality_verdict") in ("BLOCKED", "NEEDS_REVIEW"):
            tasks.append(_task(
                "SHALLOW", fmt, "review-format-contract",
                f"quality {entry.get('quality_score')} verdict {entry.get('quality_verdict')}"))

    report = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "tools/format_contract/staleness_checker.py",
        "task_count": len(tasks),
        "tasks": tasks,
    }
    if refreshed:
        report["refreshed"] = refreshed
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh", action="store_true",
        help="Auto-recompile stale contracts instead of emitting STALE tasks")
    args = parser.parse_args(argv)
    report = check_all(refresh=args.refresh)
    by_kind: dict[str, int] = {}
    for task in report["tasks"]:
        by_kind[task["condition"]] = by_kind.get(task["condition"], 0) + 1
    refreshed = report.get("refreshed", [])
    if refreshed:
        print(f"[fcl-heal] auto-refreshed {len(refreshed)} contracts: {', '.join(refreshed)}")
    print(f"[fcl-heal] {report['task_count']} repair tasks -> {OUT_PATH} ({by_kind})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
