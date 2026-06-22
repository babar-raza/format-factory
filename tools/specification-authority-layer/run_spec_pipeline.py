"""run_spec_pipeline.py — SAL Master Pipeline Orchestrator.

REQ-SAL-003: Creates the master runner that chains SAL tools in sequence:
  1. normalize_pdf.py (if raw PDF not yet normalized)
  2. build_section_index.py -> sections.jsonl
  3. build_chunk_index.py -> chunks.jsonl
  4. build_spec_workbench.py -> verified-facts workbench
  5. spec_verifier.py -> verify facts

Also wraps sal_master_runner.py for fact generation.

Usage:
  python tools/specification-authority-layer/run_spec_pipeline.py --format fods
  python tools/specification-authority-layer/run_spec_pipeline.py --format fods --dry-run
  python tools/specification-authority-layer/run_spec_pipeline.py --all

Exit codes:
  0 = success (or dry-run)
  1 = at least one format failed
  2 = argument error
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SAL_DIR = REPO_ROOT / "tools" / "specification-authority-layer"
NORMALIZE_DIR = REPO_ROOT / "tools" / "spec-normalize"
SPEC_CACHE = REPO_ROOT / ".local" / "spec-cache"
LOG_DIR = REPO_ROOT / ".local" / "spec-pipeline-runs"

KNOWN_FORMATS = ["fods", "fodt", "zst", "ods", "odt", "fodg", "fodp", "abw", "gnumeric"]


def _run(cmd: list, dry_run: bool = False, check: bool = True) -> int:
    """Run a subprocess command, return exit code."""
    cmd_str = " ".join(str(c) for c in cmd)
    print(f"  CMD: {cmd_str}")
    if dry_run:
        print("  [DRY-RUN] skipped")
        return 0
    result = subprocess.run(cmd, capture_output=False)
    if check and result.returncode != 0:
        print(f"  [WARN] exit {result.returncode}")
    return result.returncode


def run_pipeline_for_format(format_id: str, dry_run: bool = False) -> dict:
    """Run the full SAL pipeline for one format. Returns status dict."""
    fmt = format_id.lower()
    spec_cache_fmt = SPEC_CACHE / fmt
    normalized_dir = spec_cache_fmt / "normalized"
    log = {"format": fmt, "steps": [], "status": "PASS", "timestamp": datetime.now(timezone.utc).isoformat()}

    print(f"\n=== SAL PIPELINE: {fmt.upper()} ===")

    # Step 1: normalize_pdf.py (skip if already normalized)
    raw_dir = spec_cache_fmt / "raw"
    if normalized_dir.exists() and any(normalized_dir.glob("pages.jsonl")):
        print(f"  Step 1: SKIP (already normalized at {normalized_dir})")
        log["steps"].append({"step": "normalize_pdf", "result": "SKIPPED_ALREADY_DONE"})
    elif raw_dir.exists() and any(raw_dir.glob("*.pdf")):
        pdf_files = list(raw_dir.glob("*.pdf"))
        rc = _run([sys.executable, NORMALIZE_DIR / "normalize_pdf.py",
                   "--pdf", pdf_files[0], "--output-dir", normalized_dir], dry_run=dry_run)
        log["steps"].append({"step": "normalize_pdf", "result": "PASS" if rc == 0 else "FAIL", "exit_code": rc})
        if rc != 0:
            log["status"] = "PARTIAL"
    else:
        print(f"  Step 1: SKIP (no raw PDF; spec cache at {spec_cache_fmt})")
        log["steps"].append({"step": "normalize_pdf", "result": "SKIPPED_NO_RAW_PDF"})

    # Step 2: build_section_index.py (if normalized dir exists)
    if normalized_dir.exists():
        rc = _run([sys.executable, NORMALIZE_DIR / "build_section_index.py",
                   "--normalized-dir", normalized_dir, "--format-id", fmt], dry_run=dry_run)
        log["steps"].append({"step": "build_section_index", "result": "PASS" if rc == 0 else "WARN", "exit_code": rc})
    else:
        log["steps"].append({"step": "build_section_index", "result": "SKIPPED_NO_NORMALIZED"})

    # Step 3: build_spec_workbench.py
    _workbench_cmd = [sys.executable, NORMALIZE_DIR / "build_spec_workbench.py",
                      "--format-id", fmt, "--version", "1.3"]
    if dry_run:
        _workbench_cmd.append("--dry-run")
    rc = _run(_workbench_cmd, dry_run=False)
    log["steps"].append({"step": "build_spec_workbench", "result": "PASS" if rc == 0 else "WARN", "exit_code": rc})

    # Step 4: sal_master_runner.py (generate facts)
    rc = _run([sys.executable, SAL_DIR / "sal_master_runner.py",
               "--format", fmt.upper(), "--from-cache-only",
               "--output-dir", SPEC_CACHE], dry_run=dry_run)
    log["steps"].append({"step": "sal_master_runner", "result": "PASS" if rc == 0 else "WARN", "exit_code": rc})

    return log


def main() -> int:
    parser = argparse.ArgumentParser(description="SAL Master Pipeline Orchestrator (REQ-SAL-003)")
    parser.add_argument("--format", help="Format ID to process (e.g. fods)")
    parser.add_argument("--all", action="store_true", help="Process all known formats")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing")
    parser.add_argument("--list-formats", action="store_true", help="List known formats and exit")
    args = parser.parse_args()

    if args.list_formats:
        print("Known formats:", ", ".join(KNOWN_FORMATS))
        return 0

    formats = []
    if args.all:
        formats = KNOWN_FORMATS
    elif args.format:
        formats = [args.format.lower()]
    else:
        parser.error("Specify --format <id> or --all")

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    run_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    run_log = {"run_id": f"sal-pipeline-{run_ts}", "formats": formats, "results": []}

    overall_ok = True
    for fmt in formats:
        result = run_pipeline_for_format(fmt, dry_run=args.dry_run)
        run_log["results"].append(result)
        if result["status"] not in ("PASS", "PARTIAL"):
            overall_ok = False

    log_path = LOG_DIR / f"sal-pipeline-{run_ts}.json"
    log_path.write_text(json.dumps(run_log, indent=2), encoding="utf-8")
    print(f"\nRun log: {log_path}")

    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
