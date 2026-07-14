"""no_stub_scan.py — Scan Python source for forbidden stub/incomplete markers.

Per the governed QName decomposition plan (§2.2 No-Stub Policy):

Forbidden terms that indicate incomplete or placeholder implementations:
  TODO, FIXME, stub, placeholder, not implemented, dummy, fake,
  temporary, TBD, later, future

Also detects:
  - Methods whose entire body is a bare `pass` statement (stub body)
  - Classes with only `pass` and no `authority_only = True` marker

Allowed exception:
  - Classes with `authority_only = True` class attribute are metadata-only
    spec authority classes and are exempt from the stub body check.

False-positive exclusions (TC-ZS-SCANNER-001, 2026-06-23):
  - Lines containing "NOT.*stub" / "NOT.*architecture_only" (anti-stub documentation)
  - Lines containing XML element patterns "text:placeholder" (ODF element name)
  - Lines matching "promoted from stub" (historical promotion notes)
  - Lines referencing gap-ledger governance ("see GAP-" pattern)
  - " mock" term removed from forbidden list (catches MagicMock in legitimate tests)

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
    "temporary",
    "TBD",
]

_FORBIDDEN_RE = re.compile(
    "|".join(re.escape(t) for t in _FORBIDDEN_TERMS),
    re.IGNORECASE,
)

_ALLOWLIST_PATTERNS: list[re.Pattern[str]] = [
    # Anti-stub documentation: "NOT an architecture_only spec stub", "NOT a stub", etc.
    re.compile(r"\bNOT\b.{0,50}\bstub\b", re.IGNORECASE),
    # References to the location of spec stubs: "spec stub is at ...", "spec stubs are under ..."
    re.compile(r"spec\s+stub[s]?\s+(is|are)\s+(at|under)", re.IGNORECASE),
    # ODF XML element names that contain "placeholder" (e.g., text:placeholder)
    re.compile(r"\w+:placeholder\b"),
    # Docstrings describing what a function scans/detects — not what the code IS
    re.compile(r"(common\s+placeholder\s+pattern|scans?\s+.{0,40}placeholder\s+pattern)", re.IGNORECASE),
    # Historical promotion notes (e.g., "promoted from stub to full package export")
    re.compile(r"promoted from\s+stub", re.IGNORECASE),
    # Governed gap-ledger references (e.g., "see GAP-XCF-LAYER-NAMES in gap-ledger.json")
    re.compile(r"see\s+GAP-[A-Z0-9\-]+\s+in\s+gap-ledger", re.IGNORECASE),
    # Docstrings noting positional/synthetic nature with gap-ledger governance
    re.compile(r"positional\s+placeholders?\s+only", re.IGNORECASE),
    # TC-SC-001: stdlib tempfile.NamedTemporaryFile usage (not a stub)
    re.compile(r"\bNamedTemporaryFile\b"),
    # TC-SC-001: ruff suppression comments that mention stub-related terms in explanation
    re.compile(r"#\s*ruff:\s*noqa\b"),
    # TC-SC-003: Read-only format write stubs — deliberate NotImplementedError by design
    # MCP-W4-004: Narrowed to exclude the overly broad raise\s+NotImplementedError\( pattern.
    # Acknowledged stubs are now governed via registry/source-structure-baseline.json
    # under the stub_exceptions section. Only docstring-level descriptions remain here.
    re.compile(r"write\s+stub\b.*read-only", re.IGNORECASE),
    re.compile(r"write\s+support\s+is\s+not\s+implemented", re.IGNORECASE),
    re.compile(r"NotImplementedError:\s+Always", re.IGNORECASE),
    # NOTE: raise\s+NotImplementedError\( removed (MCP-W4-004 / twinkly-nibbling-platypus).
    # Governed stubs are in registry/source-structure-baseline.json#stub_exceptions.
    # New raise NotImplementedError(...) lines will now be flagged by V149.
    # TC-SC-004: Governed TODOs with explicit taskcard/change-tracking IDs
    re.compile(r"TODO\([A-Z]+-[A-Z]*-?\d+\)"),
]


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


def _load_stub_exceptions() -> set[str]:
    """Load acknowledged stub file paths from registry/source-structure-baseline.json.

    MCP-W4-004 (twinkly-nibbling-platypus): replaces the overly broad
    raise\\s+NotImplementedError\\( allowlist pattern with governed baseline entries.
    """
    baseline_path = _REPO_ROOT / "registry" / "source-structure-baseline.json"
    if not baseline_path.exists():
        return set()
    try:
        import json as _json
        data = _json.loads(baseline_path.read_text(encoding="utf-8"))
        exceptions = data.get("stub_exceptions") or {}
        # Normalize paths to use forward slashes for cross-platform matching
        return {k.replace("\\", "/") for k in exceptions}
    except Exception:
        return set()


_STUB_EXCEPTIONS: set[str] = _load_stub_exceptions()


def _in_stub_exceptions(path: Path) -> bool:
    """Return True if this file is in the governed stub exceptions list."""
    try:
        rel = path.relative_to(_REPO_ROOT).as_posix()
    except ValueError:
        rel = path.as_posix()
    return rel in _STUB_EXCEPTIONS


def scan_file(path: Path) -> list[dict[str, Any]]:
    """Scan a single Python file and return a list of violation dicts."""
    violations: list[dict[str, Any]] = []
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return violations

    # Files in stub_exceptions are exempt from raise NotImplementedError checks
    # (MCP-W4-004) but not from other forbidden-term checks
    is_stub_excepted = _in_stub_exceptions(path)

    # 1. Forbidden term scan (line-by-line)
    for lineno, line in enumerate(source.splitlines(), start=1):
        m = _FORBIDDEN_RE.search(line)
        if m:
            # Apply allowlist: suppress known false-positive patterns
            if any(ap.search(line) for ap in _ALLOWLIST_PATTERNS):
                continue
            # MCP-W4-004: suppress raise NotImplementedError in governed stub files
            if is_stub_excepted and "NotImplementedError" in line and "raise" in line:
                continue
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
                # TC-SC-002: Skip nested duplicate packages (pip editable-install artifacts)
                rel_to_root = py_file.relative_to(root_path)
                rel_parts = rel_to_root.parts
                if len(rel_parts) >= 2 and rel_parts[0] == rel_parts[1]:
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
