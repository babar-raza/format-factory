"""Tests for select_poc_gaps.py v3/v4 — stream-aware gap selection + stale detection."""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"))

from select_poc_gaps import (
    _depth_bonus,
    _classify_stream,
    _yaml_hash,
    detect_stale,
    select_gaps,
    split_by_stream,
    build_payload,
    load_skill_registry,
)


def test_depth_bonus_high():
    assert _depth_bonus("save_same_format") > 0
    assert _depth_bonus("export_csv") > 0
    assert _depth_bonus("dogfood_status") > 0
    assert _depth_bonus("write_pbm") > 0


def test_depth_bonus_low():
    assert _depth_bonus("get_row_count") < 0
    assert _depth_bonus("enumerate_sheets") < 0
    assert _depth_bonus("inspect_object_model") < 0


def test_depth_bonus_neutral():
    assert _depth_bonus("load") == 0
    assert _depth_bonus("edit_cells") == 0


def test_classify_stream_external():
    gap = {"decision": "EXTERNAL_GATE_ESCALATION", "capability_path": "blockers.1"}
    assert _classify_stream(gap) == "supervisor"


def test_classify_stream_mainstream():
    gap = {"decision": "GOVERNED_SKILL_REQUIRED", "capability_path": "dotnet_status.load"}
    assert _classify_stream(gap) == "mainstream"


def test_split_by_stream():
    gaps = [
        {"stream": "mainstream", "gap_id": "g1"},
        {"stream": "mainstream", "gap_id": "g2"},
        {"stream": "supervisor", "gap_id": "g3"},
    ]
    streams = split_by_stream(gaps)
    assert len(streams["mainstream"]) == 2
    assert len(streams["supervisor"]) == 1
    assert len(streams["acceleration"]) == 0


MINIMAL_MATRIX = {
    "poc_matrix_version": "1.0",
    "sprint": "R99-TEST",
    "commercial_net_products": [
        {
            "format": "FODS",
            "dotnet_status": {
                "save_same_format": "NOT_IMPLEMENTED",
            },
            "dogfood_status": {
                "fods_to_csv_dotnet": "GAP_DOGFOOD_EXTERNAL",
            },
            "blockers": ["Gate 11 G11-G: requires approval"],
        }
    ],
    "foss_reduced_products": [],
}


def test_select_gaps_returns_list():
    gaps = select_gaps(MINIMAL_MATRIX)
    assert isinstance(gaps, list)
    assert len(gaps) >= 2


def test_gaps_have_stream_field():
    gaps = select_gaps(MINIMAL_MATRIX)
    for gap in gaps:
        assert "stream" in gap
        assert gap["stream"] in ("mainstream", "acceleration", "skills", "supervisor")


def test_gaps_have_depth_bonus():
    gaps = select_gaps(MINIMAL_MATRIX)
    for gap in gaps:
        assert "depth_bonus" in gap


def test_build_payload_has_streams():
    payload = build_payload(Path("test-matrix.yaml"), MINIMAL_MATRIX)
    assert "streams" in payload
    assert isinstance(payload["streams"], dict)


def test_load_skill_registry_missing(tmp_path):
    result = load_skill_registry(tmp_path / "nonexistent.yaml")
    assert result is None


def test_save_export_ranked_higher_than_query():
    matrix = {
        "commercial_net_products": [
            {
                "format": "TEST",
                "dotnet_status": {
                    "save_same_format": "NOT_IMPLEMENTED",
                    "get_row_count": "NOT_IMPLEMENTED",
                },
            }
        ],
        "foss_reduced_products": [],
    }
    gaps = select_gaps(matrix)
    save_gap = next(g for g in gaps if "save" in g["capability_path"])
    query_gap = next(g for g in gaps if "get" in g["capability_path"])
    assert save_gap["priority_score"] > query_gap["priority_score"]


# --- v4 (R101): stale detection and yaml_hash tests ---


def test_detect_stale_matching():
    """Negative: matching sprint is NOT stale."""
    assert detect_stale("R101", "R101") is False


def test_detect_stale_mismatch():
    """Positive: mismatched sprint IS stale."""
    assert detect_stale("R98", "R101") is True


def test_detect_stale_none_requested():
    """Negative: no requested sprint means not stale."""
    assert detect_stale("R98", None) is False


def test_detect_stale_none_matrix():
    """Negative: no matrix sprint means not stale."""
    assert detect_stale(None, "R101") is False


def test_detect_stale_whitespace():
    """Negative: trailing whitespace should be stripped."""
    assert detect_stale("R101 ", " R101") is False


def test_yaml_hash_none():
    assert _yaml_hash(None) == "none"


def test_yaml_hash_empty():
    """Empty dict is falsy in Python, so _yaml_hash returns 'none'."""
    assert _yaml_hash({}) == "none"


def test_yaml_hash_deterministic():
    data = {"a": 1, "b": 2}
    assert _yaml_hash(data) == _yaml_hash(data)


def test_yaml_hash_order_independent():
    assert _yaml_hash({"a": 1, "b": 2}) == _yaml_hash({"b": 2, "a": 1})


def test_build_payload_stale_flag():
    """Positive: stale flag set when sprint mismatch."""
    payload = build_payload(Path("test.yaml"), MINIMAL_MATRIX, requested_sprint="R200")
    assert payload["is_stale"] is True
    assert payload["requested_sprint"] == "R200"


def test_build_payload_not_stale():
    """Negative: stale flag clear when sprint matches."""
    payload = build_payload(Path("test.yaml"), MINIMAL_MATRIX, requested_sprint="R99-TEST")
    assert payload["is_stale"] is False


def test_build_payload_has_registry_hash():
    payload = build_payload(Path("test.yaml"), MINIMAL_MATRIX)
    assert "skill_registry_hash" in payload


def test_build_payload_registry_hash_with_data():
    registry = {"skills": [{"skill_id": "test", "status": "active"}]}
    payload = build_payload(Path("test.yaml"), MINIMAL_MATRIX, skill_registry=registry)
    assert payload["skill_registry_hash"] != "none"


def test_build_payload_no_stale_when_no_requested():
    payload = build_payload(Path("test.yaml"), MINIMAL_MATRIX)
    assert payload["is_stale"] is False
    assert payload["requested_sprint"] is None
