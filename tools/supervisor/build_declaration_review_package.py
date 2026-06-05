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

    # R108: Also check declaration's evidence_root for manifest (autonomous_cycle writes there)
    decl_evidence_root = repo_root / decl.get("evidence_root", "") if decl.get("evidence_root") else None

    zip_path = out_dir / f"declaration-review-package.zip"
    missing = []

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # --- Core declaration files ---
        add_file_to_zip(zf, declaration_path, "evidence/evidence-declaration.yaml", missing)
        # R108: Try manifest from .local/evidences/{run_id}/ first, then declaration evidence_root
        manifest_path = evidence_root / "evidence-manifest.yaml"
        if not manifest_path.exists() and decl_evidence_root:
            alt_manifest = decl_evidence_root / "evidence-manifest.yaml"
            if alt_manifest.exists():
                manifest_path = alt_manifest
        add_file_to_zip(zf, manifest_path, "evidence/evidence-manifest.yaml", missing)

        # --- Materialized evidence ---
        mat_manifest = materialized_dir / "materialized-evidence-manifest.yaml"
        add_file_to_zip(zf, mat_manifest, "materialized/materialized-evidence-manifest.yaml", missing)

        missing_report = materialized_dir / "missing-evidence-report.md"
        add_file_to_zip(zf, missing_report, "materialized/missing-evidence-report.md", missing)

        patch = materialized_dir / "source-change-diffs.patch"
        add_file_to_zip(zf, patch, "materialized/source-change-diffs.patch", missing)

        # --- R105: Stream-scoped supervisor outputs ---
        # Files from the run_id's own review directory go under supervisor/
        # (these are stream-correct because they were generated for this run)
        review_run_dir = repo_root / ".local" / "supervisor" / "reviews" / run_id
        for fname in [
            "work-item-grades.json",
            "work-item-grades.md",
            "work-item-grades.yaml",
            "supervisor-review.md",
            "supervisor-review.json",
            "combined-next-worker-prompt.md",
            "supervisor-cycle-manifest.yaml",
        ]:
            src = review_run_dir / fname
            if src.exists():
                add_file_to_zip(zf, src, f"supervisor/{fname}", [])
            else:
                # Fallback to global reports/supervisor/ for grades/prompts
                fallback = repo_root / "reports" / "supervisor" / fname
                if fallback.exists():
                    add_file_to_zip(zf, fallback, f"supervisor/{fname}", [])

        # Materialized evidence review (stream-specific if available)
        mat_review = repo_root / "reports" / "supervisor" / "materialized-evidence-review.md"
        add_file_to_zip(zf, mat_review, "supervisor/materialized-evidence-review.md", missing)

        # --- R105: Global state goes under global-state/ (explicitly cross-stream) ---
        # These files reflect whichever stream ran the autonomous-cycle last,
        # NOT necessarily this declaration's stream.
        for fname in [
            "latest-cycle-summary.md",
            "evidence-review.md",
            "contradictions.md",
            "session-resume.md",
            "next-sprint.md",
            "approval-gates.md",
            "context-pack.md",
            "mcp-status.md",
            "mcp-status.json",
        ]:
            src = repo_root / "reports" / "supervisor" / fname
            add_file_to_zip(zf, src, f"global-state/supervisor/{fname}", [])

        # --- Product-code ledger snapshot ---
        ledger = repo_root / "reports" / "r90" / "product-code-change-ledger.json"
        add_file_to_zip(zf, ledger, "global-state/product-code-change-ledger.json", missing)

        # --- POC matrix snapshot ---
        poc = repo_root / "product-capability-matrix" / "poc-targets.yaml"
        add_file_to_zip(zf, poc, "global-state/poc-targets.yaml", missing)

        # --- R92 work-item grades for r91 review ---
        for fname in ["r91-work-item-grades.json", "r91-work-item-grades.md"]:
            src = repo_root / "reports" / "r92" / fname
            add_file_to_zip(zf, src, f"historical/{fname}", [])

        # --- Context pack (global, may reference any stream) ---
        context_yaml = repo_root / ".supervisor" / "context-pack.yaml"
        add_file_to_zip(zf, context_yaml, "global-state/context-pack.yaml", [])

        # --- MCP proof ---
        mcp_json = repo_root / ".vscode" / "mcp.json"
        add_file_to_zip(zf, mcp_json, "global-state/mcp.json", [])

        # --- Selected product gaps (global, may be stale/wrong-stream) ---
        gaps_json = repo_root / ".local" / "supervisor" / "selected-product-gaps.json"
        add_file_to_zip(zf, gaps_json, "global-state/selected-product-gaps.json", [])

        # --- Continuation signal ---
        cont_signal = repo_root / ".local" / "supervisor" / "continuation-signal.json"
        add_file_to_zip(zf, cont_signal, "global-state/continuation-signal.json", [])

        # --- R104: Walk declaration evidence_root directory recursively ---
        seen_arcnames = set()
        decl_evidence_root = decl.get("evidence_root", "")
        if decl_evidence_root:
            ev_dir = repo_root / decl_evidence_root
            if ev_dir.is_dir():
                for ev_file in sorted(ev_dir.rglob("*")):
                    if ev_file.is_file():
                        rel = ev_file.relative_to(repo_root)
                        arcname = f"sprint-evidence/{rel.as_posix()}"
                        if arcname not in seen_arcnames:
                            zf.write(ev_file, arcname)
                            seen_arcnames.add(arcname)

        # --- R104: Include evidence_artifacts from declaration ---
        for art in decl.get("evidence_artifacts", []):
            art_path = art.get("path", "")
            if not art_path:
                continue
            src = repo_root / art_path
            if not src.exists() or not src.is_file():
                continue
            arcname = f"sprint-evidence/{art_path}"
            if arcname not in seen_arcnames:
                zf.write(src, arcname)
                seen_arcnames.add(arcname)

        # --- R104: Include work item evidence_paths ---
        for item in decl.get("planned_work_items", []):
            for ep in item.get("evidence_paths", []):
                src = repo_root / ep
                if src.exists() and src.is_file():
                    arcname = f"sprint-evidence/{ep}"
                    if arcname not in seen_arcnames:
                        zf.write(src, arcname)
                        seen_arcnames.add(arcname)

        # --- Review-directory artifacts (grades, prompts, inspection) ---
        review_out = repo_root / ".local" / "supervisor" / "reviews" / run_id
        if review_out.is_dir():
            for review_file in sorted(review_out.iterdir()):
                if review_file.is_file() and review_file.name != "declaration-review-package.zip":
                    arcname = f"review/{review_file.name}"
                    if arcname not in seen_arcnames:
                        zf.write(review_file, arcname)
                        seen_arcnames.add(arcname)

        # --- R104: Include declared changed files (tools/tests/supervisor) ---
        for cf in decl.get("changed_files", []):
            src = repo_root / cf
            if src.exists() and src.is_file():
                arcname = f"changed-files/{cf}"
                if arcname not in seen_arcnames:
                    zf.write(src, arcname)
                    seen_arcnames.add(arcname)

        # --- R104: Stream identity validation ---
        stream_warnings = []
        try:
            # Detect stream from sprint_id
            import re
            sid = sprint_id.upper()
            m = re.match(r"FORMAT-FACTORY-(SUPERVISOR|ACCELERATION|SKILLS|MAINSTREAM)-R\d+", sid)
            detected_stream = m.group(1).lower() if m else "mainstream"

            # Check state files for wrong-stream references
            for check_name, check_path in [
                ("context-pack.yaml", repo_root / ".supervisor" / "context-pack.yaml"),
                ("evidence-review.md", repo_root / "reports" / "supervisor" / "evidence-review.md"),
                ("contradictions.md", repo_root / "reports" / "supervisor" / "contradictions.md"),
            ]:
                if check_path.exists():
                    content = check_path.read_text(encoding="utf-8", errors="replace")[:2000]
                    # Check if content references a different stream's sprint
                    for other_stream in ["SUPERVISOR", "ACCELERATION", "SKILLS", "MAINSTREAM"]:
                        if other_stream.lower() == detected_stream:
                            continue
                        pattern = f"FORMAT-FACTORY-{other_stream}-R\\d+"
                        if re.search(pattern, content, re.IGNORECASE):
                            stream_warnings.append(
                                f"{check_name} references {other_stream} stream (current: {detected_stream})"
                            )
        except Exception:
            pass

        # --- Package manifest ---
        pkg_manifest = {
            "run_id": run_id,
            "sprint_id": sprint_id,
            "built_at": timestamp,
            "zip_path": str(zip_path),
            "artifacts_missing": missing,
            "artifacts_missing_count": len(missing),
            "stream_identity_warnings": stream_warnings,
            "declared_changed_files_count": len(decl.get("changed_files", [])),
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
