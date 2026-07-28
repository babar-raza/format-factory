"""Regression tests for governed exception and analytics backfill tools."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tools.backfill.analytics_wiring_backfill import WiringError
from tools.backfill.analytics_wiring_backfill import run as wire_analytics
from tools.backfill.exception_hierarchy_backfill import RepairError
from tools.backfill.exception_hierarchy_backfill import run as repair_exceptions


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _canonical(package: Path) -> None:
    _write(
        package / "exceptions.py",
        "from format_factory.core import FormatFactoryError\n\n"
        "class DemoError(FormatFactoryError):\n"
        "    pass\n\n"
        "class DemoParseError(DemoError):\n"
        "    pass\n",
    )


def test_exception_repair_is_dry_run_by_default_and_idempotent(tmp_path: Path) -> None:
    package = tmp_path / "demo"
    _canonical(package)
    shadow = package / "codec.py"
    _write(
        shadow,
        '"""codec"""\n'
        "from __future__ import annotations\n\n"
        "class DemoParseError(DemoError):\n"
        "    pass\n\n"
        "def parse():\n"
        "    raise DemoParseError()\n",
    )

    plan = repair_exceptions(package)
    assert plan["changed_files"] == ["codec.py"]
    assert "class DemoParseError" in shadow.read_text(encoding="utf-8")

    applied = repair_exceptions(package, apply=True)
    assert applied["changed_files"] == ["codec.py"]
    repaired = shadow.read_text(encoding="utf-8")
    assert "from .exceptions import DemoParseError" in repaired
    assert "class DemoParseError" not in repaired
    ast.parse(repaired)
    assert repair_exceptions(package)["changed_files"] == []


def test_exception_repair_uses_nested_relative_import(tmp_path: Path) -> None:
    package = tmp_path / "demo"
    _canonical(package)
    nested = package / "reader" / "codec.py"
    _write(nested, "class DemoError(Exception):\n    pass\n")
    repair_exceptions(package, apply=True)
    assert "from ..exceptions import DemoError" in nested.read_text(encoding="utf-8")


def test_exception_repair_fails_closed_on_invalid_canonical_root(tmp_path: Path) -> None:
    package = tmp_path / "demo"
    _write(package / "exceptions.py", "class DemoError(Exception):\n    pass\n")
    with pytest.raises(RepairError, match="FormatFactoryError"):
        repair_exceptions(package)


def test_exception_repair_fails_closed_on_decorated_duplicate(tmp_path: Path) -> None:
    package = tmp_path / "demo"
    _canonical(package)
    _write(
        package / "codec.py",
        "@decorate\nclass DemoError(Exception):\n    pass\n",
    )
    with pytest.raises(RepairError, match="decorated"):
        repair_exceptions(package, apply=True)


def test_analytics_wiring_uses_literal_all_and_is_idempotent(tmp_path: Path) -> None:
    package = tmp_path / "demo"
    _write(
        package / "demo_analytics.py",
        "__all__ = ['z_score', 'summarize']\n\n"
        "def summarize():\n    return 1\n\n"
        "def z_score():\n    return 2\n\n"
        "def _internal():\n    return 3\n",
    )
    _write(package / "__init__.py", "__all__ = ('load',)\n")

    plan = wire_analytics(package)
    assert plan["exports"] == ["summarize", "z_score"]
    assert plan["change_required"] is True
    applied = wire_analytics(package, apply=True)
    assert applied["changed_files"] == ["__init__.py"]
    text = (package / "__init__.py").read_text(encoding="utf-8")
    assert "from .demo_analytics import summarize, z_score" in text
    assert "__all__ += ('summarize', 'z_score')" in text
    assert wire_analytics(package)["change_required"] is False


def test_analytics_wiring_infers_only_local_public_definitions(tmp_path: Path) -> None:
    package = tmp_path / "demo"
    _write(
        package / "analytics.py",
        "from elsewhere import imported\n\n"
        "class Report:\n    pass\n\n"
        "def summarize():\n    return imported\n",
    )
    result = wire_analytics(package, apply=True)
    assert result["exports"] == ["Report", "summarize"]
    assert "imported" not in result["exports"]


def test_analytics_wiring_replaces_its_owned_block(tmp_path: Path) -> None:
    package = tmp_path / "demo"
    module = package / "analytics.py"
    _write(module, "def before():\n    pass\n")
    wire_analytics(package, apply=True)
    _write(module, "def after():\n    pass\n")
    wire_analytics(package, apply=True)
    text = (package / "__init__.py").read_text(encoding="utf-8")
    assert text.count("# BEGIN FORMAT FACTORY ANALYTICS EXPORTS") == 1
    assert "from .analytics import after" in text
    assert "before" not in text


def test_analytics_wiring_rejects_ambiguous_modules(tmp_path: Path) -> None:
    package = tmp_path / "demo"
    _write(package / "analytics.py", "def a():\n    pass\n")
    _write(package / "demo_analytics.py", "def b():\n    pass\n")
    with pytest.raises(WiringError, match="exactly one"):
        wire_analytics(package)
