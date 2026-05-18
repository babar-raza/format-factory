# tests/python/test_cross_format_api_consistency.py
# R23 Gate 5 — Cross-package Python FOSS API consistency tests
# Sprint: FORMAT-FACTORY-R23-MEGA-TRAIN-001
# publication_authorized: false
#
# These tests ensure all five Python FOSS packages expose a consistent
# public API surface. They import from src/python/ directly (conftest.py adds it).

import importlib
import pytest

MODULES = ["zst", "fodp", "fodg", "gnumeric", "abw"]

REQUIRED_STRING_ATTRS = [
    "__version__",
    "__track__",
]

REQUIRED_ATTRS = [
    "__version__",
    "__track__",
    "__commercial_ready__",
    "__capability_level__",
]


@pytest.mark.parametrize("mod", MODULES)
def test_module_has_all_required_attrs(mod):
    """Each module must expose all required public API attributes."""
    m = importlib.import_module(mod)
    for attr in REQUIRED_ATTRS:
        assert hasattr(m, attr), f"{mod}.{attr} is missing (required API)"


@pytest.mark.parametrize("mod", MODULES)
def test_module_version_is_string(mod):
    """__version__ must be a string in all modules."""
    m = importlib.import_module(mod)
    assert isinstance(m.__version__, str), (
        f"{mod}.__version__ must be str, got {type(m.__version__)}"
    )


@pytest.mark.parametrize("mod", MODULES)
def test_module_track_is_string(mod):
    """__track__ must be a string in all modules."""
    m = importlib.import_module(mod)
    assert isinstance(m.__track__, str), (
        f"{mod}.__track__ must be str, got {type(m.__track__)}"
    )


@pytest.mark.parametrize("mod", MODULES)
def test_module_track_is_foss(mod):
    """__track__ must be 'foss' in all Python FOSS packages."""
    m = importlib.import_module(mod)
    assert m.__track__ == "python-foss", (
        f"{mod}.__track__ must be 'python-foss', got {m.__track__!r}"
    )


@pytest.mark.parametrize("mod", MODULES)
def test_module_commercial_ready_is_false(mod):
    """__commercial_ready__ must be False in all Python FOSS packages."""
    m = importlib.import_module(mod)
    assert m.__commercial_ready__ is False, (
        f"{mod}.__commercial_ready__ must be False (alpha-foss-preview state), "
        f"got {m.__commercial_ready__!r}"
    )


@pytest.mark.parametrize("mod", MODULES)
def test_module_capability_level_not_none(mod):
    """__capability_level__ must not be None."""
    m = importlib.import_module(mod)
    assert m.__capability_level__ is not None, (
        f"{mod}.__capability_level__ must not be None"
    )


@pytest.mark.parametrize("mod", MODULES)
def test_module_capability_level_is_alpha_foss_preview(mod):
    """__capability_level__ must be 'alpha-foss-preview' per R22 API normalization."""
    m = importlib.import_module(mod)
    assert m.__capability_level__ == "alpha-foss-preview", (
        f"{mod}.__capability_level__ must be 'alpha-foss-preview' (R22 baseline), "
        f"got {m.__capability_level__!r}"
    )


@pytest.mark.parametrize("mod", MODULES)
def test_module_version_format(mod):
    """__version__ must follow semver or dev format (e.g. '0.1.0.dev0')."""
    m = importlib.import_module(mod)
    version = m.__version__
    # Must contain at least one dot
    assert "." in version, (
        f"{mod}.__version__ {version!r} does not look like a version string"
    )


def test_all_modules_same_version():
    """All Python FOSS modules must have the same __version__ (consistency check)."""
    versions = set()
    for mod_name in MODULES:
        m = importlib.import_module(mod_name)
        versions.add(m.__version__)
    assert len(versions) == 1, (
        f"All modules must have the same version, got: {versions}"
    )


def test_all_modules_same_track():
    """All Python FOSS modules must have the same __track__."""
    tracks = set()
    for mod_name in MODULES:
        m = importlib.import_module(mod_name)
        tracks.add(m.__track__)
    assert len(tracks) == 1, (
        f"All modules must have the same track, got: {tracks}"
    )


def test_all_modules_same_capability_level():
    """All Python FOSS modules must have the same __capability_level__."""
    levels = set()
    for mod_name in MODULES:
        m = importlib.import_module(mod_name)
        levels.add(str(m.__capability_level__))
    assert len(levels) == 1, (
        f"All modules must have the same capability_level, got: {levels}"
    )
