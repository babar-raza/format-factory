"""Tests for the governed stale-lease reclaim (GAP-015 with the GAP-016 interlock).

The safety-critical function is `plan_reclaim`, which decides what may be taken
over. It is pure, so these tests exercise the decision directly. The bar is not
"does it reclaim" but "can it ever reclaim something it must not".
"""

from __future__ import annotations

from typing import Any

import pytest

from tools.ff6 import reclaim_stale_leases as rsl


def _snapshot(
    *, lease_status: str = "STALE", pid: int | None = 4242, agent_known: bool = True
) -> dict[str, Any]:
    agents = []
    if agent_known:
        agents.append(
            {"agent_id": "agent-old", "pid": pid, "status": "STALE_SUSPECT"}
        )
    return {
        "active_agents": agents,
        "live_leases": [
            {
                "lease_id": "lease-abc",
                "agent_id": "agent-old",
                "task_id": "TC-OLD-001",
                "resource_display": "some/file.py",
                "resource_key": "some/file.py",
                "mode": "EXCLUSIVE_WRITE",
                "origin": "explicit",
                "status": lease_status,
            }
        ],
    }


def _plan(monkeypatch: pytest.MonkeyPatch, alive: bool | None, **kwargs: Any):
    monkeypatch.setattr(rsl, "process_alive", lambda pid: alive)
    return rsl.plan_reclaim(_snapshot(**kwargs))


# ── The interlock: a live owner is never reclaimed ─────────────────────────


def test_never_reclaims_when_the_owner_process_is_alive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """GAP-016: an agent can be marked STALE while still working."""
    decisions = _plan(monkeypatch, alive=True)
    assert decisions[0]["action"] == "SKIP"
    assert "still running" in decisions[0]["why"]


def test_never_reclaims_when_liveness_is_undeterminable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Uncertainty must resolve to leaving the lease alone, not to reclaiming."""
    decisions = _plan(monkeypatch, alive=None)
    assert decisions[0]["action"] == "SKIP"
    assert "could not be determined" in decisions[0]["why"]


def test_never_reclaims_when_the_owner_agent_is_unknown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No agent record means no pid means no liveness proof."""
    decisions = _plan(monkeypatch, alive=None, agent_known=False)
    assert decisions[0]["action"] == "SKIP"


def test_reclaims_only_when_the_owner_process_is_confirmed_gone(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    decisions = _plan(monkeypatch, alive=False)
    assert decisions[0]["action"] == "RECLAIM"
    assert "is gone" in decisions[0]["why"]


# ── Only leases the system itself calls STALE are candidates ───────────────


@pytest.mark.parametrize("status", ["ACTIVE", "STALE_SUSPECT", "COMPLETED", ""])
def test_non_stale_leases_are_never_considered(
    monkeypatch: pytest.MonkeyPatch, status: str
) -> None:
    """ACTIVE and STALE_SUSPECT are explicitly out of scope."""
    assert _plan(monkeypatch, alive=False, lease_status=status) == []


def test_planning_has_no_side_effects(monkeypatch: pytest.MonkeyPatch) -> None:
    """plan_reclaim must never call the coordination CLI."""
    def _boom(*args: Any, **kwargs: Any):
        raise AssertionError("plan_reclaim must not invoke coordination")

    monkeypatch.setattr(rsl, "_run", _boom)
    monkeypatch.setattr(rsl, "process_alive", lambda pid: False)
    assert rsl.plan_reclaim(_snapshot())[0]["action"] == "RECLAIM"


# ── process_alive's contract ───────────────────────────────────────────────


@pytest.mark.parametrize("pid", [None, 0, -1])
def test_missing_or_invalid_pid_is_undeterminable_not_dead(pid: int | None) -> None:
    """Returning False here would make every pid-less lease reclaimable."""
    assert rsl.process_alive(pid) is None


def test_this_live_process_is_reported_alive() -> None:
    import os

    assert rsl.process_alive(os.getpid()) is True


# ── The preflight must never stop the run it exists to unblock ─────────────


def test_exits_zero_even_when_coordination_is_unreadable(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    def _broken() -> dict[str, Any]:
        raise RuntimeError("coordination unavailable")

    monkeypatch.setattr(rsl, "_snapshot", _broken)
    assert rsl.main(["--dry-run"]) == 0
    assert "could not read coordination state" in capsys.readouterr().err


def test_dry_run_reports_without_touching_anything(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    monkeypatch.setattr(rsl, "_snapshot", lambda: _snapshot())
    monkeypatch.setattr(rsl, "process_alive", lambda pid: False)

    def _boom(*args: Any, **kwargs: Any):
        raise AssertionError("--dry-run must not invoke coordination")

    monkeypatch.setattr(rsl, "_run", _boom)
    assert rsl.main(["--dry-run"]) == 0
    assert "would reclaim 1" in capsys.readouterr().out


def test_real_snapshot_plans_without_error() -> None:
    """Against the live coordination state: plans, and skips live owners."""
    decisions = rsl.plan_reclaim(rsl._snapshot())
    assert all(d["action"] in {"RECLAIM", "SKIP"} for d in decisions)
    for decision in decisions:
        if decision["owner_alive"] is True:
            assert decision["action"] == "SKIP"
