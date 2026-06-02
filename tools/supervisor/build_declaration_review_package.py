"""
build_declaration_review_package.py — Declaration Review Package Builder

Packages declaration-only evidence into a reviewable ZIP for external transfer
or archival. Supports the case where no inner ZIP was produced.

Packages:
- evidence-declaration.yaml
- evidence-manifest.yaml (if present)
- materialized-evidence-manifest.yaml (from materializer output)
- missing-evidence-report.md
- source-change-diffs.patch
- work-item-grades.json
- work-item-grades.md
- reports/supervisor/materialized-evidence-review.md
- reports/r90/product-code-change-ledger.json (snapshot)
- product-capability-matrix/poc-targets.yaml (snapshot)
- reports/supervisor/session-resume.md
- reports/supervisor/next-sprint.md
- reports/supervisor/work-item-grades.json
- reports/supervisor/work-item-grades.md

Output:
- .local/supervisor/reviews/<run_id>/declaration-review-package.zip

Exit codes:
  0 — package built successfully
  2 — package built with missing artifacts (partial)
  9 — unexpected error
"""

import argparse
import hashlib
import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def add_file_to_zip(zf: zipfile.ZipFile, src: Path, arcname: str, missing_list: list):
    """Add a file to the ZIP, recording it as missing if not found."""
    if src.exists() and src.is_file():
        zf.write(src, arcname)
        return True
    else:
        missing_list.append(str(src))
        return False


def build_package(declaration_path: Path, repo_root: Path, out_dir: Path) -> dict:
    """Build the declaration review package ZIP."""
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load declaration for run_id
    with open(declaration_path, encoding="utf-8") as f:
        decl = yaml.safe_load(f)

    run_id = decl.get("run_id", "unknown")
    sprint_id = decl.get("sprint_id", "unknown")
    timestamp = datetime.now().isoformat()

    # Materialized output dir
    materialized_dir = repo_root / ".local" / "supervisor" / "materialized" / run_id
    evidence_root = repo_root / ".local" / "evidences" / run_id

    zip_path = out_dir / f"declaration-review-package.zip"
    missing = []

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # --- Core declaration files ---
        add_file_to_zip(zf, declaration_path, "evidence/evidence-declaration.yaml", missing)
        manifest_path = evidence_root / "evidence-manifest.yaml"
        add_file_to_zip(zf, manifest_path, "evidence/evidence-manifest.yaml", missing)

        # --- Materialized evidence ---
        mat_manifest = materialized_dir / "materialized-evidence-manifest.yaml"
        add_file_to_zip(zf, mat_manifest, "materialized/materialized-evidence-manifest.yaml", missing)

        missing_report = materialized_dir / "missing-evidence-report.md"
        add_file_to_zip(zf, missing_report, "materialized/missing-evidence-report.md", missing)

        patch = materialized_dir / "source-change-diffs.patch"
        add_file_to_zip(zf, patch, "materialized/source-change-diffs.patch", missing)

        # --- Supervisor outputs ---
        for fname in [
            "work-item-grades.json",
            "work-item-grades.md",
            "work-item-grades.yaml",
            "session-resume.md",
            "next-sprint.md",
            "materialized-evidence-review.md",
        ]:
            src = repo_root / "reports" / "supervisor" / fname
            add_file_to_zip(zf, src, f"supervisor/{fname}", missing)

        # --- Product-code ledger snapshot ---
        ledger = repo_root / "reports" / "r90" / "product-code-change-ledger.json"
        add_file_to_zip(zf, ledger, "state/product-code-change-ledger.json", missing)

        # --- POC matrix snapshot ---
        poc = repo_root / "product-capability-matrix" / "poc-targets.yaml"
        add_file_to_zip(zf, poc, "state/poc-targets.yaml", missing)

        # --- R92 work-item grades for r91 review ---
        for fname in ["r91-work-item-grades.json", "r91-work-item-grades.md"]:
            src = repo_root / "reports" / "r92" / fname
            add_file_to_zip(zf, src, f"r91-review/{fname}", missing)

        # --- Package manifest ---
        pkg_manifest = {
            "run_id": run_id,
            "sprint_id": sprint_id,
            "built_at": timestamp,
            "zip_path": str(zip_path),
            "artifacts_missing": missing,
            "artifacts_missing_count": len(missing),
        }
        zf.writestr(
            "package-manifest.json",
            json.dumps(pkg_manifest, indent=2)
        )

    # Compute ZIP SHA-256
    zip_sha = sha256_file(zip_path)
    zip_size = zip_path.stat().st_size

    # Write SHA sidecar
    sidecar = {
        "run_id": run_id,
        "sprint_id": sprint_id,
        "built_at": timestamp,
        "zip_sha256": zip_sha,
        "zip_size_bytes": zip_size,
        "artifacts_missing_count": len(missing),
    }
    sidecar_path = out_dir / "declaration-review-package.sha256.json"
    sidecar_path.write_text(json.dumps(sidecar, indent=2), encoding="utf-8")

    print(f"Declaration review package: {zip_path}")
    print(f"ZIP SHA-256: {zip_sha}")
    print(f"ZIP size: {zip_size} bytes")
    print(f"Missing artifacts: {len(missing)}")

    exit_code = 0 if not missing else 2
    return {
        "exit_code": exit_code,
        "run_id": run_id,
        "zip_path": str(zip_path),
        "zip_sha256": zip_sha,
        "zip_size_bytes": zip_size,
        "missing_count": len(missing),
        "missing": missing,
        "sidecar_path": str(sidecar_path),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Build a declaration review package ZIP"
    )
    parser.add_argument(
        "--declaration",
        required=True,
        type=Path,
        help="Path to evidence-declaration.yaml",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory (default: .local/supervisor/reviews/<run_id>/)",
    )
    args = parser.parse_args()

    decl_path = args.declaration
    if not decl_path.is_absolute():
        decl_path = Path.cwd() / decl_path
    if not decl_path.exists():
        print(f"ERROR: Declaration not found: {decl_path}", file=sys.stderr)
        sys.exit(9)

    repo_root = args.repo_root
    if not repo_root.is_absolute():
        repo_root = Path.cwd() / repo_root

    try:
        with open(decl_path, encoding="utf-8") as f:
            decl = yaml.safe_load(f)
        run_id = decl.get("run_id", "unknown")
    except Exception:
        run_id = "unknown"

    out_dir = args.out_dir or (repo_root / ".local" / "supervisor" / "reviews" / run_id)

    result = build_package(decl_path, repo_root, out_dir)

    if result["exit_code"] == 0:
        print("BUILD: SUCCESS (all artifacts included)")
    else:
        print(f"BUILD: PARTIAL ({result['missing_count']} artifacts missing)")

    sys.exit(result["exit_code"])


if __name__ == "__main__":
    main()
