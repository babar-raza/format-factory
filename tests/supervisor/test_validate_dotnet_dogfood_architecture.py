"""
Regression tests for ISSUE-001: .NET dogfood architecture gap classification.
Sprint: FORMAT-FACTORY-DOTNET-DOGFOOD-ARCHITECTURE-GAP-INVESTIGATION-AND-PLANNING-001
"""
import json
import pathlib
import pytest

REPO_ROOT = pathlib.Path(__file__).parent.parent.parent
REPORT_DIR = REPO_ROOT / "reports" / "dotnet-dogfood-architecture-gap"

BLOCKED_GAP_IDS = {
    "commercial-net-fods-dogfood-status-fods-to-csv-dotnet",
    "commercial-net-fods-dogfood-status-fods-to-html-dotnet",
    "commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet",
    "commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet",
}


def load_json(filename: str):
    path = REPORT_DIR / filename
    assert path.exists(), f"Required file missing: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


# T1: blocked-dogfood-gap-ledger.json exists and has exactly 4 entries
def test_t1_blocked_gap_ledger_has_four_entries():
    data = load_json("blocked-dogfood-gap-ledger.json")
    assert len(data) == 4, f"Expected 4 entries, got {len(data)}"


# T2: each ledger entry has allowed_skill_invocation == false
def test_t2_all_ledger_entries_skill_invocation_false():
    data = load_json("blocked-dogfood-gap-ledger.json")
    for entry in data:
        assert entry.get("allowed_skill_invocation") is False, \
            f"Gap {entry.get('gap_id')} has allowed_skill_invocation != false"


# T3: each ledger entry has blocker_type == "missing_target_writer_library"
def test_t3_all_ledger_entries_have_correct_blocker_type():
    data = load_json("blocked-dogfood-gap-ledger.json")
    for entry in data:
        assert entry.get("blocker_type") == "missing_target_writer_library", \
            f"Gap {entry.get('gap_id')} has wrong blocker_type: {entry.get('blocker_type')}"


# T4: each ledger entry has future_decision_required == true
def test_t4_all_ledger_entries_future_decision_required():
    data = load_json("blocked-dogfood-gap-ledger.json")
    for entry in data:
        assert entry.get("future_decision_required") is True, \
            f"Gap {entry.get('gap_id')} has future_decision_required != true"


# T5: dogfood-skill-routing-matrix.json exists and all entries have skill_invocation_allowed == false
def test_t5_routing_matrix_all_blocked():
    data = load_json("dogfood-skill-routing-matrix.json")
    assert len(data) == 4, f"Expected 4 routing matrix entries, got {len(data)}"
    for entry in data:
        assert entry.get("skill_invocation_allowed") is False, \
            f"Gap {entry.get('gap_id')} has skill_invocation_allowed != false"


# T6: actionable-gap-replacement-candidates.json exists and has at least 1 entry
def test_t6_actionable_candidates_not_empty():
    data = load_json("actionable-gap-replacement-candidates.json")
    assert len(data) >= 1, "actionable-gap-replacement-candidates.json must have at least 1 entry"


# T7: no candidate in actionable list appears in the blocked ledger
def test_t7_actionable_candidates_not_in_blocked_ledger():
    candidates = load_json("actionable-gap-replacement-candidates.json")
    ledger = load_json("blocked-dogfood-gap-ledger.json")
    blocked_ids = {e.get("gap_id") for e in ledger}
    for candidate in candidates:
        cid = candidate.get("gap_id", candidate.get("id", ""))
        assert cid not in blocked_ids, \
            f"Candidate {cid} appears in both actionable list and blocked ledger"


# T8: top-gap-table.json exists and has exactly 4 entries all with score == 125
def test_t8_top_gap_table_four_entries_score_125():
    data = load_json("top-gap-table.json")
    assert len(data) == 4, f"Expected 4 top-gap entries, got {len(data)}"
    for entry in data:
        assert entry.get("score") == 125, \
            f"Gap {entry.get('gap_id')} has score {entry.get('score')}, expected 125"


# T9: architecture-gap-decision-record.md exists and contains the decision string
def test_t9_architecture_decision_record_contains_decision():
    path = REPORT_DIR / "architecture-gap-decision-record.md"
    assert path.exists(), f"Missing: {path}"
    content = path.read_text(encoding="utf-8")
    assert "ISSUE_001_ACCEPTED_AS_ARCHITECTURE_GAP" in content, \
        "architecture-gap-decision-record.md must contain 'ISSUE_001_ACCEPTED_AS_ARCHITECTURE_GAP'"


# T10: target-writer-library-matrix.json exists and all entries have exists == false
def test_t10_target_writer_matrix_all_missing():
    data = load_json("target-writer-library-matrix.json")
    assert len(data) == 4, f"Expected 4 writer matrix entries, got {len(data)}"
    for entry in data:
        assert entry.get("exists") is False, \
            f"Writer {entry.get('target_writer')} has exists != false (writer should not exist)"


# T11: Export Policy — no gap in blocked ledger has an unexpected classification
def test_t11_export_policy_blocked_classification_correct():
    data = load_json("blocked-dogfood-gap-ledger.json")
    allowed_classifications = {
        "GAP_DOGFOOD_EXTERNAL",
        "GAP_DOGFOOD_EXTERNAL_ARCHITECTURE_BLOCKED",
    }
    for entry in data:
        classification = entry.get("classification", "")
        assert classification in allowed_classifications, \
            f"Gap {entry.get('gap_id')} has unexpected classification: {classification}"


# T12: Export Policy — actionable-gap-replacement-candidates contains zero entries from blocked ledger
def test_t12_export_policy_no_blocked_gap_in_candidates():
    candidates = load_json("actionable-gap-replacement-candidates.json")
    ledger = load_json("blocked-dogfood-gap-ledger.json")
    blocked_ids = {e.get("gap_id") for e in ledger}
    for candidate in candidates:
        cid = candidate.get("gap_id", candidate.get("id", ""))
        assert cid not in blocked_ids, \
            f"Export Policy violation: blocked gap {cid} found in actionable candidates"
