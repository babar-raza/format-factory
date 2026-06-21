"""
update_source_baseline.py — Update mutable 'loc' tracking fields after a healing sprint.

POLICY (enforced mechanically):
  - NEVER increases baseline_loc_cap (frozen write-once by design)
  - ONLY updates the mutable 'loc' and 'functions' tracking fields
  - Called after an analytics-separation sprint successfully extracts functions
  - Exit 0 only when ALL processed files have actual_loc <= baseline_loc_cap
  - Exit 1 when any processed file is still over its cap

Usage:
  # Update a single file:
  python tools/supervisor/update_source_baseline.py --path src/python/zst/zst_codec.py

  # Update multiple files:
  python tools/supervisor/update_source_baseline.py \\
      --path src/python/zst/zst_codec.py \\
      --path src/python/xcf/xcf_parser.py

  # Dry-run (report without writing):
  python tools/supervisor/update_source_baseline.py --path src/python/zst/zst_codec.py --dry-run

  # Update all known_violations entries:
  python tools/supervisor/update_source_baseline.py --all
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent

_BASELINE_PATH = REPO_ROOT / "registry" / "source-structure-baseline.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _count_loc(path: Path) -> int:
    """Count lines of code in a file."""
    try:
        return sum(1 for _ in path.open(encoding="utf-8", errors="replace"))
    except OSError as exc:
        raise RuntimeError(f"Cannot read {path}: {exc}") from exc


def _count_functions(path: Path) -> int:
    """Count top-level function definitions in a Python file."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
        return sum(
            1 for node in ast.iter_child_nodes(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        )
    except SyntaxError:
        # Fall back to line-based grep if AST fails
        try:
            return sum(
                1 for line in path.open(encoding="utf-8", errors="replace")
                if line.startswith("def ") or line.startswith("async def ")
            )
        except OSError:
            return 0
    except OSError:
        return 0


def _load_baseline() -> dict:
    if not _BASELINE_PATH.exists():
        raise RuntimeError(f"Baseline not found: {_BASELINE_PATH}")
    return json.loads(_BASELINE_PATH.read_text(encoding="utf-8"))


def _write_baseline_atomic(data: dict) -> None:
    """Write baseline atomically via temp file + rename to avoid corruption."""
    content = json.dumps(data, indent=2) + "\n"
    fd, tmp_path = tempfile.mkstemp(
        dir=_BASELINE_PATH.parent,
        prefix=".source-structure-baseline-",
        suffix=".json.tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, _BASELINE_PATH)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def process_path(
    rel_path: str,
    baseline: dict,
    dry_run: bool,
    run_id: Optional[str],
) -> dict:
    """
    Process one baseline entry.

    Returns a result dict with keys:
      rel_path, actual_loc, actual_functions, baseline_loc_cap,
      was_over_cap, still_over_cap, updated, error
    """
    known_violations = baseline.get("known_violations", {})
    if rel_path not in known_violations:
        return {
            "rel_path": rel_path,
            "error": f"Not in known_violations: {rel_path}",
            "still_over_cap": True,
            "updated": False,
        }

    entry = known_violations[rel_path]
    cap = entry.get("baseline_loc_cap")
    if cap is None:
        return {
            "rel_path": rel_path,
            "error": "baseline_loc_cap missing from entry",
            "still_over_cap": True,
            "updated": False,
        }

    abs_path = REPO_ROOT / rel_path.replace("/", os.sep)
    if not abs_path.exists():
        return {
            "rel_path": rel_path,
            "error": f"File not found on disk: {abs_path}",
            "still_over_cap": True,
            "updated": False,
        }

    try:
        actual_loc = _count_loc(abs_path)
        actual_functions = _count_functions(abs_path) if abs_path.suffix == ".py" else entry.get("functions", 0)
    except RuntimeError as exc:
        return {
            "rel_path": rel_path,
            "error": str(exc),
            "still_over_cap": True,
            "updated": False,
        }

    was_over_cap = entry.get("loc", 0) > cap
    still_over_cap = actual_loc > cap

    result = {
        "rel_path": rel_path,
        "actual_loc": actual_loc,
        "actual_functions": actual_functions,
        "baseline_loc_cap": cap,
        "was_over_cap": was_over_cap,
        "still_over_cap": still_over_cap,
        "updated": False,
        "error": None,
    }

    if not dry_run:
        # POLICY: only update mutable tracking fields; never touch baseline_loc_cap
        old_loc = entry.get("loc")
        entry["loc"] = actual_loc
        if abs_path.suffix == ".py":
            entry["functions"] = actual_functions
        entry["last_healed_check"] = _now_iso()
        if run_id:
            entry["last_healed_by"] = run_id
        result["updated"] = True
        result["old_loc"] = old_loc

    return result


def run(
    paths: list[str],
    dry_run: bool = False,
    run_id: Optional[str] = None,
    verbose: bool = True,
) -> int:
    """
    Process paths and update baseline.

    Returns 0 if all files are at or under their cap; 1 otherwise.
    """
    try:
        baseline = _load_baseline()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 9

    results = []
    for rel_path in paths:
        # Normalize separators to forward slash (baseline keys use forward slash)
        norm = rel_path.replace("\\", "/")
        result = process_path(norm, baseline, dry_run, run_id)
        results.append(result)
        if verbose:
            _print_result(result)

    if not dry_run and any(r.get("updated") for r in results):
        try:
            _write_baseline_atomic(baseline)
            if verbose:
                print(f"\nBaseline written: {_BASELINE_PATH}")
        except Exception as exc:
            print(f"ERROR writing baseline: {exc}", file=sys.stderr)
            return 9

    still_over = [r for r in results if r.get("still_over_cap") or r.get("error")]
    errors = [r for r in results if r.get("error")]

    if verbose:
        print(f"\n--- Summary ---")
        print(f"  Processed:    {len(results)}")
        print(f"  Now under cap: {len(results) - len(still_over)}")
        print(f"  Still over cap: {len([r for r in results if r.get('still_over_cap') and not r.get('error')])}")
        print(f"  Errors:       {len(errors)}")
        if dry_run:
            print("  (dry-run — baseline NOT written)")

    # Exit 0 only if every file is at or under its cap and no errors
    return 0 if not still_over else 1


def _print_result(result: dict) -> None:
    rel = result["rel_path"]
    if result.get("error"):
        print(f"  ERROR  {rel}: {result['error']}")
        return
    cap = result["baseline_loc_cap"]
    actual = result["actual_loc"]
    status = "OK (under cap)" if actual <= cap else f"OVER CAP by {actual - cap}"
    old = result.get("old_loc")
    change = f" (was {old})" if old is not None and old != actual else ""
    print(f"  {status:20s}  {rel}  [{actual}{change} / cap {cap}]")


def main() -> int:
    p = argparse.ArgumentParser(
        prog="update_source_baseline.py",
        description=(
            "Update mutable 'loc' tracking fields in source-structure-baseline.json "
            "after a healing sprint. Never increases baseline_loc_cap."
        ),
    )
    p.add_argument(
        "--path",
        dest="paths",
        action="append",
        default=[],
        metavar="REL_PATH",
        help="Repo-relative path to update (may be repeated). "
             "Example: src/python/zst/zst_codec.py",
    )
    p.add_argument(
        "--all",
        action="store_true",
        help="Update all entries in known_violations",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Report without writing to baseline",
    )
    p.add_argument(
        "--run-id",
        default=None,
        help="Optional run identifier recorded in last_healed_by field",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-file output",
    )
    args = p.parse_args()

    if args.all:
        try:
            baseline = _load_baseline()
        except RuntimeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 9
        paths = list(baseline.get("known_violations", {}).keys())
    else:
        paths = args.paths

    if not paths:
        p.error("Provide at least one --path or use --all")

    if not args.quiet:
        mode = "DRY-RUN" if args.dry_run else "UPDATE"
        print(f"update_source_baseline.py [{mode}] — {_now_iso()}")
        print(f"Baseline: {_BASELINE_PATH}")
        print(f"Files to process: {len(paths)}")
        print()

    return run(
        paths=paths,
        dry_run=args.dry_run,
        run_id=args.run_id,
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    sys.exit(main())
