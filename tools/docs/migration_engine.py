"""
tools/docs/migration_engine.py

Core migration utility for the documentation-structure-migration capability (DOCS-REORG-001).

Subcommands:
  inventory   — list all docs/ root files with classification metadata
  scan-refs   — scan entire repo for references to docs/ root files
  manifest    — generate/validate the migration manifest YAML
  move        — execute a single manifest item (git mv + reference updates)
  validate    — post-move validation
  rollback    — restore a moved file from backup

Usage:
  python tools/docs/migration_engine.py inventory [--output PATH]
  python tools/docs/migration_engine.py scan-refs [--output PATH] [--check-stale]
  python tools/docs/migration_engine.py manifest [--validate]
  python tools/docs/migration_engine.py move --source SRC --dest DEST [--dry-run]
  python tools/docs/migration_engine.py validate [--source SRC] [--dest DEST] [--full] [--wave N]
  python tools/docs/migration_engine.py rollback --source SRC
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterator

import yaml

REPO_ROOT = Path(__file__).parent.parent.parent
DOCS_ROOT = REPO_ROOT / "docs"
BACKUP_DIR = REPO_ROOT / ".local" / "archive" / "docs-reorg-backup"
MANIFEST_PATH = REPO_ROOT / "reports" / "documentation" / "docs-root-migration-manifest.yaml"
REF_GRAPH_PATH = REPO_ROOT / "reports" / "documentation" / "docs-reference-graph.yaml"

# Root-retention allowlist — these never move
ROOT_RETENTION = {
    "README.md",
    "agent-methodology-index.md",
    "planning-methodology.md",
    "agent-execution-handoff-standard.md",
    "plan-hardening-checklist.md",
    "fresh-chat-continuity-brief.md",
    "gates.md",
    "spec-to-feature-correction-plan-summary.md",
}

# File types that may contain references
SEARCHABLE_EXTENSIONS = {".md", ".yaml", ".yml", ".json", ".py", ".sh", ".ps1", ".txt", ".rst"}

# Directories to skip during reference scanning
SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".local/archive",
    "node_modules",
}

# Classifiers for reference type based on containing file patterns
def classify_reference(ref_file: Path, context: str) -> str:
    """Classify a reference by the file it appears in and context."""
    parts = ref_file.parts
    name = ref_file.name
    rel = str(ref_file.relative_to(REPO_ROOT)).replace("\\", "/")

    # Evidence / historical artifacts — all .local/ except active taskcards
    if rel.startswith(".local/") and ".local/taskcards/" not in rel:
        return "HISTORICAL_EVIDENCE"
    # Historical docs folders
    if rel.startswith("docs/history/") or rel.startswith("docs/_audit/") or rel.startswith("docs/audits/"):
        return "HISTORICAL_EVIDENCE"
    # Bundle metadata (evidence bundles at root)
    if rel.startswith("bundle-metadata/") or "bundle-metadata/" in rel:
        return "HISTORICAL_EVIDENCE"
    if any(p in rel for p in ["reports/certification", "reports/snoopy",
                                "reports/forensics", "reports/layer-audit"]):
        return "HISTORICAL_EVIDENCE"

    # Test references
    if "tests/" in rel:
        return "ACTIVE_TEST_REFERENCE"

    # Registry references
    if any(n in name for n in ["registry.yaml", "skill-registry.yaml", "capability-routing"]):
        return "ACTIVE_REGISTRY_REFERENCE"

    # CI/workflow
    if ".github/" in rel or "workflows/" in rel:
        return "ACTIVE_COMMAND_REFERENCE"

    # Python runtime references
    if ref_file.suffix == ".py":
        return "ACTIVE_RUNTIME_REFERENCE"

    # AGENTS.md / CLAUDE.md — governance
    if name in ("AGENTS.md", "CLAUDE.md", "GOVERNANCE.md"):
        return "ACTIVE_GOVERNANCE_REFERENCE"

    # Plans / taskcards
    if rel.startswith("plans/") or "taskcards/" in rel or ".local/taskcards/" in rel:
        return "ACTIVE_PLAN_OR_TASKCARD"

    # Reports (current, not historical)
    if rel.startswith("reports/") and "evidences" not in rel:
        return "HISTORICAL_EVIDENCE"

    # Command/skill files
    if ".claude/commands/" in rel or ".governance/" in rel:
        return "ACTIVE_COMMAND_REFERENCE"

    # Supervisor registry files (skill/capability registries are registry refs)
    if ".supervisor/" in rel:
        return "ACTIVE_REGISTRY_REFERENCE"

    # General markdown link
    return "ACTIVE_DOCUMENTATION_LINK"


def iter_repo_files() -> Iterator[Path]:
    """Yield all searchable repository files, excluding skip dirs."""
    for root, dirs, files in os.walk(REPO_ROOT):
        root_path = Path(root)
        # Prune skip dirs in-place
        dirs[:] = [
            d for d in dirs
            if not any(
                str(root_path / d).replace("\\", "/").endswith(skip.replace("\\", "/"))
                or d == skip or d.startswith(".git")
                for skip in SKIP_DIRS
            )
        ]
        for fname in files:
            fpath = root_path / fname
            if fpath.suffix.lower() in SEARCHABLE_EXTENSIONS:
                yield fpath


def get_docs_root_files() -> list[Path]:
    """Return all files directly under docs/ (not in subdirs), excluding retained ones."""
    result = []
    for p in DOCS_ROOT.iterdir():
        if p.is_file() and p.suffix in {".md", ".yaml", ".yml", ".json"}:
            result.append(p)
    return sorted(result)


def file_hash(path: Path) -> str:
    """SHA-256 hash of file contents."""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


# ---------------------------------------------------------------------------
# SUBCOMMAND: inventory
# ---------------------------------------------------------------------------

def cmd_inventory(args: argparse.Namespace) -> int:
    """List all docs/ root files with basic classification metadata."""
    files = get_docs_root_files()
    records = []
    for f in files:
        name = f.name
        is_retained = name in ROOT_RETENTION
        records.append({
            "filename": name,
            "current_path": f"docs/{name}",
            "stem": f.stem,
            "suffix": f.suffix,
            "size_bytes": f.stat().st_size,
            "sha256": file_hash(f),
            "remain_at_root": is_retained,
            "root_retention_reason": _retention_reason(name) if is_retained else None,
        })

    output = {
        "subcommand": "inventory",
        "docs_root": "docs/",
        "total_files": len(records),
        "retained_at_root": sum(1 for r in records if r["remain_at_root"]),
        "movable": sum(1 for r in records if not r["remain_at_root"]),
        "files": records,
    }

    out_path = Path(args.output) if args.output else None
    _write_or_print(output, out_path, "inventory")
    return 0


def _retention_reason(name: str) -> str:
    reasons = {
        "README.md": "canonical_entry_point",
        "agent-methodology-index.md": "validator_enforced_root_location",
        "planning-methodology.md": "validator_enforced_root_location",
        "agent-execution-handoff-standard.md": "validator_enforced_root_location",
        "plan-hardening-checklist.md": "validator_enforced_root_location",
        "fresh-chat-continuity-brief.md": "validator_enforced_root_location",
        "gates.md": "cross_cutting_policy_root_convention",
        "spec-to-feature-correction-plan-summary.md": "mandatory_agent_pre_read",
    }
    return reasons.get(name, "unknown")


# ---------------------------------------------------------------------------
# SUBCOMMAND: scan-refs
# ---------------------------------------------------------------------------

def cmd_scan_refs(args: argparse.Namespace) -> int:
    """Scan entire repository for references to docs/ root files."""
    movable_files = [
        f for f in get_docs_root_files()
        if f.name not in ROOT_RETENTION
    ]

    # Build lookup: basename -> path
    target_names = {f.name for f in movable_files}
    target_stems = {f.stem for f in movable_files}

    # Patterns to search for
    patterns = []
    for f in movable_files:
        # Exact path references
        patterns.append(re.compile(
            r"(?:docs/)" + re.escape(f.name), re.IGNORECASE
        ))

    ref_graph: dict[str, list[dict]] = {f.name: [] for f in movable_files}
    stale_count = 0

    print(f"[scan-refs] Scanning {REPO_ROOT} for {len(movable_files)} movable doc references...")

    for repo_file in iter_repo_files():
        # Skip the docs root files themselves
        if repo_file.parent == DOCS_ROOT:
            continue
        try:
            text = repo_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        for f in movable_files:
            doc_name = f.name
            # Search for docs/<name> pattern
            search_str = f"docs/{doc_name}"
            if search_str not in text and f"docs\\{doc_name}" not in text:
                continue

            # Find line numbers
            for lineno, line in enumerate(text.splitlines(), 1):
                if f"docs/{doc_name}" in line or f"docs\\{doc_name}" in line:
                    ref_type = classify_reference(repo_file, line)
                    ref_graph[doc_name].append({
                        "file": str(repo_file.relative_to(REPO_ROOT)).replace("\\", "/"),
                        "line": lineno,
                        "context": line.strip()[:200],
                        "reference_type": ref_type,
                    })
                    if args.check_stale and ref_type.startswith("ACTIVE_"):
                        stale_count += 1

    # Summarize
    summary: list[dict] = []
    for f in movable_files:
        refs = ref_graph[f.name]
        active = [r for r in refs if r["reference_type"].startswith("ACTIVE_")]
        historical = [r for r in refs if r["reference_type"] == "HISTORICAL_EVIDENCE"]
        summary.append({
            "filename": f.name,
            "current_path": f"docs/{f.name}",
            "total_references": len(refs),
            "active_references": len(active),
            "historical_references": len(historical),
            "references": refs,
        })

    output = {
        "subcommand": "scan-refs",
        "scanned_movable_files": len(movable_files),
        "files_with_active_refs": sum(1 for s in summary if s["active_references"] > 0),
        "files_with_zero_active_refs": sum(1 for s in summary if s["active_references"] == 0),
        "stale_active_refs_to_old_paths": stale_count if args.check_stale else "not_checked",
        "results": summary,
    }

    out_path = Path(args.output) if args.output else REF_GRAPH_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _write_or_print(output, out_path, "scan-refs")

    if args.check_stale and stale_count > 0:
        print(f"[scan-refs] FAIL: {stale_count} stale active references to old docs/ paths found")
        return 1
    return 0


# ---------------------------------------------------------------------------
# SUBCOMMAND: manifest (validate only — generation is done by TC-DOCS-005)
# ---------------------------------------------------------------------------

def cmd_manifest(args: argparse.Namespace) -> int:
    """Validate the frozen migration manifest."""
    if not MANIFEST_PATH.exists():
        print(f"[manifest] Manifest not found: {MANIFEST_PATH}")
        return 1

    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    items = manifest.get("items", [])
    errors = []

    for item in items:
        mid = item.get("migration_id", "?")
        src = item.get("source_path", "")
        dst = item.get("destination_path", "")
        if not src:
            errors.append(f"{mid}: missing source_path")
        if not dst:
            errors.append(f"{mid}: missing destination_path")
        if item.get("move_status") == "COMPLETE" and not (REPO_ROOT / dst).exists():
            errors.append(f"{mid}: COMPLETE but destination does not exist: {dst}")

    if errors:
        for e in errors:
            print(f"[manifest] ERROR: {e}")
        return 1

    print(f"[manifest] OK: {len(items)} items, all valid")
    return 0


# ---------------------------------------------------------------------------
# SUBCOMMAND: move
# ---------------------------------------------------------------------------

def cmd_move(args: argparse.Namespace) -> int:
    """Execute a single file move: git mv + update active references."""
    src = REPO_ROOT / args.source
    dst = REPO_ROOT / args.dest

    if not src.exists():
        print(f"[move] Source not found: {src}")
        return 1
    if dst.exists():
        print(f"[move] Destination already exists: {dst}")
        return 1

    # Backup
    if not args.dry_run:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        backup_path = BACKUP_DIR / src.name
        shutil.copy2(src, backup_path)
        print(f"[move] Backed up to {backup_path}")

    # Git mv
    if not args.dry_run:
        result = subprocess.run(
            ["git", "mv", str(src), str(dst)],
            cwd=REPO_ROOT, capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"[move] git mv failed: {result.stderr}")
            return 1
        print(f"[move] git mv {args.source} -> {args.dest}")
    else:
        print(f"[move] DRY RUN: would git mv {args.source} -> {args.dest}")

    # Update active references
    old_ref = args.source.replace("\\", "/")
    new_ref = args.dest.replace("\\", "/")
    updated_files = []

    if not args.dry_run:
        for repo_file in iter_repo_files():
            if repo_file == dst:
                continue
            try:
                text = repo_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            if old_ref not in text and old_ref.replace("/", "\\") not in text:
                continue
            ref_type = classify_reference(repo_file, "")
            if ref_type == "HISTORICAL_EVIDENCE":
                continue  # Preserve historical references as-is
            new_text = text.replace(old_ref, new_ref)
            new_text = new_text.replace(old_ref.replace("/", "\\"), new_ref)
            if new_text != text:
                repo_file.write_text(new_text, encoding="utf-8")
                updated_files.append(str(repo_file.relative_to(REPO_ROOT)))

        if updated_files:
            print(f"[move] Updated {len(updated_files)} files:")
            for uf in updated_files:
                print(f"         {uf}")
    else:
        print(f"[move] DRY RUN: would update references from {old_ref} -> {new_ref}")

    return 0


# ---------------------------------------------------------------------------
# SUBCOMMAND: validate
# ---------------------------------------------------------------------------

def cmd_validate(args: argparse.Namespace) -> int:
    """Validate post-move state."""
    errors = []

    if args.source and args.dest:
        # Single-file validation
        src_path = REPO_ROOT / args.source
        dst_path = REPO_ROOT / args.dest
        stub_mode = getattr(args, "stub", False)
        if src_path.exists() and not stub_mode:
            errors.append(f"Source still exists (should be gone): {args.source}")
        if src_path.exists() and stub_mode:
            # Verify stub is thin (< 50 lines, contains deprecation notice)
            stub_text = src_path.read_text(encoding="utf-8", errors="replace")
            stub_lines = stub_text.splitlines()
            if len(stub_lines) > 50:
                errors.append(f"Stub too large ({len(stub_lines)} lines > 50): {args.source}")
            if "DEPRECATED" not in stub_text and "deprecated" not in stub_text.lower():
                errors.append(f"Stub missing deprecation notice: {args.source}")
            if args.dest not in stub_text:
                errors.append(f"Stub does not reference canonical path {args.dest}: {args.source}")
        if not dst_path.exists():
            errors.append(f"Destination does not exist: {args.dest}")
        # Check for stale active refs to old path
        old_ref = args.source.replace("\\", "/")
        # Files exempt from stale-ref checking (they document migration, not operational deps)
        migration_exempt = {
            "reports/documentation/docs-root-migration-manifest.yaml",
            "reports/documentation/docs-root-destination-map.yaml",
            "reports/documentation/docs-root-inventory.yaml",
            "reports/documentation/docs-historical-reference-disposition.yaml",
        }
        for repo_file in iter_repo_files():
            rel_path = str(repo_file.relative_to(REPO_ROOT)).replace("\\", "/")
            if rel_path in migration_exempt:
                continue
            # Skip migration plan files documenting source→dest paths
            if rel_path.startswith("plans/.claude/"):
                continue
            try:
                text = repo_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            if old_ref in text:
                ref_type = classify_reference(repo_file, "")
                if ref_type != "HISTORICAL_EVIDENCE":
                    errors.append(
                        f"Stale active ref in {rel_path}: {old_ref}"
                    )

    elif args.full:
        # Full validation: check all moved items in manifest
        if not MANIFEST_PATH.exists():
            print("[validate] No manifest found; skipping full validation")
            return 0
        manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
        for item in manifest.get("items", []):
            if item.get("move_status") != "COMPLETE":
                continue
            dst = REPO_ROOT / item["destination_path"]
            src = REPO_ROOT / item["source_path"]
            if not dst.exists():
                errors.append(f"Missing dest: {item['destination_path']}")
            if src.exists() and item.get("compatibility_strategy") != "TEMPORARY_COMPATIBILITY_STUB":
                errors.append(f"Source still present (not a stub): {item['source_path']}")

    if errors:
        for e in errors:
            print(f"[validate] FAIL: {e}")
        return 1

    print("[validate] PASS")
    return 0


# ---------------------------------------------------------------------------
# SUBCOMMAND: rollback
# ---------------------------------------------------------------------------

def cmd_rollback(args: argparse.Namespace) -> int:
    """Restore a file from backup."""
    src_name = Path(args.source).name
    backup_path = BACKUP_DIR / src_name
    restore_path = REPO_ROOT / args.source

    if not backup_path.exists():
        print(f"[rollback] No backup found: {backup_path}")
        return 1

    shutil.copy2(backup_path, restore_path)
    print(f"[rollback] Restored {src_name} to {restore_path}")
    return 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_or_print(data: dict, path: Path | None, label: str) -> None:
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True),
                        encoding="utf-8")
        print(f"[{label}] Written to {path}")
    else:
        print(yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="docs/ root migration engine (DOCS-REORG-001)"
    )
    sub = parser.add_subparsers(dest="subcommand")

    # inventory
    p_inv = sub.add_parser("inventory", help="List docs/ root files")
    p_inv.add_argument("--output", help="Output YAML path")

    # scan-refs
    p_scan = sub.add_parser("scan-refs", help="Scan repo for docs/ root references")
    p_scan.add_argument("--output", help="Output YAML path")
    p_scan.add_argument("--check-stale", action="store_true",
                        help="Fail if active refs to old paths found (post-move check)")

    # manifest
    p_man = sub.add_parser("manifest", help="Validate migration manifest")
    p_man.add_argument("--validate", action="store_true", default=True)

    # move
    p_move = sub.add_parser("move", help="Execute a single file move + ref updates")
    p_move.add_argument("--source", required=True, help="Source relative path (docs/file.md)")
    p_move.add_argument("--dest", required=True, help="Destination relative path")
    p_move.add_argument("--dry-run", action="store_true")

    # validate
    p_val = sub.add_parser("validate", help="Post-move validation")
    p_val.add_argument("--source", help="Old path (for single-file check)")
    p_val.add_argument("--dest", help="New path (for single-file check)")
    p_val.add_argument("--full", action="store_true", help="Full manifest validation")
    p_val.add_argument("--wave", type=int, help="Wave number (informational)")
    p_val.add_argument("--stub", action="store_true", help="Allow stub at old path (compatibility stub case)")

    # rollback
    p_roll = sub.add_parser("rollback", help="Restore file from backup")
    p_roll.add_argument("--source", required=True, help="Original path to restore")

    args = parser.parse_args()

    dispatch = {
        "inventory": cmd_inventory,
        "scan-refs": cmd_scan_refs,
        "manifest": cmd_manifest,
        "move": cmd_move,
        "validate": cmd_validate,
        "rollback": cmd_rollback,
    }

    if args.subcommand not in dispatch:
        parser.print_help()
        return 1

    return dispatch[args.subcommand](args)


if __name__ == "__main__":
    sys.exit(main())
