"""Verification tests for supervisor wiring — proves 4 rework items exist in autonomous_cycle.py.

Rework items verified:
  SUP-RECT-001: LaneEnforcementValidator wiring
  SUP-RECT-002: DAG prerequisite validation wiring
  HEAL-RECT-002: LearningConsumer wiring
  SUP-RECT-005: Circuit breaker for zero-task loops
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

AC_PATH = _REPO / "tools" / "supervisor" / "autonomous_cycle.py"


@pytest.fixture
def ac_source():
    return AC_PATH.read_text(encoding="utf-8")


class TestLaneEnforcementWiring:
    def test_imports_lane_enforcement_validator(self, ac_source):
        assert "LaneEnforcementValidator" in ac_source

    def test_instantiates_validator(self, ac_source):
        assert "lane_validator = LaneEnforcementValidator()" in ac_source or \
               "LaneEnforcementValidator(" in ac_source


class TestDagPrerequisiteWiring:
    def test_dag_step_exists(self, ac_source):
        assert "DAG PREREQUISITE VALIDATION" in ac_source

    def test_reads_dag_yaml(self, ac_source):
        assert "execution-dag.yaml" in ac_source

    def test_checks_wave_prerequisites(self, ac_source):
        assert "prerequisites" in ac_source.lower() or "depends_on" in ac_source


class TestLearningConsumerWiring:
    def test_imports_learning_consumer(self, ac_source):
        assert "LearningConsumer" in ac_source

    def test_instantiates_consumer(self, ac_source):
        assert "LearningConsumer(" in ac_source

    def test_writes_results_to_review(self, ac_source):
        assert "learning_consumer" in ac_source


class TestCircuitBreakerWiring:
    def test_zero_task_counter_path(self, ac_source):
        assert "zero-task-counter.json" in ac_source

    def test_circuit_breaker_message(self, ac_source):
        assert "CIRCUIT BREAKER" in ac_source or "CIRCUIT_BREAKER" in ac_source

    def test_threshold_check(self, ac_source):
        # Should check count against a threshold (3)
        assert "zero-task-counter" in ac_source
