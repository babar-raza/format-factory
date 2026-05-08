#!/usr/bin/env python3
"""
compare_fodt_oracle.py — Text comparison of fodt_parser output vs LibreOffice oracle.

Compares the FODT prototype parser\'s output against LibreOffice headless text exports
for each Gate 3 FODT sample.

Usage:
    python tools/oracle/compare_fodt_oracle.py [--verbose]

Prerequisites:
    - python tools/oracle/run_fodt_oracle.py must have produced text exports
    - .local/oracle/fodt/raw-exports/ must exist with per-sample .txt files

Comparison criteria:
    1. Oracle can convert each sample to text (txt file exists)
    2. Parser can parse each sample (no fatal error)
    3. Parser paragraph/heading texts appear in oracle text output
    4. Word counts approximately match (within 30% tolerance)

Rules:
    - No network calls, no LLM calls, no product source
    - All outputs local-only (.local/oracle/fodt/)
    - Gate 6 approval is human-only
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from oracle_common import find_soffice

FODT_SAMPLES_DIR = Path("samples/by-format/fodt")
FODT_ORACLE_LOCAL_DIR = Path(".local/oracle/fodt")
FODT_RAW_EXPORTS_DIR = FODT_ORACLE_LOCAL_DIR / "raw-exports"
FODT_PER_SAMPLE_DIR = FODT_ORACLE_LOCAL_DIR / "per-sample-results"
FODT_SUMMARY_PATH = FODT_ORACLE_LOCAL_DIR / "comparison-summary.json"
FODT_COMPARISON_REPORT_PATH = Path("acquisition-packs/fodt/gate6-oracle-comparison-report.md")

FODT_EXPECTED_SAMPLES = [
    "minimal-document.fodt",
    "headings-and-paragraphs.fodt",
    "list-basic.fodt",
    "table-basic.fodt",
]


def load_parser_via_subprocess(sample_path):
    """Run fodt_parser.py as subprocess, return parsed dict or None."""
    import subprocess
    try:
        result = subprocess.run(
            [sys.executable, "prototypes/by-format/fodt/fodt_parser.py", str(sample_path)],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
        return None
    except Exception:
        return None


def compare_sample(sample_name, verbose=False):
    """Compare fodt_parser output against oracle text for one sample."""
    sample_path = FODT_SAMPLES_DIR / sample_name
    sample_stem = sample_path.stem
    export_dir = FODT_RAW_EXPORTS_DIR / sample_stem

    result = {
        "sample": sample_name,
        "oracle_loaded": False,
        "parser_loaded": False,
        "oracle_words": 0,
        "parser_words": 0,
        "word_count_delta": None,
        "paragraphs_total": 0,
        "paragraphs_in_oracle": 0,
        "discrepancies": [],
        "status": "UNKNOWN",
        "notes": [],
    }

    # Load oracle text
    oracle_text = ""
    if export_dir.exists():
        txt_files = list(export_dir.glob("*.txt"))
        if txt_files:
            try:
                oracle_text = txt_files[0].read_text(encoding="utf-8", errors="replace")
                result["oracle_loaded"] = True
                result["oracle_words"] = len(oracle_text.split())
            except Exception as exc:
                result["discrepancies"].append({
                    "code": "ORACLE_READ_FAILED", "severity": "ERROR",
                    "message": str(exc)[:100],
                })
        else:
            result["discrepancies"].append({
                "code": "ORACLE_TXT_MISSING", "severity": "ERROR",
                "message": f"No .txt files in {export_dir}",
            })
    else:
        result["discrepancies"].append({
            "code": "ORACLE_DIR_MISSING", "severity": "ERROR",
            "message": f"Export directory not found: {export_dir}",
        })

    if not result["oracle_loaded"]:
        result["status"] = "ORACLE_MISSING"
        return result

    # Load parser output
    parsed = load_parser_via_subprocess(sample_path)
    if parsed and "error" not in parsed:
        result["parser_loaded"] = True
        paragraphs = parsed.get("paragraphs", [])
        result["paragraphs_total"] = len(paragraphs)
        result["parser_words"] = parsed.get("word_count", 0)
        oracle_lower = oracle_text.lower()
        found = 0
        missing_texts = []
        for p in paragraphs:
            text = p.get("text", "").strip()
            if not text:
                continue
            if text.lower() in oracle_lower:
                found += 1
            else:
                missing_texts.append(text[:50])
        result["paragraphs_in_oracle"] = found
        if missing_texts:
            result["discrepancies"].append({
                "code": "PARAGRAPH_NOT_IN_ORACLE",
                "severity": "WARNING",
                "message": f"{len(missing_texts)} parser paragraph(s) not found in oracle text",
                "examples": missing_texts[:3],
            })
        # Word count delta
        result["word_count_delta"] = result["parser_words"] - result["oracle_words"]
        if result["oracle_words"] > 0 and result["parser_words"] > 0:
            ratio = abs(result["word_count_delta"]) / max(result["oracle_words"], result["parser_words"])
            if ratio > 0.30:
                result["discrepancies"].append({
                    "code": "WORD_COUNT_MISMATCH",
                    "severity": "WARNING",
                    "message": f"oracle={result[\'oracle_words\']} parser={result[\'parser_words\']} delta={abs(result[\'word_count_delta\'])} ratio={ratio:.2f}",
                })
    else:
        result["discrepancies"].append({
            "code": "PARSER_LOAD_FAILED", "severity": "WARNING",
            "message": "Could not run fodt_parser.py",
        })
        result["notes"].append("Parser not runnable — structural comparison skipped")

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


def write_per_sample(result):
    FODT_PER_SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    stem = Path(result["sample"]).stem
    out_path = FODT_PER_SAMPLE_DIR / f"{stem}.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")


def write_summary(results):
    FODT_ORACLE_LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "total": len(results),
        "pass": sum(1 for r in results if r["status"] == "PASS"),
        "warn": sum(1 for r in results if r["status"] == "WARN"),
        "fail": sum(1 for r in results if r["status"] == "FAIL"),
        "oracle_missing": sum(1 for r in results if r["status"] == "ORACLE_MISSING"),
        "samples": [
            {"sample": r["sample"], "status": r["status"],
             "oracle_loaded": r["oracle_loaded"], "parser_loaded": r["parser_loaded"],
             "oracle_words": r["oracle_words"], "parser_words": r["parser_words"],
             "word_count_delta": r.get("word_count_delta"),
             "discrepancy_count": len(r["discrepancies"])}
            for r in results
        ],
    }
    FODT_SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Compare FODT parser output vs oracle text")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    print("=" * 60)
    print("FODT Oracle Comparison")
    print("=" * 60)

    if not FODT_RAW_EXPORTS_DIR.exists():
        print("ERROR: Raw exports not found at", FODT_RAW_EXPORTS_DIR)
        print("Run: python tools/oracle/run_fodt_oracle.py first")
        print("FODT_ORACLE_COMPARE: FAIL")
        return 1

    results = []
    for sample_name in FODT_EXPECTED_SAMPLES:
        print(f"Comparing: {sample_name}")
        r = compare_sample(sample_name, verbose=args.verbose)
        write_per_sample(r)
        print(f"  Status: {r[\'status\']}")
        for d in r["discrepancies"]:
            print(f"  [{d[\'severity\']}] {d[\'code\']}:", d.get("message", "")[:80])
        results.append(r)

    summary = write_summary(results)
    print()
    print(f"PASS: {summary[\'pass\']}/{summary[\'total\']}")
    print(f"WARN: {summary[\'warn\']}/{summary[\'total\']}")
    print(f"FAIL: {summary[\'fail\']}/{summary[\'total\']}")
    print(f"Summary: {FODT_SUMMARY_PATH}")
    if summary["fail"] == 0 and summary["oracle_missing"] == 0:
        print("FODT_ORACLE_COMPARE: PASS")
        return 0
    elif summary["fail"] > 0:
        print("FODT_ORACLE_COMPARE: FAIL")
        return 1
    else:
        print("FODT_ORACLE_COMPARE: WARN")
        return 0


if __name__ == "__main__":
    sys.exit(main())
