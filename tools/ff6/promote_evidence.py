"""Promote evidence from nonpromoting to promoting by executing tests.

The reconciler produces ``supporting_nonpromoting`` proof because it checks
file/symbol existence, not test execution.  This tool bridges the gap:

1. Runs the format's test suite
2. Records the test count, pass count, and hash of source files
3. Writes a promoting reconciliation overlay that ``_is_certified()`` accepts

Usage::

    python -m tools.ff6.promote_evidence nrrd
    python -m tools.ff6.promote_evidence --all
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
RECONCILIATION_DIR = REPO_ROOT / "reports" / "format-contract-layer"
FF6_FORMATS = ("ipynb", "ora", "nrrd", "xliff", "safetensors", "ubl")


def _source_hash(format_id: str) -> str:
    """SHA-256 of all source files for a format, concatenated."""
    src_dir = REPO_ROOT / "src" / "python" / format_id
    if not src_dir.exists():
        return "missing"
    h = hashlib.sha256()
    for f in sorted(src_dir.rglob("*.py")):
        h.update(f.read_bytes())
    return h.hexdigest()


def _test_hash(format_id: str) -> str:
    """SHA-256 of all test files for a format, concatenated."""
    test_dir = REPO_ROOT / "tests" / "python" / format_id
    if not test_dir.exists():
        return "missing"
    h = hashlib.sha256()
    for f in sorted(test_dir.rglob("*.py")):
        h.update(f.read_bytes())
    return h.hexdigest()


def _run_tests(format_id: str) -> dict[str, Any]:
    """Run pytest for a format and parse the result."""
    test_dir = REPO_ROOT / "tests" / "python" / format_id
    if not test_dir.exists():
        return {"passed": False, "error": f"test directory not found: {test_dir}"}

    pytest_exe = REPO_ROOT / ".venv" / "Scripts" / "pytest.exe"
    if not pytest_exe.exists():
        pytest_exe = REPO_ROOT / ".venv" / "Scripts" / "pytest"
    if not pytest_exe.exists():
        pytest_exe = REPO_ROOT / ".venv" / "bin" / "pytest"

    try:
        result = subprocess.run(
            [str(pytest_exe), str(test_dir), "-q", "--tb=no"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(REPO_ROOT),
        )
    except subprocess.TimeoutExpired:
        return {"passed": False, "error": "test suite timed out (120s)"}

    last_line = ""
    for line in result.stdout.strip().splitlines():
        if "passed" in line or "failed" in line or "error" in line:
            last_line = line.strip()

    passed_count = 0
    failed_count = 0
    if last_line:
        import re
        m_passed = re.search(r"(\d+) passed", last_line)
        m_failed = re.search(r"(\d+) failed", last_line)
        if m_passed:
            passed_count = int(m_passed.group(1))
        if m_failed:
            failed_count = int(m_failed.group(1))

    return {
        "passed": result.returncode == 0 and failed_count == 0,
        "exit_code": result.returncode,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "summary_line": last_line,
    }


def promote(format_id: str, *, dry_run: bool = False) -> dict[str, Any]:
    """Attempt to promote a format's evidence."""
    recon_path = RECONCILIATION_DIR / f"{format_id}-obligation-reconciliation.json"
    if not recon_path.exists():
        return {"format_id": format_id, "promoted": False, "reason": "no reconciliation report"}

    recon = json.loads(recon_path.read_text(encoding="utf-8"))
    summary = recon.get("summary", {})
    unresolved = summary.get("unresolved", -1)

    if unresolved != 0:
        return {"format_id": format_id, "promoted": False, "reason": f"{unresolved} unresolved obligations"}

    test_result = _run_tests(format_id)
    if not test_result["passed"]:
        return {
            "format_id": format_id,
            "promoted": False,
            "reason": f"tests failed: {test_result.get('summary_line', test_result.get('error'))}",
            "test_result": test_result,
        }

    now = datetime.now(timezone.utc).isoformat()

    digests: dict[str, str] = {}
    for subdir in (f"src/python/{format_id}", f"tests/python/{format_id}"):
        full = REPO_ROOT / subdir
        if full.is_dir():
            for f in sorted(full.rglob("*.py")):
                rel = f.relative_to(REPO_ROOT).as_posix()
                digests[rel] = hashlib.sha256(f.read_bytes()).hexdigest()

    recon["proof_strength"] = "promoting"
    recon["promotion_effect"] = "certifiable"
    recon["referenced_input_digests"] = digests
    recon["promotion_evidence"] = {
        "promoted_at": now,
        "test_passed_count": test_result["passed_count"],
        "test_failed_count": test_result["failed_count"],
    }

    if not dry_run:
        recon_path.write_text(json.dumps(recon, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return {
        "format_id": format_id,
        "promoted": True,
        "test_result": test_result,
        "digests_count": len(digests),
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(
        prog="python -m tools.ff6.promote_evidence",
        description="Promote evidence from nonpromoting to promoting",
    )
    parser.add_argument("format_id", nargs="?", help="Format to promote (or --all)")
    parser.add_argument("--all", action="store_true", help="Promote all formats")
    parser.add_argument("--dry-run", action="store_true", help="Don't write changes")
    args = parser.parse_args()

    if not args.format_id and not args.all:
        parser.error("specify a format_id or --all")

    formats = list(FF6_FORMATS) if args.all else [args.format_id]
    results = []
    for fid in formats:
        print(f"\n{'='*40}")
        print(f"Promoting: {fid}")
        result = promote(fid, dry_run=args.dry_run)
        results.append(result)
        if result["promoted"]:
            tr = result["test_result"]
            print(f"  PROMOTED: {tr['passed_count']} tests passed, 0 failed")
        else:
            print(f"  NOT PROMOTED: {result['reason']}")

    promoted = sum(1 for r in results if r["promoted"])
    total = len(results)
    print(f"\n{promoted}/{total} formats promoted")
    return 0 if promoted > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
