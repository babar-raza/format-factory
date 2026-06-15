"""Tests for SUP-RECT-001 (lane ownership) and SUP-RECT-002 (DAG ordering) validators.

Validates that governance_validators.py enforces:
  - Lane file ownership (changed_files within lane-allowed paths)
  - DAG wave ordering (lane prerequisites met before execution)
"""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from governance_validators import (
    validate_lane_ownership,
    validate_dag_ordering,
    LANE_ALLOWED_PATHS,
    LANE_WAVE_MAP,
    WAVE_PREREQUISITES,
    GLOBAL_ALLOWED_PATHS,
)


# ---------------------------------------------------------------------------
# SUP-RECT-001: Lane Ownership Validator
# ---------------------------------------------------------------------------

class TestLaneOwnershipValidator:
    def test_no_lane_id_passes_backward_compatible(self):
        decl = {"changed_files": ["src/python/fods/model.py"]}
        result = validate_lane_ownership(decl)
        assert result["result"] == "PASS"
        assert "skipped" in result["summary"].lower()

    def test_lane_with_allowed_files_passes(self):
        decl = {
            "lane_id": "lane-09-fods-rebuild",
            "changed_files": [
                "src/python/fods/model.py",
                "tests/python/fods/test_model.py",
            ],
        }
        result = validate_lane_ownership(decl)
        assert result["result"] == "PASS"

    def test_lane_with_violation_fails(self):
        decl = {
            "lane_id": "lane-09-fods-rebuild",
            "changed_files": [
                "src/python/fods/model.py",
                "src/python/fodt/parser.py",  # outside lane-09 allowed paths
            ],
        }
        result = validate_lane_ownership(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert len(result["items"]) == 1
        assert "fodt" in result["items"][0]["file"]

    def test_global_allowed_paths_always_permitted(self):
        decl = {
            "lane_id": "lane-11-zst",
            "changed_files": [
                "src/python/zst/zst_codec.py",
                ".local/evidences/my-run/evidence-declaration.yaml",
                "reports/supervisor/latest-review.md",
            ],
        }
        result = validate_lane_ownership(decl)
        assert result["result"] == "PASS"

    def test_empty_changed_files_passes(self):
        decl = {"lane_id": "lane-01-sal-pipeline", "changed_files": []}
        result = validate_lane_ownership(decl)
        assert result["result"] == "PASS"

    def test_multiple_violations_all_reported(self):
        decl = {
            "lane_id": "lane-11-zst",
            "changed_files": [
                "src/python/fods/model.py",
                "src/python/fodt/parser.py",
                "tools/supervisor/governance_validators.py",
            ],
        }
        result = validate_lane_ownership(decl)
        assert result["result"] == "FAIL"
        assert len(result["items"]) == 3

    def test_backslash_paths_normalized(self):
        decl = {
            "lane_id": "lane-09-fods-rebuild",
            "changed_files": [
                "src\\python\\fods\\model.py",
            ],
        }
        result = validate_lane_ownership(decl)
        assert result["result"] == "PASS"

    def test_unknown_lane_id_passes(self):
        decl = {
            "lane_id": "lane-99-unknown",
            "changed_files": [".local/evidences/foo/bar.yaml"],
        }
        result = validate_lane_ownership(decl)
        # Global paths still allowed even for unknown lane
        assert result["result"] == "PASS"

    def test_lane_constants_exist(self):
        assert isinstance(LANE_ALLOWED_PATHS, dict)
        assert len(LANE_ALLOWED_PATHS) >= 10
        assert isinstance(GLOBAL_ALLOWED_PATHS, list)
        assert len(GLOBAL_ALLOWED_PATHS) >= 2


# ---------------------------------------------------------------------------
# SUP-RECT-002: DAG Ordering Validator
# ---------------------------------------------------------------------------

class TestDagOrderingValidator:
    def test_no_lane_id_passes_backward_compatible(self):
        decl = {}
        result = validate_dag_ordering(decl)
        assert result["result"] == "PASS"
        assert "skipped" in result["summary"].lower()

    def test_wave_0_no_prerequisites(self):
        decl = {"lane_id": "lane-00-coordinator"}
        result = validate_dag_ordering(decl)
        assert result["result"] == "PASS"

    def test_wave_1a_needs_wave_0(self):
        decl = {
            "lane_id": "lane-14-supervision",
            "completed_waves": [],  # wave-0 not completed
        }
        result = validate_dag_ordering(decl)
        assert result["result"] == "WARN"
        assert "wave-0" in str(result["items"])

    def test_wave_1a_with_wave_0_completed(self):
        decl = {
            "lane_id": "lane-14-supervision",
            "completed_waves": ["wave-0"],
        }
        result = validate_dag_ordering(decl)
        assert result["result"] == "PASS"

    def test_wave_5_needs_wave_3(self):
        decl = {
            "lane_id": "lane-09-fods-rebuild",
            "completed_waves": ["wave-0", "wave-1a", "wave-1b", "wave-2"],
        }
        result = validate_dag_ordering(decl)
        assert result["result"] == "WARN"
        assert "wave-3" in str(result["items"])

    def test_wave_5_all_prerequisites_met(self):
        decl = {
            "lane_id": "lane-09-fods-rebuild",
            "completed_waves": ["wave-0", "wave-1a", "wave-1b", "wave-2", "wave-3"],
        }
        result = validate_dag_ordering(decl)
        assert result["result"] == "PASS"

    def test_unknown_lane_passes(self):
        decl = {"lane_id": "lane-99-unknown"}
        result = validate_dag_ordering(decl)
        assert result["result"] == "PASS"
        assert "not in wave map" in result["summary"]

    def test_lane_wave_map_completeness(self):
        assert isinstance(LANE_WAVE_MAP, dict)
        assert len(LANE_WAVE_MAP) >= 14
        for lane, wave in LANE_WAVE_MAP.items():
            assert wave in WAVE_PREREQUISITES, f"{lane} maps to unknown wave {wave}"

    def test_wave_prerequisites_consistency(self):
        # Every prerequisite wave should itself be a key in WAVE_PREREQUISITES
        for wave, prereqs in WAVE_PREREQUISITES.items():
            for p in prereqs:
                assert p in WAVE_PREREQUISITES, f"{wave} has prereq {p} not in map"


# ---------------------------------------------------------------------------
# Integration: run_all_governance_validators includes new validators
# ---------------------------------------------------------------------------

class TestNewValidatorsInRunAll:
    def test_run_all_includes_lane_and_dag(self):
        from governance_validators import run_all_governance_validators
        decl = {
            "run_id": "test-run",
            "sprint_id": "TEST-001",
            "planned_work_items": [],
            "completed_work_items": [],
            "incomplete_work_items": [],
            "changed_files": [],
        }
        result = run_all_governance_validators(decl)
        validator_names = [v["validator"] for v in result["validators"]]
        assert "lane_ownership_validator" in validator_names
        assert "dag_ordering_validator" in validator_names
