"""Tests for autonomy routing pilot fixtures — YAML-driven route validation."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml
import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from tools.supervisor.autonomy_route_decider import decide_route

_FIXTURES_DIR = _REPO / "tests" / "fixtures" / "autonomy-routing-pilots"


def _load_pilots():
    """Load all pilot fixture YAML files."""
    pilots = []
    for p in sorted(_FIXTURES_DIR.glob("route-pilot-*.yaml")):
        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        pilots.append(data)
    return pilots


_PILOTS = _load_pilots()


def _get_pilot(pilot_id: str) -> dict:
    for p in _PILOTS:
        if p["id"] == pilot_id:
            return p
    raise KeyError(f"Pilot {pilot_id!r} not found")


class TestPilotFixtures:
    def test_pilot_001_product_impl_autonomous(self):
        pilot = _get_pilot("route-pilot-001")
        d = decide_route(
            pilot["task_id"], pilot["task_category"], pilot["task_summary"],
            risk_level=pilot.get("risk_level", "LOW"),
            hints=pilot.get("hints"),
        )
        assert d.final_route == pilot["expected_route"]
        assert d.autonomous_allowed == pilot["expected_autonomous_allowed"]
        assert d.blocked == pilot["expected_blocked"]

    def test_pilot_002_machinery_no_decision(self):
        pilot = _get_pilot("route-pilot-002")
        d = decide_route(
            pilot["task_id"], pilot["task_category"], pilot["task_summary"],
            risk_level=pilot.get("risk_level", "LOW"),
            hints=pilot.get("hints"),
        )
        assert d.final_route == pilot["expected_route"]
        assert d.autonomous_allowed == pilot["expected_autonomous_allowed"]

    def test_pilot_003_product_testing_autonomous(self):
        pilot = _get_pilot("route-pilot-003")
        d = decide_route(
            pilot["task_id"], pilot["task_category"], pilot["task_summary"],
            risk_level=pilot.get("risk_level", "LOW"),
            hints=pilot.get("hints"),
        )
        assert d.final_route == pilot["expected_route"]
        assert d.autonomous_allowed is True

    def test_pilot_004_machinery_governed(self):
        pilot = _get_pilot("route-pilot-004")
        d = decide_route(
            pilot["task_id"], pilot["task_category"], pilot["task_summary"],
            risk_level=pilot.get("risk_level", "LOW"),
            hints=pilot.get("hints"),
        )
        assert d.final_route == pilot["expected_route"]
        assert d.machinery_mutation_allowed is True

    def test_pilot_005_unknown_blocked(self):
        pilot = _get_pilot("route-pilot-005")
        d = decide_route(
            pilot["task_id"], pilot["task_category"], pilot["task_summary"],
            risk_level=pilot.get("risk_level", "LOW"),
            hints=pilot.get("hints"),
        )
        assert d.final_route == pilot["expected_route"]
        assert d.blocked is True
        assert d.autonomous_allowed is False

    def test_all_pilots_loaded(self):
        assert len(_PILOTS) >= 5, f"Expected at least 5 pilots, got {len(_PILOTS)}"
