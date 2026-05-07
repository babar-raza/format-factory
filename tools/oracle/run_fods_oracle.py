#!/usr/bin/env python3
"""
run_fods_oracle.py — Run LibreOffice headless oracle exports for FODS Gate 6.

Converts each FODS sample to CSV using LibreOffice headless, storing raw
exports under .local/oracle/fods/raw-exports/ (local-only, gitignored).

Usage:
    python tools/oracle/run_fods_oracle.py [--soffice PATH] [--dry-run]

Prerequisites:
    python tools/oracle/preflight_oracle.py must pass before running this tool.

Outputs (all local-only under .local/oracle/fods/):
    - raw-exports/{sample_stem}/{sample_stem}.Sheet1.csv  (per sheet)
    - oracle-manifest.yaml  — metadata about this oracle run

Rules:
    - No network calls
    - No LLM calls
    - No product source
    - Raw outputs stay under .local/oracle/fods/ (gitignored)
    - Only the 4 synthetic Gate 3 samples are processed
    - Multi-sheet export: LibreOffice produces one CSV per sheet
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SAMPLES_DIR = Path("samples/by-format/fods")
ORACLE_LOCAL_DIR = Path(".local/oracle/fods")
RAW_EXPORTS_DIR = ORACLE_LOCAL_DIR / "raw-exports"
MANIFEST_PATH = ORACLE_LOCAL_DIR / "oracle-manifest.yaml"

EXPECTED_SAMPLES = [
    "minimal-spreadsheet.fods",
    "multi-sheet-basic.fods",
    "typed-values-basic.fods",
    "formula-basic.fods",
]

LIBREOFFICE_CANDIDATES = [
    "soffice",
    "libreoffice",
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/usr/bin/soffice",
    "/usr/bin/libreoffice",
    "/usr/lib/libreoffice/program/soffice",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
]


def find_soffice(override=None):
    candidates = ([override] if override else []) + LIBREOFFICE_CANDIDATES
    for c in candidates:
        try:
            r = subprocess.run([c, "--version"], capture_output=True, text=True, timeout=15)
            if r.returncode == 0 and r.stdout.strip():
                return c, r.stdout.strip()
        except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired):
            continue
    return None, None


def convert_fods_to_csv(soffice_path: str, fods_path: Path, out_dir: Path) -> dict:
    """
    Convert a .fods file to CSV using LibreOffice headless.
    Returns dict with status, files, and error info.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(
            [
                soffice_path,
                "--headless",
                "--convert-to",
                "csv",
                "--infilter=calc_csv:44,34,UTF8",
                "--outdir",
                str(out_dir),
                str(fods_path),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        produced = list(out_dir.glob("*.csv"))
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout.strip()[:500],
            "stderr": result.stderr.strip()[:500],
            "csv_files": [str(f.name) for f in produced],
            "csv_count": len(produced),
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": "Timeout after 120 seconds",
            "csv_files": [],
            "csv_count": 0,
        }
    except Exception as exc:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(exc)[:500],
            "csv_files": [],
            "csv_count": 0,
        }


def write_manifest(manifest_path: Path, soffice_version: str, results: list):
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Oracle run manifest — local-only, auto-generated",
        f"oracle_tool: LibreOffice headless",
        f"oracle_version: {soffice_version}",
        f"platform: {platform.system()} {platform.version()[:40]}",
        f"samples_dir: {SAMPLES_DIR}",
        f"raw_exports_dir: {RAW_EXPORTS_DIR}",
        f"sample_count: {len(results)}",
        "results:",
    ]
    for r in results:
        lines.append(f"  - sample: {r['sample']}")
        lines.append(f"    success: {'true' if r['success'] else 'false'}")
        lines.append(f"    csv_count: {r['csv_count']}")
        if not r['success']:
            lines.append(f"    error: {r.get('stderr', 'unknown')[:200]}")
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Run FODS oracle CSV exports via LibreOffice")
    parser.add_argument("--soffice", default=None, help="Path to soffice binary")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without running")
    args = parser.parse_args()

    print("=" * 60)
    print("FODS Oracle Runner — LibreOffice Headless CSV Export")
    print("=" * 60)

    soffice_path, version = find_soffice(args.soffice)
    if not soffice_path:
        print("ERROR: LibreOffice not found. Run preflight_oracle.py first.")
        print("ORACLE_RUN: FAIL")
        return 1

    print(f"Oracle: {soffice_path} ({version})")
    print()

    # Verify samples exist
    missing = [s for s in EXPECTED_SAMPLES if not (SAMPLES_DIR / s).exists()]
    if missing:
        print(f"ERROR: Missing samples: {missing}")
        print("ORACLE_RUN: FAIL")
        return 1

    results = []
    for sample_name in EXPECTED_SAMPLES:
        fods_path = SAMPLES_DIR / sample_name
        sample_stem = fods_path.stem
        out_dir = RAW_EXPORTS_DIR / sample_stem

        print(f"Processing: {sample_name}")
        if args.dry_run:
            print(f"  [dry-run] Would convert to {out_dir}/")
            results.append({"sample": sample_name, "success": True, "csv_count": 0})
            continue

        r = convert_fods_to_csv(soffice_path, fods_path, out_dir)
        r["sample"] = sample_name

        if r["success"]:
            print(f"  OK — {r['csv_count']} CSV file(s): {r['csv_files']}")
        else:
            print(f"  FAIL — returncode={r['returncode']} stderr={r['stderr'][:100]}")

        results.append(r)

    if not args.dry_run:
        write_manifest(MANIFEST_PATH, version, results)
        print()
        print(f"Manifest written to: {MANIFEST_PATH}")

    pass_count = sum(1 for r in results if r["success"])
    print()
    print(f"Results: {pass_count}/{len(results)} samples converted successfully")

    if pass_count == len(results):
        print("ORACLE_RUN: PASS")
        print("Next step: python tools/oracle/compare_fods_oracle.py")
        return 0
    else:
        print("ORACLE_RUN: PARTIAL" if pass_count > 0 else "ORACLE_RUN: FAIL")
        return 1


if __name__ == "__main__":
    sys.exit(main())
