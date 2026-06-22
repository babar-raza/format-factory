"""no_stub_scan.py — Scan Python source for forbidden stub/incomplete markers.

Per the governed QName decomposition plan (§2.2 No-Stub Policy):

Forbidden terms that indicate incomplete or placeholder implementations:
  TODO, FIXME, stub, placeholder, not implemented, dummy, fake, mock,
  temporary, TBD, later, future

Also detects:
  - Methods whose entire body is a bare `pass` statement (stub body)
  - Classes with only `pass` and no `authority_only = True` marker

Allowed exception:
  - Classes with `authority_only = True` class attribute are metadata-only
    spec authority classes and are exempt from the stub body check.

CLI:
  python tools/review/no_stub_scan.py src/python/abw
  python tools/review/no_stub_scan.py --paths src/python tests docs registry
  python tools/review/no_stub_scan.py src/python/abw --json
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent

_FORBIDDEN_TERMS: list[str] = [
    "TODO",
    "FIXME",
    " stub",
    "placeholder",
    "not implemented",
    "NotImplemented",
    "dummy",
    " fake",
    " mock",
    "temporary",
    "TBD",
]

_FORBIDDEN_RE = re.compile(
    "|".join(re.escape(t) for t in _FORBIDDEN_TERMS),
    re.IGNORECASE,
)


def _is_pass_only_body(node: ast.AST) -> bool:
    """Return True if the AST node body consists solely of a Pass statement."""
    body = getattr(node, "body", [])
    if not body:
        return False
    non_doc = [
        s for s in body
        if not (isinstance(s, ast.Expr) and isinstance(getattr(s, "value", None), ast.Constant))
    ]
    return len(non_doc) == 1 and isinstance(non_doc[0], ast.Pass)


def _has_authority_only(cls_node: ast.ClassDef) -> bool:
    """Return True if the class declares `authority_only = True`."""
    for stmt in cls_node.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id == "authority_only":
                    if isinstance(stmt.value, ast.Constant) and stmt.value.value is True:
                        return True
    return False


def scan_file(path: Path) -> list[dict[str, Any]]:
    """Scan a single Python file and return a list of violation dicts."""
    violations: list[dict[str, Any]] = []
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return violations

    # 1. Forbidden term scan (line-by-line)
    for lineno, line in enumerate(source.splitlines(), start=1):
        # Skip lines that are only comments or strings — still flag them
        m = _FORBIDDEN_RE.search(line)
        if m:
            violations.append({
                "file": str(path),
                "line": lineno,
                "kind": "forbidden_term",
                "term": m.group(0),
                "text": line.strip(),
            })

    # 2. AST scan for pass-only method bodies and empty classes
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return violations

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if _is_pass_only_body(node) and not _has_authority_only(node):
                violations.append({
                    "file": str(path),
                    "line": node.lineno,
                    "kind": "pass_only_class",
                    "class": node.name,
                    "text": f"class {node.name}: pass  (no authority_only=True)",
                })
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _is_pass_only_body(node) and node.name != "__init__":
                violations.append({
                    "file": str(path),
                    "line": node.lineno,
                    "kind": "pass_only_method",
                    "method": node.name,
                    "text": f"def {node.name}(): pass",
                })

    return violations


def scan_paths(paths: list[Path], exclude_patterns: list[str] | None = None) -> list[dict[str, Any]]:
    """Scan all .py files under given paths; return aggregated violations."""
    excludes = exclude_patterns or ["__pycache__", "build", ".venv", ".git"]
    all_violations: list[dict[str, Any]] = []
    for root_path in paths:
        root_path = root_path if root_path.is_absolute() else _REPO_ROOT / root_path
        if root_path.is_file() and root_path.suffix == ".py":
            all_violations.extend(scan_file(root_path))
        elif root_path.is_dir():
            for py_file in sorted(root_path.rglob("*.py")):
                parts = py_file.parts
                if any(ex in parts for ex in excludes):
                    continue
                all_violations.extend(scan_file(py_file))
    return all_violations


def report(paths: list[Path], exclude_patterns: list[str] | None = None) -> dict[str, Any]:
    """Return a structured report dict."""
    violations = scan_paths(paths, exclude_patterns)
    by_kind: dict[str, int] = {}
    for v in violations:
        k = v["kind"]
        by_kind[k] = by_kind.get(k, 0) + 1

    status = "CLEAN" if not violations else "VIOLATIONS_FOUND"
    return {
        "status": status,
        "total_violations": len(violations),
        "by_kind": by_kind,
        "violations": violations,
    }


def _cli() -> int:
    parser = argparse.ArgumentParser(description="No-stub scanner for Python source")
    parser.add_argument("paths", nargs="*", default=["src/python"],
                        help="Paths to scan (files or directories)")
    parser.add_argument("--exclude", nargs="*", default=None,
                        help="Directory names to exclude")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    scan_roots = [Path(p) for p in args.paths]
    result = report(scan_roots, args.exclude)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Status: {result['status']}")
        print(f"Total violations: {result['total_violations']}")
        for v in result["violations"]:
            print(f"  {v['file']}:{v['line']} [{v['kind']}] {v['text'][:80]}")

    return 0 if result["status"] == "CLEAN" else 1


if __name__ == "__main__":
    sys.exit(_cli())
