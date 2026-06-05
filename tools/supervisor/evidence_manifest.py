"""
evidence_manifest.py — Evidence Manifest Generator and Validator
Generates or validates an evidence-manifest.yaml for a given evidence directory.

The manifest catalogs every artifact in the evidence directory with:
  - path (relative to repo root)
  - type (from schema enum)
  - sha256 hash
  - size in bytes
  - optional description, produced_by, related_work_item_ids

Can also validate an existing manifest against the filesystem (check that
every declared artifact exists and hashes match).

Exit codes:
  0 — success (generated or validated)
  1 — validation failed (missing files or hash mismatch)
  9 — unexpected error

Usage:
  python tools/supervisor/evidence_manifest.py generate --declaration PATH [--out PATH]
  python tools/supervisor/evidence_manifest.py validate --manifest PATH [--repo-root PATH]
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent
SCHEMA_DIR = REPO_ROOT / ".supervisor" / "schemas"

ARTIFACT_TYPE_MAP = {
    "evidence-declaration.yaml": "declaration",
    "evidence-manifest.yaml": "manifest",
    "final-verdict.md": "verdict",
    "test-results.txt": "test-log",
    "test-log.txt": "test-log",
    "pytest.log": "test-log",
}

KNOWN_TYPES = {
    "declaration", "manifest", "verdict", "report", "test-log",
    "validation-log", "proof", "code", "config", "data", "other",
}


def sha256_file(path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def infer_type(filename: str) -> str:
    """Infer artifact type from filename."""
    if filename in ARTIFACT_TYPE_MAP:
        return ARTIFACT_TYPE_MAP[filename]
    ext = Path(filename).suffix.lower()
    type_by_ext = {
        ".yaml": "config",
        ".yml": "config",
        ".json": "data",
        ".md": "report",
        ".txt": "report",
        ".py": "code",
        ".log": "validation-log",
    }
    return type_by_ext.get(ext, "other")


def generate_from_declaration(declaration_path: Path, repo_root: Path) -> dict:
    """Generate a manifest from an evidence-declaration.yaml.

    Scans the evidence_root directory for all files and builds the manifest.
    Enriches entries with SHA-256 and size. Uses the declaration's
    evidence_artifacts for type/description when available.
    """
    decl = yaml.safe_load(declaration_path.read_text(encoding="utf-8"))
    run_id = decl.get("run_id", "unknown")
    evidence_root = decl.get("evidence_root", "")

    if not evidence_root:
        raise ValueError("Declaration has no evidence_root")

    root_path = repo_root / evidence_root
    if not root_path.is_dir():
        raise FileNotFoundError(f"evidence_root does not exist: {root_path}")

    # Build lookup from declaration's evidence_artifacts
    decl_artifacts = {}
    for art in decl.get("evidence_artifacts", []):
        p = art.get("path", "")
        if p:
            decl_artifacts[p] = art

    # Scan all files in evidence_root
    artifacts = []
    for file_path in sorted(root_path.rglob("*")):
        if not file_path.is_file():
            continue
        # A manifest cannot contain a stable hash of itself after rewrite.
        if file_path.name == "evidence-manifest.yaml":
            continue
        rel_path = str(file_path.relative_to(repo_root)).replace("\\", "/")

        # Use declaration metadata if available
        decl_art = decl_artifacts.get(rel_path, {})
        art_type = decl_art.get("type", infer_type(file_path.name))
        description = decl_art.get("description", "")

        entry = {
            "path": rel_path,
            "type": art_type,
            "sha256": sha256_file(file_path),
            "size_bytes": file_path.stat().st_size,
        }
        if description:
            entry["description"] = description

        # Mark declaration and manifest as required
        if file_path.name in ("evidence-declaration.yaml", "evidence-manifest.yaml", "final-verdict.md"):
            entry["required"] = True

        artifacts.append(entry)

    # R103: Also include declared evidence_artifacts that live outside evidence_root
    seen_paths = {a["path"] for a in artifacts}
    for art in decl.get("evidence_artifacts", []):
        rel = art.get("path", "")
        if not rel or rel in seen_paths:
            continue
        full = repo_root / rel
        if not full.exists() or not full.is_file():
            continue
        entry = {
            "path": rel.replace("\\", "/"),
            "type": art.get("type", infer_type(full.name)),
            "sha256": sha256_file(full),
            "size_bytes": full.stat().st_size,
        }
        desc = art.get("description", "")
        if desc:
            entry["description"] = desc
        artifacts.append(entry)
        seen_paths.add(rel)

    manifest = {
        "run_id": run_id,
        "evidence_root": evidence_root,
        "generated_at": datetime.now().isoformat(),
        "artifacts": artifacts,
    }
    return manifest


def validate_manifest(manifest_path: Path, repo_root: Path) -> dict:
    """Validate an existing manifest: check file existence and SHA-256 hashes.

    Returns a result dict with valid=True/False and lists of errors.
    """
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    errors = []

    if "run_id" not in manifest:
        errors.append("Missing required field: run_id")
    if "evidence_root" not in manifest:
        errors.append("Missing required field: evidence_root")
    if "artifacts" not in manifest:
        errors.append("Missing required field: artifacts")
        return {"valid": False, "errors": errors, "checked": 0, "mismatches": 0}

    checked = 0
    mismatches = 0
    missing = 0

    for i, art in enumerate(manifest["artifacts"]):
        rel_path = art.get("path", "")
        if not rel_path:
            errors.append(f"artifacts[{i}]: missing path")
            continue

        full_path = repo_root / rel_path
        if not full_path.exists():
            errors.append(f"artifacts[{i}]: file not found: {rel_path}")
            missing += 1
            continue

        checked += 1
        declared_sha = art.get("sha256", "")
        if declared_sha:
            actual_sha = sha256_file(full_path)
            if actual_sha != declared_sha:
                errors.append(
                    f"artifacts[{i}]: SHA-256 mismatch for {rel_path}: "
                    f"declared={declared_sha[:16]}... actual={actual_sha[:16]}..."
                )
                mismatches += 1

        declared_size = art.get("size_bytes")
        if declared_size is not None:
            actual_size = full_path.stat().st_size
            if actual_size != declared_size:
                errors.append(
                    f"artifacts[{i}]: size mismatch for {rel_path}: "
                    f"declared={declared_size} actual={actual_size}"
                )

        art_type = art.get("type", "")
        if art_type and art_type not in KNOWN_TYPES:
            errors.append(f"artifacts[{i}]: unknown type '{art_type}' for {rel_path}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "checked": checked,
        "missing": missing,
        "mismatches": mismatches,
        "artifact_count": len(manifest.get("artifacts", [])),
    }


def write_manifest(manifest: dict, out_path: Path) -> None:
    """Write manifest YAML to disk."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        yaml.dump(manifest, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate or validate evidence-manifest.yaml"
    )
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("generate", help="Generate manifest from declaration")
    gen.add_argument("--declaration", type=Path, required=True)
    gen.add_argument("--out", type=Path, help="Output path (default: alongside declaration)")
    gen.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    gen.add_argument("--json", action="store_true")

    val = sub.add_parser("validate", help="Validate existing manifest")
    val.add_argument("--manifest", type=Path, required=True)
    val.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    val.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "generate":
        try:
            manifest = generate_from_declaration(args.declaration, args.repo_root)
        except (ValueError, FileNotFoundError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1

        out_path = args.out
        if not out_path:
            out_path = args.declaration.parent / "evidence-manifest.yaml"
        write_manifest(manifest, out_path)

        if getattr(args, "json", False):
            print(json.dumps(manifest, indent=2))
        else:
            print(f"MANIFEST_GENERATED: {out_path}")
            print(f"  Artifacts: {len(manifest['artifacts'])}")
            print(f"  Run ID: {manifest['run_id']}")
        return 0

    elif args.command == "validate":
        result = validate_manifest(args.manifest, args.repo_root)

        if getattr(args, "json", False):
            print(json.dumps(result, indent=2))
        else:
            status = "VALID" if result["valid"] else "INVALID"
            print(f"MANIFEST_{status}: {args.manifest}")
            print(f"  Checked: {result['checked']}, Missing: {result['missing']}, Mismatches: {result['mismatches']}")
            for err in result["errors"]:
                print(f"  ERROR: {err}")

        return 0 if result["valid"] else 1

    else:
        parser.print_help()
        return 9


if __name__ == "__main__":
    sys.exit(main())
