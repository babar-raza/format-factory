"""Contextual material-stub detector for product source.

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


def _is_public_scope(stack: list[ast.AST]) -> bool:
    for node in reversed(stack):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return not node.name.startswith("_")
    return False


def _scope_name(stack: list[ast.AST]) -> str:
    names = [
        node.name
        for node in stack
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    ]
    return ".".join(names) if names else "<module>"


def _classify_stub(node: ast.AST, stack: list[ast.AST], source_lines: list[str]) -> dict[str, Any] | None:
    reason = None
    severity = "advisory"
    if isinstance(node, ast.Pass):
        reason = "pass_statement"
        severity = "material" if _is_public_scope(stack) else "advisory"
    elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and node.value.value is Ellipsis:
        reason = "ellipsis_statement"
        severity = "material" if _is_public_scope(stack) else "advisory"
    elif isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call):
        func = node.exc.func
        if isinstance(func, ast.Name) and func.id == "NotImplementedError":
            reason = "raises_not_implemented_error"
            severity = "material" if _is_public_scope(stack) else "advisory"
    elif isinstance(node, ast.Raise) and isinstance(node.exc, ast.Name) and node.exc.id == "NotImplementedError":
        reason = "raises_not_implemented_error"
        severity = "material" if _is_public_scope(stack) else "advisory"

    if reason is None:
        return None

    line = source_lines[node.lineno - 1].strip() if node.lineno and node.lineno <= len(source_lines) else ""
    return {
        "scope": _scope_name(stack),
        "line": node.lineno,
        "reason": reason,
        "severity": severity,
        "source": line,
        "classification_note": (
            "Public API scope requires follow-up classification."
            if severity == "material"
            else "Non-public or structural placeholder; not automatically material."
        ),
    }


def _is_stub_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return True if the function body is stub-only (no real logic).

    A function is a stub if its body contains only:
    - docstrings (string constants)
    - pass statements
    - ellipsis (...)
    - raise NotImplementedError(...)
    """
    for stmt in node.body:
        if isinstance(stmt, ast.Pass):
            continue
        if isinstance(stmt, ast.Expr):
            if isinstance(stmt.value, ast.Constant):
                # Docstring or ellipsis
                continue
            # Any other expression (function call, etc.) is real logic
            return False
        if isinstance(stmt, ast.Raise):
            exc = stmt.exc
            if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name) and exc.func.id == "NotImplementedError":
                continue
            if isinstance(exc, ast.Name) and exc.id == "NotImplementedError":
                continue
            # Raising something else is real logic
            return False
        # Any other statement (return, assign, for, if, try, etc.) is real logic
        return False
    return True


class StubVisitor(ast.NodeVisitor):
    def __init__(self, source_lines: list[str]) -> None:
        self.source_lines = source_lines
        self.stack: list[ast.AST] = []
        self.findings: list[dict[str, Any]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.stack.append(node)
        if _is_stub_function(node):
            # Only report stubs for functions whose ENTIRE body is stub-like
            self._report_function_stub(node)
        else:
            # Skip walking into implemented functions — pass inside
            # except handlers is normal error handling, not a stub
            pass
        self.stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        self.stack.append(node)
        if _is_stub_function(node):
            self._report_function_stub(node)
        self.stack.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        self.stack.append(node)
        self.generic_visit(node)
        self.stack.pop()

    def _report_function_stub(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Report stub findings for a function whose body is entirely stub-like."""
        for stmt in node.body:
            finding = _classify_stub(stmt, self.stack, self.source_lines)
            if finding:
                self.findings.append(finding)

    def generic_visit(self, node: ast.AST) -> Any:
        # Only classify stubs at module/class level (not inside function bodies)
        if not any(isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)) for s in self.stack):
            finding = _classify_stub(node, self.stack, self.source_lines)
            if finding:
                self.findings.append(finding)
        return super().generic_visit(node)


def scan_path(path: Path) -> dict[str, Any]:
    target = path if path.is_absolute() else REPO_ROOT / path
    files = [target] if target.is_file() else sorted(target.rglob("*.py"))
    scanned = []
    findings = []
    for file_path in files:
        skip_dirs = {"__pycache__", "build", ".egg-info"}
        if file_path.suffix != ".py" or any(d in file_path.parts for d in skip_dirs):
            continue
        if any(part.endswith(".egg-info") for part in file_path.parts):
            continue
        text = file_path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text, filename=str(file_path))
        except SyntaxError as exc:
            findings.append(
                {
                    "file": _rel(file_path),
                    "line": exc.lineno,
                    "scope": "<parse>",
                    "reason": "syntax_error",
                    "severity": "material",
                    "source": str(exc),
                }
            )
            continue
        visitor = StubVisitor(text.splitlines())
        visitor.visit(tree)
        scanned.append(_rel(file_path))
        for finding in visitor.findings:
            finding["file"] = _rel(file_path)
            findings.append(finding)

    material = [f for f in findings if f["severity"] == "material"]
    return {
        "metadata": {
            "authoritative_plan": "plans/.claude/crispy-jingling-snail.md",
            "generated_by": "codex",
            "mission_id": "CERT-EXHAUST-20260628",
            "visibility": "internal",
            "tool": "stub_detector",
        },
        "target": _rel(target),
        "files_scanned": scanned,
        "file_count": len(scanned),
        "finding_count": len(findings),
        "material_finding_count": len(material),
        "findings": sorted(findings, key=lambda f: (f.get("file", ""), f.get("line") or 0)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--run-id", default=None, help="Certification run ID (from run_manager)")
    args = parser.parse_args()

    result = scan_path(args.path)
    if args.run_id:
        import subprocess as _sp
        _rev = "UNAVAILABLE"
        try:
            _r = _sp.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=REPO_ROOT, timeout=10)
            if _r.returncode == 0:
                _rev = _r.stdout.strip()
        except Exception:
            pass
        result["metadata"] = {
            "run_id": args.run_id,
            "source_revision": _rev,
            "generated_at": __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc).isoformat(),
        }
    if args.output:
        output = args.output if args.output.is_absolute() else REPO_ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"output": _rel(output), "material_finding_count": result["material_finding_count"]}, sort_keys=True))
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if result["material_finding_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
