"""Shared fixtures for oracle negative control tests (TC-W5-002)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture
def minimal_pkg() -> dict:
    """Minimal oracle package dict sufficient for executor calls."""
    return {
        "oracle_id": "oracle-test-v1",
        "oracle_version": 1,
        "format_id": "csv",
        "format_version": "RFC 4180",
    }


@pytest.fixture
def real_csv_sample() -> Path:
    """Return the path to a known-good CSV sample file."""
    path = REPO_ROOT / "samples" / "by-format" / "csv" / "minimal-2x2.csv"
    if not path.exists():
        pytest.skip(f"CSV sample not found: {path}")
    return path
