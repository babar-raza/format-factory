"""Root conftest.py -- auto-assigns test layer markers.

Layers (cumulative when used with the runner):
  layer0: Structural - health check, import smoke
  layer1: Focused - single-format unit tests
  layer2: Family - related format group tests (unused as marker; runner scopes via paths)
  layer3: Integration - supervisor, governance, evidence
  layer4: Golden - roundtrip, cross-format, export
  layer5: Broad - packaging, skills, ai, playbook, etc.
  layer6: Full - entire test suite (all tests get this)

Each test receives exactly ONE "home" layer marker (layer0-layer5) plus layer6.
The runner constructs cumulative expressions like ``-m "layer0 or layer1"`` for layer 1.
Bare ``pytest`` (no -m flag) runs everything as before.

Flags:
  --skip-arithmetic  Skip tests listed in registry/arithmetic-deepening-tests.txt.
                     These are generated arithmetic-formula tests with no spec backing.
                     Use for routine development runs. Full suite still includes them.
"""
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_ARITHMETIC_MANIFEST = _REPO_ROOT / "registry" / "arithmetic-deepening-tests.txt"


def _load_arithmetic_manifest() -> frozenset[str]:
    """Load the set of arithmetic-deepening test file paths (relative, POSIX-style)."""
    if not _ARITHMETIC_MANIFEST.exists():
        return frozenset()
    lines = _ARITHMETIC_MANIFEST.read_text(encoding="utf-8").splitlines()
    return frozenset(line.strip() for line in lines if line.strip())


@pytest.fixture(autouse=True, scope="module")
def _restore_sys_path():
    """Restore sys.path after each test module to prevent import pollution.

    Snapshots sys.path at the START of each module's tests (after the module's
    own sys.path.insert calls) and restores it after the module completes.
    This prevents one module's path additions from leaking into later modules.
    """
    snapshot = list(sys.path)
    yield
    sys.path[:] = snapshot

_LAYER_MARKERS = [f"layer{i}" for i in range(7)]

# Keywords that identify golden/roundtrip/export tests (layer4)
_GOLDEN_KEYWORDS = ("roundtrip", "cross_format", "cross-format", "dogfood")


def pytest_addoption(parser):
    """Register --no-state, --no-network, and --skip-arithmetic flags."""
    parser.addoption("--no-state", action="store_true", default=False,
                     help="Skip tests marked @pytest.mark.state_dependent")
    parser.addoption("--no-network", action="store_true", default=False,
                     help="Skip tests marked @pytest.mark.network")
    parser.addoption(
        "--skip-arithmetic", action="store_true", default=False,
        help=(
            "Skip arithmetic-formula deepening tests (registry/arithmetic-deepening-tests.txt). "
            "These have no spec backing. Use for faster routine runs. "
            "Full suite (layer6) always includes them."
        ),
    )


def pytest_configure(config):
    """Register layer markers (belt-and-suspenders with pyproject.toml)."""
    for i in range(7):
        config.addinivalue_line("markers", f"layer{i}: Test layer {i}")
    config.addinivalue_line("markers", "state_dependent: Test reads live repo state files")
    config.addinivalue_line("markers", "network: Test makes real network calls")
    config.addinivalue_line(
        "markers",
        "arithmetic_deepening: Arithmetic-formula deepening test with no spec backing (generated, suspended)",
    )


def pytest_collection_modifyitems(config, items):
    """Assign exactly one home-layer marker to each collected test."""
    # Apply --no-state / --no-network skip markers
    skip_state = config.getoption("--no-state", default=False)
    skip_network = config.getoption("--no-network", default=False)
    if skip_state:
        skip_marker = pytest.mark.skip(reason="--no-state flag: skipping state_dependent tests")
        for item in items:
            if "state_dependent" in item.keywords:
                item.add_marker(skip_marker)
    if skip_network:
        skip_marker = pytest.mark.skip(reason="--no-network flag: skipping network tests")
        for item in items:
            if "network" in item.keywords:
                item.add_marker(skip_marker)

    # Apply --skip-arithmetic: skip tests whose file is in the arithmetic manifest
    if config.getoption("--skip-arithmetic", default=False):
        arith_files = _load_arithmetic_manifest()
        if arith_files:
            skip_arith = pytest.mark.skip(
                reason=(
                    "--skip-arithmetic: arithmetic-formula test with no spec backing. "
                    "Run without --skip-arithmetic or use layer6 to include these."
                )
            )
            for item in items:
                rel = str(Path(item.fspath).relative_to(_REPO_ROOT)).replace("\\", "/")
                if rel in arith_files:
                    item.add_marker(skip_arith)

    for item in items:
        fspath = str(item.fspath).replace("\\", "/")
        name = item.name.lower()

        # Determine home layer based on file path and test name
        if "test_health_check" in fspath or "public_api_smoke" in fspath:
            home = 0
        elif any(kw in fspath.lower() or kw in name for kw in _GOLDEN_KEYWORDS):
            home = 4
        elif "/tests/python/" in fspath:
            home = 1
        elif (
            "/tests/supervisor/" in fspath
            or "/tests/evidence/" in fspath
            or "/tests/capability_layer/" in fspath
        ):
            home = 3
        else:
            # packaging, skills, ai, playbook, governance, state, etc.
            home = 5

        # Assign home layer marker
        item.add_marker(getattr(pytest.mark, f"layer{home}"))
        # Every test is also in the full suite (layer6)
        item.add_marker(pytest.mark.layer6)
