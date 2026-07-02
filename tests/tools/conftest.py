"""Shared fixtures for tools tests."""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "project_status"


@pytest.fixture
def fixture_repo(tmp_path):
    """Return a temp copy of the project_status fixture directory.

    Uses the fixtures/ directory directly (read-only) for most tests.
    Use this fixture when tests need to mutate the directory.
    """
    import shutil
    dest = tmp_path / "repo"
    shutil.copytree(str(FIXTURE_ROOT), str(dest))
    return dest


@pytest.fixture
def fixture_repo_ro():
    """Return the fixture repo root (read-only — do not mutate)."""
    return FIXTURE_ROOT
