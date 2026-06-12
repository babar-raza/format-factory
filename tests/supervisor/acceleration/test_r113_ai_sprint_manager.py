"""TC-TEST-003: AI Sprint Manager tests.

Key tests: agentic_low_risk unavailable -> status=skipped (NOT fixture).
advisory_only: true in all outputs.
"""

import json
from pathlib import Path
from unittest import mock

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent


@pytest.fixture
def mgr_output_dir(tmp_path):
    return tmp_path / "mgr"


def test_pre_pass_produces_output(mgr_output_dir):
    from tools.supervisor.ai_sprint_manager import run_pass
    result = run_pass("pre", "test-sprint", mgr_output_dir)
    assert (mgr_output_dir / "pre-sprint-plan.json").exists()
    assert result["advisory_only"] is True
    assert result["authority_state"] == "ai_draft"
    assert result["non_authoritative"] is True


def test_pre_pass_has_required_fields(mgr_output_dir):
    from tools.supervisor.ai_sprint_manager import run_pass
    result = run_pass("pre", "test-sprint", mgr_output_dir)
    data = json.loads((mgr_output_dir / "pre-sprint-plan.json").read_text())
    assert "lane_design" in data
    assert "dependency_map" in data
    assert data.get("advisory_only") is True


def test_mid_pass_produces_output(mgr_output_dir):
    from tools.supervisor.ai_sprint_manager import run_pass
    result = run_pass("mid", "test-sprint", mgr_output_dir)
    assert (mgr_output_dir / "mid-sprint-reroute.json").exists()
    assert result["advisory_only"] is True


def test_final_pass_produces_output_and_recommendation(mgr_output_dir):
    from tools.supervisor.ai_sprint_manager import run_pass
    result = run_pass("final", "test-sprint", mgr_output_dir)
    assert (mgr_output_dir / "final-review.json").exists()
    assert (mgr_output_dir / "next-sprint-recommendation.md").exists()


def test_agentic_low_risk_unavailable_produces_skipped_not_fixture(mgr_output_dir):
    """When agentic_low_risk has no model, output status must be 'skipped', never fixture content."""
    from tools.supervisor.ai_sprint_manager import run_pass
    from tools.ai.schemas.models import ModelSelectionDecision, AIRole

    # Mock router to return fail_closed
    fail_decision = ModelSelectionDecision(
        role=AIRole.agentic_low_risk,
        fail_closed=True,
        reason="no_model_for_agentic_low_risk_and_fallback_forbidden",
    )
    with mock.patch("tools.ai.control_plane.model_router.ModelRouter") as mock_router_cls:
        mock_router = mock.MagicMock()
        mock_router.select.return_value = fail_decision
        mock_router_cls.return_value = mock_router
        result = run_pass("pre", "test-sprint-skipped", mgr_output_dir)

    assert result.get("status") == "skipped", f"Expected 'skipped', got {result.get('status')}"
    assert "fixture" not in str(result.get("ai_output", "")).lower()


def test_authority_files_not_modified_by_sprint_manager(mgr_output_dir):
    """Sprint manager must not modify poc-targets.yaml or skill-registry.yaml."""
    import hashlib
    poc = _REPO / "product-capability-matrix/poc-targets.yaml"
    skill = _REPO / ".supervisor/skill-registry.yaml"
    before_poc = hashlib.sha256(poc.read_bytes()).hexdigest() if poc.exists() else ""
    before_skill = hashlib.sha256(skill.read_bytes()).hexdigest() if skill.exists() else ""

    from tools.supervisor.ai_sprint_manager import run_pass
    run_pass("pre", "test-sprint", mgr_output_dir)

    after_poc = hashlib.sha256(poc.read_bytes()).hexdigest() if poc.exists() else ""
    after_skill = hashlib.sha256(skill.read_bytes()).hexdigest() if skill.exists() else ""
    assert before_poc == after_poc
    assert before_skill == after_skill
