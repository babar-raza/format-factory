"""TC-TEST-004: Source Pattern Miner tests."""

import json
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent


@pytest.fixture
def patterns_dir(tmp_path):
    return tmp_path / "patterns"


def test_miner_produces_json_output(patterns_dir):
    from tools.supervisor.source_pattern_miner import mine_patterns
    result = mine_patterns("fods", "export csv", output_dir=patterns_dir, sprint_id="test")
    out = patterns_dir / "fods-patterns.json"
    assert out.exists()
    assert result["authority_state"] == "ai_draft"
    assert result["non_authoritative"] is True


def test_format_isolation(patterns_dir):
    """fods query must not return fodt chunks."""
    from tools.supervisor.source_pattern_miner import mine_patterns
    result = mine_patterns("fods", "paragraph", output_dir=patterns_dir, sprint_id="test")
    for chunk in result["lexical_patterns"]:
        assert "fodt" not in chunk["id"].lower(), (
            f"fods query returned fodt chunk: {chunk['id']}"
        )


def test_empty_corpus_is_not_failure(patterns_dir):
    """If no source files found, corpus_empty=True but no exception."""
    from tools.supervisor.source_pattern_miner import mine_patterns
    result = mine_patterns("nonexistent_format_xyz", "test", output_dir=patterns_dir, sprint_id="test")
    assert result["corpus_empty"] is True
    assert result["authority_state"] == "ai_draft"


def test_src_not_modified_by_miner(patterns_dir):
    import hashlib
    src = _REPO / "src"
    before = {str(p): p.stat().st_mtime for p in src.rglob("*") if p.is_file()} if src.exists() else {}
    from tools.supervisor.source_pattern_miner import mine_patterns
    mine_patterns("sylk", "csv", output_dir=patterns_dir, sprint_id="test")
    after = {str(p): p.stat().st_mtime for p in src.rglob("*") if p.is_file()} if src.exists() else {}
    assert before == after, "src/ files modified by source_pattern_miner"


def test_output_json_structure(patterns_dir):
    from tools.supervisor.source_pattern_miner import mine_patterns
    mine_patterns("fodt", "paragraph heading", output_dir=patterns_dir, sprint_id="test")
    data = json.loads((patterns_dir / "fodt-patterns.json").read_text())
    assert "lexical_patterns" in data
    assert "ai_pattern_summary" in data
    assert "format_id" in data
    assert data["format_id"] == "fodt"
