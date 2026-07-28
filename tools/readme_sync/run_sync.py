"""README sync orchestrator."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from tools.readme_sync.collector import REPO_ROOT, collect_format_state
from tools.readme_sync.drift_detector import check_all_drift, readme_targets
from tools.readme_sync.reconciler import (
    backup_readme,
    render_existing_with_generated,
    strip_timestamps,
    verify_preservation,
)
from tools.readme_sync.renderer import generate_blocks
from tools.readme_sync.section_schema import get_schema_for_format
from tools.readme_sync.validator import validate_readme


def target_path(format_id: str, track: str) -> Path:
    return REPO_ROOT / "src" / ("python" if track == "python" else "net") / format_id / "README.md"


def sync_one(format_id: str, track: str, *, dry_run: bool = False) -> dict:
    path = target_path(format_id, track)
    if not path.exists():
        return {"path": str(path.relative_to(REPO_ROOT)), "changed": False, "ok": False, "errors": ["README missing"]}
    original = path.read_text(encoding="utf-8", errors="replace")
    state = collect_format_state(format_id, track)
    rendered = render_existing_with_generated(original, generate_blocks(state))
    schema = get_schema_for_format(format_id, track)
    preserved, missing = verify_preservation(original, rendered, schema)
    errors: list[str] = []
    if not preserved:
        errors.extend(f"Maintained fragment missing: {m}" for m in missing)
    changed = strip_timestamps(original) != strip_timestamps(rendered)
    backup = None
    if changed and not dry_run and not errors:
        backup = backup_readme(path, format_id, track)
        path.write_text(rendered, encoding="utf-8")
        validation = validate_readme(path, format_id, track, original=original)
        if not validation.ok:
            path.write_text(original, encoding="utf-8")
            errors.extend(validation.errors)
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "changed": changed and not dry_run and not errors,
        "would_change": changed if dry_run else False,
        "ok": not errors,
        "errors": errors,
        "backup": str(backup.relative_to(REPO_ROOT)) if backup else None,
    }


def validate_targets(targets: list[tuple[str, str, Path]]) -> int:
    failed = False
    for format_id, track, path in targets:
        result = validate_readme(path, format_id, track)
        status = "PASS" if result.ok else "FAIL"
        print(f"{status} {path.relative_to(REPO_ROOT)}")
        for error in result.errors:
            print(f"  ERROR: {error}")
        for warning in result.warnings:
            print(f"  WARN: {warning}")
        failed = failed or not result.ok
    return 1 if failed else 0


def _guarded(args):
    """Coordination generator guard (TC-COORD-009): lease the README output
    set before writing. Read-only modes and --dry-run stay unguarded."""
    import sys
    from contextlib import nullcontext
    from pathlib import Path

    if args.mode not in ("full", "single") or args.dry_run:
        return nullcontext()
    repo = Path(__file__).resolve().parents[2]
    try:
        supervisor_dir = repo / "tools" / "supervisor"
        if str(supervisor_dir) not in sys.path:
            sys.path.insert(0, str(supervisor_dir))
        from coordination.generator_guard import guarded_generation
        return guarded_generation(
            "readme_sync", repo / "tools" / "readme_sync" /
            "output-manifest.yaml")
    except ImportError as exc:
        print(f"WARNING: coordination guard unavailable ({exc}); running unguarded")
        return nullcontext()


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchronize per-format README generated blocks")
    parser.add_argument("--mode", choices=["full", "single", "validate", "drift-only"], default="full")
    parser.add_argument("--format")
    parser.add_argument("--track", choices=["python", "dotnet"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.mode in {"single", "drift-only"} and bool(args.format) ^ bool(args.track):
        parser.error("--format and --track must be supplied together")

    try:
        with _guarded(args):
            return _run_modes(args, parser)
    except Exception as exc:
        if type(exc).__name__ == "GeneratorBlocked":
            print(f"BLOCKED: {exc}")
            return 2
        raise


def _run_modes(args, parser) -> int:

    if args.mode == "single":
        if not args.format or not args.track:
            parser.error("--mode single requires --format and --track")
        result = sync_one(args.format, args.track, dry_run=args.dry_run)
        print(result)
        return 0 if result["ok"] else 1

    if args.mode == "full":
        targets = readme_targets()
        results = [sync_one(format_id, track, dry_run=args.dry_run) for format_id, track, _ in targets]
        changed = sum(1 for result in results if result["changed"])
        would_change = sum(1 for result in results if result["would_change"])
        failures = [result for result in results if not result["ok"]]
        for result in results:
            if result["changed"] or result["would_change"] or not result["ok"]:
                print(result)
        if args.dry_run:
            print(f"{would_change} files would change")
        else:
            print(f"{changed} files changed")
        return 1 if failures else 0

    if args.mode == "validate":
        targets = [(args.format, args.track, target_path(args.format, args.track))] if args.format and args.track else readme_targets()
        return validate_targets(targets)

    if args.mode == "drift-only":
        if args.format and args.track:
            from tools.readme_sync.drift_detector import check_readme_drift

            report = {"checks": [check_readme_drift(args.format, args.track, target_path(args.format, args.track))]}
            report["overall"] = "DRIFT" if report["checks"][0]["drifted"] else "NO_DRIFT"
        else:
            report = check_all_drift()
        stale = [c["path"] for c in report["checks"] if c["drifted"]]
        if stale:
            print("DRIFT detected in: " + ", ".join(stale))
            return 1
        print("NO_DRIFT")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
