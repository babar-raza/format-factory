"""Real package-install proof: wheel-installed packages import and their core API works.

This test is executed INSIDE the ephemeral proof venv created by
tools/run_package_install_proof.py — never against the repo source tree.
It proves the B9 oracle-to-package boundary (GAP-FORENSIC-001):
pip install <wheel> -> import <format> -> call the primary load/parse API
on the same sample corpus the oracle verified.

Contract with the orchestrator (all via environment variables):
  FF_PROOF_SPECS    path to a JSON file: {format_id: {module_import, smoke_module,
                    smoke_callable, smoke_sample_abs | smoke_inline_bytes,
                    expected, package_name}}
                    (serialized from packaging/python/package-matrix.yaml — the
                    single source of truth; this file hardcodes NO fleet list)
  FF_PROOF_FORMATS  comma-separated format_ids to prove in this run; others skip
  FF_REPO_ROOT      repo root (used only to assert modules do NOT come from src/)

Run it via `/package-install-proof` (the governed skill) or the orchestrator
directly. Running it under the project venv will fail the wheel-origin check
by design: editable .pth installs are not install proof.
"""
from __future__ import annotations

import importlib
import json
import os
import sys
import sysconfig
from pathlib import Path

import pytest


def _load_specs() -> dict:
    specs_path = os.environ.get("FF_PROOF_SPECS")
    if not specs_path or not Path(specs_path).exists():
        pytest.skip(
            "FF_PROOF_SPECS not set — run via tools/run_package_install_proof.py "
            "(or /package-install-proof)",
            allow_module_level=True,
        )
    return json.loads(Path(specs_path).read_text(encoding="utf-8"))


_SPECS = _load_specs()
_REQUESTED = {
    f for f in os.environ.get("FF_PROOF_FORMATS", "").split(",") if f
} or set(_SPECS)
_FORMATS = sorted(_SPECS)


def _skip_if_not_requested(fmt: str) -> None:
    if fmt not in _REQUESTED:
        pytest.skip(f"{fmt} not in FF_PROOF_FORMATS for this run")


@pytest.mark.parametrize("fmt", _FORMATS)
def test_wheel_import(fmt: str) -> None:
    """The top-level package imports and resolves to the installed wheel,
    not to the repo source tree (editable installs would be fake proof)."""
    _skip_if_not_requested(fmt)
    module_import = _SPECS[fmt]["module_import"]
    module = importlib.import_module(module_import)

    mod_file = getattr(module, "__file__", None)
    assert mod_file, f"{fmt} has no __file__ — cannot verify wheel origin"
    mod_path = Path(mod_file).resolve()

    site_packages = Path(sysconfig.get_paths()["purelib"]).resolve()
    assert site_packages in mod_path.parents, (
        f"{fmt} resolved to {mod_path}, not to site-packages {site_packages} — "
        "this is not a wheel install"
    )

    repo_root = os.environ.get("FF_REPO_ROOT")
    if repo_root:
        src_python = (Path(repo_root) / "src" / "python").resolve()
        assert src_python not in mod_path.parents, (
            f"{fmt} resolved into the repo source tree ({mod_path}) — "
            "editable/.pth shadowing detected; proof invalid"
        )


def test_csv_is_format_factory_not_stdlib() -> None:
    """The csv wheel intentionally shadows stdlib csv inside this ephemeral venv.
    Prove the import is Format Factory's package: stdlib csv has no csv_parser."""
    _skip_if_not_requested("csv")
    csv_parser = importlib.import_module("csv.csv_parser")
    assert hasattr(csv_parser, "parse_csv_strict")


_EXPECTED_CHECKS = {
    "dict": lambda v: isinstance(v, dict),
    "list": lambda v: isinstance(v, list),
    "bytes": lambda v: isinstance(v, (bytes, bytearray)),
    "object": lambda v: v is not None,
}


@pytest.mark.parametrize("fmt", _FORMATS)
def test_api_smoke(fmt: str) -> None:
    """The primary load/parse API works on the oracle-verified sample corpus."""
    _skip_if_not_requested(fmt)
    spec = _SPECS[fmt]
    module = importlib.import_module(spec["smoke_module"])
    fn = getattr(module, spec["smoke_callable"], None)
    assert fn is not None, f"{spec['smoke_module']} has no {spec['smoke_callable']}"

    if "smoke_inline_bytes" in spec:
        result = fn(spec["smoke_inline_bytes"].encode("utf-8"))
    else:
        sample = Path(spec["smoke_sample_abs"])
        assert sample.exists(), f"sample missing: {sample}"
        result = fn(str(sample))

    expected = spec["expected"]
    check = _EXPECTED_CHECKS.get(expected)
    assert check is not None, f"unknown expected kind {expected!r} in matrix"
    assert check(result), (
        f"{fmt}: {spec['smoke_callable']} returned {type(result).__name__}, "
        f"matrix expects {expected}"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
