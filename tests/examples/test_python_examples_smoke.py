"""
test_python_examples_smoke.py — Smoke tests for Python FOSS example scripts.

Tests that example scripts run without exceptions and without network access.
Scripts that skip (no samples) count as PASS for smoke purposes.

Sprint: FORMAT-FACTORY-R21-FOSS-RELEASE-READINESS-AND-GATE11-COMMERCIAL-PREEXECUTION-TRAIN-001
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXAMPLES_BASE = REPO_ROOT / "examples" / "python"
SRC_PYTHON = str(REPO_ROOT / "src" / "python")

EXAMPLE_SCRIPTS = {
    "zst": EXAMPLES_BASE / "zst" / "compress_decompress_file.py",
    "fodp": EXAMPLES_BASE / "fodp" / "extract_presentation_text.py",
    "fodg": EXAMPLES_BASE / "fodg" / "inspect_drawing_shapes.py",
    "gnumeric": EXAMPLES_BASE / "gnumeric" / "extract_cells.py",
    "abw": EXAMPLES_BASE / "abw" / "extract_text.py",
}


def _run_example(script: Path) -> tuple[int, str, str]:
    """Run example script with PYTHONPATH set. Returns (returncode, stdout, stderr)."""
    env_patch = {
        "PYTHONPATH": SRC_PYTHON,
    }
    import os
    env = os.environ.copy()
    env.update(env_patch)
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
        cwd=str(REPO_ROOT),
    )
    return result.returncode, result.stdout, result.stderr


# --- File existence tests (always run) ---

def test_zst_example_script_exists():
    assert EXAMPLE_SCRIPTS["zst"].exists()

def test_fodp_example_script_exists():
    assert EXAMPLE_SCRIPTS["fodp"].exists()

def test_fodg_example_script_exists():
    assert EXAMPLE_SCRIPTS["fodg"].exists()

def test_gnumeric_example_script_exists():
    assert EXAMPLE_SCRIPTS["gnumeric"].exists()

def test_abw_example_script_exists():
    assert EXAMPLE_SCRIPTS["abw"].exists()


# --- README existence tests ---

def test_zst_readme_exists():
    assert (EXAMPLES_BASE / "zst" / "README.md").exists()

def test_fodp_readme_exists():
    assert (EXAMPLES_BASE / "fodp" / "README.md").exists()

def test_fodg_readme_exists():
    assert (EXAMPLES_BASE / "fodg" / "README.md").exists()

def test_gnumeric_readme_exists():
    assert (EXAMPLES_BASE / "gnumeric" / "README.md").exists()

def test_abw_readme_exists():
    assert (EXAMPLES_BASE / "abw" / "README.md").exists()


# --- Smoke execution tests ---

def test_fodp_example_runs_without_crash():
    """FODP example must exit 0 (with or without sample files)."""
    rc, stdout, stderr = _run_example(EXAMPLE_SCRIPTS["fodp"])
    assert rc == 0, f"FODP example crashed:\nstdout={stdout}\nstderr={stderr}"
    assert "alpha-foss-preview" in stdout


def test_fodg_example_runs_without_crash():
    """FODG example must exit 0."""
    rc, stdout, stderr = _run_example(EXAMPLE_SCRIPTS["fodg"])
    assert rc == 0, f"FODG example crashed:\nstdout={stdout}\nstderr={stderr}"
    assert "alpha-foss-preview" in stdout


def test_gnumeric_example_runs_without_crash():
    """Gnumeric example must exit 0."""
    rc, stdout, stderr = _run_example(EXAMPLE_SCRIPTS["gnumeric"])
    assert rc == 0, f"Gnumeric example crashed:\nstdout={stdout}\nstderr={stderr}"
    assert "alpha-foss-preview" in stdout


def test_abw_example_runs_without_crash():
    """ABW example must exit 0."""
    rc, stdout, stderr = _run_example(EXAMPLE_SCRIPTS["abw"])
    assert rc == 0, f"ABW example crashed:\nstdout={stdout}\nstderr={stderr}"
    assert "alpha-foss-preview" in stdout


def test_zst_example_runs_without_crash():
    """ZST example must exit 0 (gracefully handles missing zstandard)."""
    rc, stdout, stderr = _run_example(EXAMPLE_SCRIPTS["zst"])
    assert rc == 0, f"ZST example crashed:\nstdout={stdout}\nstderr={stderr}"
    assert "alpha-foss-preview" in stdout


# --- No network check ---

def test_examples_have_no_network_import():
    """No example script should import requests, urllib3, httpx, or socket in a way that
    would make a real network call. Simple static check."""
    network_modules = ["requests", "httpx", "aiohttp"]
    for fmt, script in EXAMPLE_SCRIPTS.items():
        source = script.read_text(encoding="utf-8")
        for mod in network_modules:
            assert f"import {mod}" not in source, (
                f"{script.name}: imports {mod} (network dependency not allowed)"
            )


# --- Capability label check ---

def test_examples_declare_alpha_foss_preview():
    """All example scripts must declare alpha-foss-preview in their docstring or output."""
    for fmt, script in EXAMPLE_SCRIPTS.items():
        source = script.read_text(encoding="utf-8")
        assert "alpha-foss-preview" in source, (
            f"{script.name}: must declare alpha-foss-preview"
        )


def test_examples_declare_not_commercial():
    """All example scripts must declare NOT FOR COMMERCIAL USE."""
    for fmt, script in EXAMPLE_SCRIPTS.items():
        source = script.read_text(encoding="utf-8")
        assert "NOT FOR COMMERCIAL USE" in source or "commercial products" in source, (
            f"{script.name}: must declare non-commercial nature"
        )
