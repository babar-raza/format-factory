"""
refresh_workbench.py — Detect spec version changes and flag workbench for refresh.

format-factory project — Spec Workbench v1
Created: TC-0020 (2026-06-18)

Detects whether the spec source has changed (by comparing SHA-256 hashes in spec-index.yaml
against the workbench's recorded source hash) and reports which format workbenches need
rebuilding. Does NOT auto-rebuild (to avoid silent data loss if spec change is unintentional).

Usage:
    python refresh_workbench.py --format-id fods --version 1.3
    python refresh_workbench.py --all                # check all known formats
    python refresh_workbench.py --all --json         # machine-readable output

Output:
    CURRENT   — workbench hash matches spec-index hash; no rebuild needed
    STALE     — workbench hash differs from spec-index hash; rebuild required
    NO_INDEX  — no spec-index.yaml found; cannot determine staleness
    NO_WB     — no workbench found; run build_spec_workbench.py first

Exit codes:
    0 — all checked workbenches are CURRENT
    1 — at least one workbench is STALE (rebuild required)
    2 — at least one workbench has NO_INDEX or NO_WB (incomplete setup)

Local-only: never reads network. Never modifies files.

License: Apache-2.0 (project-owned, format-factory)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _spec_cache_dir(fmt: str, ver: str) -> Path:
    return _repo_root() / ".local" / "spec-cache" / fmt / ver


def _spec_cache_root() -> Path:
    return _repo_root() / ".local" / "spec-cache"


# ---------------------------------------------------------------------------
# Hash extraction
# ---------------------------------------------------------------------------

def _extract_hash_from_index(spec_index_path: Path) -> str | None:
    """Extract SHA-256 from spec-index.yaml. Returns None if not found."""
    try:
        text = spec_index_path.read_text(encoding="utf-8")
        # Match: sha256: "sha256:abc123" or sha256: abc123
        m = re.search(r'sha256:\s*"?(sha256:[a-f0-9]{64})"?', text)
        if m:
            return m.group(1)
        # Match: file_hash: abc123 (bare hex)
        m2 = re.search(r'file_hash:\s*([a-f0-9]{64})', text)
        if m2:
            return f"sha256:{m2.group(1)}"
        # Match: hash: sha256:abc123
        m3 = re.search(r'hash:\s*"?(sha256:[a-f0-9]{64})"?', text)
        if m3:
            return m3.group(1)
    except Exception:
        pass
    return None


def _extract_hash_from_workbench(workbench_dir: Path) -> str | None:
    """Extract recorded source hash from workbench artifacts."""
    # Try verified-facts-auto-seed.yaml first (most reliable)
    for candidate in [
        workbench_dir / "verified-facts-auto-seed.yaml",
        workbench_dir / "workbench-report.md",
    ]:
        if candidate.exists():
            try:
                text = candidate.read_text(encoding="utf-8")
                m = re.search(r'source_sha256:\s*"?(sha256:[a-f0-9]{64})"?', text)
                if m:
                    return m.group(1)
            except Exception:
                pass

    # Try task-packets directory
    packets_dir = workbench_dir / "task-packets"
    if packets_dir.exists():
        for pf in sorted(packets_dir.glob("*.yaml"))[:1]:
            try:
                text = pf.read_text(encoding="utf-8")
                m = re.search(r'source_sha256:\s*"?(sha256:[a-f0-9]{64})"?', text)
                if m:
                    return m.group(1)
            except Exception:
                pass

    return None


# ---------------------------------------------------------------------------
# Per-format check
# ---------------------------------------------------------------------------

def check_format(fmt: str, ver: str) -> dict[str, Any]:
    """Check staleness of a single format+version workbench."""
    spec_dir = _spec_cache_dir(fmt, ver)
    spec_index = spec_dir / "spec-index.yaml"
    workbench_dir = spec_dir / "workbench"

    result: dict[str, Any] = {
        "format_id": fmt,
        "version": ver,
        "spec_dir": str(spec_dir),
        "status": "UNKNOWN",
        "spec_hash": None,
        "workbench_hash": None,
        "action_required": None,
    }

    if not spec_index.exists():
        result["status"] = "NO_INDEX"
        result["action_required"] = "Acquire spec and run normalize_pdf.py to create spec-index.yaml"
        return result

    if not workbench_dir.exists():
        result["status"] = "NO_WB"
        result["action_required"] = "Run build_spec_workbench.py to create workbench"
        return result

    spec_hash = _extract_hash_from_index(spec_index)
    wb_hash = _extract_hash_from_workbench(workbench_dir)

    result["spec_hash"] = spec_hash
    result["workbench_hash"] = wb_hash

    if spec_hash is None:
        result["status"] = "NO_INDEX_HASH"
        result["action_required"] = "spec-index.yaml exists but no SHA-256 found; add file_hash field"
        return result

    if wb_hash is None:
        # Workbench exists but has no hash recorded — treat as stale to be safe
        result["status"] = "STALE"
        result["action_required"] = (
            "Workbench exists but no source_sha256 recorded; "
            "rebuild with build_spec_workbench.py to record hash"
        )
        return result

    if spec_hash == wb_hash:
        result["status"] = "CURRENT"
        result["action_required"] = None
    else:
        result["status"] = "STALE"
        result["action_required"] = (
            f"Spec hash changed ({wb_hash[:30]}... -> {spec_hash[:30]}...); "
            "run build_spec_workbench.py to refresh workbench"
        )

    return result


# ---------------------------------------------------------------------------
# Discover all formats
# ---------------------------------------------------------------------------

def _discover_all_formats() -> list[tuple[str, str]]:
    """Return (format_id, version) pairs for all spec-cache entries."""
    root = _spec_cache_root()
    if not root.exists():
        return []
    pairs: list[tuple[str, str]] = []
    for fmt_dir in sorted(root.iterdir()):
        if not fmt_dir.is_dir():
            continue
        for ver_dir in sorted(fmt_dir.iterdir()):
            if not ver_dir.is_dir():
                continue
            pairs.append((fmt_dir.name, ver_dir.name))
    return pairs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Detect stale spec workbenches (TC-0020 refresh tooling)"
    )
    parser.add_argument("--format-id", help="Format ID to check (e.g. fods)")
    parser.add_argument("--version", help="Spec version (e.g. 1.3)")
    parser.add_argument("--all", action="store_true", help="Check all discovered formats")
    parser.add_argument("--json", action="store_true", dest="json_out",
                        help="Output machine-readable JSON")
    args = parser.parse_args(argv)

    if not args.all and not (args.format_id and args.version):
        parser.error("Provide --format-id and --version, or use --all")

    if args.all:
        pairs = _discover_all_formats()
        if not pairs:
            print("No spec-cache entries found.", file=sys.stderr)
            return 2
    else:
        pairs = [(args.format_id, args.version)]

    results = [check_format(fmt, ver) for fmt, ver in pairs]

    if args.json_out:
        print(json.dumps(results, indent=2))
    else:
        width = max(len(r["format_id"]) for r in results) + 2
        print(f"{'FORMAT':<{width}} {'VERSION':<15} {'STATUS':<15} ACTION")
        print("-" * 80)
        for r in results:
            action = r.get("action_required") or "-"
            if len(action) > 45:
                action = action[:42] + "..."
            print(f"{r['format_id']:<{width}} {r['version']:<15} {r['status']:<15} {action}")

    # Exit code
    statuses = {r["status"] for r in results}
    if "STALE" in statuses:
        return 1
    if statuses - {"CURRENT"}:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
