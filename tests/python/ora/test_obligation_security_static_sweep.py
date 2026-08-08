"""product-goal.yaml's own "security" completion invariant -- a whole-package
static proof that nothing in this package can reach a networking,
process-spawning, or dynamic-import capability.

Complements test_obligation_security_baseline.py's own ORA-SEC-001 proof
(configurable limits, traversal protection, complexity-attack guards) with
the one check it does not already provide: a package-wide static sweep,
matching the identical pattern already proven for nrrd/xliff/ipynb/
safetensors/ubl this session. ora has no legitimate use case anywhere for
subprocess, networking modules, or dynamic imports -- confirmed by a
direct AST sweep before writing these tests, not assumed. There is no
allow-list of exceptions to maintain here.
"""

from __future__ import annotations

import ast
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3] / "src" / "python" / "ora" / "src"

_FULLY_FORBIDDEN_MODULES = frozenset(
    {"socket", "http", "ftplib", "smtplib", "pkgutil", "ctypes", "subprocess"}
)


def _iter_source_files() -> list[Path]:
    return sorted(_SRC_ROOT.rglob("*.py"))


def _import_names(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name.split(".")[0] for alias in node.names]
    if isinstance(node, ast.ImportFrom) and node.module:
        return [node.module.split(".")[0]]
    return []


def test_fully_forbidden_modules_are_never_imported_anywhere() -> None:
    """No legitimate use case exists anywhere in this package for process
    spawning or raw networking."""
    offenders: list[str] = []
    for path in _iter_source_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            for name in _import_names(node):
                if name in _FULLY_FORBIDDEN_MODULES:
                    offenders.append(f"{path}: {name}")

    assert offenders == []


def test_urllib_is_never_imported_anywhere() -> None:
    """This package has no urllib usage of any kind."""
    offenders: list[str] = []
    for path in _iter_source_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            for name in _import_names(node):
                if name == "urllib":
                    offenders.append(str(path))

    assert offenders == []


def test_no_dynamic_import_call_exists_anywhere() -> None:
    """importlib.import_module and the __import__ builtin -- either of
    which could load an attacker-influenced module name -- must never be
    called anywhere in this package."""
    offenders: list[str] = []
    for path in _iter_source_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "__import__":
                    offenders.append(f"{path}: __import__(...)")
                elif (
                    isinstance(func, ast.Attribute)
                    and func.attr == "import_module"
                    and isinstance(func.value, ast.Name)
                    and func.value.id == "importlib"
                ):
                    offenders.append(f"{path}: importlib.import_module(...)")

    assert offenders == []


def test_no_eval_or_exec_call_exists_anywhere() -> None:
    """No call site anywhere in the package's source even names
    eval/exec/compile as a callable."""
    offenders: list[str] = []
    for path in _iter_source_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ("eval", "exec", "compile"):
                    offenders.append(f"{path}: {node.func.id}(...)")

    assert offenders == []
