"""TC-TEST-004: Test Plan Generator tests."""

import json
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent


@pytest.fixture
def plans_dir(tmp_path):
    return tmp_path / "testplans"


def test_generator_produces_6_template_proposals(plans_dir):
    from tools.supervisor.test_plan_generator import generate_test_plan, _TEMPLATE_PROPOSALS
    result = generate_test_plan("fods-dogfood-csv", output_dir=plans_dir, sprint_id="test")
    assert len(result["template_proposals"]) == len(_TEMPLATE_PROPOSALS)


def test_all_proposals_are_ai_draft(plans_dir):
    from tools.supervisor.test_plan_generator import generate_test_plan
    result = generate_test_plan("fodt-dogfood-markdown", output_dir=plans_dir, sprint_id="test")
    for p in result["template_proposals"]:
        assert p["authority_state"] == "ai_draft"
        assert p["reviewer_accepted"] is True


def test_output_json_parses(plans_dir):
    from tools.supervisor.test_plan_generator import generate_test_plan
    generate_test_plan("netpbm-export", output_dir=plans_dir, sprint_id="test")
    out = plans_dir / "netpbm-export-test-plan.json"
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["authority_state"] == "ai_draft"
    assert data["non_authoritative"] is True


def test_all_template_types_present(plans_dir):
    from tools.supervisor.test_plan_generator import generate_test_plan, _TEMPLATE_PROPOSALS
    result = generate_test_plan("sylk-csv-export", output_dir=plans_dir, sprint_id="test")
    types = {p["test_type"] for p in result["template_proposals"]}
    for expected_type in _TEMPLATE_PROPOSALS:
        assert expected_type in types, f"Missing proposal type: {expected_type}"


def test_gap_id_in_all_proposals(plans_dir):
    from tools.supervisor.test_plan_generator import generate_test_plan
    gap = "fods-dogfood-csv"
    result = generate_test_plan(gap, output_dir=plans_dir, sprint_id="test")
    for p in result["template_proposals"]:
        assert p["gap_id"] == gap
