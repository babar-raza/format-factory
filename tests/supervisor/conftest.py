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


@pytest.fixture(autouse=True, scope="session")
def _guard_production_db(tmp_path_factory):
    """Prevent tests from connecting to the production control-index.db.

    Redirects DEFAULT_DB_PATH to a session-scoped temp path so any test
    that forgets to use tmp_path will hit an isolated database instead of
    the real .local/supervisor/control-index.db (212 MB, OneDrive-synced).
    """
    import control_index
    sentinel = tmp_path_factory.mktemp("guard") / "guard-control-index.db"
    original = control_index.DEFAULT_DB_PATH
    control_index.DEFAULT_DB_PATH = sentinel
    yield
    control_index.DEFAULT_DB_PATH = original


@pytest.fixture(autouse=True)
def _guard_coordination_root(monkeypatch, tmp_path):
    """Prevent tests from touching the production coordination DB.

    The coordination root (Mission AGENT-COORD-2026-07-15) defaults to
    %LOCALAPPDATA%/ff-coordination/<repo-key>/. Any test that exercises
    coordination-aware code (WorkerClaims/MissionLock mirrors, hooks,
    preflight) is redirected to an isolated per-test root. Tests that set
    FF_AGENT_COORDINATION_ROOT themselves override this fixture value.
    """
    monkeypatch.setenv("FF_AGENT_COORDINATION_ROOT",
                       str(tmp_path / "coordination-guard"))


@pytest.fixture(autouse=True)
def _subprocess_timeout_guard(monkeypatch):
    """Enforce a 60s default timeout on all subprocess.run calls.

    Prevents any subprocess from hanging indefinitely. Tests that need
    longer can pass an explicit timeout= kwarg (which is not overridden).
    """
    import subprocess as _sp
    _original_run = _sp.run

    def _guarded_run(*args, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = 60
        return _original_run(*args, **kwargs)

    monkeypatch.setattr(_sp, "run", _guarded_run)
