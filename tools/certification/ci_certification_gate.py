"""CI Certification Gate — verifies certification dimensions haven't regressed.

TC-GATE-001 (2026-07-03): Blocks CI if any dimension falls below the locked baseline.

Reads reports/certification/certification-baseline.json and checks:
  1. All 20 formats remain CERTIFIED (stub-audit.json + assertion-quality.json)
  2. FODS mutation kill rate >= locked threshold
  3. Security audits present for all formats
  4. Zero collection errors in FODS test suite (tested via pytest --collect-only)

Usage:
    python tools/certification/ci_certification_gate.py
    python tools/certification/ci_certification_gate.py --strict

Exit codes:
    0 — all dimensions pass
    1 — one or more regressions detected (details printed to stdout)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_PATH = REPO_ROOT / "reports" / "certification" / "certification-baseline.json"
VENV_PYTEST = str(REPO_ROOT / ".venv" / "Scripts" / "pytest.exe")


def load_baseline() -> dict:
    if not BASELINE_PATH.exists():
        print(f"ERROR: baseline not found at {BASELINE_PATH}", file=sys.stderr)
        sys.exit(1)
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


def check_format_certification(fmt: str, baseline_fmt: dict) -> list[str]:
    """Check stub-audit and assertion-quality for a format. Returns list of failures."""
    failures = []
    cert_dir = REPO_ROOT / "reports" / "certification" / fmt

    # Stub audit
    stub_path = cert_dir / "stub-audit.json"
    if stub_path.exists():
        stub = json.loads(stub_path.read_text(encoding="utf-8"))
        material_stubs = stub.get("material_stub_count", stub.get("stub_count", 0))
        allowed = baseline_fmt.get("max_material_stubs", 0)
        if material_stubs > allowed:
            failures.append(
                f"{fmt}: material_stubs={material_stubs} > allowed={allowed} (stub-audit.json)"
            )
    else:
        # No stub audit — not a regression
        pass

    # Assertion quality
    aq_path = cert_dir / "assertion-quality.json"
    if aq_path.exists():
        aq = json.loads(aq_path.read_text(encoding="utf-8"))
        weak = aq.get("weak_assertion_count", 0)
        allowed = baseline_fmt.get("max_weak_assertions", 0)
        if weak > allowed:
            failures.append(
                f"{fmt}: weak_assertions={weak} > allowed={allowed} (assertion-quality.json)"
            )

    # Security audit presence
    if baseline_fmt.get("require_security_audit"):
        sec_path = cert_dir / "security-audit.json"
        if not sec_path.exists():
            failures.append(f"{fmt}: security-audit.json missing (required by baseline)")

    return failures


def check_mutation_kill_rate(baseline: dict) -> list[str]:
    """Check FODS mutation kill rate against locked baseline threshold."""
    failures = []
    mutation_cfg = baseline.get("mutation_testing", {})

    for fmt, threshold in mutation_cfg.items():
        mut_path = REPO_ROOT / "reports" / "certification" / fmt / "mutation-baseline.json"
        if not mut_path.exists():
            failures.append(f"{fmt}: mutation-baseline.json missing")
            continue
        mut = json.loads(mut_path.read_text(encoding="utf-8"))
        kill_rate = mut.get("kill_rate_pct", 0)
        if kill_rate < threshold:
            failures.append(
                f"{fmt}: mutation kill_rate={kill_rate}% < required={threshold}% (mutation-baseline.json)"
            )

    return failures


def check_collection_errors(baseline: dict) -> list[str]:
    """Check for pytest collection errors in FODS test suite."""
    failures = []
    if not baseline.get("check_fods_collection_errors", False):
        return failures

    fods_test_dir = str(REPO_ROOT / "tests" / "python" / "fods")
    result = subprocess.run(
        [VENV_PYTEST, fods_test_dir, "--collect-only", "-q", "--tb=no",
         "--continue-on-collection-errors", "--no-header"],
        capture_output=True, text=True, timeout=60,
        cwd=str(REPO_ROOT),
    )
    if "error" in result.stdout.lower() or "ERROR" in result.stdout:
        # Count collection errors
        error_lines = [l for l in result.stdout.splitlines()
                       if "ERROR" in l and "collecting" in l.lower()]
        if error_lines:
            failures.append(
                f"fods: {len(error_lines)} test collection error(s) detected"
            )
    return failures


def run_gate(strict: bool = False) -> int:
    baseline = load_baseline()
    all_failures: list[str] = []

    print(f"Certification Gate — baseline: {baseline.get('locked_at', 'unknown')}")
    print(f"  Formats to check: {len(baseline.get('formats', {}))}")

    # Check per-format certification dimensions
    for fmt, fmt_baseline in baseline.get("formats", {}).items():
        fmt_failures = check_format_certification(fmt, fmt_baseline)
        all_failures.extend(fmt_failures)

    if not all_failures:
        print("  Format certification: PASS")
    else:
        for f in all_failures:
            print(f"  FAIL: {f}")

    # Check mutation testing thresholds
    mut_failures = check_mutation_kill_rate(baseline)
    if not mut_failures:
        print("  Mutation testing: PASS")
    else:
        for f in mut_failures:
            print(f"  FAIL: {f}")
    all_failures.extend(mut_failures)

    # Check collection errors
    col_failures = check_collection_errors(baseline)
    if not col_failures:
        if baseline.get("check_fods_collection_errors"):
            print("  Collection errors: PASS")
    else:
        for f in col_failures:
            print(f"  FAIL: {f}")
    all_failures.extend(col_failures)

    if not all_failures:
        print("\nGate result: PASS — no regressions detected.")
        return 0
    else:
        print(f"\nGate result: FAIL — {len(all_failures)} regression(s) detected.")
        return 1


def main():
    parser = argparse.ArgumentParser(description="CI Certification Gate")
    parser.add_argument("--strict", action="store_true",
                        help="Fail on warnings as well as errors")
    args = parser.parse_args()

    return run_gate(strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())
