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
    """core's module set is a governed boundary, not an accident.

    `arithmetic` was added under TC-FF6-SHARED-CHECKED-ARITHMETIC-001 after two
    independent product archetypes (NRRD, SafeTensors) were each found to
    hand-roll the same bounded multiply and to have already diverged on it
    (directive GAP-010). Extending this set is a deliberate act: anything added
    here must be machinery two formats have *proven* they repeat, not machinery
    one format might someday want.
    """
    modules = {
        path.stem
        for path in (PACKAGE / "src" / "format_factory" / "core").glob("*.py")
    }
    assert modules == {
        "__init__",
        "arithmetic",
        "diagnostics",
        "errors",
        "limits",
        "protocols",
    }


def test_build_backend_is_exactly_pinned_and_hash_locked() -> None:
    project = tomllib.loads((PACKAGE / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["build-system"]["requires"] == ["setuptools==80.9.0"]
    lock = (PACKAGE / "requirements-build.lock").read_text(encoding="utf-8")
    assert "setuptools==80.9.0" in lock
    assert "--hash=sha256:" in lock
