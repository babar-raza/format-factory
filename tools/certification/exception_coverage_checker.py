"""Exception contract and coverage scanner for certification.

generated_by: codex
mission_id: CERT-EXHAUST-20260628
visibility: internal
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]


def _rel(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def _exception_name(node: ast.AST | None) -> str | None:
    if node is None:
        return None
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Call):
        return _exception_name(node.func)
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _is_exception_class(node: ast.ClassDef) -> bool:
    if node.name.endswith("Error") or node.name.endswith("Exception"):
        return True
    for base in node.bases:
        name = _exception_name(base)
        if name and (name.endswith("Error") or name.endswith("Exception")):
            return True
    return False


def _scan_source(src_path: Path) -> dict[str, Any]:
    exception_classes: dict[str, dict[str, Any]] = {}
    raise_sites: list[dict[str, Any]] = []
    files = sorted(src_path.rglob("*.py")) if src_path.is_dir() else [src_path]

    for path in files:
        skip_dirs = {"__pycache__", "build", ".egg-info"}
        if any(d in path.parts for d in skip_dirs):
            continue
        if any(part.endswith(".egg-info") for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and _is_exception_class(node):
                exception_classes[node.name] = {"name": node.name, "file": _rel(path), "line": node.lineno}
            elif isinstance(node, ast.Raise):
                name = _exception_name(node.exc)
                if name:
                    raise_sites.append({"exception": name, "file": _rel(path), "line": node.lineno})

    return {"exception_classes": exception_classes, "raise_sites": raise_sites}


def _scan_tests(test_path: Path, exception_names: set[str]) -> dict[str, list[dict[str, Any]]]:
    coverage = {name: [] for name in exception_names}
    if not test_path.exists():
        return coverage
    files = sorted(test_path.rglob("*.py")) if test_path.is_dir() else [test_path]
    for path in files:
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for name in exception_names:
            if name in text:
                coverage[name].append({"file": _rel(path), "match": "text_reference"})
    return coverage


def check_exception_coverage(src_path: Path, test_path: Path | None = None) -> dict[str, Any]:
    src = src_path if src_path.is_absolute() else REPO_ROOT / src_path
    tests = None if test_path is None else (test_path if test_path.is_absolute() else REPO_ROOT / test_path)
    source_scan = _scan_source(src)
    exception_names = set(source_scan["exception_classes"])
    test_refs = _scan_tests(tests, exception_names) if tests else {name: [] for name in exception_names}
    raised = {site["exception"] for site in source_scan["raise_sites"]}

    exceptions = []
    for name, meta in sorted(source_scan["exception_classes"].items()):
        exceptions.append(
            {
                **meta,
                "raised_in_source": name in raised,
                "test_reference_count": len(test_refs.get(name, [])),
                "test_references": test_refs.get(name, []),
                "coverage_status": "REFERENCED_BY_TEST" if test_refs.get(name) else "NO_TEST_REFERENCE_FOUND",
            }
        )

    return {
        "metadata": {
            "authoritative_plan": "plans/.claude/crispy-jingling-snail.md",
            "generated_by": "codex",
            "mission_id": "CERT-EXHAUST-20260628",
            "visibility": "internal",
            "tool": "exception_coverage_checker",
        },
        "source_path": _rel(src),
        "test_path": _rel(tests) if tests else None,
        "exception_count": len(exceptions),
        "raise_site_count": len(source_scan["raise_sites"]),
        "exceptions": exceptions,
        "raise_sites": sorted(source_scan["raise_sites"], key=lambda x: (x["file"], x["line"])),
        "uncovered_exception_count": sum(1 for item in exceptions if item["coverage_status"] != "REFERENCED_BY_TEST"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src-path", required=True, type=Path)
    parser.add_argument("--test-path", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = check_exception_coverage(args.src_path, args.test_path)
    if args.output:
        output = args.output if args.output.is_absolute() else REPO_ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"output": _rel(output), "uncovered_exception_count": result["uncovered_exception_count"]}, sort_keys=True))
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
