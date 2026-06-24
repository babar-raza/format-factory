"""traceability_validator.py — Walk the full spec chain for qname registry entries.

TC-TRACEABILITY-001 (cheerful-floating-glade plan).

Chain:
    qname_registry entry (python_file)
    → python_file exists on disk
    → python_file contains class with spec_qname == entry.qname
    → test file imports that class
    → test has assertion on spec_qname

Output: reports/traceability/{format}-chain.yaml per format.

CLI:
    python tools/validators/traceability_validator.py [--format ndjson] [--output-dir reports/traceability]
    python tools/validators/traceability_validator.py --all

Read-only: no source files are modified.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

try:
    import yaml as _yaml_lib
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

_REPO_ROOT = Path(__file__).parent.parent.parent


def _find_class_with_spec_qname(source: str, expected_qname: str) -> str | None:
    """Return the class name that has spec_qname == expected_qname, or None."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                if (
                    any(isinstance(t, ast.Name) and t.id == "spec_qname" for t in stmt.targets)
                    and isinstance(stmt.value, ast.Constant)
                    and stmt.value.value == expected_qname
                ):
                    return node.name
            if isinstance(stmt, ast.AnnAssign):
                if (
                    isinstance(stmt.target, ast.Name)
                    and stmt.target.id == "spec_qname"
                    and isinstance(stmt.value, ast.Constant)
                    and stmt.value.value == expected_qname
                ):
                    return node.name
    return None


def _find_tests_importing_class(class_name: str, fmt: str, repo_root: Path) -> list[str]:
    """Find test files that import class_name for this format."""
    test_dirs = [
        repo_root / "tests" / "python" / fmt.lower(),
        repo_root / "tests" / "net" / fmt.lower(),
    ]
    results = []
    for test_dir in test_dirs:
        if not test_dir.exists():
            continue
        for test_file in sorted(test_dir.rglob("test_*.py")):
            try:
                src = test_file.read_text(encoding="utf-8", errors="replace")
                if class_name in src:
                    results.append(str(test_file.relative_to(repo_root)))
            except OSError:
                continue
    return results


def _test_has_spec_qname_assertion(test_file: Path) -> bool:
    """Return True if the test file has an assertion on spec_qname."""
    try:
        src = test_file.read_text(encoding="utf-8", errors="replace")
        return "spec_qname" in src
    except OSError:
        return False


def validate_format(fmt: str, repo_root: Path) -> list[dict]:
    """Run the traceability chain for a single format. Returns list of chain entries."""
    registry_path = repo_root / "shared" / "qname-registry" / f"{fmt}.yaml"
    if not registry_path.exists():
        return [{"error": f"Registry not found: {registry_path}"}]

    try:
        if _HAS_YAML:
            entries = _yaml_lib.safe_load(registry_path.read_text(encoding="utf-8")) or []
        else:
            return [{"error": "PyYAML not available — install pyyaml"}]
    except Exception as exc:
        return [{"error": f"Cannot parse registry: {exc}"}]

    chain_results = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        qname = entry.get("qname", "")
        python_file = entry.get("python_file")
        status = entry.get("status", "seeded")

        chain: dict = {
            "qname": qname,
            "status": status,
            "python_file": python_file,
            "link_1_file_exists": None,
            "link_2_class_found": None,
            "class_name": None,
            "link_3_test_imports": None,
            "test_files": [],
            "link_4_spec_qname_assertion": None,
            "chain_complete": False,
            "broken_at": None,
        }

        if not python_file:
            chain["broken_at"] = "link_1_file_exists"
            chain["link_1_file_exists"] = False
            chain_results.append(chain)
            continue

        # Link 1: file exists
        target = repo_root / python_file
        chain["link_1_file_exists"] = target.exists()
        if not chain["link_1_file_exists"]:
            chain["broken_at"] = "link_1_file_exists"
            chain_results.append(chain)
            continue

        # Link 2: class with spec_qname
        try:
            src = target.read_text(encoding="utf-8", errors="replace")
        except OSError:
            chain["link_2_class_found"] = False
            chain["broken_at"] = "link_2_class_found"
            chain_results.append(chain)
            continue

        class_name = _find_class_with_spec_qname(src, qname)
        chain["class_name"] = class_name
        chain["link_2_class_found"] = class_name is not None
        if not chain["link_2_class_found"]:
            chain["broken_at"] = "link_2_class_found"
            chain_results.append(chain)
            continue

        # Link 3: test imports class
        test_files = _find_tests_importing_class(class_name, fmt, repo_root)
        chain["test_files"] = test_files
        chain["link_3_test_imports"] = len(test_files) > 0
        if not chain["link_3_test_imports"]:
            chain["broken_at"] = "link_3_test_imports"
            chain_results.append(chain)
            continue

        # Link 4: test has spec_qname assertion
        has_assertion = any(
            _test_has_spec_qname_assertion(repo_root / tf) for tf in test_files
        )
        chain["link_4_spec_qname_assertion"] = has_assertion
        if not has_assertion:
            chain["broken_at"] = "link_4_spec_qname_assertion"
            chain_results.append(chain)
            continue

        chain["chain_complete"] = True
        chain_results.append(chain)

    return chain_results


def _write_output(fmt: str, chain: list[dict], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / f"{fmt}-chain.yaml"
    complete = sum(1 for c in chain if c.get("chain_complete"))
    broken = sum(1 for c in chain if c.get("broken_at"))
    data = {
        "format": fmt,
        "total_entries": len(chain),
        "chain_complete": complete,
        "broken_links": broken,
        "entries": chain,
    }
    if _HAS_YAML:
        out.write_text(
            _yaml_lib.dump(data, default_flow_style=False, allow_unicode=True),
            encoding="utf-8",
        )
    else:
        out.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return out


def run(
    formats: list[str],
    output_dir: Path,
    repo_root: Path,
    verbose: bool = False,
) -> int:
    rc = 0
    for fmt in formats:
        chain = validate_format(fmt, repo_root)
        out = _write_output(fmt, chain, output_dir)
        complete = sum(1 for c in chain if c.get("chain_complete"))
        broken_entries = [c for c in chain if c.get("broken_at")]
        print(f"{fmt}: {len(chain)} entries, {complete} complete, {len(broken_entries)} broken -> {out}")
        if verbose:
            for entry in broken_entries:
                print(f"  BROKEN [{entry.get('broken_at')}]: {entry.get('qname')} ({entry.get('python_file')})")
    return rc


def main() -> None:
    parser = argparse.ArgumentParser(description="Walk qname registry chain for traceability")
    parser.add_argument("--format", dest="fmt", help="Single format to validate (e.g. ndjson)")
    parser.add_argument("--all", action="store_true", help="Validate all registered formats")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/traceability"),
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    repo_root = _REPO_ROOT
    output_dir = repo_root / args.output_dir if not args.output_dir.is_absolute() else args.output_dir

    if args.all:
        registry_dir = repo_root / "shared" / "qname-registry"
        formats = [p.stem for p in sorted(registry_dir.glob("*.yaml")) if p.stem != "schema"]
    elif args.fmt:
        formats = [args.fmt.lower()]
    else:
        # Default: pilot formats
        formats = ["ndjson", "fods"]

    rc = run(formats, output_dir, repo_root, verbose=args.verbose)
    sys.exit(rc)


if __name__ == "__main__":
    main()
