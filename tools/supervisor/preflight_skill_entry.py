"""
preflight_skill_entry.py — Skill: preflight-skill-entry

Validate a proposed skill-registry.yaml entry BEFORE insertion.
Exits 0 if valid. Exits 1 with a clear FIELD_MISSING or STATUS_INVALID message if not.

Usage:
    python tools/supervisor/preflight_skill_entry.py <skill_yaml_file>
    python tools/supervisor/preflight_skill_entry.py --inline "skill_id: foo\ncommand: /foo\n..."

LOC budget: <60 lines
"""
import argparse
import sys
from pathlib import Path
import yaml

_REQUIRED_FIELDS = {"skill_id", "purpose", "command", "status"}
_VALID_STATUSES = {"active", "deprecated", "experimental", "retired", "deferred"}


def validate_entry(entry: dict) -> list[str]:
    """Return list of error messages; empty list means valid."""
    errors = []
    for field in sorted(_REQUIRED_FIELDS):
        if not entry.get(field):
            errors.append(f"FIELD_MISSING: required field '{field}' is absent or empty")
    status = entry.get("status", "")
    if status and status not in _VALID_STATUSES:
        errors.append(f"STATUS_INVALID: '{status}' not in {sorted(_VALID_STATUSES)}")
    if entry.get("command_file"):
        repo = Path(__file__).resolve().parent.parent.parent
        cf_path = repo / entry["command_file"]
        if not cf_path.exists():
            errors.append(f"COMMAND_FILE_MISSING: '{entry['command_file']}' does not exist on disk")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Preflight-validate a skill-registry entry")
    parser.add_argument("skill_yaml_file", nargs="?", help="Path to a YAML file containing one skill entry")
    parser.add_argument("--inline", default=None, help="Inline YAML string for the skill entry")
    args = parser.parse_args()

    if args.inline:
        entry = yaml.safe_load(args.inline) or {}
    elif args.skill_yaml_file:
        entry = yaml.safe_load(Path(args.skill_yaml_file).read_text(encoding="utf-8")) or {}
    else:
        print("ERROR: provide a YAML file path or --inline YAML string", file=sys.stderr)
        sys.exit(1)

    errors = validate_entry(entry)
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        sys.exit(1)
    print(f"PREFLIGHT_PASS: entry '{entry.get('skill_id')}' is valid")


if __name__ == "__main__":
    main()
