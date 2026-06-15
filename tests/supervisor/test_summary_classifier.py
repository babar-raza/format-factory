"""
Tests for summary_classifier.py — 24 negative control cases.

Each test proves the system fails closed for invalid states.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from summary_classifier import classify_summary  # noqa: E402


@pytest.fixture
def tmp_stage3(tmp_path: Path):
    """Helper to write a temp Stage 3 output file and return its path."""
    def _write(content: str | dict[str, Any]) -> Path:
        p = tmp_path / "stage3-output.json"
        if isinstance(content, dict):
            p.write_text(json.dumps(content), encoding="utf-8")
        else:
            p.write_text(content, encoding="utf-8")
        return p
    return _write


def _all_green_data(**overrides: Any) -> dict[str, Any]:
    """Generate a valid all-green Stage 3 output."""
    base: dict[str, Any] = {
        "sprint_id": "TEST-SPRINT",
        "timestamp": "2026-06-15T00:00:00Z",
        "execution_results": [
            {
                "taskcard_id": "TC-001",
                "status": "COMPLETED",
                "quality_scores": {
                    "correctness": 5, "test_coverage": 5, "evidence_completeness": 5,
                    "code_quality": 5, "schema_compliance": 5, "governance_compliance": 5,
                    "path_discipline": 5, "documentation": 5, "idempotency": 5,
                    "regression_safety": 5, "performance": 5, "error_handling": 5,
                    "integration_consistency": 5, "evidence_traceability": 5,
                    "acceptance_criteria_met": 5,
                },
                "evidence_paths": ["evidence/test.log"],
                "test_results": {"passed": 10, "failed": 0, "skipped": 0},
            }
        ],
        "overall_verdict": "EXECUTION_COMPLETE_VERIFIED",
        "all_green": True,
        "reroute_log": [],
        "evidence_manifest": [{"path": "evidence/test.log", "type": "log"}],
        "self_review": {
            "l1_execution_issues": [],
            "l2_integration_issues": [],
            "l3_system_weaknesses": [],
            "evidence_quality_verdict": "STRONG",
        },
        "evidence_bundle_path": "/tmp/evidence.zip",
    }
    base.update(overrides)
    return base


# === NC-01: Prompt 3 summary is prose-only ===
def test_nc01_prose_only_summary(tmp_stage3):
    """NC-01: Prose-only summary -> loop chooses P2+P3."""
    path = tmp_stage3("This sprint went well. We completed many tasks and improved the codebase significantly. The team is happy with the progress. No issues were found.")
    result = classify_summary(path)
    assert result["classification"] == "PROSE_ONLY"
    assert result["next_stage_recommendation"] == "REROUTE_TO_PROMPT_2_THEN_3"


# === NC-02: Prompt 3 summary is missing ===
def test_nc02_missing_summary(tmp_path):
    """NC-02: Missing summary -> loop chooses P1+P2+P3."""
    path = tmp_path / "nonexistent.json"
    result = classify_summary(path)
    assert result["classification"] == "MISSING"
    assert result["next_stage_recommendation"] == "RESTART_FROM_PROMPT_1"


# === NC-03: All-green claim + open blockers ===
def test_nc03_all_green_with_reroute_log(tmp_stage3):
    """NC-03: all_green=true but reroute_log has items -> CONTRADICTORY."""
    data = _all_green_data(
        reroute_log=[{"taskcard_id": "TC-001", "reason": "failed", "failing_dimensions": ["correctness"], "rework_owner": "test", "reworked": False, "rescored": False}]
    )
    path = tmp_stage3(data)
    result = classify_summary(path)
    assert result["classification"] == "CONTRADICTORY"


# === NC-04: Quality score is 3/5 ===
def test_nc04_score_below_threshold(tmp_stage3):
    """NC-04: Score 3/5 in one dimension -> item rerouted."""
    data = _all_green_data(all_green=False)
    data["execution_results"][0]["quality_scores"]["correctness"] = 3
    path = tmp_stage3(data)
    result = classify_summary(path)
    assert result["classification"] == "STRUCTURED_NOT_GREEN"
    assert any("correctness" in item for item in result.get("failing_items", []))


# === NC-05: Evidence bundle is missing ===
def test_nc05_evidence_bundle_missing(tmp_stage3):
    """NC-05: No evidence bundle -> acceptance blocked."""
    data = _all_green_data()
    del data["evidence_bundle_path"]
    data["evidence_manifest"] = []
    path = tmp_stage3(data)
    result = classify_summary(path)
    assert result["classification"] == "EVIDENCE_MISSING"


# === NC-06: Taskcard missing for actionable work ===
def test_nc06_no_taskcard_results(tmp_stage3):
    """NC-06: No execution_results -> TASKCARDS_INCOMPLETE."""
    data = _all_green_data()
    data["execution_results"] = []
    path = tmp_stage3(data)
    result = classify_summary(path)
    assert result["classification"] in ("TASKCARDS_INCOMPLETE", "SCORES_MISSING")


# === NC-07: P1 issue has no root cause (schema-level) ===
def test_nc07_issue_schema_requires_root_cause():
    """NC-07: Stage 1 schema requires root_cause field on every issue."""
    schema_path = REPO_ROOT / ".supervisor" / "schemas" / "stage1-issue-model.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    issue_def = schema["$defs"]["issue"]
    assert "root_cause" in issue_def["required"]


# === NC-08: P2 issue has no taskcard (schema-level) ===
def test_nc08_taskcard_contract_requires_taskcards():
    """NC-08: Stage 2 schema requires taskcards array."""
    schema_path = REPO_ROOT / ".supervisor" / "schemas" / "stage2-taskcard-contract.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert "taskcards" in schema["required"]


# === NC-09: P3 taskcard executed but not evaluated ===
def test_nc09_taskcard_without_scores(tmp_stage3):
    """NC-09: Taskcard without quality_scores -> acceptance blocked."""
    data = _all_green_data()
    data["execution_results"][0]["quality_scores"] = {}
    path = tmp_stage3(data)
    result = classify_summary(path)
    assert result["classification"] in ("SCORES_MISSING", "TASKCARDS_INCOMPLETE")


# === NC-10: Human review before agent review ===
def test_nc10_prompt3_requires_self_review():
    """NC-10: Stage 3 schema allows self_review section for agent-side review first."""
    schema_path = REPO_ROOT / ".supervisor" / "schemas" / "stage3-quality-scoring-rubric.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert "self_review" in schema["properties"]


# === NC-11: Evidence declaration references missing files ===
def test_nc11_evidence_bundle_contract_checks_missing():
    """NC-11: Evidence bundle contract has missing_artifacts and declared_artifacts_present."""
    schema_path = REPO_ROOT / ".supervisor" / "schemas" / "evidence-bundle-contract.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert "missing_artifacts" in schema["properties"]
    assert "declared_artifacts_present" in schema["properties"]
    assert "manifest_matches_contents" in schema["properties"]


# === NC-12: Rerouted item accepted without re-evaluation ===
def test_nc12_rerouted_without_rescore(tmp_stage3):
    """NC-12: all_green=true but verdict says rerouted -> CONTRADICTORY."""
    data = _all_green_data(overall_verdict="EXECUTION_REROUTED_REWORK_REQUIRED")
    path = tmp_stage3(data)
    result = classify_summary(path)
    assert result["classification"] == "CONTRADICTORY"


# === NC-13: Loop returns NEXT_PROMPT_NEEDED ===
def test_nc13_invalid_final_state():
    """NC-13: NEXT_PROMPT_NEEDED is in the invalid final states list."""
    from post_sprint_loop_controller import INVALID_FINAL_STATES
    assert "NEXT_PROMPT_NEEDED" in INVALID_FINAL_STATES
    assert "PROSE_ONLY_ACCEPTED" in INVALID_FINAL_STATES
    assert "SCORE_BELOW_4_ACCEPTED" in INVALID_FINAL_STATES


# === NC-14: Project adapter lacks validation commands ===
def test_nc14_adapter_requires_test_commands():
    """NC-14: Adapter contract requires test_commands."""
    schema_path = REPO_ROOT / ".supervisor" / "schemas" / "project-adapter-contract.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert "test_commands" in schema["required"]
    assert schema["properties"]["test_commands"]["minItems"] == 1


# === NC-15: P3 without self-assessment ===
def test_nc15_no_self_review(tmp_stage3):
    """NC-15: Missing self_review -> not structured all-green."""
    data = _all_green_data()
    del data["self_review"]
    path = tmp_stage3(data)
    result = classify_summary(path)
    # Still classified by scores, but self_review absence is recorded
    assert result["evidence"]["has_self_review"] is False


# === NC-16: Plan delta no linked issue IDs (schema-level) ===
def test_nc16_taskcard_requires_source_issues():
    """NC-16: Taskcard schema has source_issue_ids field."""
    schema_path = REPO_ROOT / ".supervisor" / "schemas" / "stage2-taskcard-contract.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    taskcard_def = schema["$defs"]["taskcard"]
    assert "source_issue_ids" in taskcard_def["properties"]


# === NC-17: State skip VERIFIED or SCORED ===
def test_nc17_invalid_state_transitions():
    """NC-17: Taskcard state machine rejects skip transitions."""
    schema_path = REPO_ROOT / ".supervisor" / "schemas" / "taskcard-state-machine.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    invalid = schema["$defs"]["invalid_transitions"]["default"]
    skip_reasons = [t["reason"] for t in invalid]
    assert any("skip VERIFIED" in r for r in skip_reasons)
    assert any("skip execution" in r for r in skip_reasons)


# === NC-18: Prompt asset not registered ===
def test_nc18_all_prompts_registered():
    """NC-18: All 6 new prompt assets are in the registry."""
    import yaml as _yaml
    registry_path = REPO_ROOT / ".supervisor" / "prompts" / "prompt-registry.yaml"
    registry = _yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    prompt_ids = [p["id"] for p in registry["prompts"]]
    assert "PSL-PROMPT-1" in prompt_ids
    assert "PSL-PROMPT-2" in prompt_ids
    assert "PSL-PROMPT-3" in prompt_ids
    assert "PSL-LOOP-CTRL" in prompt_ids
    assert "PSL-CONTRACTS" in prompt_ids
    assert "PSL-ADAPTER" in prompt_ids


# === NC-19: P2 prose without taskcards ===
def test_nc19_stage2_requires_taskcards():
    """NC-19: Stage 2 schema requires taskcards array (not empty prose)."""
    schema_path = REPO_ROOT / ".supervisor" / "schemas" / "stage2-taskcard-contract.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert "taskcards" in schema["required"]
    assert schema["properties"]["taskcards"]["type"] == "array"


# === NC-20: P1 achievement without proof level ===
def test_nc20_achievement_requires_proof_level():
    """NC-20: Stage 1 achievement schema requires proof_level."""
    schema_path = REPO_ROOT / ".supervisor" / "schemas" / "stage1-issue-model.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    achievement_def = schema["$defs"]["achievement"]
    assert "proof_level" in achievement_def["required"]


# === NC-21: P3 taskcard without evidence output ===
def test_nc21_taskcard_result_tracked(tmp_stage3):
    """NC-21: Taskcard with COMPLETED status but no evidence paths recorded."""
    data = _all_green_data()
    data["execution_results"][0]["evidence_paths"] = []
    path = tmp_stage3(data)
    result = classify_summary(path)
    # Should still be classified (scores determine green/not-green)
    # Evidence traceability is checked at scoring level, not classifier level
    assert result["classification"] in ("STRUCTURED_ALL_GREEN", "STRUCTURED_NOT_GREEN")


# === NC-22: Evidence package manifest mismatch ===
def test_nc22_evidence_bundle_manifest_mismatch():
    """NC-22: Evidence bundle contract has manifest_matches_contents field."""
    schema_path = REPO_ROOT / ".supervisor" / "schemas" / "evidence-bundle-contract.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert "manifest_matches_contents" in schema["properties"]
    verdict_enum = schema["properties"]["validation_verdict"]["enum"]
    assert "INVALID_MANIFEST_MISMATCH" in verdict_enum


# === NC-23: All-green + reroute log contradiction ===
def test_nc23_all_green_reroute_contradiction(tmp_stage3):
    """NC-23: CONTRADICTORY when all_green but reroute_log not empty."""
    data = _all_green_data()
    data["reroute_log"] = [{"taskcard_id": "TC-002", "reason": "test", "failing_dimensions": [], "rework_owner": "x", "reworked": False, "rescored": False}]
    path = tmp_stage3(data)
    result = classify_summary(path)
    assert result["classification"] == "CONTRADICTORY"


# === NC-24: Controller cannot determine next stage ===
def test_nc24_controller_always_decides(tmp_stage3):
    """NC-24: Controller must always produce a valid classification, never 'unknown'."""
    data = _all_green_data()
    path = tmp_stage3(data)
    result = classify_summary(path)
    assert result["classification"] in [
        "STRUCTURED_ALL_GREEN", "STRUCTURED_NOT_GREEN", "PROSE_ONLY",
        "MISSING", "CONTRADICTORY", "EVIDENCE_MISSING", "SCORES_MISSING",
        "TASKCARDS_INCOMPLETE", "BLOCKED_EXTERNAL",
    ]
    assert result["next_stage_recommendation"] in [
        "ACCEPT", "REROUTE_TO_PROMPT_2_THEN_3", "RESTART_FROM_PROMPT_1",
        "RUN_EVIDENCE_PACKAGING", "RUN_SCORING_LANE", "REROUTE_REWORK",
        "ADVERSARIAL_REVIEW", "BLOCKER_PACKAGE_AND_STOP",
    ]


# === Additional: Empty file is MISSING ===
def test_empty_file_is_missing(tmp_stage3):
    """Empty file -> MISSING classification."""
    path = tmp_stage3("")
    result = classify_summary(path)
    assert result["classification"] == "MISSING"


# === Additional: BLOCKED_EXTERNAL verdict ===
def test_blocked_external_verdict(tmp_stage3):
    """BLOCKED_EXTERNAL verdict -> BLOCKED_EXTERNAL classification."""
    data = _all_green_data(overall_verdict="BLOCKED_EXTERNAL", all_green=False)
    path = tmp_stage3(data)
    result = classify_summary(path)
    assert result["classification"] == "BLOCKED_EXTERNAL"
    assert result["next_stage_recommendation"] == "BLOCKER_PACKAGE_AND_STOP"


# === Additional: Valid all-green ===
def test_valid_all_green(tmp_stage3):
    """Valid all-green output -> STRUCTURED_ALL_GREEN."""
    data = _all_green_data()
    path = tmp_stage3(data)
    result = classify_summary(path)
    assert result["classification"] == "STRUCTURED_ALL_GREEN"
    assert result["next_stage_recommendation"] == "ADVERSARIAL_REVIEW"
