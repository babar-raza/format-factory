"""validate_cross_language_parity.py — Cross-language spec parity checker.

Reads shared/qname-registry/<format>.yaml and verifies that:
- For each entry with python_file (not null): file exists AND contains spec_qname matching qname
- For each entry with dotnet_file (not null): file exists AND contains QName constant matching qname
- Entries with python_file: null are EXPECTED PARTIAL (not a failure — Python has no equivalent)

Exit codes:
  0 — ALL_PASS (all entries with non-null files verified)
  1 — PARTIAL_BY_DESIGN (some entries have null files — expected during bootstrap)
  2 — FAIL (file missing or QName mismatch)

Usage:
  python tools/spec/validate_cross_language_parity.py --format fodt
"""

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def _load_yaml_registry(registry_path: Path) -> list[dict]:
    """Load a YAML registry file as a list of dicts."""
    try:
        import yaml  # type: ignore[import]
    except ImportError:
        # Minimal YAML list parser for simple registry files
        entries = []
        current: dict = {}
        for line in registry_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("- "):
                if current:
                    entries.append(current)
                current = {}
                rest = line[2:].strip()
                if ":" in rest:
                    k, _, v = rest.partition(":")
                    current[k.strip()] = v.strip().strip('"').strip("'") or None
            elif line.startswith("  ") and ":" in line:
                k, _, v = line.strip().partition(":")
                val = v.strip().strip('"').strip("'")
                current[k.strip()] = None if val in ("null", "~", "") else val
        if current:
            entries.append(current)
        return entries

    return yaml.safe_load(registry_path.read_text(encoding="utf-8")) or []


def _check_python_file(entry: dict, repo_root: Path) -> dict:
    """Check a Python spec file for spec_qname attribute matching entry's qname."""
    python_file = entry.get("python_file")
    qname = entry.get("qname", "")

    if python_file is None or python_file == "null":
        return {
            "status": "partial_by_design",
            "qname": qname,
            "lang": "python",
            "reason": "python_file is null (expected — no Python equivalent for this qname)",
        }

    file_path = repo_root / python_file
    if not file_path.exists():
        return {
            "status": "fail",
            "qname": qname,
            "lang": "python",
            "file": python_file,
            "reason": f"python_file does not exist: {python_file}",
        }

    content = file_path.read_text(encoding="utf-8", errors="replace")
    if "spec_qname" not in content:
        return {
            "status": "fail",
            "qname": qname,
            "lang": "python",
            "file": python_file,
            "reason": f"spec_qname attribute missing in {python_file}",
        }

    # Extract spec_qname value and compare to registry qname
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("spec_qname"):
            # e.g.: spec_qname = "text:p"
            if "=" in stripped:
                rhs = stripped.split("=", 1)[1].strip().strip('"').strip("'")
                if rhs == qname:
                    return {
                        "status": "pass",
                        "qname": qname,
                        "lang": "python",
                        "file": python_file,
                    }
                else:
                    return {
                        "status": "fail",
                        "qname": qname,
                        "lang": "python",
                        "file": python_file,
                        "reason": f"spec_qname mismatch: file has '{rhs}', registry has '{qname}'",
                    }

    return {
        "status": "fail",
        "qname": qname,
        "lang": "python",
        "file": python_file,
        "reason": f"spec_qname found in file but could not parse its value in {python_file}",
    }


def _check_dotnet_file(entry: dict, repo_root: Path) -> dict:
    """Check a .NET spec file for QName constant matching entry's qname."""
    dotnet_file = entry.get("dotnet_file")
    qname = entry.get("qname", "")

    if dotnet_file is None or dotnet_file == "null":
        return {
            "status": "partial_by_design",
            "qname": qname,
            "lang": "dotnet",
            "reason": "dotnet_file is null (expected — no .NET equivalent for this qname)",
        }

    file_path = repo_root / dotnet_file
    if not file_path.exists():
        return {
            "status": "fail",
            "qname": qname,
            "lang": "dotnet",
            "file": dotnet_file,
            "reason": f"dotnet_file does not exist: {dotnet_file}",
        }

    content = file_path.read_text(encoding="utf-8", errors="replace")
    if "QName" not in content:
        return {
            "status": "fail",
            "qname": qname,
            "lang": "dotnet",
            "file": dotnet_file,
            "reason": f"QName constant missing in {dotnet_file}",
        }

    # Extract QName value: e.g.: public const string QName = "office:body";
    for line in content.splitlines():
        stripped = line.strip()
        if "QName" in stripped and "=" in stripped and '"' in stripped:
            # Extract string value between quotes
            parts = stripped.split('"')
            if len(parts) >= 2:
                rhs = parts[1]
                if rhs == qname:
                    return {
                        "status": "pass",
                        "qname": qname,
                        "lang": "dotnet",
                        "file": dotnet_file,
                    }
                else:
                    return {
                        "status": "fail",
                        "qname": qname,
                        "lang": "dotnet",
                        "file": dotnet_file,
                        "reason": f"QName mismatch: file has '{rhs}', registry has '{qname}'",
                    }

    return {
        "status": "fail",
        "qname": qname,
        "lang": "dotnet",
        "file": dotnet_file,
        "reason": f"QName found in file but could not parse its value in {dotnet_file}",
    }


def run_parity_check(format_name: str, repo_root: Path) -> tuple[int, list[dict]]:
    """Run parity check for a format. Returns (exit_code, results)."""
    registry_path = repo_root / "shared" / "qname-registry" / f"{format_name}.yaml"

    if not registry_path.exists():
        return 1, [
            {
                "status": "partial_by_design",
                "reason": f"Registry file absent: {registry_path.relative_to(repo_root)} — bootstrap phase",
            }
        ]

    entries = _load_yaml_registry(registry_path)
    results: list[dict] = []

    for entry in entries:
        py_result = _check_python_file(entry, repo_root)
        dn_result = _check_dotnet_file(entry, repo_root)
        results.append({"qname": entry.get("qname"), "python": py_result, "dotnet": dn_result})

    # Determine exit code
    has_fail = any(
        r["python"]["status"] == "fail" or r["dotnet"]["status"] == "fail"
        for r in results
    )
    has_partial = any(
        r["python"]["status"] == "partial_by_design" or r["dotnet"]["status"] == "partial_by_design"
        for r in results
    )

    if has_fail:
        return 2, results
    if has_partial:
        return 1, results
    return 0, results


def _print_report(results: list[dict], exit_code: int, format_name: str) -> None:
    """Print a human-readable parity report."""
    status_labels = {0: "ALL_PASS", 1: "PARTIAL_BY_DESIGN", 2: "FAIL"}
    print(f"Cross-language parity check — format: {format_name}")
    print(f"Status: {status_labels.get(exit_code, 'UNKNOWN')} (exit {exit_code})")
    print()

    pass_count = partial_count = fail_count = 0
    for row in results:
        qname = row.get("qname", "<unknown>")
        py = row.get("python", {})
        dn = row.get("dotnet", {})

        for check in (py, dn):
            st = check.get("status", "")
            lang = check.get("lang", "?")
            if st == "pass":
                pass_count += 1
                print(f"  PASS   [{lang:6}] {qname}")
            elif st == "partial_by_design":
                partial_count += 1
                print(f"  PARTIAL[{lang:6}] {qname}  — {check.get('reason', '')}")
            elif st == "fail":
                fail_count += 1
                print(f"  FAIL   [{lang:6}] {qname}  — {check.get('reason', '')}")

    print()
    print(f"Summary: {pass_count} PASS, {partial_count} PARTIAL (by design), {fail_count} FAIL")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cross-language parity checker for spec registry")
    parser.add_argument("--format", required=True, help="Format name (e.g. fodt, fods)")
    parser.add_argument("--repo-root", default=None, help="Override repo root path")
    parser.add_argument("--quiet", action="store_true", help="Suppress output (exit code only)")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root) if args.repo_root else REPO_ROOT
    exit_code, results = run_parity_check(args.format, repo_root)

    if not args.quiet:
        _print_report(results, exit_code, args.format)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
