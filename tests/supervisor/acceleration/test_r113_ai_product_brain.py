"""TC-TEST-003: AI Product Brain tests."""

import hashlib
import json
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
_POC = _REPO / "product-capability-matrix/poc-targets.yaml"


@pytest.fixture
def brain_output_dir(tmp_path):
    return tmp_path / "brain"


def _poc_checksum():
    return hashlib.sha256(_POC.read_bytes()).hexdigest()


def test_brain_produces_all_four_outputs(brain_output_dir):
    from tools.supervisor.ai_product_brain import run_brain
    result = run_brain(sprint_id="test-brain", output_dir=brain_output_dir)
    for fname in ["product-capability-graph.json", "poc-distance-score.json",
                  "product-gap-rankings.json", "over-investment-analysis.json"]:
        f = brain_output_dir / fname
        assert f.exists(), f"Missing: {fname}"
        data = json.loads(f.read_text())
        assert data.get("authority_state") == "ai_draft"
        assert data.get("non_authoritative") is True


def test_brain_does_not_modify_poc_targets(brain_output_dir):
    before = _poc_checksum()
    from tools.supervisor.ai_product_brain import run_brain
    run_brain(sprint_id="test-brain", output_dir=brain_output_dir)
    after = _poc_checksum()
    assert before == after, "poc-targets.yaml was modified by ai_product_brain"


def test_brain_result_has_products_analyzed(brain_output_dir):
    from tools.supervisor.ai_product_brain import run_brain
    result = run_brain(sprint_id="test-brain", output_dir=brain_output_dir)
    assert result["products_analyzed"] >= 0
    assert result["authority_state"] == "ai_draft"
    assert result["non_authoritative"] is True


def test_brain_distance_scores_sorted(brain_output_dir):
    from tools.supervisor.ai_product_brain import run_brain
    run_brain(sprint_id="test-brain", output_dir=brain_output_dir)
    data = json.loads((brain_output_dir / "poc-distance-score.json").read_text())
    scores = [s["distance_score"] for s in data["scores"]]
    assert scores == sorted(scores, reverse=True), "Distance scores not sorted descending"


def test_brain_capability_graph_structure(brain_output_dir):
    from tools.supervisor.ai_product_brain import run_brain
    run_brain(sprint_id="test-brain", output_dir=brain_output_dir)
    data = json.loads((brain_output_dir / "product-capability-graph.json").read_text())
    assert "products" in data
    for p in data["products"]:
        assert "product" in p
        assert "gap_count" in p
        assert "pass_count" in p
