"""conftest.py for tests/ai — caps LLM timeout and wires network marker."""
import os
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
for _p in [str(_REPO), str(_REPO / "tools")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)


@pytest.fixture(autouse=True)
def _cap_grader_timeout(monkeypatch):
    """Cap the LLM grader / gateway timeout to 8 s for all AI tests.

    Mirrors the same fixture in tests/supervisor/conftest.py.
    Tests that explicitly need a longer timeout can call
    monkeypatch.setenv("GRADER_LLM_TIMEOUT", "<n>") directly.
    """
    if not os.environ.get("GRADER_LLM_TIMEOUT"):
        monkeypatch.setenv("GRADER_LLM_TIMEOUT", "8")
