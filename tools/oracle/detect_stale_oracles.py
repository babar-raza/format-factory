"""detect_stale_oracles.py — Stale oracle detection (TC-W1A-003).

Detects stale oracle packages by:
1. Comparing per-case input_hash (where present) to actual corpus file hash
2. Comparing executor hash to stored dependency_hashes.executor_hash (where present)

Produces: oracle/reports/stale-oracle-report.json
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ORACLE_ROOT = REPO_ROOT / "oracle" / "formats"
REPORTS_DIR = REPO_ROOT / "oracle" / "reports"


def hash_file(path: Path) -> str:
    """Return sha256 hex digest of file content, prefixed with 'sha256:'."""
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def check_corpus_hashes(fmt_id: str, pkg: dict, repo_root: Path) -> list[dict]:
    """Compare stored input_hash values vs actual file hashes for all cases with sample_ref."""
    findings: list[dict] = []

    all_cases = (
        pkg.get("valid_cases", [])
        + pkg.get("invalid_cases", [])
        + pkg.get("roundtrip_cases", [])
    )

    for case in all_cases:
        sample_ref = case.get("sample_ref")
        stored_hash = case.get("input_hash")

        if not sample_ref or sample_ref == "null":
            continue

        sample_path = repo_root / sample_ref
        if not sample_path.exists() or not sample_path.is_file():
            findings.append({
                "case_id": case.get("case_id", "?"),
                "status": "MISSING_SAMPLE",
                "sample_ref": sample_ref,
                "stored_hash": stored_hash,
                "actual_hash": None,
                "detail": f"Sample file not found or is not a regular file: {sample_ref}",
            })
            continue

        actual_hash = hash_file(sample_path)

        if stored_hash is None:
            # No stored hash — sample exists, mark as HASH_NOT_STORED (not stale, just unverified)
            findings.append({
                "case_id": case.get("case_id", "?"),
                "status": "HASH_NOT_STORED",
                "sample_ref": sample_ref,
                "stored_hash": None,
                "actual_hash": actual_hash,
                "detail": "No input_hash stored — consider adding for future stale detection",
            })
        elif actual_hash != stored_hash:
            findings.append({
                "case_id": case.get("case_id", "?"),
                "status": "STALE_HASH_MISMATCH",
                "sample_ref": sample_ref,
                "stored_hash": stored_hash,
                "actual_hash": actual_hash,
                "detail": "Corpus file has changed since oracle case was defined",
            })
        else:
            findings.append({
                "case_id": case.get("case_id", "?"),
                "status": "CLEAN",
                "sample_ref": sample_ref,
                "stored_hash": stored_hash,
                "actual_hash": actual_hash,
                "detail": "Corpus hash matches stored input_hash",
            })

    return findings


def check_executor_staleness(pkg: dict, repo_root: Path) -> dict:
    """Compare current execute_oracle.py hash vs stored dependency_hashes.executor_hash."""
    executor_path = repo_root / "tools" / "oracle" / "execute_oracle.py"
    if not executor_path.exists():
        return {"status": "EXECUTOR_NOT_FOUND", "detail": "execute_oracle.py not found"}

    current_hash = hash_file(executor_path)
    dep_hashes = pkg.get("dependency_hashes", {})
    stored_hash = dep_hashes.get("executor_hash")

    if not stored_hash:
        return {
            "status": "EXECUTOR_HASH_NOT_STORED",
            "current_hash": current_hash,
            "detail": "No stored executor_hash in dependency_hashes block",
        }

    if current_hash != stored_hash:
        return {
            "status": "EXECUTOR_STALE",
            "stored_hash": stored_hash,
            "current_hash": current_hash,
            "detail": "execute_oracle.py has changed since last oracle run — re-run recommended",
        }

    return {
        "status": "CLEAN",
        "current_hash": current_hash,
        "detail": "Executor hash matches stored dependency_hashes.executor_hash",
    }


def detect_all(repo_root: Path) -> dict:
    """Run all stale checks across all formats. Returns summary dict."""
    oracle_root = repo_root / "oracle" / "formats"
    stale_formats: list[str] = []
    clean_formats: list[str] = []
    details: dict[str, dict] = {}

    for fmt_dir in sorted(oracle_root.iterdir()):
        if not fmt_dir.is_dir():
            continue
        pkg_path = fmt_dir / "oracle-package.yaml"
        if not pkg_path.exists():
            continue

        fmt_id = fmt_dir.name
        try:
            pkg = yaml.safe_load(pkg_path.read_text(encoding="utf-8"))
        except Exception as e:
            details[fmt_id] = {"error": str(e), "corpus_findings": [], "executor_check": {}}
            continue

        corpus_findings = check_corpus_hashes(fmt_id, pkg, repo_root)
        executor_check = check_executor_staleness(pkg, repo_root)

        # Only STALE_HASH_MISMATCH (hash changed) and EXECUTOR_STALE count as true staleness.
        # MISSING_SAMPLE and HASH_NOT_STORED are informational — not staleness indicators.
        stale_corpus = [f for f in corpus_findings if f["status"] == "STALE_HASH_MISMATCH"]
        executor_stale = executor_check.get("status") == "EXECUTOR_STALE"

        if stale_corpus or executor_stale:
            fmt_status = "STALE"
            stale_formats.append(fmt_id)
        else:
            fmt_status = "CLEAN"
            clean_formats.append(fmt_id)

        details[fmt_id] = {
            "format_id": fmt_id,
            "status": fmt_status,
            "corpus_findings": corpus_findings,
            "executor_check": executor_check,
            "stale_case_count": len(stale_corpus),
            "missing_sample_count": len([f for f in corpus_findings if f["status"] == "MISSING_SAMPLE"]),
            "hash_not_stored_count": len([f for f in corpus_findings if f["status"] == "HASH_NOT_STORED"]),
        }

    return {
        "stale_formats": stale_formats,
        "clean_formats": clean_formats,
        "details": details,
    }


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    result = detect_all(REPO_ROOT)
    stale = result["stale_formats"]
    clean = result["clean_formats"]
    details = result["details"]

    total = len(stale) + len(clean)
    report = {
        "report_id": "stale-oracle-report",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mission_id": "FF-ORC-HARDENING-002",
        "total_formats": total,
        "stale_count": len(stale),
        "clean_count": len(clean),
        "stale_formats": stale,
        "clean_formats": clean,
        "overall_verdict": "ALL_CLEAN" if not stale else f"{len(stale)}_STALE_FORMATS",
        "details": details,
    }

    out_path = REPORTS_DIR / "stale-oracle-report.json"
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Written: {out_path}", file=sys.stderr)

    print(f"\nStale Oracle Report:")
    print(f"  Total formats: {total}")
    print(f"  Clean: {len(clean)}")
    print(f"  Stale: {len(stale)}")
    if stale:
        print(f"  Stale formats: {stale}")
    else:
        print(f"  Verdict: ALL_CLEAN")

    return 0 if not stale else 1


if __name__ == "__main__":
    sys.exit(main())
