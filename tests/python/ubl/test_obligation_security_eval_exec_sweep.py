"""product-goal.yaml's own "security" completion invariant -- the one check
test_obligation_security_baseline.py's own comprehensive UBL-SEC-001 sweep
does not already provide.

That file's own test_no_source_file_imports_networking_execution_or_plugin_modules
already blocks a broad forbidden-module set (socket, urllib, http, ftplib,
smtplib, subprocess, importlib, pkgutil, ctypes) -- importlib being fully
forbidden already rules out importlib.import_module. What it does not check
is the builtin eval/exec/compile/__import__ call surface, which import-based
scanning cannot see. Added here rather than editing that file, to avoid
disturbing an existing, passing UBL-SEC-001 obligation proof -- the same
pattern already applied to nrrd's own equivalent gap this session.
"""

from __future__ import annotations

import ast
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3] / "src" / "python" / "ubl" / "src"


def test_no_eval_or_exec_call_exists_anywhere() -> None:
    """No call site anywhere in the package's source even names
    eval/exec/compile as a callable."""
    offenders: list[str] = []
    for path in sorted(_SRC_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ("eval", "exec", "compile"):
                    offenders.append(f"{path}: {node.func.id}(...)")

    assert offenders == []


def test_no_dunder_import_call_exists_anywhere() -> None:
    """__import__ is a builtin, not an import statement, so the sibling
    forbidden-module sweep (which blocks `import importlib` entirely)
    cannot see a direct __import__(...) call."""
    offenders: list[str] = []
    for path in sorted(_SRC_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "__import__"
            ):
                offenders.append(f"{path}: __import__(...)")

    assert offenders == []
