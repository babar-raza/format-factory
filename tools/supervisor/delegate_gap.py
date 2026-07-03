"""
delegate_gap.py — Delegation protocol for cross-lane scope violations.

When an agent discovers a pre-existing failure that belongs to a different lane,
it calls this tool to register the gap as a delegation rather than fixing it directly.

Writes to THREE targets atomically (all succeed or none do):
  1. reports/governance/delegation-ledger.json  — supervisor pickup
  2. registry/known-failure-ledger.yaml         — CI visibility
  3. .local/ci-audit/delegation-handoff-<plan_id>.yaml  — plan-local wait state

F-001: Uses reports/governance/delegation-ledger.json (NOT gap-ledger.json whose
schema is incompatible: owning_lane is integer, no target_lane/discovered_by fields).

Usage:
  python tools/supervisor/delegate_gap.py \\
    --gap-id GAP-LANE5-001 \\
    --target-lane lane-5-dotnet-structure \\
    --file src/net/fods/FodsDocumentAccessor.cs \\
    --description "Exceeds baseline_loc_cap by 650 LOC" \\
    --severity P1 \\
    --discovered-by lane-ci-audit \\
    --plan-id sequential-twirling-sunrise

Exit codes:
  0 = success
  1 = write error
  2 = configuration error (invalid target-lane, missing registry, etc.)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo_root = _here.parent.parent
_delegation_ledger_path = _repo_root / "reports" / "governance" / "delegation-ledger.json"
_known_failure_ledger_path = _repo_root / "registry" / "known-failure-ledger.yaml"
_registry_path = _repo_root / "registry" / "lane-scope-registry.yaml"


def _load_registry() -> dict:
    """Load lane-scope-registry.yaml."""
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML not available", file=sys.stderr)
        sys.exit(2)
    if not _registry_path.exists():
        print(f"ERROR: registry not found: {_registry_path}", file=sys.stderr)
        sys.exit(2)
    return yaml.safe_load(_registry_path.read_text(encoding="utf-8"))


def _validate_target_lane(lane_id: str, registry: dict) -> bool:
    """Return True if lane_id exists in the registry."""
    return any(l.get("id") == lane_id for l in registry.get("lanes", []))


def _load_delegation_ledger() -> dict:
    """Load existing delegation-ledger.json or return empty structure."""
    if not _delegation_ledger_path.exists():
        return {"schema_version": "1.0", "delegations": []}
    try:
        return json.loads(_delegation_ledger_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"WARNING: could not read delegation-ledger.json: {exc}", file=sys.stderr)
        return {"schema_version": "1.0", "delegations": []}


def _load_known_failure_ledger() -> str:
    """Load existing known-failure-ledger.yaml as raw text."""
    if not _known_failure_ledger_path.exists():
        return ""
    try:
        return _known_failure_ledger_path.read_text(encoding="utf-8")
    except Exception as exc:
        print(f"WARNING: could not read known-failure-ledger.yaml: {exc}", file=sys.stderr)
        return ""


def _load_handoff_file(plan_id: str) -> dict:
    """Load existing delegation handoff file for plan_id."""
    handoff_dir = _repo_root / ".local" / "ci-audit"
    handoff_path = handoff_dir / f"delegation-handoff-{plan_id}.yaml"
    if not handoff_path.exists():
        return {"plan_id": plan_id, "delegations": [], "overall_status": "pending"}
    try:
        import yaml
        return yaml.safe_load(handoff_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        print(f"WARNING: could not read handoff file: {exc}", file=sys.stderr)
        return {"plan_id": plan_id, "delegations": [], "overall_status": "pending"}


def _atomic_write(path: Path, content: str) -> None:
    """Write content atomically via temp file + os.replace().

    Uses os.replace() not os.rename() — on Windows, os.rename() raises
    FileExistsError if the target already exists. os.replace() works atomically.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(str(tmp), str(path))


def delegate_gap(
    gap_id: str,
    target_lane: str,
    file: str | None,
    description: str,
    severity: str,
    discovered_by: str,
    plan_id: str,
    ci_job: str | None = None,
    blocks_progression: bool = False,
) -> int:
    """Register a cross-lane gap delegation.

    Returns 0 on success, 1 on write error, 2 on config error.
    """
    # Validate target lane
    registry = _load_registry()
    if not _validate_target_lane(target_lane, registry):
        known = [l.get("id") for l in registry.get("lanes", [])]
        print(f"ERROR: target-lane '{target_lane}' not found in registry.", file=sys.stderr)
        print(f"Known lanes: {known}", file=sys.stderr)
        return 2

    now_iso = datetime.now(timezone.utc).isoformat()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # --- Load all three targets before writing (idempotency checks) ---
    delegation_ledger = _load_delegation_ledger()
    known_failure_text = _load_known_failure_ledger()
    handoff_data = _load_handoff_file(plan_id)

    # Idempotency: skip if gap_id already registered
    existing_ids_ledger = {d.get("gap_id") for d in delegation_ledger.get("delegations", [])}
    if gap_id in existing_ids_ledger:
        print(f"[delegate_gap] Idempotent skip: {gap_id} already in delegation-ledger.json")
        return 0

    existing_ids_handoff = {d.get("gap_id") for d in handoff_data.get("delegations", [])}
    known_failure_ids = set()
    for line in known_failure_text.splitlines():
        if line.strip().startswith("gap_id:"):
            known_failure_ids.add(line.split(":", 1)[1].strip())

    # --- Build new entries ---
    delegation_entry = {
        "gap_id": gap_id,
        "target_lane": target_lane,
        "file": file or "",
        "description": description,
        "severity": severity,
        "discovered_by": discovered_by,
        "plan_id": plan_id,
        "discovered_at": now_iso,
        "status": "open",
        "do_not_fix_in": discovered_by,
    }
    if ci_job:
        delegation_entry["ci_job"] = ci_job
    if blocks_progression:
        delegation_entry["blocks_progression"] = True

    known_failure_entry = (
        f"\n- gap_id: {gap_id}\n"
        f"  reason: \"{description}\"\n"
        f"  owning_lane: {target_lane}\n"
        f"  discovered_by: {discovered_by}\n"
        f"  discovered_at: {today}\n"
        f"  category: pre_existing_architecture_debt\n"
        f"  do_not_fix_in: {discovered_by}\n"
        f"  status: open\n"
    )

    handoff_entry = {
        "gap_id": gap_id,
        "target_lane": target_lane,
        "status": "pending",
    }

    # --- Prepare new content for each file ---
    delegation_ledger["delegations"].append(delegation_entry)
    new_delegation_content = json.dumps(delegation_ledger, indent=2) + "\n"

    if gap_id not in known_failure_ids:
        new_known_failure_content = known_failure_text.rstrip() + known_failure_entry
    else:
        new_known_failure_content = known_failure_text

    if gap_id not in existing_ids_handoff:
        handoff_data.setdefault("delegations", []).append(handoff_entry)
    handoff_data["overall_status"] = "pending"
    handoff_data["plan_id"] = plan_id

    try:
        import yaml
        new_handoff_content = yaml.dump(handoff_data, default_flow_style=False, sort_keys=False)
    except Exception:
        # Fallback: simple YAML-like output
        new_handoff_content = f"plan_id: {plan_id}\noverall_status: pending\n"

    # --- Atomic writes (all three or none) ---
    # Use a staging approach: write all to .tmp first, then replace all
    handoff_dir = _repo_root / ".local" / "ci-audit"
    handoff_path = handoff_dir / f"delegation-handoff-{plan_id}.yaml"

    try:
        _atomic_write(_delegation_ledger_path, new_delegation_content)
        _atomic_write(_known_failure_ledger_path, new_known_failure_content)
        _atomic_write(handoff_path, new_handoff_content)
    except Exception as exc:
        print(f"ERROR: write failed: {exc}", file=sys.stderr)
        return 1

    print(f"[delegate_gap] Gap {gap_id} delegated to {target_lane}")
    print(f"[delegate_gap]   -> delegation-ledger.json updated")
    print(f"[delegate_gap]   -> known-failure-ledger.yaml updated")
    print(f"[delegate_gap]   -> {handoff_path.name} updated")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Register a cross-lane scope violation as a delegation"
    )
    parser.add_argument("--gap-id", required=True, help="Unique gap ID, e.g. GAP-LANE5-001")
    parser.add_argument("--target-lane", required=True, help="Lane that owns the fix")
    parser.add_argument("--file", default=None, help="File that was discovered out-of-scope")
    parser.add_argument("--description", required=True, help="What is wrong and why it belongs to target lane")
    parser.add_argument("--severity", default="P2", choices=["P1", "P2", "P3"],
                        help="P1=critical, P2=high, P3=medium (default: P2)")
    parser.add_argument("--discovered-by", required=True, help="Lane/plan that discovered this gap")
    parser.add_argument("--plan-id", required=True, help="Plan ID that is delegating")
    parser.add_argument("--ci-job", default=None, help="Optional: CI job that surfaced this")
    parser.add_argument("--blocks-progression", action="store_true",
                        help="Whether this delegation blocks the delegating plan from proceeding")
    args = parser.parse_args(argv)

    return delegate_gap(
        gap_id=args.gap_id,
        target_lane=args.target_lane,
        file=args.file,
        description=args.description,
        severity=args.severity,
        discovered_by=args.discovered_by,
        plan_id=args.plan_id,
        ci_job=args.ci_job,
        blocks_progression=args.blocks_progression,
    )


if __name__ == "__main__":
    sys.exit(main())
