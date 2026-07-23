"""Packaging boundary tests for format-factory-core.

visibility: generated
generated_by: codex
"""

from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "src" / "python" / "core"


def test_namespace_parent_has_no_init() -> None:
    assert not (PACKAGE / "src" / "format_factory" / "__init__.py").exists()


def test_core_has_no_format_or_agent_dependencies() -> None:
    forbidden = ("tools.", "supervisor", "governance", "importlib.metadata.entry_points")
    for path in (PACKAGE / "src" / "format_factory" / "core").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            assert marker not in text, (path, marker)


def test_core_exports_only_approved_responsibilities() -> None:
    modules = {
        path.stem
        for path in (PACKAGE / "src" / "format_factory" / "core").glob("*.py")
    }
    assert modules == {"__init__", "diagnostics", "errors", "limits", "protocols"}


def test_build_backend_is_exactly_pinned_and_hash_locked() -> None:
    project = tomllib.loads((PACKAGE / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["build-system"]["requires"] == ["setuptools==80.9.0"]
    lock = (PACKAGE / "requirements-build.lock").read_text(encoding="utf-8")
    assert "setuptools==80.9.0" in lock
    assert "--hash=sha256:" in lock
