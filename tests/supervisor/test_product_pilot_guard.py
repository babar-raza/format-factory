"""
Tests for tools/supervisor/product_action_guard.py
Sprint: FORMAT-FACTORY-AUTONOMOUS-SYSTEM-ACCEPTANCE-PERSISTENT-PRODUCT-LOOP-001
"""
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from tools.supervisor.product_action_guard import (
    check_action,
    is_action_safe,
    classify_product_gaps,
    generate_product_pilot_actions,
    write_product_gap_classification,
    GuardViolation,
    SAFE_PRODUCT_PILOT_ACTIONS,
)


# ── Forbidden action types ─────────────────────────────────────────────────

@pytest.mark.parametrize("forbidden_type", [
    "GIT_PUSH",
    "GIT_COMMIT",
    "GIT_RESET",
    "GATE_8_APPROVAL",
    "GATE_11_APPROVAL",
    "PACKAGE_PUBLISH",
    "MCP_ACTIVATE",
    "MUTATE_POC_TARGETS",
    "MUTATE_PRODUCT_SOURCE",
])
def test_forbidden_action_raises(forbidden_type):
    action = {"action_type": forbidden_type, "external_gate": False}
    with pytest.raises(GuardViolation):
        check_action(action)


@pytest.mark.parametrize("forbidden_type", [
    "GIT_PUSH",
    "GIT_COMMIT",
    "GATE_11_APPROVAL",
    "PACKAGE_PUBLISH",
    "MCP_ACTIVATE",
])
def test_forbidden_action_not_safe(forbidden_type):
    action = {"action_type": forbidden_type, "external_gate": False}
    assert not is_action_safe(action)


# ── External gate check ────────────────────────────────────────────────────

def test_external_gate_true_raises():
    action = {"action_type": "RUN_JSON_VALIDATION", "external_gate": True}
    with pytest.raises(GuardViolation, match="external_gate"):
        check_action(action)


def test_external_gate_false_allowed():
    action = {"action_type": "RUN_JSON_VALIDATION", "external_gate": False}
    check_action(action)  # should not raise


# ── Safe actions ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("safe_type", [
    "RUN_JSON_VALIDATION",
    "RUN_YAML_VALIDATION",
    "RUN_MD_NONEMPTY_CHECK",
    "RUN_COMMAND_DISCOVERY",
    "GENERATE_EVIDENCE_STUB",
    "CLASSIFY_PRODUCT_GAPS",
])
def test_safe_actions_pass(safe_type):
    action = {"action_type": safe_type, "external_gate": False}
    assert is_action_safe(action)


def test_safe_product_pilot_actions_all_pass():
    for action_type in SAFE_PRODUCT_PILOT_ACTIONS:
        action = {"action_type": action_type, "external_gate": False}
        assert is_action_safe(action), f"{action_type} should be safe"


# ── Write path protection ──────────────────────────────────────────────────

def test_write_to_src_blocked():
    action = {
        "action_type": "WRITE_TO_SRC",
        "target_path": "src/net/fods/SomeFile.cs",
        "external_gate": False,
    }
    assert not is_action_safe(action)


def test_read_from_src_not_blocked():
    # READ actions on src/ should not be blocked
    action = {
        "action_type": "RUN_JSON_VALIDATION",
        "target_path": "src/net/fods/FormatFactory.Fods.csproj",
        "external_gate": False,
    }
    assert is_action_safe(action)


# ── Gap classification ─────────────────────────────────────────────────────

def test_classify_product_gaps_missing_file():
    result = classify_product_gaps(Path("NONEXISTENT_poc_targets_xyz.yaml"))
    assert result["status"] == "POC_TARGETS_NOT_FOUND"
    assert result["autonomous_gaps"] == []


def test_classify_product_gaps_real_file():
    """Classify the actual poc-targets.yaml without mutating it."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    poc_path = repo_root / "poc-targets.yaml"
    if not poc_path.exists():
        pytest.skip("poc-targets.yaml not found")
    result = classify_product_gaps(poc_path)
    assert result["status"] == "CLASSIFIED"
    assert "total_targets" in result
    assert isinstance(result["commercial_ready"], list)
    # Known state: 3 commercial-ready formats
    assert result["commercial_ready_count"] >= 3


# ── Pilot action generation ────────────────────────────────────────────────

def test_generate_pilot_actions_returns_list():
    classification = {"status": "CLASSIFIED", "autonomous_gaps": [], "external_gate_gaps": [], "commercial_ready": []}
    actions = generate_product_pilot_actions(classification)
    assert isinstance(actions, list)
    assert len(actions) >= 1


def test_generated_pilot_actions_are_safe():
    classification = {"status": "CLASSIFIED", "autonomous_gaps": [], "external_gate_gaps": [], "commercial_ready": []}
    actions = generate_product_pilot_actions(classification)
    for action in actions:
        assert is_action_safe(action), f"Pilot action {action.get('action_type')} failed guard"


def test_generated_pilot_actions_no_external_gate():
    classification = {"status": "CLASSIFIED", "autonomous_gaps": [], "external_gate_gaps": [], "commercial_ready": []}
    actions = generate_product_pilot_actions(classification)
    for action in actions:
        assert action.get("external_gate") is False


# ── Write classification ───────────────────────────────────────────────────

def test_write_product_gap_classification(tmp_path):
    classification = {"status": "CLASSIFIED", "autonomous_gaps": [], "commercial_ready_count": 3}
    out = write_product_gap_classification(classification, output_path=tmp_path / "product-gap-classification.json")
    assert out.exists()
    import json
    data = json.loads(out.read_text())
    assert data["status"] == "CLASSIFIED"
