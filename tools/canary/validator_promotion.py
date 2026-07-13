"""validator_promotion.py — Validator shadow lifecycle management CLI.

Sub-commands:
  shadow  --validator <id> [--threshold N] [--formats *] [--notes TEXT]
  status  --validator <id>
  promote --validator <id>
  demote  --validator <id> [--to shadow|advisory]

All sub-commands read/write .supervisor/validator-shadow-registry.yaml
status also reads .local/supervisor/validator-shadow-log.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_PATH = _REPO_ROOT / ".supervisor" / "validator-shadow-registry.yaml"
SHADOW_LOG_PATH = _REPO_ROOT / ".local" / "supervisor" / "validator-shadow-log.jsonl"


def load_registry() -> dict:
    """Load and return the shadow registry dict."""
    if not REGISTRY_PATH.exists():
        return {"validator_shadow_entries": []}
    try:
        data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8")) or {}
        data.setdefault("validator_shadow_entries", [])
        return data
    except Exception as exc:
        print(f"ERROR: could not read registry: {exc}", file=sys.stderr)
        sys.exit(1)


def save_registry(data: dict) -> None:
    """Save registry atomically using tmp-rename."""
    tmp = REGISTRY_PATH.with_suffix(".tmp")
    tmp.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True), encoding="utf-8")
    os.replace(str(tmp), str(REGISTRY_PATH))


def find_entry(entries: list, validator_id: str) -> dict | None:
    for e in entries:
        if e.get("validator_id") == validator_id:
            return e
    return None


def cmd_shadow(args: argparse.Namespace) -> int:
    """Add or update a validator entry in shadow mode."""
    data = load_registry()
    entries = data["validator_shadow_entries"]
    entry = find_entry(entries, args.validator)
    today = date.today().isoformat()
    threshold = args.threshold if args.threshold is not None else 10
    formats = args.formats if args.formats else ["*"]
    if entry is None:
        entry = {"validator_id": args.validator}
        entries.append(entry)
    entry.update({
        "mode": "shadow",
        "format_scope": formats,
        "shadow_since": today,
        "shadow_promotion_threshold": threshold,
        "notes": args.notes or "",
    })
    save_registry(data)
    print(f"OK: {args.validator} added to shadow mode (threshold={threshold})")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Print observation count and threshold progress for a validator."""
    data = load_registry()
    entry = find_entry(data["validator_shadow_entries"], args.validator)
    if entry is None:
        print(f"WARN: {args.validator} not found in shadow registry")
        threshold = 0
    else:
        threshold = entry.get("shadow_promotion_threshold", 0)
        print(f"Validator: {args.validator}")
        print(f"  Mode:      {entry.get('mode', 'shadow')}")
        print(f"  Since:     {entry.get('shadow_since', 'unknown')}")
        print(f"  Threshold: {threshold}")

    # Count observations from log
    total = 0
    would_block = 0
    if SHADOW_LOG_PATH.exists():
        for line in SHADOW_LOG_PATH.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
                if rec.get("validator_id") == args.validator:
                    total += 1
                    if rec.get("would_have_blocked"):
                        would_block += 1
            except Exception:
                pass

    print(f"  Observations: {total} total, {would_block} would-have-blocked")
    if threshold > 0:
        pct = int(100 * would_block / threshold)
        print(f"  Promotion progress: {would_block}/{threshold} ({pct}%)")
    return 0


def cmd_promote(args: argparse.Namespace) -> int:
    """Promote a validator from shadow to blocking mode."""
    data = load_registry()
    entry = find_entry(data["validator_shadow_entries"], args.validator)
    if entry is None:
        print(f"ERROR: {args.validator} not found in shadow registry", file=sys.stderr)
        return 1
    if entry.get("mode") == "blocking":
        print(f"OK: {args.validator} is already blocking (no change)")
        return 0
    entry["mode"] = "blocking"
    entry["promoted_at"] = datetime.now(timezone.utc).isoformat()
    save_registry(data)
    print(f"OK: {args.validator} promoted to blocking mode")
    return 0


def cmd_demote(args: argparse.Namespace) -> int:
    """Demote a validator to shadow or advisory mode."""
    data = load_registry()
    entry = find_entry(data["validator_shadow_entries"], args.validator)
    if entry is None:
        print(f"ERROR: {args.validator} not found in shadow registry", file=sys.stderr)
        return 1
    target_mode = getattr(args, "to", None) or "shadow"
    entry["mode"] = target_mode
    entry["demoted_at"] = datetime.now(timezone.utc).isoformat()
    save_registry(data)
    print(f"OK: {args.validator} demoted to {target_mode} mode")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validator shadow lifecycle management CLI"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_shadow = sub.add_parser("shadow", help="Add validator to shadow mode")
    p_shadow.add_argument("--validator", required=True, help="Validator function name (def validate_*)")
    p_shadow.add_argument("--threshold", type=int, default=None, help="Observation threshold before promotion (default: 10)")
    p_shadow.add_argument("--formats", nargs="+", default=["*"], help="Format scope (default: *)")
    p_shadow.add_argument("--notes", default="", help="Notes for this shadow entry")

    p_status = sub.add_parser("status", help="Show observation count and threshold progress")
    p_status.add_argument("--validator", required=True, help="Validator function name")

    p_promote = sub.add_parser("promote", help="Promote validator to blocking mode")
    p_promote.add_argument("--validator", required=True, help="Validator function name")

    p_demote = sub.add_parser("demote", help="Demote validator to shadow or advisory mode")
    p_demote.add_argument("--validator", required=True, help="Validator function name")
    p_demote.add_argument("--to", default="shadow", choices=["shadow", "advisory"], help="Target mode (default: shadow)")

    args = parser.parse_args()
    dispatch = {
        "shadow": cmd_shadow,
        "status": cmd_status,
        "promote": cmd_promote,
        "demote": cmd_demote,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
