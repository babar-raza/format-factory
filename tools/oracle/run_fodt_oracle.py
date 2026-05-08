#!/usr/bin/env python3
"""
run_fodt_oracle.py — Run LibreOffice headless oracle exports for FODT Gate 6.

Converts each FODT sample to text using LibreOffice headless, storing raw
exports under .local/oracle/fodt/raw-exports/ (local-only, gitignored).

Usage:
    python tools/oracle/run_fodt_oracle.py [--soffice-path PATH] [--dry-run]

Environment:
    FORMAT_FACTORY_SOFFICE — explicit path to soffice binary (overrides discovery)

Prerequisites:
    python tools/oracle/preflight_oracle.py must pass before running this tool.

Outputs (all local-only under .local/oracle/fodt/):
    - raw-exports/{sample_stem}/{sample_stem}.txt  (plain text export)
    - oracle-manifest.yaml  — metadata about this oracle run

Rules:
    - No network calls
    - No LLM calls
    - No product source
    - Raw outputs stay under .local/oracle/fodt/ (gitignored)
    - Only the 4 synthetic Gate 3 samples are processed
    - Text export: LibreOffice --convert-to txt:Text
"""

import argparse
import platform
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from oracle_common import find_soffice

FODT_SAMPLES_DIR = Path("samples/by-format/fodt")
FODT_ORACLE_LOCAL_DIR = Path(".local/oracle/fodt")
FODT_RAW_EXPORTS_DIR = FODT_ORACLE_LOCAL_DIR / "raw-exports"
FODT_MANIFEST_PATH = FODT_ORACLE_LOCAL_DIR / "oracle-manifest.yaml"

FODT_EXPECTED_SAMPLES = [
    "minimal-document.fodt",
    "headings-and-paragraphs.fodt",
    "list-basic.fodt",
    "table-basic.fodt",
]


def convert_fodt_to_text(soffice_path, fodt_path, out_dir):
    """Convert a .fodt file to plain text using LibreOffice headless."""
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(
            [soffice_path, "--headless", "--convert-to", "txt:Text",
             "--outdir", str(out_dir), str(fodt_path)],
            capture_output=True, text=True, timeout=120,
        )
        txt_files = list(out_dir.glob("*.txt"))
        oracle_text = ""
        if txt_files:
            oracle_text = txt_files[0].read_text(encoding="utf-8", errors="replace")
        return {
            "success": result.returncode == 0 or bool(txt_files),
            "returncode": result.returncode,
            "stdout": result.stdout.strip()[:500],
            "stderr": result.stderr.strip()[:500],
            "txt_file": txt_files[0].name if txt_files else None,
            "txt_count": len(txt_files),
            "oracle_text_words": len(oracle_text.split()),
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "returncode": -1, "stdout": "", "stderr": "Timeout after 120s",
                "txt_file": None, "txt_count": 0, "oracle_text_words": 0}
    except Exception as exc:
        return {"success": False, "returncode": -1, "stdout": "", "stderr": str(exc)[:500],
                "txt_file": None, "txt_count": 0, "oracle_text_words": 0}


def write_manifest(manifest_path, soffice_version, results):
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# FODT Oracle run manifest — local-only, auto-generated",
        f"oracle_tool: LibreOffice headless",
        f"oracle_version: {soffice_version}",
        f"platform: {platform.system()} {platform.version()[:40]}",
        f"samples_dir: {FODT_SAMPLES_DIR}",
        f"raw_exports_dir: {FODT_RAW_EXPORTS_DIR}",
        f"sample_count: {len(results)}",
        "results:",
    ]
    for r in results:
        lines.append(f"  - sample: {r['sample']}")
        lines.append(f"    success: {'true' if r['success'] else 'false'}")
        lines.append(f"    txt_count: {r['txt_count']}")
        lines.append(f"    oracle_text_words: {r['oracle_text_words']}")
        if not r["success"]:
            lines.append(f"    error: {r.get('stderr', 'unknown')[:200]}")
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Run FODT oracle text exports via LibreOffice")
    parser.add_argument("--soffice-path", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("=" * 60)
    print("FODT Oracle Runner — LibreOffice Headless Text Export")
    print("=" * 60)

    soffice_path, version = find_soffice(override=args.soffice_path, verbose=True)
    if not soffice_path:
        print("ERROR: LibreOffice not found. Run preflight_oracle.py first.")
        print("FODT_ORACLE_RUN: FAIL")
        return 1

    print(f"Oracle: {soffice_path} ({version})")

    missing = [s for s in FODT_EXPECTED_SAMPLES if not (FODT_SAMPLES_DIR / s).exists()]
    if missing:
        print(f"ERROR: Missing samples: {missing}")
        print("FODT_ORACLE_RUN: FAIL")
        return 1

    results = []
    for sample_name in FODT_EXPECTED_SAMPLES:
        fodt_path = FODT_SAMPLES_DIR / sample_name
        sample_stem = fodt_path.stem
        out_dir = FODT_RAW_EXPORTS_DIR / sample_stem
        print(f"Processing: {sample_name}")
        if args.dry_run:
            print(f"  [dry-run] Would convert to {out_dir}/")
            results.append({"sample": sample_name, "success": True, "txt_count": 0,
                             "oracle_text_words": 0, "txt_file": None})
            continue
        r = convert_fodt_to_text(soffice_path, fodt_path, out_dir)
        r["sample"] = sample_name
        status = "OK" if r["success"] else "FAIL"
        print(f"  {status} — words={r['oracle_text_words']} txt={r['txt_file']}")
        results.append(r)

    if not args.dry_run:
        write_manifest(FODT_MANIFEST_PATH, version, results)
        print(f"\nManifest written to: {FODT_MANIFEST_PATH}")

    pass_count = sum(1 for r in results if r["success"])
    print(f"\nResults: {pass_count}/{len(results)} samples converted successfully")
    if pass_count == len(results):
        print("FODT_ORACLE_RUN: PASS")
        print("Next step: python tools/oracle/compare_fodt_oracle.py")
        return 0
    else:
        print("FODT_ORACLE_RUN: FAIL")
        return 1


if __name__ == "__main__":
    sys.exit(main())
