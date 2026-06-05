"""TC-TEST-003: AI Evidence Critic tests."""

import json
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent


@pytest.fixture
def critic_dir(tmp_path):
    return tmp_path / "critic"


def test_critic_produces_critique_json(critic_dir):
    from tools.supervisor.ai_evidence_critic import run_critic
    result = run_critic("test-sprint", critic_dir)
    assert (critic_dir / "evidence-critique.json").exists()
    assert result["advisory_only"] is True
    assert result["authority_state"] == "ai_draft"


def test_critic_has_sprint_grade(critic_dir):
    from tools.supervisor.ai_evidence_critic import run_critic
    result = run_critic("test-sprint", critic_dir)
    grade = result["sprint_grade"]
    assert "product_progress" in grade
    assert "governance_progress" in grade
    assert "poc_movement" in grade


def test_machinery_creep_is_advisory_only(critic_dir):
    from tools.supervisor.ai_evidence_critic import run_critic
    result = run_critic("test-sprint", critic_dir)
    # MACHINERY_CREEP verdict must say advisory_only
    assert "ADVISORY_ONLY" in result.get("machinery_creep_verdict", "")


def test_critic_does_not_modify_authority_files(critic_dir):
    import hashlib
    poc = _REPO / "product-capability-matrix/poc-targets.yaml"
    before = hashlib.sha256(poc.read_bytes()).hexdigest() if poc.exists() else ""
    from tools.supervisor.ai_evidence_critic import run_critic
    run_critic("test-sprint", critic_dir)
    after = hashlib.sha256(poc.read_bytes()).hexdigest() if poc.exists() else ""
    assert before == after


def test_critic_produces_overclaim_md(critic_dir):
    from tools.supervisor.ai_evidence_critic import run_critic
    run_critic("test-sprint", critic_dir)
    assert (critic_dir / "overclaim-risk.md").exists()
    content = (critic_dir / "overclaim-risk.md").read_text()
    assert "authority_state: ai_draft" in content
    assert "advisory_only: true" in content
