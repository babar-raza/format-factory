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
    """Cap the LLM grader timeout and disable LLM prompt-rewriting for all supervisor tests.

    Two guards:
    1. GRADER_LLM_TIMEOUT=8: caps gateway wall-clock deadline to 10 s (8 + 2 grace).
       Prevents an SSL read stall from blocking the test suite. Tests that need a longer
       timeout can override GRADER_LLM_TIMEOUT explicitly.
    2. LLM_REWRITE_DISABLED=1: disables rewrite_prompt_with_context() immediately,
       skipping the litellm import (~6 s cold-start) and live network call. Unit tests
       that verify prompt structure don't need LLM enhancement. Integration tests that
       need LLM rewriting should unset this env var explicitly.
    """
    if not os.environ.get("GRADER_LLM_TIMEOUT"):
        monkeypatch.setenv("GRADER_LLM_TIMEOUT", "8")
    if not os.environ.get("LLM_REWRITE_DISABLED"):
        monkeypatch.setenv("LLM_REWRITE_DISABLED", "1")
