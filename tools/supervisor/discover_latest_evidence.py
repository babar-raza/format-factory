"""
discover_latest_evidence.py — Format Factory Local Supervisor Control Plane
Discovers the latest evidence bundle ZIP from known search paths.

Exit codes:
  0 — success (bundle found, sprint_id extracted if available)
  1 — no bundle found
  2 — malformed ZIP (found but unreadable)
  9 — unexpected error

Usage:
  python tools/supervisor/discover_latest_evidence.py
  python tools/supervisor/discover_latest_evidence.py --path /explicit/path/to/bundle.zip
  python tools/supervisor/discover_latest_evidence.py --json
  python tools/supervisor/discover_latest_evidence.py --output-dir reports/supervisor
"""

import argparse
import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path


SEARCH_PATHS = [
    ".local",           # all subdirs — agents may drop bundles anywhere under .local/
    "evidence-bundles",
    "reports",
]
BUNDLE_PATTERNS = ["**/*.zip"]
SPRINT_ID_PATHS = [
    "bundle-metadata/sprint-id.txt",
    "sprint-id.txt",
    "metadata/sprint-id.txt",
]


def find_bundles(repo_root: Path) -> list[Path]:
    """Find all ZIP files in known search paths, sorted by mtime descending."""
    bundles = []
    for search_dir in SEARCH_PATHS:
        candidate = repo_root / search_dir
        if candidate.is_dir():
            for pattern in BUNDLE_PATTERNS:
                bundles.extend(candidate.glob(pattern))
    # Sort by modification time, newest first
    bundles.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return bundles


def read_sprint_id_from_zip(bundle_path: Path) -> str:
    """Read sprint_id from bundle metadata inside ZIP."""
    import re as _re

    def _sprint_num(path: str) -> int:
        m = _re.search(r"/r(\d+)/", path)
        return int(m.group(1)) if m else 0

    try:
        with zipfile.ZipFile(bundle_path, "r") as zf:
            # 1. Try sprint-id.txt (full content = sprint_id)
            for sprint_id_path in SPRINT_ID_PATHS:
                try:
                    data = zf.read(sprint_id_path)
                    value = data.decode("utf-8", errors="replace").strip()
                    if value and "\n" not in value:
                        return value
                except KeyError:
                    continue
            # 2. Try bundle-metadata/sprint-summary.md (has sprint_id: field)
            for summary_path in ["bundle-metadata/sprint-summary.md", "sprint-summary.md"]:
                try:
                    content = zf.read(summary_path).decode("utf-8", errors="replace")
                    for line in content.splitlines():
                        line = line.strip()
                        if line.startswith("sprint_id:"):
                            return line.split(":", 1)[1].strip()
                except KeyError:
                    continue
            # 3. Try most-recent sprint final-verdict.md (prefer high-numbered /r<N>/ paths)
            verdict_files = [n for n in zf.namelist() if n.endswith("final-verdict.md")]
            verdict_files.sort(key=_sprint_num, reverse=True)
            for name in verdict_files[:5]:
                try:
                    content = zf.read(name).decode("utf-8", errors="replace")
                    for line in content.splitlines():
                        if line.startswith("sprint_id:") or line.startswith("SPRINT_ID:"):
                            return line.split(":", 1)[1].strip()
                        if "FORMAT-FACTORY" in line and "-" in line:
                            # Extract the sprint ID token from the line
                            parts = line.strip().lstrip("#*").strip().split()
                            for p in parts:
                                if p.startswith("FORMAT-FACTORY"):
                                    return p.rstrip("*.")
                except Exception:
                    pass
            return "unknown"
    except zipfile.BadZipFile:
        raise ValueError(f"Malformed ZIP: {bundle_path}")


def count_entries(bundle_path: Path) -> int:
    """Count entries in ZIP."""
    try:
        with zipfile.ZipFile(bundle_path, "r") as zf:
            return len(zf.namelist())
    except Exception:
        return 0


def discover(repo_root: Path, explicit_path: Path | None = None) -> dict:
    """Main discovery logic. Returns result dict."""
    timestamp = datetime.now().isoformat()

    if explicit_path:
        if not explicit_path.exists():
            return {
                "status": "error",
                "exit_code": 1,
                "error": f"Explicit bundle path not found: {explicit_path}",
                "timestamp": timestamp,
            }
        bundles = [explicit_path]
    else:
        bundles = find_bundles(repo_root)

    if not bundles:
        return {
            "status": "no_bundle",
            "exit_code": 1,
            "message": f"No evidence bundles found in: {SEARCH_PATHS}",
            "search_paths": SEARCH_PATHS,
            "timestamp": timestamp,
        }

    bundle_path = bundles[0]

    # Verify the ZIP is readable
    try:
        sprint_id = read_sprint_id_from_zip(bundle_path)
        entry_count = count_entries(bundle_path)
    except ValueError as e:
        return {
            "status": "malformed_zip",
            "exit_code": 2,
            "error": str(e),
            "bundle_path": str(bundle_path),
            "timestamp": timestamp,
        }
    except Exception as e:
        return {
            "status": "error",
            "exit_code": 9,
            "error": f"Unexpected error reading {bundle_path}: {e}",
            "bundle_path": str(bundle_path),
            "timestamp": timestamp,
        }

    bundle_mtime = datetime.fromtimestamp(bundle_path.stat().st_mtime).isoformat()
    bundle_size = bundle_path.stat().st_size

    return {
        "status": "found",
        "exit_code": 0,
        "bundle_path": str(bundle_path.resolve()),
        "sprint_id": sprint_id,
        "entry_count": entry_count,
        "bundle_mtime": bundle_mtime,
        "bundle_size_bytes": bundle_size,
        "all_bundles_found": [str(b.resolve()) for b in bundles[:5]],
        "timestamp": timestamp,
    }


def write_state(result: dict, state_dir: Path) -> None:
    """Write current-run.json to .supervisor/state/"""
    state_dir.mkdir(parents=True, exist_ok=True)
    state_file = state_dir / "current-run.json"
    existing = {}
    if state_file.exists():
        try:
            existing = json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    existing["last_discovery"] = result
    state_file.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def write_markdown(result: dict, output_dir: Path) -> None:
    """Write discovery-summary.md to output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / "discovery-summary.md"
    status = result.get("status", "unknown")
    lines = [
        "# Evidence Bundle Discovery Summary",
        f"Timestamp: {result.get('timestamp', 'unknown')}",
        f"Status: {status}",
    ]
    if status == "found":
        lines += [
            f"Bundle: {result['bundle_path']}",
            f"Sprint ID: {result['sprint_id']}",
            f"Entry count: {result['entry_count']}",
            f"Bundle mtime: {result['bundle_mtime']}",
            f"Bundle size: {result['bundle_size_bytes']} bytes",
        ]
    elif status == "no_bundle":
        lines.append(f"Message: {result.get('message', '')}")
    elif status == "malformed_zip":
        lines.append(f"Error: {result.get('error', '')}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    print("WARNING: discover_latest_evidence.py is legacy. "
          "Use 'supervisor_loop.py autonomous-cycle --declaration <path>' instead.",
          file=sys.stderr)
    parser = argparse.ArgumentParser(description="Discover latest Format Factory evidence bundle")
    parser.add_argument("--path", type=Path, help="Explicit bundle path (skip search)")
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/supervisor"),
        help="Directory for summary output",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root (default: current directory)",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    result = discover(repo_root, explicit_path=args.path)

    # Write state to .supervisor/state/
    state_dir = repo_root / ".supervisor" / "state"
    try:
        write_state(result, state_dir)
    except Exception as e:
        print(f"Warning: could not write state file: {e}", file=sys.stderr)

    # Write markdown summary
    try:
        write_markdown(result, args.output_dir)
    except Exception as e:
        print(f"Warning: could not write markdown summary: {e}", file=sys.stderr)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = result.get("status", "unknown")
        if status == "found":
            print("DISCOVERY: OK")
            print(f"  Bundle: {result['bundle_path']}")
            print(f"  Sprint ID: {result['sprint_id']}")
            print(f"  Entries: {result['entry_count']}")
        elif status == "no_bundle":
            print("DISCOVERY: NO_BUNDLE_FOUND")
            print(f"  {result.get('message', '')}")
        elif status == "malformed_zip":
            print("DISCOVERY: MALFORMED_ZIP")
            print(f"  {result.get('error', '')}")
        else:
            print(f"DISCOVERY: ERROR — {result.get('error', '')}")

    return result.get("exit_code", 9)


if __name__ == "__main__":
    sys.exit(main())
