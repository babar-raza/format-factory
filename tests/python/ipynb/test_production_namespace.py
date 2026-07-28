"""Characterization and package-chassis checks for the production namespace."""

from __future__ import annotations

import importlib.metadata
import importlib.util
import json
from pathlib import Path

import pytest

from format_factory.ipynb import (
    IpynbDocument,
    dump,
    dumps,
    load,
    loads,
    probe,
    upgrade,
    validate,
)

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "src" / "python" / "ipynb"
SAMPLE = ROOT / "samples" / "by-format" / "ipynb" / "valid" / "minimal.ipynb"


def test_implicit_namespace_has_no_parent_init() -> None:
    assert not (PACKAGE / "src" / "format_factory" / "__init__.py").exists()
    spec = importlib.util.find_spec("format_factory.ipynb")
    assert spec is not None
    assert spec.origin is not None
    source_root = str((PACKAGE / "src").resolve())
    distributions = [
        distribution
        for distribution in importlib.metadata.distributions()
        if distribution.metadata.get("Name", "").lower()
        == "format-factory-ipynb"
    ]
    installed_roots = [
        str(Path(distribution.locate_file("")).resolve())
        for distribution in distributions
        if source_root not in str(Path(distribution.locate_file("")).resolve())
    ]
    resolved_origin = str(Path(spec.origin).resolve())
    if not installed_roots:
        assert source_root in str(Path(spec.origin).resolve())
    else:
        assert any(root in resolved_origin for root in installed_roots)
        assert source_root not in resolved_origin


def test_common_lifecycle_and_unknown_member_preservation(tmp_path: Path) -> None:
    source = json.dumps(
        {
            "nbformat": 4,
            "nbformat_minor": 6,
            "metadata": {"vendor": {"enabled": True}},
            "cells": [
                {
                    "cell_type": "markdown",
                    "id": "known-id",
                    "metadata": {},
                    "source": "# title",
                    "vendor_cell": {"retained": 1},
                }
            ],
            "vendor_root": ["retained"],
        }
    )
    result = probe(source)
    assert result.matched
    assert result.profile == "nbformat-4.6"

    document = loads(source, mode="preservation")
    assert isinstance(document, IpynbDocument)
    assert validate(document).is_valid
    assert document.raw["vendor_root"] == ["retained"]
    assert document.cells[0]["vendor_cell"] == {"retained": 1}

    destination = tmp_path / "roundtrip.ipynb"
    dump(document, destination, profile="declared")
    reloaded = load(destination, mode="preservation")
    assert reloaded.raw["vendor_root"] == ["retained"]
    assert reloaded.cells[0]["vendor_cell"] == {"retained": 1}


def test_deterministic_cell_ids_are_created_only_by_explicit_upgrade() -> None:
    source = json.dumps(
        {
            "nbformat": 4,
            "nbformat_minor": 4,
            "metadata": {},
            "cells": [{"cell_type": "markdown", "metadata": {}, "source": "same"}],
        }
    )
    first = load(source).raw
    second = load(source).raw
    assert "id" not in first["cells"][0]
    assert "id" not in second["cells"][0]

    first_upgrade = upgrade(first).document
    second_upgrade = upgrade(second).document
    assert first_upgrade.cells[0]["id"] == second_upgrade.cells[0]["id"]
    assert dumps(first_upgrade) == dumps(second_upgrade)


def test_default_writer_emits_45_and_rejects_nonfinite_json() -> None:
    document = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {},
        "cells": [
            {
                "cell_type": "code",
                "id": "nan-cell",
                "metadata": {},
                "source": "",
                "outputs": [],
                "execution_count": None,
            }
        ],
    }
    document["metadata"]["nonfinite"] = float("nan")
    with pytest.raises(Exception, match="serialize"):
        dumps(document)

    document["metadata"].pop("nonfinite")
    serialized = json.loads(dumps(document))
    assert (serialized["nbformat"], serialized["nbformat_minor"]) == (4, 5)
    assert serialized["cells"][0]["id"] == "nan-cell"


def test_package_chassis_and_python_policy() -> None:
    package_root = PACKAGE / "src" / "format_factory" / "ipynb"
    for layer in (
        "model",
        "codec/reader",
        "codec/writer",
        "validation",
        "security",
        "adapters",
        "analytics",
        "cli",
    ):
        assert (package_root / layer).is_dir()
    assert (package_root / "py.typed").is_file()

    pyproject = (PACKAGE / "pyproject.toml").read_text(encoding="utf-8")
    assert 'requires-python = ">=3.11"' in pyproject
    assert 'include = ["format_factory.ipynb*"]' in pyproject
    assert 'build-backend = "_build_backend"' in pyproject
    assert 'backend-path = ["."]' in pyproject
    assert (PACKAGE / "_build_backend.py").is_file()
    assert (PACKAGE / "MANIFEST.in").is_file()
    assert "Programming Language :: Python :: 3.9" not in pyproject
    assert "Programming Language :: Python :: 3.10" not in pyproject


def test_repository_fixture_is_loadable() -> None:
    document = load(SAMPLE, mode="preservation")
    assert document.nbformat == 4
    assert document.cell_count >= 0
