"""run_portfolio_oracle.py — Portfolio Oracle Runner (TC-W7-001).

Runs the oracle for all 20 active formats and produces
oracle/reports/portfolio-regression-report.json.

Usage:
    python tools/oracle/run_portfolio_oracle.py
    python tools/oracle/run_portfolio_oracle.py --python .venv/Scripts/python.exe
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = REPO_ROOT / "oracle" / "reports" / "portfolio-regression-report.json"

FORMATS = [
    "fods", "fodt", "ods", "odt", "csv", "tsv", "gnumeric", "dif", "sylk",
    "abw", "ndjson", "toml", "zst", "qoi", "xcf", "pbm", "pgm", "ppm", "fodg", "fodp",
]


def run_format(fmt: str, python_exe: str) -> dict:
    """Run oracle for one format, return summary dict."""
    result = subprocess.run(
        [python_exe, str(REPO_ROOT / "tools" / "oracle" / "execute_oracle.py"), "--format", fmt],
        capture_output=True, text=True, timeout=120,
        cwd=str(REPO_ROOT),
    )

    summary_path = REPO_ROOT / "oracle" / "formats" / fmt / "reports" / "oracle-run-summary.json"
    if summary_path.exists():
        try:
            data = json.loads(summary_path.read_text(encoding="utf-8"))
            res = data.get("results", {})
            return {
                "format_id": fmt,
                "pass": res.get("PASS", 0),
                "fail": res.get("FAIL", 0),
                "not_applicable": res.get("NOT_APPLICABLE", 0),
                "skipped": res.get("SKIPPED_MISSING_PROVIDER", 0) + res.get("SKIPPED_MISSING_DEPENDENCY", 0),
                "total": data.get("total_cases", 0),
                "verdict": data.get("verdict", ""),
                "depth": data.get("format_depth_score", "D0"),
            }
        except (json.JSONDecodeError, KeyError) as e:
            return {"format_id": fmt, "error": f"summary parse error: {e}", "pass": 0, "fail": 0, "total": 0}

    if result.returncode != 0:
        return {"format_id": fmt, "error": result.stderr[:300], "pass": 0, "fail": 0, "total": 0}

    return {"format_id": fmt, "error": "no summary file", "pass": 0, "fail": 0, "total": 0}


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Portfolio oracle runner for all 20 formats.")
    parser.add_argument("--python", default=None, help="Python executable to use (default: sys.executable)")
    args = parser.parse_args()

    python_exe = args.python or sys.executable

    print(f"[portfolio-oracle] Running oracle for {len(FORMATS)} formats using {python_exe}", file=sys.stderr)

    format_results = []
    total_fail = 0

    for fmt in FORMATS:
        print(f"[portfolio-oracle]   → {fmt}", file=sys.stderr)
        r = run_format(fmt, python_exe)
        format_results.append(r)
        total_fail += r.get("fail", 0)
        fail_count = r.get("fail", 0)
        status = "FAIL" if fail_count else "PASS"
        print(f"[portfolio-oracle]     {fmt}: {r.get('pass',0)}/{r.get('total',0)} pass, {fail_count} fail [{status}]",
              file=sys.stderr)

    portfolio_verdict = "ALL_PASS_OR_SKIPPED" if total_fail == 0 else f"FAIL_COUNT_{total_fail}"

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mission_id": "FF-ORC-HARDENING-002",
        "taskcard": "TC-W7-001",
        "python_exe": python_exe,
        "total_formats": len(FORMATS),
        "total_fail": total_fail,
        "portfolio_verdict": portfolio_verdict,
        "formats": {r["format_id"]: r for r in format_results},
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"\n[portfolio-oracle] Portfolio verdict: {portfolio_verdict}", file=sys.stderr)
    print(f"[portfolio-oracle] Report: {REPORT_PATH}", file=sys.stderr)

    return 0 if total_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
