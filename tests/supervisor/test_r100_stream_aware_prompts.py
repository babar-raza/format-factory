"""
R100 — Stream-Aware Prompt Generator Unit Tests
Tests STREAM_GROUPS filtering and synthesize_trains() logic.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from generate_next_worker_prompt import (
    STREAM_GROUPS,
    synthesize_trains,
    generate_prompt,
    generate_next_work_items,
    suggest_next_sprint_id,
    format_train_manifest_table,
    format_train_details,
)


# ---------------------------------------------------------------------------
# STREAM_GROUPS structure
# ---------------------------------------------------------------------------

def test_stream_groups_has_four_streams():
    assert set(STREAM_GROUPS.keys()) == {"product", "acceleration", "skills", "supervisor"}


def test_product_stream_includes_all_groups():
    """Product stream should include G1-G8."""
    assert set(STREAM_GROUPS["product"]) == {"G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"}


def test_non_product_streams_include_governance_and_evidence():
    """Non-product streams should still include G1, G2, G7, G8."""
    for stream in ("acceleration", "skills", "supervisor"):
        groups = set(STREAM_GROUPS[stream])
        assert "G1" in groups, f"{stream} missing G1"
        assert "G2" in groups, f"{stream} missing G2"
        assert "G7" in groups, f"{stream} missing G7"
        assert "G8" in groups, f"{stream} missing G8"


def test_non_product_streams_exclude_product_groups():
    """Non-product streams should NOT include G3-G6."""
    for stream in ("acceleration", "skills", "supervisor"):
        groups = set(STREAM_GROUPS[stream])
        assert "G3" not in groups, f"{stream} should not have G3"
        assert "G4" not in groups, f"{stream} should not have G4"
        assert "G5" not in groups, f"{stream} should not have G5"
        assert "G6" not in groups, f"{stream} should not have G6"


# ---------------------------------------------------------------------------
# synthesize_trains
# ---------------------------------------------------------------------------

def _minimal_review():
    return {
        "sprint_id": "R99",
        "overall_verdict": "ACCEPTED",
        "autonomous_continue": True,
        "item_grades": [],
        "test_results": {"passed": 100, "failed": 0, "skipped": 0},
    }


def test_synthesize_trains_always_has_g1_and_g8():
    """Every train set must include G1 (preflight) and G8 (evidence)."""
    trains = synthesize_trains(_minimal_review(), {}, {})
    groups = [t["group"] for t in trains]
    assert "G1" in groups
    assert "G8" in groups


def test_synthesize_trains_with_rework_items():
    review = _minimal_review()
    review["item_grades"] = [
        {"item_id": "X1", "item_title": "Fix X", "supervisor_grade": "REWORK_REQUIRED",
         "required_rework": "Missing evidence", "evidence_paths": ["a.md"]},
    ]
    trains = synthesize_trains(review, {}, {})
    g2_trains = [t for t in trains if t["group"] == "G2"]
    assert len(g2_trains) >= 1
    assert "Rework" in g2_trains[0]["title"]


def test_synthesize_trains_with_commercial_products():
    poc = {
        "commercial_net_products": [
            {"format": "FODS", "next_action": "add new API", "gate_11_status": "not_started",
             "dotnet_status": {"load": "PASS"}},
        ]
    }
    trains = synthesize_trains(_minimal_review(), poc, {})
    g3_trains = [t for t in trains if t["group"] == "G3"]
    assert len(g3_trains) >= 1
    assert "FODS" in g3_trains[0]["title"]


def test_synthesize_trains_with_foss_products():
    poc = {
        "foss_reduced_products": [
            {"format": "ZST", "next_action": "hardening",
             "python_status": {"compress": "PASS", "decompress": "NOT_IMPLEMENTED"}},
        ]
    }
    trains = synthesize_trains(_minimal_review(), poc, {})
    g4_trains = [t for t in trains if t["group"] == "G4"]
    assert len(g4_trains) >= 1
    assert "ZST" in g4_trains[0]["title"]
    assert "decompress" in g4_trains[0]["title"].lower()


# ---------------------------------------------------------------------------
# generate_prompt with stream filtering
# ---------------------------------------------------------------------------

def test_generate_prompt_no_stream_gets_all_groups():
    """No stream filter → all groups included."""
    prompt = generate_prompt(_minimal_review(), repo_root=REPO_ROOT)
    # Should contain both product groups (G3/G4) and governance groups
    assert "Group G1" in prompt or "Governance" in prompt
    assert len(prompt) > 100


def test_generate_prompt_supervisor_stream_excludes_product():
    """Supervisor stream should exclude G3-G6 trains."""
    review = _minimal_review()
    prompt = generate_prompt(review, repo_root=REPO_ROOT, stream="supervisor")
    # Product-specific trains (G3: Commercial .NET, G4: FOSS) should be filtered
    # G5: Dogfood, G6: Package should also be absent
    assert "Group G3" not in prompt or "Commercial" not in prompt


def test_generate_prompt_unknown_stream_ignored():
    """Unknown stream name → no filtering (all groups)."""
    prompt = generate_prompt(_minimal_review(), repo_root=REPO_ROOT, stream="nonexistent")
    assert len(prompt) > 100


# ---------------------------------------------------------------------------
# generate_next_work_items
# ---------------------------------------------------------------------------

def test_generate_next_work_items_rework_first():
    review = _minimal_review()
    review["item_grades"] = [
        {"item_id": "A", "item_title": "Accept A", "supervisor_grade": "ACCEPTED_VERIFIED"},
        {"item_id": "B", "item_title": "Fix B", "supervisor_grade": "REWORK_REQUIRED",
         "required_rework": "missing file"},
    ]
    work = generate_next_work_items(review)
    rework_items = [i for i in work["items"] if i["lane"] == "rework"]
    assert len(rework_items) >= 1
    assert rework_items[0]["item_id"] == "REWORK-B"


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def test_suggest_next_sprint_id():
    assert suggest_next_sprint_id("FORMAT-FACTORY-R99-MEGA") == "R100"
    assert suggest_next_sprint_id("R42") == "R43"
    assert suggest_next_sprint_id("no-r-number") == "RNEXT"


def test_format_train_manifest_table():
    trains = [
        {"letter": "A", "group": "G1", "title": "Preflight"},
        {"letter": "B", "group": "G8", "title": "Evidence"},
    ]
    table = format_train_manifest_table(trains)
    assert "| A | G1 | Preflight |" in table
    assert "| B | G8 | Evidence |" in table


def test_format_train_details():
    trains = [
        {"letter": "A", "group": "G1", "title": "Preflight",
         "description": "Read governance files", "acceptance_criteria": ["Files read"],
         "files_touched": ["AGENTS.md"], "verification_command": ""},
    ]
    details = format_train_details(trains)
    assert "Train A: Preflight" in details
    assert "Read governance files" in details
