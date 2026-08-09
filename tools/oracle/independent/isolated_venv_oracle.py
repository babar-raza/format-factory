"""Generic subprocess bridge into an isolated, collision-avoiding oracle venv.

Shared by any format whose own top-level package name collides with its
reference implementation's import name -- currently nrrd/pynrrd
(`setup_nrrd_pynrrd_venv.py`, `nrrd_pynrrd_probe.py`); safetensors's own
`reference` extra (`safetensors==0.8.0`) has the identical shape of
problem against this repository's own top-level `safetensors` package
and can reuse this same helper once its own isolated venv and probe
script are built the same way.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any


def run_probe(
    venv_python: Path, probe_script: Path, *args: str, timeout: float = 30.0
) -> dict[str, Any]:
    """Run `probe_script` inside `venv_python`, isolated from this
    process's own site-packages and `PYTHONPATH`, and return its parsed
    JSON stdout.

    Raises `FileNotFoundError` if `venv_python` does not exist --
    callers should check `venv_python.exists()` first (or catch this)
    and skip gracefully, matching this suite's existing
    SKIPPED_MISSING_PROVIDER pattern for optional external tooling
    (e.g. `execute_oracle.py::execute_fods_libreoffice_case`'s own
    `shutil.which("soffice")` check).
    """
    if not venv_python.exists():
        raise FileNotFoundError(f"isolated oracle venv not built: {venv_python}")
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    proc = subprocess.run(
        [str(venv_python), str(probe_script), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
        cwd=str(probe_script.parent),
    )
    if proc.returncode != 0:
        raise RuntimeError(f"probe exited {proc.returncode}: {proc.stderr[-500:]}")
    parsed: dict[str, Any] = json.loads(proc.stdout)
    return parsed
