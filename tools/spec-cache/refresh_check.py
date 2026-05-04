"""
refresh_check.py — Specification Cache Staleness Scanner
format-factory / tools/spec-cache/

Purpose:
    Scan .local/spec-cache/ spec-index.yaml entries and report which are stale,
    missing files, or have hash mismatches. Does NOT re-download anything.
    Produces a human-readable staleness report and exits non-zero if any stale
    entries are found.

Policy:
    - This tool NEVER performs network access.
    - This tool NEVER deletes or modifies cached spec files.
    - This tool NEVER overwrites spec-index.yaml entries.
    - This tool does NOT call LLM endpoints.
    - Stale entries must be resolved manually: re-run acquire_spec.py with
      --allow-network and --overwrite after verifying T3 authorization.

Staleness reasons:
    - stale_flag     : entry has stale: true in spec-index.yaml
    - missing_file   : cached file does not exist on disk
    - hash_mismatch  : SHA-256 of cached file does not match content_hash
    - not_stale      : entry appears current

Exit codes:
    0 — all entries current (or no entries found)
    1 — one or more stale entries found
    2 — argument or configuration error

See also:
    docs/specification-cache.md — full policy and authorization model
    tools/spec-cache/spec_index.py — spec-index.yaml library
    tools/spec-cache/acquire_spec.py — download and index a spec file
"""

import argparse
import pathlib
import sys

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

# Import spec_index from same directory
_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import spec_index


# ---------------------------------------------------------------------------
# Report builders
# ---------------------------------------------------------------------------


def _report_entry(entry: dict, cache_root: pathlib.Path, verbose: bool) -> tuple[bool, str]:
    """
    Check a single entry and return (is_stale, reason).
    Prints details if verbose=True.
    """
    format_id = entry.get("format_id", "?")
    version = entry.get("version", "?")
    index_path = entry.get("_index_path", "unknown")

    stale_flag, reason = spec_index.is_stale(entry, cache_root=cache_root)

    if verbose or stale_flag:
        status_str = f"STALE ({reason})" if stale_flag else "current"
        print(f"  [{status_str}]  {format_id}/{version}  —  {index_path}")

        if stale_flag and verbose:
            _print_stale_advice(reason, format_id, version)

    return stale_flag, reason


def _print_stale_advice(reason: str, format_id: str, version: str) -> None:
    """Print human-readable remediation advice for a stale entry."""
    if reason == "stale_flag":
        print(
            f"    Advice: Entry is manually marked stale. "
            f"Re-run acquire_spec.py --format-id {format_id} --version {version} "
            "--allow-network --overwrite after T3 authorization."
        )
    elif reason == "missing_file":
        print(
            f"    Advice: Cached file is missing. "
            f"Re-run acquire_spec.py --format-id {format_id} --version {version} "
            "--allow-network --overwrite after T3 authorization."
        )
    elif reason == "hash_mismatch":
        print(
            f"    Advice: Cached file has changed since indexing. "
            f"Possible corruption or unauthorized modification. "
            f"Verify file integrity, then re-run acquire_spec.py "
            f"--format-id {format_id} --version {version} --allow-network --overwrite."
        )


# ---------------------------------------------------------------------------
# Main scan logic
# ---------------------------------------------------------------------------


def _cmd_scan(args: argparse.Namespace) -> int:
    """Scan all entries and report staleness."""
    cache_root = spec_index.get_cache_root()
    entries = spec_index.list_all_entries()

    if not entries:
        print("No spec-index.yaml entries found in .local/spec-cache/")
        print(f"Cache root: {cache_root}")
        return 0

    # Filter by format_id if specified
    if args.format_id:
        entries = [e for e in entries if e.get("format_id") == args.format_id]
        if not entries:
            print(f"No entries found for format_id={args.format_id}")
            return 0

    total = len(entries)
    stale_count = 0
    stale_reasons: dict[str, int] = {}

    print(f"Scanning {total} spec-index.yaml {'entry' if total == 1 else 'entries'}...")
    print()

    for entry in entries:
        # Pop internal path key before passing to is_stale
        entry_copy = dict(entry)
        entry_copy.pop("_index_path", None)
        entry["_index_path"] = entry.get("_index_path", "unknown")  # keep for display

        stale_flag, reason = _report_entry(entry, cache_root, verbose=args.verbose)
        if stale_flag:
            stale_count += 1
            stale_reasons[reason] = stale_reasons.get(reason, 0) + 1

    print()
    print("─" * 60)
    print(f"Summary: {total} entries scanned, {stale_count} stale")

    if stale_count > 0:
        print("Stale breakdown:")
        for reason, count in sorted(stale_reasons.items()):
            print(f"  {reason:20} : {count}")
        print()
        print("STALE entries found. Remediation required before Gate 2.")
        print("See: docs/specification-cache.md for T3 authorization steps.")
        return 1
    else:
        if not args.verbose:
            print("All entries current.")
        return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    """Validate spec-index.yaml entries against the schema."""
    entries = spec_index.list_all_entries()

    if not entries:
        print("No spec-index.yaml entries found.")
        return 0

    if args.format_id:
        entries = [e for e in entries if e.get("format_id") == args.format_id]
        if not entries:
            print(f"No entries found for format_id={args.format_id}")
            return 0

    all_valid = True
    for entry in entries:
        index_path = entry.pop("_index_path", "unknown")
        errors = spec_index.validate_entry(entry)
        if errors:
            print(f"INVALID: {index_path}")
            for err in errors:
                print(f"  - {err}")
            all_valid = False
        else:
            stale_flag, reason = spec_index.is_stale(entry)
            status = f"STALE ({reason})" if stale_flag else "VALID"
            print(f"{status}: {entry.get('format_id')}/{entry.get('version')}  —  {index_path}")

    return 0 if all_valid else 1


def _cmd_show(args: argparse.Namespace) -> int:
    """Show a specific entry in full detail."""
    if not args.format_id or not args.version:
        print("ERROR: --format-id and --version are required for show", file=sys.stderr)
        return 2

    entry = spec_index.read_entry(args.format_id, args.version)
    if entry is None:
        print(f"No entry found for {args.format_id}/{args.version}")
        return 1

    print(f"spec-index.yaml entry: {args.format_id}/{args.version}")
    print("─" * 60)
    for key, value in sorted(entry.items()):
        print(f"  {key:30}: {value}")

    stale_flag, reason = spec_index.is_stale(entry)
    print()
    print(f"  Staleness check: {'STALE (' + reason + ')' if stale_flag else 'current'}")
    return 0


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="refresh_check.py",
        description=(
            "Scan .local/spec-cache/ for stale spec entries. "
            "Reports stale entries; does NOT re-download anything."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  # Scan all entries:\n"
            "  python refresh_check.py scan\n"
            "\n"
            "  # Scan with verbose output:\n"
            "  python refresh_check.py scan --verbose\n"
            "\n"
            "  # Scan a specific format:\n"
            "  python refresh_check.py scan --format-id fods\n"
            "\n"
            "  # Validate entry schema:\n"
            "  python refresh_check.py validate\n"
            "\n"
            "  # Show a specific entry:\n"
            "  python refresh_check.py show --format-id fods --version 1.3\n"
        ),
    )

    subparsers = p.add_subparsers(dest="command", help="Command to run")

    # scan subcommand
    scan_p = subparsers.add_parser("scan", help="Scan entries for staleness")
    scan_p.add_argument(
        "--format-id",
        default=None,
        help="Only check this format_id (default: all)",
    )
    scan_p.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Print all entries, not just stale ones",
    )

    # validate subcommand
    val_p = subparsers.add_parser("validate", help="Validate entry schemas")
    val_p.add_argument("--format-id", default=None, help="Only validate this format_id")

    # show subcommand
    show_p = subparsers.add_parser("show", help="Show a specific entry in detail")
    show_p.add_argument("--format-id", required=True)
    show_p.add_argument("--version", required=True)

    return p


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 2

    if args.command == "scan":
        return _cmd_scan(args)
    elif args.command == "validate":
        return _cmd_validate(args)
    elif args.command == "show":
        return _cmd_show(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
