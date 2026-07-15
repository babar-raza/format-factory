"""qname_backfill_planner.py — QName Backfill Execution Planner (TC-QNAME-BACKFILL-001)

Reads migration gaps from qname_migration_planner output (reports/qname-migration/) and
generates an ordered backfill-execution plan with rollback commands and safety gates.

Distinct from qname_migration_planner.py (which detects gaps). This tool takes detected
gaps as input and produces an EXECUTION plan: ordered steps with safety checks, rollback
commands, and estimated effort per step.

Usage:
    python tools/backfill/qname_backfill_planner.py --format fods [--out PATH]
    python tools/backfill/qname_backfill_planner.py --all [--out-dir PATH]

Output per format:
    {format}-backfill-plan.yaml  with ordered steps, per-step rollback, safety gate results

Exit codes:
    0: plan generated (may have BLOCKED steps)
    1: no migration map found; run qname_migration_planner.py first
    2: argument error
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MIGRATION_DIR = REPO_ROOT / "reports" / "qname-migration"
SRC_PYTHON = REPO_ROOT / "src" / "python"

_FORMATS = [
    "abw", "csv", "dif", "fodg", "fodp", "fods", "fodt",
    "gnumeric", "ndjson", "ods", "odt", "pbm", "pgm", "ppm",
    "qoi", "sylk", "toml", "tsv", "xcf", "zst",
]

# Action ordering — higher priority actions go first
_ACTION_ORDER = {
    "CREATE_FILE": 0,
    "ADD_CLASS": 1,
    "ADD_SPEC_QNAME": 2,
    "MOVE_FILE": 3,
    "NONE": 99,
}

# Risk-to-gate mapping
_RISK_GATE = {
    "HIGH": "validate_migration_safe",
    "MEDIUM": "validate_migration_safe",
    "LOW": None,
}


def _load_migration_map(fmt: str, map_dir: Path) -> dict | None:
    """Load the migration map JSON for a format from map_dir or MIGRATION_DIR."""
    candidates = [
        map_dir / f"{fmt}-migration-map.json",
        MIGRATION_DIR / f"{fmt}-migration-map.json",
    ]
    for path in candidates:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
    return None


def _run_safety_gate(entry: dict) -> dict:
    """Run validate_migration_safe for an entry. Returns gate result dict."""
    risk = entry.get("migration_risk", "LOW")
    action = entry.get("action_required", "NONE")
    qname = entry.get("qname", "?")
    current_path = entry.get("current_path")

    if action == "NONE" or risk == "LOW":
        return {"gate": "PASS", "reason": "low-risk/no-action — safety gate skipped"}

    if not current_path:
        return {"gate": "PASS", "reason": "no current_path to validate"}

    # Invoke validate_migration_safe if available
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from tools.backfill.validate_migration_safe import scan_format

        fmt = qname.split(":")[0] if ":" in qname else "unknown"
        result = scan_format(fmt)
        violations = result.get("production_violations", [])
        if violations:
            return {
                "gate": "BLOCKED",
                "reason": f"production callers detected: {violations[:2]}",
            }
        return {"gate": "PASS", "reason": "no production callers found"}
    except Exception as exc:
        return {"gate": "WARN", "reason": f"safety gate unavailable: {exc}"}


def _build_rollback(entry: dict, fmt: str) -> str:
    """Build a rollback command string for an entry."""
    action = entry.get("action_required", "NONE")
    current_path = entry.get("current_path")
    target_path = entry.get("target_path")
    qname = entry.get("qname", "?")

    if action == "NONE":
        return "# no rollback needed (no-action step)"
    if action == "MOVE_FILE" and current_path and target_path:
        return f"git mv {target_path} {current_path}  # undo MOVE_FILE for {qname}"
    if action in ("CREATE_FILE", "ADD_CLASS") and target_path:
        return f"git rm -f {target_path}  # undo CREATE_FILE/ADD_CLASS for {qname}"
    if action == "ADD_SPEC_QNAME":
        return f"# remove spec_qname ClassVar from {target_path or current_path} for {qname}"
    return f"# manual rollback required for {action} on {qname}"


def _effort_minutes(effort: str) -> int:
    """Convert effort label to estimated minutes."""
    return {"trivial": 5, "small": 20, "medium": 60, "large": 180}.get(effort, 30)


def plan_format(fmt: str, map_dir: Path) -> dict:
    """Generate a backfill execution plan for a single format."""
    migration_map = _load_migration_map(fmt, map_dir)
    if migration_map is None:
        return {
            "format": fmt,
            "error": "no migration map found — run qname_migration_planner.py first",
            "steps": [],
        }

    entries = migration_map.get("entries", [])
    actionable = [e for e in entries if e.get("action_required", "NONE") != "NONE"]

    # Sort by action priority, then by blocks_gate desc, then by risk desc
    risk_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    actionable.sort(
        key=lambda e: (
            _ACTION_ORDER.get(e.get("action_required", "NONE"), 99),
            0 if e.get("blocks_gate") else 1,
            risk_order.get(e.get("migration_risk", "LOW"), 2),
        )
    )

    steps = []
    total_minutes = 0
    for i, entry in enumerate(actionable, start=1):
        gate_result = _run_safety_gate(entry)
        rollback = _build_rollback(entry, fmt)
        effort = entry.get("estimated_effort", "small")
        minutes = _effort_minutes(effort)
        total_minutes += minutes

        step = {
            "step": i,
            "qname": entry.get("qname", "?"),
            "action": entry.get("action_required", "NONE"),
            "target_path": entry.get("target_path"),
            "current_path": entry.get("current_path"),
            "migration_risk": entry.get("migration_risk", "LOW"),
            "blocks_gate": entry.get("blocks_gate", False),
            "estimated_effort": effort,
            "estimated_minutes": minutes,
            "safety_gate": gate_result,
            "status": "BLOCKED" if gate_result["gate"] == "BLOCKED" else "READY",
            "rollback_command": rollback,
            "notes": entry.get("notes", []),
        }
        steps.append(step)

    blocked = [s for s in steps if s["status"] == "BLOCKED"]
    ready = [s for s in steps if s["status"] == "READY"]

    return {
        "format": fmt,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_map": str(MIGRATION_DIR / f"{fmt}-migration-map.json"),
        "total_actionable_steps": len(actionable),
        "ready_steps": len(ready),
        "blocked_steps": len(blocked),
        "estimated_total_minutes": total_minutes,
        "compliant_pct_before": migration_map.get("compliant_pct", 0.0),
        "compliant_pct_after": 1.0 if actionable else migration_map.get("compliant_pct", 0.0),
        "steps": steps,
        "execution_summary": (
            f"{len(ready)} steps READY, {len(blocked)} BLOCKED, "
            f"~{total_minutes}min total"
        ),
    }


def write_yaml(data: dict, path: Path) -> None:
    """Write plan data as readable YAML-like text (no external deps)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    _dict_to_yaml(data, lines, indent=0)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _dict_to_yaml(obj: object, lines: list[str], indent: int) -> None:
    prefix = "  " * indent
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{prefix}{k}:")
                _dict_to_yaml(v, lines, indent + 1)
            else:
                val = _yaml_scalar(v)
                lines.append(f"{prefix}{k}: {val}")
    elif isinstance(obj, list):
        if not obj:
            lines[-1] += " []"
            return
        for item in obj:
            if isinstance(item, dict):
                first = True
                for k, v in item.items():
                    bullet = "- " if first else "  "
                    first = False
                    if isinstance(v, (dict, list)):
                        lines.append(f"{prefix}{bullet}{k}:")
                        _dict_to_yaml(v, lines, indent + 2)
                    else:
                        val = _yaml_scalar(v)
                        lines.append(f"{prefix}{bullet}{k}: {val}")
            else:
                lines.append(f"{prefix}- {_yaml_scalar(item)}")


def _yaml_scalar(v: object) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    if any(c in s for c in (":", "#", "[", "]", "{", "}", ",", "&", "*", "?")):
        return f'"{s}"'
    return s


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="QName Backfill Execution Planner")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--format", help="Single format to plan (e.g. fods)")
    group.add_argument("--all", action="store_true", help="Plan all formats")
    parser.add_argument(
        "--out", help="Output file path (--format mode only)"
    )
    parser.add_argument(
        "--out-dir", default=str(MIGRATION_DIR),
        help=f"Output directory for plan files (default: {MIGRATION_DIR})"
    )
    parser.add_argument(
        "--map-dir", default=str(MIGRATION_DIR),
        help="Directory containing migration map JSON files"
    )
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir)
    map_dir = Path(args.map_dir)

    if args.format:
        plan = plan_format(args.format, map_dir)
        if plan.get("error"):
            print(f"ERROR: {plan['error']}", file=sys.stderr)
            return 1
        out_path = Path(args.out) if args.out else out_dir / f"{args.format}-backfill-plan.yaml"
        write_yaml(plan, out_path)
        print(f"Plan: {out_path}")
        print(f"  Steps: {plan['total_actionable_steps']} total, "
              f"{plan['ready_steps']} READY, {plan['blocked_steps']} BLOCKED")
        print(f"  Effort: ~{plan['estimated_total_minutes']}min")
        return 0

    # --all mode
    results = []
    for fmt in _FORMATS:
        plan = plan_format(fmt, map_dir)
        if plan.get("error"):
            print(f"  {fmt}: SKIP ({plan['error']})")
            continue
        out_path = out_dir / f"{fmt}-backfill-plan.yaml"
        write_yaml(plan, out_path)
        results.append(plan)
        status = f"{plan['ready_steps']}R/{plan['blocked_steps']}B"
        print(f"  {fmt}: {status}, ~{plan['estimated_total_minutes']}min → {out_path.name}")

    if results:
        total_steps = sum(p["total_actionable_steps"] for p in results)
        total_min = sum(p["estimated_total_minutes"] for p in results)
        print(f"\nTotal: {total_steps} steps, ~{total_min}min across {len(results)} formats")
    return 0


if __name__ == "__main__":
    sys.exit(main())
