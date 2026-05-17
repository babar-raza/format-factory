# tests/packaging/test_python_local_package_imports.py
# R22 Gate 4 — Smoke import tests for Python FOSS packages (src/python direct import)
# Sprint: FORMAT-FACTORY-R22-FULL-THROTTLE-RELEASE-CANDIDATE-AND-GATE11-PROTOTYPE-TRAIN-001
# publication_authorized: false
#
# These tests import the package source directly from src/python/ (no pip install required).
# This validates that each module is importable and exposes the expected public API.

import os
import sys
import pytest

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_PYTHON = os.path.join(REPO_ROOT, "src", "python")

# Ensure src/python is on the path
if SRC_PYTHON not in sys.path:
    sys.path.insert(0, SRC_PYTHON)

MODULES = ["zst", "fodp", "fodg", "gnumeric", "abw"]


@pytest.mark.parametrize("mod", MODULES)
def test_module_importable(mod):
    """Each Python FOSS module must be importable."""
    import importlib
    m = importlib.import_module(mod)
    assert m is not None, f"Module {mod!r} could not be imported"


@pytest.mark.parametrize("mod", MODULES)
def test_module_has_capability_level(mod):
    """Each module must expose __capability_level__ (API normalization gate)."""
    import importlib
    m = importlib.import_module(mod)
    assert hasattr(m, "__capability_level__"), \
        f"{mod}.__capability_level__ is missing (G1 API normalization requirement)"
    # __capability_level__ may be an int or a string label (e.g. 'alpha-foss-preview')
    assert m.__capability_level__ is not None, \
        f"{mod}.__capability_level__ must not be None"


@pytest.mark.parametrize("mod", MODULES)
def test_module_has_version(mod):
    """Each module must expose __version__."""
    import importlib
    m = importlib.import_module(mod)
    assert hasattr(m, "__version__"), f"{mod}.__version__ is missing"
    assert isinstance(m.__version__, str), f"{mod}.__version__ must be a str"


@pytest.mark.parametrize("mod", MODULES)
def test_module_capability_level_is_set(mod):
    """__capability_level__ must be set (non-empty string or non-negative int)."""
    import importlib
    m = importlib.import_module(mod)
    level = m.__capability_level__
    if isinstance(level, int):
        assert level >= 0, f"{mod}.__capability_level__ int must be >= 0"
    else:
        assert str(level).strip(), f"{mod}.__capability_level__ string must not be empty"
