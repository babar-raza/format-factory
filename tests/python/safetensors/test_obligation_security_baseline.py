"""product-goal.yaml's own "security" completion invariant -- a whole-package
static proof that nothing in this package can reach a networking,
process-spawning, or attacker-influenced dynamic-import capability.

Unlike nrrd/xliff/ubl/ipynb, safetensors' own obligation register has no
dedicated SEC-001 capability -- this file is the first security-baseline
sweep for this format, matching the identical whole-package-scan pattern
already proven for the other five this session.

safetensors' own one legitimate exception, individually verified below
rather than silently allow-listed: ``adapters/numpy.py`` and
``adapters/torch.py`` each call ``importlib.import_module(...)`` exactly
once, to lazily load an OPTIONAL dependency (numpy/torch) only when a
caller actually requests array/tensor interop, so the base package never
requires either installed -- the same lazy-optional-dependency pattern
already used and previously verified for xliff's own ``xmlschema`` extra
this session. Both call sites pass a fixed string literal ("numpy",
"torch"), never a caller-supplied or otherwise dynamic value, so there is
no path for an attacker-controlled module name to reach either call.
"""

from __future__ import annotations

import ast
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3] / "src" / "python" / "safetensors" / "src"

_FULLY_FORBIDDEN_MODULES = frozenset(
    {"socket", "urllib", "http", "ftplib", "smtplib", "subprocess", "pkgutil", "ctypes"}
)

#: (file suffix, expected fixed-literal argument) for each legitimate
#: importlib.import_module call site.
_ALLOWED_DYNAMIC_IMPORTS = {
    "adapters/numpy.py": "numpy",
    "adapters/torch.py": "torch",
}


def _iter_source_files() -> list[Path]:
    return sorted(_SRC_ROOT.rglob("*.py"))


def _import_names(node: ast.stmt) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name.split(".")[0] for alias in node.names]
    if isinstance(node, ast.ImportFrom) and node.module:
        return [node.module.split(".")[0]]
    return []


def test_fully_forbidden_modules_are_never_imported_anywhere() -> None:
    """No legitimate use case exists anywhere in this package for any of
    these -- unlike importlib, which has exactly two narrow, individually
    verified legitimate uses checked by the dedicated test below."""
    offenders: list[str] = []
    for path in _iter_source_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            for name in _import_names(node):
                if name in _FULLY_FORBIDDEN_MODULES:
                    offenders.append(f"{path}: {name}")

    assert offenders == []


def test_no_eval_or_exec_call_exists_anywhere() -> None:
    offenders: list[str] = []
    for path in _iter_source_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ("eval", "exec", "compile"):
                    offenders.append(f"{path}: {node.func.id}(...)")

    assert offenders == []


def test_no_dynamic_import_call_exists_outside_the_two_allowed_optional_dependency_sites() -> (
    None
):
    offenders: list[str] = []
    for path in _iter_source_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        allowed_literal = next(
            (
                literal
                for suffix, literal in _ALLOWED_DYNAMIC_IMPORTS.items()
                if path.as_posix().endswith(suffix)
            ),
            None,
        )
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
                    if allowed_literal is None:
                        offenders.append(f"{path}: importlib.import_module(...) (unexpected site)")
                    elif not (
                        len(node.args) == 1
                        and isinstance(node.args[0], ast.Constant)
                        and node.args[0].value == allowed_literal
                    ):
                        offenders.append(
                            f"{path}: importlib.import_module(...) does not pass the "
                            f"expected fixed literal {allowed_literal!r}"
                        )

    assert offenders == []


def test_every_allowed_dynamic_import_site_still_exists_and_is_checked() -> None:
    """Guards against the allow-list silently going stale (e.g. a file
    rename) and the check above passing vacuously because nothing matched
    its suffix anymore."""
    existing = {path.as_posix() for path in _iter_source_files()}
    for suffix in _ALLOWED_DYNAMIC_IMPORTS:
        assert any(path.endswith(suffix) for path in existing), (
            f"expected {suffix} to still exist; update _ALLOWED_DYNAMIC_IMPORTS "
            "if it was intentionally renamed or removed"
        )
