"""TC-TEST-003: AI Implementation Designer tests."""

import json
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent


@pytest.fixture
def design_output_dir(tmp_path):
    return tmp_path / "designs"


def test_designer_produces_four_docs(design_output_dir):
    from tools.supervisor.ai_implementation_designer import design_gap
    paths = design_gap("fods", "dogfood-csv", design_output_dir, sprint_id="test")
    for doc_type in ["design", "test-strategy", "dogfood-strategy", "risk-review"]:
        assert doc_type in paths, f"Missing doc type: {doc_type}"
        assert Path(_REPO / paths[doc_type]).exists(), f"Missing file: {paths[doc_type]}"


def test_designer_frontmatter_has_authority_state(design_output_dir):
    from tools.supervisor.ai_implementation_designer import design_gap
    design_gap("fodt", "dogfood-markdown", design_output_dir, sprint_id="test")
    design_file = design_output_dir / "fodt-dogfood-markdown-design.md"
    content = design_file.read_text()
    assert "authority_state: ai_draft" in content
    assert "non_authoritative: true" in content


def test_designer_summary_json_has_track(design_output_dir):
    from tools.supervisor.ai_implementation_designer import design_gap
    design_gap("sylk", "csv-export", design_output_dir, sprint_id="test")
    summary = json.loads((design_output_dir / "sylk-csv-export-summary.json").read_text())
    assert summary["track"] in ("foss_reduced", "commercial_net", "unknown")
    assert summary["authority_state"] == "ai_draft"


def test_designer_no_src_files_created(design_output_dir):
    src_before = set((_REPO / "src").rglob("*"))
    from tools.supervisor.ai_implementation_designer import design_gap
    design_gap("netpbm", "export", design_output_dir, sprint_id="test")
    src_after = set((_REPO / "src").rglob("*"))
    assert src_before == src_after, "src/ was modified by ai_implementation_designer"


def test_designer_allowed_files_from_track_rules(design_output_dir):
    from tools.supervisor.ai_implementation_designer import design_gap, _TRACK_FILE_RULES
    design_gap("fods", "dogfood-csv", design_output_dir, sprint_id="test")
    summary = json.loads((design_output_dir / "fods-dogfood-csv-summary.json").read_text())
    expected_allowed = _TRACK_FILE_RULES["fods"]["allowed"]
    assert summary["allowed_files"] == expected_allowed
