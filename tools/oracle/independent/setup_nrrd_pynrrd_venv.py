"""Build (or rebuild) the isolated pynrrd oracle venv.

Why an isolated venv: this project's own `format-factory-nrrd`
distribution and the real `pynrrd` reference implementation both use the
top-level import name `nrrd` (see this package's own `reference` extra,
`pynrrd==1.1.3`, in src/python/nrrd/pyproject.toml). Installing pynrrd
into the main project venv would shadow this repository's own legacy
top-level `nrrd` compatibility package (src/python/nrrd/__init__.py),
still imported directly by several legacy test files
(tests/python/nrrd/test_nrrd_*.py). A dedicated venv with ONLY pynrrd
installed sidesteps the collision entirely: it never sees this
project's own site-packages or PYTHONPATH (nrrd_pynrrd_probe.py, the
script this venv runs, is invoked with PYTHONPATH stripped -- see
`tools/oracle/independent/isolated_venv_oracle.py::run_probe`).

The venv itself is never committed (`.local/` is gitignored) -- this
script is the reproducible, committed mechanism any future session or
CI machine uses to (re)build it locally, on demand.

Usage: python tools/oracle/independent/setup_nrrd_pynrrd_venv.py
Idempotent: safe to re-run, recreates the venv if it already exists.
"""

from __future__ import annotations

import re
import subprocess
import sys
import venv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
VENV_DIR = REPO_ROOT / ".local" / "oracle" / "nrrd" / "pynrrd-venv"
PYPROJECT = REPO_ROOT / "src" / "python" / "nrrd" / "pyproject.toml"

#: Matches `reference = ["pynrrd==1.1.3"]` in the nrrd package's own
#: pyproject.toml, so this venv's pin can never silently drift from the
#: version the product itself declares as its reference implementation.
_REFERENCE_EXTRA_PATTERN = re.compile(r'reference\s*=\s*\[\s*"([^"]+)"\s*\]')


def pinned_pynrrd_requirement() -> str:
    text = PYPROJECT.read_text(encoding="utf-8")
    match = _REFERENCE_EXTRA_PATTERN.search(text)
    if match is None:
        raise RuntimeError(f"could not find the `reference` extra pin in {PYPROJECT}")
    return match.group(1)


def venv_python(venv_dir: Path = VENV_DIR) -> Path:
    return venv_dir / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")


def build() -> Path:
    requirement = pinned_pynrrd_requirement()
    venv.EnvBuilder(with_pip=True, clear=True).create(VENV_DIR)
    python = venv_python()
    subprocess.run([str(python), "-m", "pip", "install", "--quiet", requirement], check=True)
    return python


if __name__ == "__main__":
    built_python = build()
    print(f"pynrrd oracle venv ready: {built_python}")
