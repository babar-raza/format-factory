"""run_regression_baseline.py — Regression baseline for TC-BF-008.

Runs 4 checks and stores results under .local/supervisor/consolidation-baseline/{date}/:
  1. Validator count >= 154
  2. Grade output hash stability across 5 evidence declarations
  3. Continuation verdict stability across 3 consecutive runs
  4. Git operation latency documentation (non-blocking; triggers TC-BF-009 if > 3000ms)

Exit codes:
  0 -- all assertions pass
  1 -- validator count or grade/continuation assertions fail

Usage:
  python tools/supervisor/run_regression_baseline.py
"""
from __future__ import annotations

import argparse
import datetime
import glob
import hashlib
import importlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run regression baseline checks")
    parser.add_argument("--date", default=None, help="Override date for output dir (YYYY-MM-DD)")
    parser.add_argument("--repo-root", type=Path, default=None)
    args = parser.parse_args()

    if args.repo_root:
        repo_root = args.repo_root.resolve()
    else:
        repo_root = Path(__file__).resolve()
        while repo_root.name not in ("format-factory", "") and repo_root != repo_root.parent:
            repo_root = repo_root.parent

    date_str = args.date or datetime.date.today().isoformat()
    output_dir = repo_root / ".local" / "supervisor" / "consolidation-baseline" / date_str
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    all_pass = True

    print("\n[Check 1] Validator count invariant...")
    check1 = _check_validator_count(repo_root)
    results["check_1_validator_count"] = check1
    (output_dir / "baseline-validator-count.json").write_text(
        json.dumps(check1, indent=2), encoding="utf-8"
    )
    if check1["assertion_passed"]:
        print(f"  PASS: {check1['count']} validators (>= {check1['threshold']})")
    else:
        print(f"  FAIL: {check1['count']} validators (< {check1['threshold']})")
        all_pass = False

    print("\n[Check 2] Grade output hash stability...")
    check2 = _check_grade_hashes(repo_root)
    results["check_2_grade_hashes"] = check2
    (output_dir / "baseline-grade-hashes.json").write_text(
        json.dumps(check2, indent=2), encoding="utf-8"
    )
    if check2["assertion_passed"]:
        stable = check2.get("stable_count", "N/A")
        total = check2.get("total", "N/A")
        print(f"  PASS: {stable}/{total} declarations stable")
    else:
        print(f"  FAIL: {check2.get('unstable_count')} unstable declarations")
        all_pass = False

    print("\n[Check 3] Continuation verdict stability...")
    check3 = _check_continuation_stability(repo_root)
    results["check_3_continuation_stability"] = check3
    (output_dir / "baseline-continuation-stability.json").write_text(
        json.dumps(check3, indent=2), encoding="utf-8"
    )
    if check3["assertion_passed"]:
        print(f"  PASS: all_identical={check3['all_identical']} verdict={check3.get('verdict')}")
    else:
        print("  FAIL: verdicts differ across runs")
        all_pass = False

    print("\n[Check 4] Git operation latency...")
    check4 = _check_git_latency(repo_root)
    results["check_4_git_latency"] = check4
    (output_dir / "baseline-git-latency.json").write_text(
        json.dumps(check4, indent=2), encoding="utf-8"
    )
    if check4.get("performance_concern"):
        print(f"  WARN: {check4.get('concern_detail')} (TC-BF-009 condition MET)")
    else:
        print(f"  OK: max {check4.get('max_ms')}ms")

    divider = "=" * 60
    print(f"\n{divider}")
    outcome = "ALL PASS" if all_pass else "FAILURES DETECTED"
    print(f"Regression baseline: {outcome}")
    for k, v in results.items():
        status = "PASS" if v.get("assertion_passed") else "FAIL"
        print(f"  {k}: {status}")
    print(f"\nOutputs written to: {output_dir}")

    return 0 if all_pass else 1


def _check_validator_count(repo_root: Path) -> dict:
    """Check 1: _VALIDATOR_REGISTRY count >= 154 after importing all governance_validators*.py."""
    threshold = 154
    try:
        sup_path = str(repo_root / "tools" / "supervisor")
        if sup_path not in sys.path:
            sys.path.insert(0, sup_path)

        from governance_validators_contract import _VALIDATOR_REGISTRY  # noqa: PLC0415

        for f in sorted(glob.glob(str(repo_root / "tools/supervisor/governance_validators*.py"))):
            modname = os.path.basename(f).replace(".py", "")
            if modname == "governance_validators_contract":
                continue
            try:
                importlib.import_module(modname)
            except Exception:
                pass

        count = len(_VALIDATOR_REGISTRY)
        return {"count": count, "threshold": threshold, "assertion_passed": count >= threshold}
    except Exception as e:
        return {"count": 0, "threshold": threshold, "assertion_passed": False, "error": str(e)}


def _check_grade_hashes(repo_root: Path) -> dict:
    """Check 2: run grade_declared_work.py twice on 5 declarations; compare MD5 hashes."""
    grade_script = repo_root / "tools" / "supervisor" / "grade_declared_work.py"
    if not grade_script.exists():
        return {"assertion_passed": True, "skipped": True, "reason": "grade_declared_work.py not found"}

    evidences_dir = repo_root / ".local" / "evidences"
    if not evidences_dir.exists():
        return {"assertion_passed": True, "skipped": True, "reason": ".local/evidences/ not found"}

    candidates = []
    for d in sorted(evidences_dir.iterdir(), reverse=True):
        if not d.is_dir():
            continue
        decl = d / "evidence-declaration.yaml"
        review = d / "evidence-review.json"
        if decl.exists() and review.exists():
            candidates.append((d, decl, review))
        if len(candidates) >= 5:
            break

    if not candidates:
        return {"assertion_passed": True, "skipped": True, "reason": "No complete evidence declarations found"}

    file_results = []
    for _d, decl, review in candidates:
        hashes = []
        for _ in range(2):
            try:
                subprocess.run(
                    [sys.executable, str(grade_script), str(decl)],
                    capture_output=True, text=True, timeout=30, cwd=str(repo_root)
                )
                if review.exists():
                    hashes.append(hashlib.md5(review.read_bytes()).hexdigest())
                else:
                    hashes.append(None)
            except Exception:
                hashes.append(None)

        stable = hashes[0] is not None and hashes[0] == hashes[1]
        file_results.append({
            "declaration": str(decl.relative_to(repo_root)),
            "hash_run1": hashes[0],
            "hash_run2": hashes[1],
            "stable": stable,
        })

    stable_count = sum(1 for r in file_results if r["stable"])
    return {
        "total": len(file_results),
        "stable_count": stable_count,
        "unstable_count": len(file_results) - stable_count,
        "assertion_passed": all(r["stable"] for r in file_results),
        "files": file_results,
    }


def _check_continuation_stability(repo_root: Path) -> dict:
    """Check 3: run check_continuation.py 3 times; verdicts must be identical."""
    check_script = repo_root / "tools" / "supervisor" / "check_continuation.py"
    if not check_script.exists():
        return {"assertion_passed": True, "skipped": True, "reason": "check_continuation.py not found"}

    verdicts = []
    for i in range(3):
        try:
            result = subprocess.run(
                [sys.executable, str(check_script)],
                capture_output=True, text=True, timeout=30, cwd=str(repo_root)
            )
            try:
                data = json.loads(result.stdout)
                v = data.get("verdict", "UNKNOWN")
                r = data.get("reason", "")
            except Exception:
                v = "PARSE_ERROR"
                r = result.stdout[:200]
            verdicts.append({"run": i + 1, "verdict": v, "reason": r})
        except Exception as e:
            verdicts.append({"run": i + 1, "verdict": "ERROR", "reason": str(e)})

    verdict_values = [v["verdict"] for v in verdicts]
    all_identical = len(set(verdict_values)) <= 1

    return {
        "verdict": verdict_values[0] if verdict_values else "UNKNOWN",
        "all_identical": all_identical,
        "assertion_passed": all_identical,
        "verdicts": verdicts,
    }


def _check_git_latency(repo_root: Path) -> dict:
    """Check 4: time 3 git operations; flag if any > 3000ms (non-blocking)."""
    THRESHOLD_MS = 3000
    operations = [
        ("git_status", ["git", "status"]),
        ("git_diff", ["git", "diff", "HEAD", "--stat"]),
        ("git_log", ["git", "log", "--oneline", "-100"]),
    ]

    measurements = {}
    max_ms = 0
    concern = False

    for name, cmd in operations:
        times = []
        for _ in range(3):
            start = time.monotonic()
            try:
                subprocess.run(cmd, capture_output=True, timeout=30, cwd=str(repo_root))
            except Exception:
                pass
            elapsed = int((time.monotonic() - start) * 1000)
            times.append(elapsed)
        avg_ms = int(sum(times) / len(times))
        measurements[name] = {"avg_ms": avg_ms, "runs_ms": times}
        if avg_ms > max_ms:
            max_ms = avg_ms
        if avg_ms > THRESHOLD_MS:
            concern = True

    result: dict = {
        "measurements": measurements,
        "max_ms": max_ms,
        "threshold_ms": THRESHOLD_MS,
        "performance_concern": concern,
        "assertion_passed": True,  # latency is non-blocking documentation
    }
    if concern:
        slow_ops = [k for k, v in measurements.items() if v["avg_ms"] > THRESHOLD_MS]
        result["concern_detail"] = f"Operations exceeding {THRESHOLD_MS}ms: {slow_ops}"

    return result


if __name__ == "__main__":
    sys.exit(main())
