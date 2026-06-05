"""
Tests for continuation state integration (TC-CONT-001).
Verifies the 3 new states and their priority ordering.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "supervisor"))

import pytest


def _classify(auto_continue=True, at_max=False, hard_stops=None, overclaimed=None,
               rework=None, dirty_classified=True, artifacts_present=True, floor_met=True):
    from autonomous_cycle import classify_continuation_state
    return classify_continuation_state(
        auto_continue_value=auto_continue,
        at_max_iterations=at_max,
        hard_stops=hard_stops or [],
        overclaimed=overclaimed or [],
        rework_items=rework or [],
        review={},
        policies_path=Path("/dev/null"),
        dirty_state_classified=dirty_classified,
        required_artifacts_present=artifacts_present,
        product_output_floor_met=floor_met,
    )


class TestContinuationStateIntegration:

    def test_scenario_1_normal_continue(self):
        """Scenario 1: All defaults → YES"""
        result = _classify()
        assert result == "YES"

    def test_scenario_2_max_iterations(self):
        """Scenario 2: Max iterations → NO_MAX_ITERATIONS"""
        result = _classify(at_max=True)
        assert result == "NO_MAX_ITERATIONS"

    def test_scenario_3_overclaimed(self):
        """Scenario 3: Overclaimed items → NO_UNSAFE_SOURCE_STATE"""
        result = _classify(overclaimed=["TC-IMPL-001"])
        assert result == "NO_UNSAFE_SOURCE_STATE"

    def test_scenario_4_dirty_state_unclassified(self):
        """Scenario 4: Dirty state not classified → NO_UNCLASSIFIED_DIRTY_STATE"""
        result = _classify(dirty_classified=False)
        assert result == "NO_UNCLASSIFIED_DIRTY_STATE"

    def test_scenario_5_missing_artifacts(self):
        """Scenario 5: Required artifacts missing → NO_MISSING_REQUIRED_ARTIFACTS"""
        result = _classify(artifacts_present=False)
        assert result == "NO_MISSING_REQUIRED_ARTIFACTS"

    def test_scenario_6_no_product_output_floor(self):
        """Scenario 6: Product output floor not met → NO_PRODUCT_OUTPUT_FLOOR"""
        result = _classify(floor_met=False)
        assert result == "NO_PRODUCT_OUTPUT_FLOOR"

    def test_scenario_7_floor_before_max_iter(self):
        """Scenario 7: Floor not met AND max iter → NO_PRODUCT_OUTPUT_FLOOR wins (priority 5 > 6)"""
        result = _classify(at_max=True, floor_met=False)
        assert result == "NO_PRODUCT_OUTPUT_FLOOR"

    def test_dirty_before_artifacts(self):
        """dirty_state_classified=False fires before required_artifacts_present=False (priority)"""
        result = _classify(dirty_classified=False, artifacts_present=False)
        assert result == "NO_UNCLASSIFIED_DIRTY_STATE"

    def test_artifacts_before_floor(self):
        """required_artifacts_present=False fires before product_output_floor_met=False"""
        result = _classify(artifacts_present=False, floor_met=False)
        assert result == "NO_MISSING_REQUIRED_ARTIFACTS"

    def test_overclaimed_before_dirty(self):
        """overclaimed fires before dirty_state_classified (NO_UNSAFE_SOURCE_STATE has higher priority)"""
        result = _classify(overclaimed=["x"], dirty_classified=False)
        assert result == "NO_UNSAFE_SOURCE_STATE"

    def test_new_states_backward_compatible(self):
        """Default values preserve backward compatibility — YES when nothing wrong"""
        # All new params default to True, so existing callers see no change
        from autonomous_cycle import classify_continuation_state
        result = classify_continuation_state(
            auto_continue_value=True,
            at_max_iterations=False,
            hard_stops=[],
            overclaimed=[],
            rework_items=[],
            review={},
            policies_path=Path("/dev/null"),
        )
        assert result == "YES"
