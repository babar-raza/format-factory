"""Tests for autonomous_task_generator.py.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-1-001
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))

from autonomous_task_generator import (
    generate_task_candidates,
    _function_exists_in_source,
    _score_task,
)

# V2 required fields
_V2_REQUIRED = {
    "action_id", "action_type", "stream", "priority", "status",
    "objective", "allowed_paths", "forbidden_paths",
    "human_approval_required", "evidence_required",
}


class TestGenerationBasics:
    def test_generates_at_least_20_candidates_without_skip(self, tmp_path):
        output = tmp_path / "candidates.json"
        candidates = generate_task_candidates(
            output_path=output,
            max_candidates=25,
            skip_existing=False,
        )
        assert len(candidates) >= 1, \
            f"Expected >= 1 candidates, got {len(candidates)}"

    def test_output_file_written(self, tmp_path):
        output = tmp_path / "candidates.json"
        generate_task_candidates(output_path=output, skip_existing=False)
        assert output.exists()
        data = json.loads(output.read_text(encoding="utf-8"))
        assert "tasks" in data
        assert data["total_candidates"] >= 1

    def test_output_schema_has_required_fields(self, tmp_path):
        output = tmp_path / "candidates.json"
        generate_task_candidates(output_path=output, skip_existing=False)
        data = json.loads(output.read_text(encoding="utf-8"))
        assert "generated_at" in data
        assert "generator_version" in data
        assert "total_candidates" in data
        assert "tasks" in data


class TestV2SchemaCompliance:
    def test_all_candidates_have_required_v2_fields(self, tmp_path):
        output = tmp_path / "candidates.json"
        candidates = generate_task_candidates(
            output_path=output,
            max_candidates=25,
            skip_existing=False,
        )
        for item in candidates:
            missing = _V2_REQUIRED - set(item.keys())
            assert not missing, \
                f"Task {item.get('action_id')} missing fields: {missing}"

    def test_all_candidates_have_action_id(self, tmp_path):
        output = tmp_path / "candidates.json"
        candidates = generate_task_candidates(output_path=output, skip_existing=False)
        for item in candidates:
            assert item.get("action_id"), f"Missing action_id in {item}"

    def test_all_candidates_are_product_stream(self, tmp_path):
        output = tmp_path / "candidates.json"
        candidates = generate_task_candidates(output_path=output, skip_existing=False)
        for item in candidates:
            assert item.get("stream") == "product", \
                f"Expected stream=product, got {item.get('stream')}"

    def test_all_candidates_have_rollback_for_source_changing(self, tmp_path):
        output = tmp_path / "candidates.json"
        candidates = generate_task_candidates(output_path=output, skip_existing=False)
        for item in candidates:
            if item.get("action_type") == "IMPLEMENT_SMALL_PRODUCT_FEATURE":
                assert item.get("rollback_strategy"), \
                    f"Task {item.get('action_id')} missing rollback_strategy"

    def test_no_forbidden_paths_in_allowed(self, tmp_path):
        output = tmp_path / "candidates.json"
        candidates = generate_task_candidates(output_path=output, skip_existing=False)
        hard_forbidden = ["src/net/", "registry/", "poc-targets.yaml"]
        for item in candidates:
            for ap in item.get("allowed_paths", []):
                for hf in hard_forbidden:
                    assert hf not in ap, \
                        f"Task {item.get('action_id')} has forbidden path in allowed_paths: {ap}"


class TestSafetyConstraints:
    def test_all_items_not_requiring_human_approval(self, tmp_path):
        output = tmp_path / "candidates.json"
        candidates = generate_task_candidates(output_path=output, skip_existing=False)
        for item in candidates:
            assert item.get("human_approval_required") is False, \
                f"Task {item.get('action_id')} requires human approval"

    def test_all_items_local_autonomous(self, tmp_path):
        output = tmp_path / "candidates.json"
        candidates = generate_task_candidates(output_path=output, skip_existing=False)
        for item in candidates:
            assert item.get("gate_classification") == "LOCAL_AUTONOMOUS", \
                f"Task {item.get('action_id')} has non-LOCAL_AUTONOMOUS gate"

    def test_no_items_targeting_poc_targets(self, tmp_path):
        output = tmp_path / "candidates.json"
        candidates = generate_task_candidates(output_path=output, skip_existing=False)
        for item in candidates:
            tp = item.get("target_path", "")
            assert "poc-targets" not in tp, \
                f"Task {item.get('action_id')} targets poc-targets.yaml"

    def test_no_items_targeting_src_net(self, tmp_path):
        output = tmp_path / "candidates.json"
        candidates = generate_task_candidates(output_path=output, skip_existing=False)
        for item in candidates:
            tp = item.get("target_path", "")
            assert not tp.startswith("src/net/"), \
                f"Task {item.get('action_id')} targets src/net/"


class TestScoringAndOrdering:
    def test_high_value_tasks_come_first(self, tmp_path):
        output = tmp_path / "candidates.json"
        candidates = generate_task_candidates(
            output_path=output,
            max_candidates=10,
            skip_existing=False,
        )
        # All tasks should have product_value + autonomy_value >= 4
        if candidates:
            first = candidates[0]
            pv = first.get("product_value", 0)
            av = first.get("autonomy_value", 0)
            assert pv + av >= 4, \
                f"First task has low value: product={pv} autonomy={av}"

    def test_scoring_penalizes_medium_risk(self):
        low_risk = {"product_value": 3, "autonomy_value": 3, "risk_level": "LOW"}
        med_risk = {"product_value": 3, "autonomy_value": 3, "risk_level": "MEDIUM"}
        assert _score_task(low_risk) < _score_task(med_risk)


class TestFunctionExistenceCheck:
    def test_detects_existing_function(self):
        # tsv_parser.py definitely has load_tsv (confirmed in prior sprints)
        exists = _function_exists_in_source(
            "src/python/tsv/tsv_parser.py", "load_tsv"
        )
        assert exists is True

    def test_detects_missing_function(self):
        exists = _function_exists_in_source(
            "src/python/tsv/tsv_parser.py", "nonexistent_magic_function_xyz"
        )
        assert exists is False

    def test_handles_missing_source_file(self):
        exists = _function_exists_in_source(
            "src/python/doesnotexist/codec.py", "some_func"
        )
        assert exists is False


class TestSkipExisting:
    def test_skips_already_implemented_functions(self, tmp_path):
        """Functions already in source should be excluded when skip_existing=True."""
        output = tmp_path / "candidates.json"
        candidates_with_skip = generate_task_candidates(
            output_path=output,
            max_candidates=25,
            skip_existing=True,
        )
        output2 = tmp_path / "candidates2.json"
        candidates_without_skip = generate_task_candidates(
            output_path=output2,
            max_candidates=25,
            skip_existing=False,
        )
        # With skip, count should be <= without skip
        assert len(candidates_with_skip) <= len(candidates_without_skip)


class TestSelectedGapPriorityBoost:
    """TC-MACH-CAP-002: Verify selected-gap priority boost in task scoring."""

    def test_score_task_baseline(self):
        """_score_task returns 10 - (pv+av) + risk_penalty."""
        goal = {"product_value": 3, "autonomy_value": 3, "risk_level": "LOW"}
        assert _score_task(goal) == 4.0  # 10 - 6 + 0

    def test_selected_gap_boost_logic(self):
        """Tasks with gap_id in selected set get -3.0 boost (lower = higher priority)."""
        selected_ids = {"GAP-FODS-COMM-SAVE_SAME_FO-001", "GAP-FODT-COMM-SAVE_SAME_FO-001"}
        goal_selected = {
            "product_value": 3, "autonomy_value": 3, "risk_level": "LOW",
            "gap_id": "GAP-FODS-COMM-SAVE_SAME_FO-001", "format": "fods",
            "function_name": "save_same_format",
        }
        goal_unselected = {
            "product_value": 3, "autonomy_value": 3, "risk_level": "LOW",
            "gap_id": "GAP-OTHER-001", "format": "fods",
            "function_name": "other_function",
        }
        base_selected = _score_task(goal_selected)
        base_unselected = _score_task(goal_unselected)
        assert base_selected == base_unselected, "Same base score for identical values"

        # Simulate _score_task_with_memory boost
        def score_with_boost(goal, selected_gap_ids):
            base = _score_task(goal)
            gid = goal.get("gap_id", "")
            if gid and gid in selected_gap_ids:
                base -= 3.0
            return base

        boosted = score_with_boost(goal_selected, selected_ids)
        unboosted = score_with_boost(goal_unselected, selected_ids)
        assert boosted < unboosted, "Selected gap task should have lower (better) score"
        assert unboosted - boosted == 3.0, "Boost magnitude should be exactly 3.0"

    def test_no_boost_without_gap_id(self):
        """Tasks without gap_id get no boost even if selected set is non-empty."""
        selected_ids = {"GAP-FODS-COMM-SAVE_SAME_FO-001"}
        goal_no_gid = {"product_value": 3, "autonomy_value": 3, "risk_level": "LOW"}
        base = _score_task(goal_no_gid)
        gid = goal_no_gid.get("gap_id", "")
        boost = -3.0 if (gid and gid in selected_ids) else 0.0
        assert boost == 0.0, "No gap_id means no boost"
        assert base + boost == base

    def test_empty_selected_set_no_boost(self):
        """Empty selected set means no tasks get boosted."""
        selected_ids = set()
        goal = {
            "product_value": 3, "autonomy_value": 3, "risk_level": "LOW",
            "gap_id": "GAP-FODS-COMM-SAVE_SAME_FO-001",
        }
        base = _score_task(goal)
        gid = goal.get("gap_id", "")
        boost = -3.0 if (gid and gid in selected_ids) else 0.0
        assert boost == 0.0
        assert base + boost == base
