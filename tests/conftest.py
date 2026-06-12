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
"""
import pytest

_LAYER_MARKERS = [f"layer{i}" for i in range(7)]

# Keywords that identify golden/roundtrip/export tests (layer4)
_GOLDEN_KEYWORDS = ("roundtrip", "cross_format", "cross-format", "dogfood")


def pytest_configure(config):
    """Register layer markers (belt-and-suspenders with pyproject.toml)."""
    for i in range(7):
        config.addinivalue_line("markers", f"layer{i}: Test layer {i}")


def pytest_collection_modifyitems(config, items):
    """Assign exactly one home-layer marker to each collected test."""
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
