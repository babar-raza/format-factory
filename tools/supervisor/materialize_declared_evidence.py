"""
materialize_declared_evidence.py — Declaration Evidence Materializer

Turns a declaration-only evidence submission into a verifiable, reviewable package.

Given an evidence-declaration.yaml, this tool:
1. Resolves the evidence root.
2. Verifies every declared evidence path and changed file.
3. Computes SHA-256 for every resolved artifact.
4. Captures git diff for declared source changes (if working tree has changes).
5. Captures source snapshots for declared src/* changes.
6. Captures product-code ledger entries referenced in the declaration.
7. Captures POC matrix snapshot.
8. Produces:
   - .local/supervisor/materialized/<run_id>/materialized-evidence-manifest.yaml
   - .local/supervisor/materialized/<run_id>/missing-evidence-report.md
   - .local/supervisor/materialized/<run_id>/source-change-diffs.patch
   - reports/supervisor/materialized-evidence-review.md

Exit codes:
  0 — all declared artifacts verified
  2 — some artifacts missing (partial; grades still generated)
  9 — unexpected error
"""

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent


def sha256_file(path: Path) -> str:
    """Compute SHA-256 of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def git_diff_file(repo_root: Path, rel_path: str) -> str:
    """Get git diff for a specific file.

    Checks in order:
    1. Working tree changes (HEAD vs working tree)
    2. Staged changes (HEAD vs index)
    3. Last committed change (HEAD~1 vs HEAD) — captures real diffs for already-committed files
    """
    try:
        # 1. Working tree diff
        result = subprocess.run(
            ["git", "diff", "HEAD", "--", rel_path],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.stdout.strip():
            return result.stdout

        # 2. Staged diff
        result2 = subprocess.run(
            ["git", "diff", "--cached", "HEAD", "--", rel_path],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result2.stdout.strip():
            return result2.stdout

        # 3. Last committed diff (R94 fix: capture real diffs for committed files)
        result3 = subprocess.run(
            ["git", "log", "-1", "-p", "--", rel_path],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result3.stdout.strip():
            return result3.stdout

        # 4. R108: Untracked file — produce full-content diff
        full_path = repo_root / rel_path
        if full_path.exists():
            result4 = subprocess.run(
                ["git", "diff", "--no-index", "/dev/null", rel_path],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result4.stdout.strip():
                return f"# NEW_FILE (untracked)\n{result4.stdout}"

        return ""
    except Exception as e:
        return f"# git diff failed: {e}\n"


def git_show_file(repo_root: Path, rel_path: str) -> str:
    """Show current HEAD content of a file as a diff context."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-1", "--", rel_path],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout.strip() or "(no git log for file)"
    except Exception as e:
        return f"(git log failed: {e})"


def load_declaration(declaration_path: Path) -> dict:
    """Load and parse the evidence declaration."""
    with open(declaration_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def verify_artifact(repo_root: Path, path_str: str) -> dict:
    """Verify an artifact path and compute SHA-256 if found."""
    p = (repo_root / path_str) if not Path(path_str).is_absolute() else Path(path_str)
    exists = p.exists()
    result = {
        "path": path_str,
        "exists": exists,
        "sha256": None,
        "size_bytes": None,
    }
    if exists and p.is_file():
        result["sha256"] = sha256_file(p)
        result["size_bytes"] = p.stat().st_size
    return result


def materialize(declaration_path: Path, repo_root: Path, out_dir: Path) -> dict:
    """Run the full materialization."""
    out_dir.mkdir(parents=True, exist_ok=True)

    decl = load_declaration(declaration_path)
    run_id = decl.get("run_id", "unknown")
    sprint_id = decl.get("sprint_id", "unknown")
    evidence_root = decl.get("evidence_root", "")
    changed_files = decl.get("changed_files", [])
    planned_items = decl.get("planned_work_items", [])
    evidence_artifacts = decl.get("evidence_artifacts", [])
    test_results = decl.get("test_results", {})

    timestamp = datetime.now().isoformat()

    # --- Collect all paths to verify ---
    all_paths_to_check = []

    # Evidence artifact paths
    for art in evidence_artifacts:
        p = art.get("path", "") if isinstance(art, dict) else str(art)
        if p:
            all_paths_to_check.append(p)

    # Changed files
    for cf in changed_files:
        if cf not in all_paths_to_check:
            all_paths_to_check.append(cf)

    # Work item evidence paths
    for item in planned_items:
        for ep in item.get("evidence_paths", []):
            if ep not in all_paths_to_check:
                all_paths_to_check.append(ep)

    # Verify all paths
    verified = []
    missing = []
    for path_str in all_paths_to_check:
        result = verify_artifact(repo_root, path_str)
        if result["exists"]:
            verified.append(result)
        else:
            missing.append(result)

    # --- Capture git diffs for ALL declared changed files (R104: not just src/*) ---
    diffs = []
    for src_path in changed_files:
        diff = git_diff_file(repo_root, src_path)
        git_log = git_show_file(repo_root, src_path)
        diffs.append({
            "path": src_path,
            "last_commit": git_log,
            "diff": diff or "(no diff available — file is committed clean with no recent changes)",
        })

    # Write diffs patch file
    patch_content = ""
    for d in diffs:
        patch_content += f"# --- {d['path']} ---\n"
        patch_content += f"# Last commit: {d['last_commit']}\n"
        patch_content += d["diff"] + "\n"

    patch_path = out_dir / "source-change-diffs.patch"
    patch_path.write_text(patch_content or "# No diffs (all committed clean)\n", encoding="utf-8")

    # --- Load ledger snapshot ---
    ledger_path = repo_root / "reports" / "r90" / "product-code-change-ledger.json"
    ledger_snapshot = {}
    if ledger_path.exists():
        try:
            ledger_snapshot = json.loads(ledger_path.read_text(encoding="utf-8"))
        except Exception:
            ledger_snapshot = {"error": "failed to parse ledger"}

    # --- Load POC matrix snapshot ---
    poc_matrix_path = repo_root / "product-capability-matrix" / "poc-targets.yaml"
    poc_snapshot = ""
    if poc_matrix_path.exists():
        poc_snapshot = poc_matrix_path.read_text(encoding="utf-8")[:2000]  # truncate for manifest

    # --- Grade each work item ---
    item_grades = []
    for item in planned_items:
        item_id = item.get("item_id", "unknown")
        declared_status = item.get("status", "unknown")
        evidence_paths = item.get("evidence_paths", [])

        # Check if all evidence paths exist
        missing_ep = [ep for ep in evidence_paths if not (repo_root / ep).exists()]
        found_ep = [ep for ep in evidence_paths if (repo_root / ep).exists()]

        if declared_status == "completed":
            if missing_ep and not found_ep:
                grade = "INSUFFICIENT_EVIDENCE"
                note = f"Declared completed but all evidence paths missing: {missing_ep}"
            elif missing_ep:
                grade = "ACCEPTED_WITH_WARNINGS"
                note = f"Some evidence paths missing: {missing_ep}. Found: {found_ep}"
            else:
                grade = "ACCEPTED"
                note = f"All {len(found_ep)} evidence path(s) verified"
        elif declared_status == "partial":
            grade = "REWORK_REQUIRED"
            note = "Declared partial — not complete"
        elif declared_status == "blocked_external_gate":
            grade = "BLOCKED_EXTERNAL_GATE"
            note = "Blocked by external gate"
        else:
            grade = "NOT_ATTEMPTED"
            note = f"Status: {declared_status}"

        item_grades.append({
            "item_id": item_id,
            "item_title": item.get("title", item_id),
            "declared_status": declared_status,
            "supervisor_grade": grade,
            "evidence_paths_found": found_ep,
            "evidence_paths_missing": missing_ep,
            "note": note,
        })

    # --- Write materialized manifest ---
    manifest = {
        "run_id": run_id,
        "sprint_id": sprint_id,
        "declaration_path": str(declaration_path),
        "materialized_at": timestamp,
        "evidence_root": evidence_root,
        "artifacts_verified": len(verified),
        "artifacts_missing": len(missing),
        "src_changes_captured": len(diffs),
        "test_results": test_results,
        "verified_artifacts": verified,
        "missing_artifacts": missing,
        "src_changes": [{"path": d["path"], "last_commit": d["last_commit"]} for d in diffs],
        "work_item_grades": item_grades,
        "ledger_entry_count": len(ledger_snapshot) if isinstance(ledger_snapshot, dict) else 0,
        "poc_matrix_snapshot_chars": len(poc_snapshot),
    }

    manifest_path = out_dir / "materialized-evidence-manifest.yaml"
    with open(manifest_path, "w", encoding="utf-8") as f:
        yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True)

    # --- Write missing evidence report ---
    missing_report_lines = [
        f"# Missing Evidence Report",
        f"# Run ID: {run_id}",
        f"# Generated: {timestamp}",
        "",
    ]
    if missing:
        missing_report_lines.append(f"## Missing Artifacts ({len(missing)})")
        for m in missing:
            missing_report_lines.append(f"- {m['path']}")
    else:
        missing_report_lines.append("## Missing Artifacts: NONE")
        missing_report_lines.append("All declared paths verified.")

    missing_report_path = out_dir / "missing-evidence-report.md"
    missing_report_path.write_text("\n".join(missing_report_lines), encoding="utf-8")

    # --- Write supervisor summary ---
    summary_lines = [
        f"# Materialized Evidence Review",
        f"# Run ID: {run_id}",
        f"# Sprint: {sprint_id}",
        f"# Generated: {timestamp}",
        "",
        "## Materialization Summary",
        "",
        f"- Artifacts verified: {len(verified)}",
        f"- Artifacts missing: {len(missing)}",
        f"- Source changes captured: {len(diffs)}",
        "",
        "## Work Item Grades",
        "",
        "| Item | Grade | Note |",
        "|------|-------|------|",
    ]
    for g in item_grades:
        summary_lines.append(f"| {g['item_id']} | {g['supervisor_grade']} | {g['note'][:80]} |")

    summary_lines += [
        "",
        "## Manifest Location",
        f"- {manifest_path}",
        "",
        "## Patch Location",
        f"- {patch_path}",
    ]

    summary_path = repo_root / "reports" / "supervisor" / "materialized-evidence-review.md"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")

    exit_code = 0 if not missing else 2
    return {
        "exit_code": exit_code,
        "run_id": run_id,
        "artifacts_verified": len(verified),
        "artifacts_missing": len(missing),
        "work_item_grades": item_grades,
        "manifest_path": str(manifest_path),
        "missing_report_path": str(missing_report_path),
        "patch_path": str(patch_path),
        "summary_path": str(summary_path),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Materialize declared evidence from an evidence-declaration.yaml"
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
        help="Repository root (default: inferred from script location)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory for materialized artifacts (default: .local/supervisor/materialized/<run_id>/)",
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

    # Load run_id for default out dir
    try:
        with open(decl_path, encoding="utf-8") as f:
            decl = yaml.safe_load(f)
        run_id = decl.get("run_id", "unknown")
    except Exception:
        run_id = "unknown"

    out_dir = args.out_dir or (repo_root / ".local" / "supervisor" / "materialized" / run_id)

    print(f"Materializing evidence for run_id={run_id}")
    print(f"Declaration: {decl_path}")
    print(f"Output: {out_dir}")

    result = materialize(decl_path, repo_root, out_dir)

    print(f"Artifacts verified: {result['artifacts_verified']}")
    print(f"Artifacts missing: {result['artifacts_missing']}")
    print(f"Work item grades: {len(result['work_item_grades'])}")
    print(f"Manifest: {result['manifest_path']}")
    print(f"Missing report: {result['missing_report_path']}")
    print(f"Patch: {result['patch_path']}")

    if result["exit_code"] == 0:
        print("MATERIALIZATION: COMPLETE (all artifacts verified)")
    else:
        print(f"MATERIALIZATION: PARTIAL ({result['artifacts_missing']} missing)")

    sys.exit(result["exit_code"])


if __name__ == "__main__":
    main()
