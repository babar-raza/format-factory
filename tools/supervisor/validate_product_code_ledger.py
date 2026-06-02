"""Validate the R90 product-code change ledger against git and the worktree.

The validator intentionally accepts a dirty worktree. Any changed ``src/`` file
must be referenced by the ledger with its current SHA-256 (or as a deletion).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DEFAULT_LEDGER = REPO_ROOT / "reports" / "r90" / "product-code-change-ledger.json"
VALID_CLASSIFICATIONS = {"BACKFILLED_PRE_GOVERNANCE", "GOVERNED_PRODUCT_CHANGE"}


def load_ledger(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("ledger root must be an object")
    return data


def _run_git(repo_root: Path, *args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _is_src_path(path: str) -> bool:
    return path.replace("\\", "/").startswith("src/")


def collect_changed_src_files(repo_root: Path, base_ref: str) -> set[str]:
    """Return committed, staged, unstaged, and untracked src changes."""
    paths: set[str] = set()
    commands = [
        ("diff", "--name-only", f"{base_ref}..HEAD", "--", "src"),
        ("diff", "--name-only", "--cached", "--", "src"),
        ("diff", "--name-only", "--", "src"),
        ("ls-files", "--others", "--exclude-standard", "--", "src"),
    ]
    for command in commands:
        for path in _run_git(repo_root, *command):
            normalized = path.replace("\\", "/")
            if _is_src_path(normalized):
                paths.add(normalized)
    return paths


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def latest_entries_by_path(entries: list[dict]) -> dict[str, dict]:
    latest: dict[str, dict] = {}
    for entry in entries:
        for source in entry.get("source_files", []):
            path = str(source.get("path", "")).replace("\\", "/")
            if path:
                latest[path] = {"entry": entry, "source": source}
    return latest


def validate_ledger(ledger: dict, repo_root: Path, base_ref: str | None = None) -> dict:
    errors: list[str] = []
    entries = ledger.get("entries")
    if not isinstance(entries, list):
        return {"valid": False, "errors": ["entries must be a list"], "changed_src_files": []}

    configured_base = base_ref or ledger.get("tracking_base_ref")
    if not configured_base:
        return {"valid": False, "errors": ["tracking_base_ref is required"], "changed_src_files": []}

    seen_ids: set[str] = set()
    for index, entry in enumerate(entries):
        entry_id = entry.get("entry_id")
        if not entry_id:
            errors.append(f"entries[{index}] missing entry_id")
        elif entry_id in seen_ids:
            errors.append(f"duplicate entry_id: {entry_id}")
        else:
            seen_ids.add(entry_id)
        if entry.get("classification") not in VALID_CLASSIFICATIONS:
            errors.append(f"{entry_id or index}: invalid classification")
        if not entry.get("capability_refs"):
            errors.append(f"{entry_id or index}: capability_refs must not be empty")
        if not entry.get("api_symbols"):
            errors.append(f"{entry_id or index}: api_symbols must not be empty")
        sources = entry.get("source_files")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{entry_id or index}: source_files must not be empty")
            continue
        for source in sources:
            path = str(source.get("path", "")).replace("\\", "/")
            if not _is_src_path(path):
                errors.append(f"{entry_id or index}: invalid src path: {path}")
            state = source.get("state", "present")
            if state not in {"present", "deleted"}:
                errors.append(f"{entry_id or index}: invalid source state for {path}: {state}")
            if state == "present" and not source.get("sha256"):
                errors.append(f"{entry_id or index}: missing sha256 for {path}")

    try:
        changed = collect_changed_src_files(repo_root, configured_base)
    except RuntimeError as exc:
        errors.append(str(exc))
        changed = set()

    referenced = latest_entries_by_path(entries)
    for path in sorted(changed):
        reference = referenced.get(path)
        if reference is None:
            errors.append(f"changed src file lacks ledger reference: {path}")
            continue
        source = reference["source"]
        full_path = repo_root / path
        if full_path.exists():
            expected = str(source.get("sha256", "")).lower()
            actual = sha256_file(full_path)
            if source.get("state", "present") != "present" or expected != actual:
                errors.append(f"changed src file lacks current ledger hash: {path}")
        elif source.get("state") != "deleted":
            errors.append(f"deleted src file lacks deletion ledger reference: {path}")

    return {
        "valid": not errors,
        "errors": errors,
        "tracking_base_ref": configured_base,
        "changed_src_files": sorted(changed),
        "referenced_src_files": sorted(referenced),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--base-ref", help="Override ledger tracking_base_ref")
    parser.add_argument("--json", action="store_true", help="Print JSON result")
    args = parser.parse_args()

    try:
        result = validate_ledger(load_ledger(args.ledger), args.repo_root, args.base_ref)
    except Exception as exc:
        result = {"valid": False, "errors": [str(exc)], "changed_src_files": []}

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"PRODUCT_CODE_LEDGER: {'PASS' if result['valid'] else 'FAIL'}")
        for error in result["errors"]:
            print(f"  ERROR: {error}")
        print(f"  changed_src_files: {len(result.get('changed_src_files', []))}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
