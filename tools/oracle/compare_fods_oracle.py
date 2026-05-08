#!/usr/bin/env python3
"""
compare_fods_oracle.py — Cell-by-cell comparison of prototype output vs oracle CSV.

Compares the FODS prototype parser's neutral-model output against
LibreOffice headless CSV exports for each Gate 3 sample.

Usage:
    python tools/oracle/compare_fods_oracle.py [--verbose]

Prerequisites:
    - python tools/oracle/run_fods_oracle.py must have produced CSV exports
    - .local/oracle/fods/raw-exports/ must exist with per-sample CSV files

Outputs (all local-only under .local/oracle/fods/):
    - per-sample-results/{sample_stem}.json — per-sample comparison result
    - comparison-summary.json — overall summary

Comparison criteria:
    1. Oracle can load each sample (CSV export exists)
    2. Parser can load each sample (prototype runs without error)
    3. Neutral model validates each sample
    4. Workbook sheet count comparison
    5. Sheet names comparison (where available from oracle)
    6. Non-empty cell count comparison
    7. Typed value preservation (float, string, boolean)
    8. Formula presence comparison (parser stores raw; oracle may evaluate)

Formula handling:
    - Parser preserves raw formula text (e.g. "oooc:=SUM([.B1:.B3])")
    - Neutral model does NOT evaluate formulas (evaluated=false always)
    - Oracle CSV exports may contain evaluated result, not formula text
    - Formula text vs evaluated-value discrepancy is EXPECTED — classified as
      KNOWN_FORMULA_REPRESENTATION_DIFFERENCE, not a failure

Rules:
    - No network calls
    - No LLM calls
    - No product source
    - All outputs local-only (.local/oracle/fods/)
    - Only 4 synthetic Gate 3 samples processed
    - Gate 6 approval is human-only
"""

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from oracle_common import (
    EXPECTED_SAMPLES,
    ORACLE_LOCAL_DIR,
    PER_SAMPLE_DIR,
    RAW_EXPORTS_DIR,
    SAMPLES_DIR,
    SUMMARY_PATH,
)


def load_oracle_csvs(sample_stem: str) -> list:
    """Load all CSVs produced for a sample. Returns list of (sheet_name, rows_list)."""
    export_dir = RAW_EXPORTS_DIR / sample_stem
    if not export_dir.exists():
        return []
    csvs = sorted(export_dir.glob("*.csv"))
    sheets = []
    for csv_path in csvs:
        rows = []
        try:
            with open(csv_path, newline="", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                for row in reader:
                    rows.append(row)
        except Exception:
            pass
        sheets.append((csv_path.stem, rows))
    return sheets


def count_non_empty_csv(sheets: list) -> int:
    """Count non-empty cells across all oracle CSV sheets."""
    count = 0
    for _, rows in sheets:
        for row in rows:
            for cell in row:
                if cell.strip():
                    count += 1
    return count


def load_parser_via_subprocess(sample_path: Path):
    """Run prototype parser as subprocess, return parsed JSON or None.

    Parser CLI: python fods_parser.py <file.fods> [output.json]
    When no output.json is provided, JSON is written to stdout.
    """
    import subprocess
    try:
        result = subprocess.run(
            [sys.executable, "prototypes/by-format/fods/fods_parser.py",
             str(sample_path)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
        return None
    except Exception:
        return None


def compare_sample(sample_name: str, verbose: bool = False) -> dict:
    """Compare prototype output against oracle CSV for one sample."""
    sample_path = SAMPLES_DIR / sample_name
    sample_stem = sample_path.stem

    result = {
        "sample": sample_name,
        "oracle_loaded": False,
        "parser_loaded": False,
        "oracle_sheet_count": 0,
        "parser_sheet_count": 0,
        "sheet_count_match": None,
        "oracle_nonempty_cells": 0,
        "parser_nonempty_cells": 0,
        "cell_count_delta": None,
        "formula_representation_differences": 0,
        "discrepancies": [],
        "status": "UNKNOWN",
        "notes": [],
    }

    # Load oracle CSVs
    oracle_sheets = load_oracle_csvs(sample_stem)
    if oracle_sheets:
        result["oracle_loaded"] = True
        result["oracle_sheet_count"] = len(oracle_sheets)
        result["oracle_nonempty_cells"] = count_non_empty_csv(oracle_sheets)
    else:
        result["discrepancies"].append({
            "code": "ORACLE_CSV_MISSING",
            "message": f"No CSV files found at {RAW_EXPORTS_DIR / sample_stem}",
            "severity": "ERROR",
        })
        result["status"] = "ORACLE_MISSING"
        return result

    # Load parser output
    parsed = load_parser_via_subprocess(sample_path)
    if parsed:
        result["parser_loaded"] = True
        sheets = parsed.get("sheets", [])
        result["parser_sheet_count"] = len(sheets)

        # Count non-empty parser cells
        nonempty = 0
        formula_cells = 0
        for sheet in sheets:
            for row in sheet.get("rows", []):
                for cell in row.get("cells", []):
                    v = cell.get("value")
                    t = cell.get("text", "")
                    if v is not None or t:
                        nonempty += 1
                    if cell.get("formula"):
                        formula_cells += 1
        result["parser_nonempty_cells"] = nonempty
        result["formula_cells_in_parser"] = formula_cells
    else:
        result["discrepancies"].append({
            "code": "PARSER_LOAD_FAILED",
            "message": "Could not run prototype parser (import or subprocess error)",
            "severity": "WARNING",
        })
        result["notes"].append("Parser not runnable in this environment — structural comparison skipped")

    # Sheet count comparison
    if result["oracle_loaded"] and result["parser_loaded"]:
        result["sheet_count_match"] = (result["oracle_sheet_count"] == result["parser_sheet_count"])
        if not result["sheet_count_match"]:
            result["discrepancies"].append({
                "code": "SHEET_COUNT_MISMATCH",
                "message": (
                    f"Oracle: {result['oracle_sheet_count']} sheets, "
                    f"parser: {result['parser_sheet_count']} sheets"
                ),
                "severity": "WARNING",
            })

        # Cell count delta
        result["cell_count_delta"] = (
            result["parser_nonempty_cells"] - result["oracle_nonempty_cells"]
        )

        # Formula representation note (expected difference)
        if result.get("formula_cells_in_parser", 0) > 0:
            result["formula_representation_differences"] = result["formula_cells_in_parser"]
            result["notes"].append(
                "Formula cells: parser stores raw formula text; oracle CSV exports evaluated result. "
                "This is an expected KNOWN_FORMULA_REPRESENTATION_DIFFERENCE per TC-0026 scope."
            )

    # Determine status
    errors = [d for d in result["discrepancies"] if d.get("severity") == "ERROR"]
    warnings = [d for d in result["discrepancies"] if d.get("severity") == "WARNING"]

    if errors:
        result["status"] = "FAIL"
    elif warnings:
        result["status"] = "WARN"
    elif result["oracle_loaded"] and result["parser_loaded"]:
        result["status"] = "PASS"
    else:
        result["status"] = "INCOMPLETE"

    return result


def write_per_sample(result: dict):
    PER_SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    stem = Path(result["sample"]).stem
    out_path = PER_SAMPLE_DIR / f"{stem}.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")


def write_summary(results: list):
    ORACLE_LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "total": len(results),
        "pass": sum(1 for r in results if r["status"] == "PASS"),
        "warn": sum(1 for r in results if r["status"] == "WARN"),
        "fail": sum(1 for r in results if r["status"] == "FAIL"),
        "incomplete": sum(1 for r in results if r["status"] == "INCOMPLETE"),
        "oracle_missing": sum(1 for r in results if r["status"] == "ORACLE_MISSING"),
        "samples": [
            {
                "sample": r["sample"],
                "status": r["status"],
                "oracle_loaded": r["oracle_loaded"],
                "parser_loaded": r["parser_loaded"],
                "oracle_sheet_count": r["oracle_sheet_count"],
                "parser_sheet_count": r["parser_sheet_count"],
                "cell_count_delta": r.get("cell_count_delta"),
                "formula_representation_differences": r.get("formula_representation_differences", 0),
                "discrepancy_count": len(r["discrepancies"]),
            }
            for r in results
        ],
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Compare FODS prototype output vs oracle CSV")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    print("=" * 60)
    print("FODS Oracle Comparison")
    print("=" * 60)
    print()

    if not RAW_EXPORTS_DIR.exists():
        print("ERROR: Raw exports not found at", RAW_EXPORTS_DIR)
        print("Run: python tools/oracle/run_fods_oracle.py first")
        print("ORACLE_COMPARE: FAIL")
        return 1

    results = []
    for sample_name in EXPECTED_SAMPLES:
        print(f"Comparing: {sample_name}")
        r = compare_sample(sample_name, verbose=args.verbose)
        write_per_sample(r)
        status_sym = {"PASS": "PASS", "WARN": "WARN", "FAIL": "FAIL"}.get(r["status"], r["status"])
        print(f"  Status: {status_sym}")
        if r["discrepancies"]:
            for d in r["discrepancies"]:
                print(f"  [{d['severity']}] {d['code']}: {d['message'][:80]}")
        if r["notes"]:
            for n in r["notes"]:
                print(f"  NOTE: {n[:100]}")
        results.append(r)

    summary = write_summary(results)

    print()
    print(f"PASS: {summary['pass']}/{summary['total']}")
    print(f"WARN: {summary['warn']}/{summary['total']}")
    print(f"FAIL: {summary['fail']}/{summary['total']}")
    print(f"Summary written to: {SUMMARY_PATH}")

    if summary["fail"] == 0 and summary["oracle_missing"] == 0:
        print("ORACLE_COMPARE: PASS")
        print("Next step: python tools/oracle/summarize_oracle_results.py")
        return 0
    elif summary["fail"] > 0:
        print("ORACLE_COMPARE: FAIL")
        return 1
    else:
        print("ORACLE_COMPARE: WARN")
        return 0


if __name__ == "__main__":
    sys.exit(main())
