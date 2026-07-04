"""conftest.py for tests/supervisor — canonical import path for supervisor modules."""
import os
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
_SUPERVISOR = _REPO / "tools" / "supervisor"

if str(_SUPERVISOR) not in sys.path:
    sys.path.insert(0, str(_SUPERVISOR))
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


@pytest.fixture(autouse=True)
def _cap_grader_timeout(monkeypatch):
    """Cap the LLM grader timeout to 8 s for all supervisor tests.

    Prevents a live endpoint hang (SSL read stall) from blocking the test
    suite for 30+ seconds. Tests that need a longer timeout can override
    GRADER_LLM_TIMEOUT explicitly. Tests that mock the LLM are unaffected
    (the env var is only read by the real gateway path).
    """
    if not os.environ.get("GRADER_LLM_TIMEOUT"):
        monkeypatch.setenv("GRADER_LLM_TIMEOUT", "8")
