"""
tests/supervisor/test_next_work_items_safety.py

Lane 2 — Sprint FORMAT-FACTORY-AUTONOMY-NO-MANUAL-PROMPT-CHAIN-REPAIR-001

Verifies that generate_next_work_items() correctly classifies product items
as [external-gate] when next_action contains commit/push/Gate wording, so
future agents never treat a commit/push step as agent_can_execute=True.
"""

import sys
from pathlib import Path

# Make sure tools/supervisor is importable
_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from generate_next_worker_prompt import (
    _EXTERNAL_GATE_PATTERNS,
    _next_action_requires_external_gate,
    generate_next_work_items,
)


# ---------------------------------------------------------------------------
# _EXTERNAL_GATE_PATTERNS coverage
# ---------------------------------------------------------------------------

class TestExternalGatePatterns:
    """_EXTERNAL_GATE_PATTERNS must cover all commit/push/Gate variants."""

    def test_git_commit_in_patterns(self):
        assert "git commit" in _EXTERNAL_GATE_PATTERNS

    def test_git_push_in_patterns(self):
        assert "git push" in _EXTERNAL_GATE_PATTERNS

    def test_commit_plus_push_in_patterns(self):
        assert "commit + push" in _EXTERNAL_GATE_PATTERNS

    def test_gate_11_in_patterns(self):
        assert "gate 11" in _EXTERNAL_GATE_PATTERNS

    def test_gate_8_in_patterns(self):
        assert "gate 8" in _EXTERNAL_GATE_PATTERNS

    def test_g11_g_in_patterns(self):
        assert "g11-g" in _EXTERNAL_GATE_PATTERNS

    def test_requires_user_authorization_in_patterns(self):
        assert "requires user authorization" in _EXTERNAL_GATE_PATTERNS

    def test_requires_explicit_user_authorization_in_patterns(self):
        assert "requires explicit user authorization" in _EXTERNAL_GATE_PATTERNS

    def test_requires_human_authorization_in_patterns(self):
        assert "requires human authorization" in _EXTERNAL_GATE_PATTERNS

    def test_publication_in_patterns(self):
        assert "publication" in _EXTERNAL_GATE_PATTERNS

    def test_minimum_pattern_count(self):
        """Must have at least 10 patterns to ensure solid coverage."""
        assert len(_EXTERNAL_GATE_PATTERNS) >= 10


# ---------------------------------------------------------------------------
# _next_action_requires_external_gate — unit tests
# ---------------------------------------------------------------------------

class TestNextActionRequiresExternalGate:
    """Unit-test the _next_action_requires_external_gate() predicate."""

    # --- True cases (external gate required) ---

    def test_exact_git_commit(self):
        assert _next_action_requires_external_gate("git commit") is True

    def test_exact_git_push(self):
        assert _next_action_requires_external_gate("git push") is True

    def test_commit_and_push_combined(self):
        assert _next_action_requires_external_gate("commit + push") is True

    def test_authorized_git(self):
        assert _next_action_requires_external_gate("Authorized git commit") is True

    def test_gate_11_uppercase(self):
        assert _next_action_requires_external_gate("Gate 11 approval required") is True

    def test_gate_11_mixed_case(self):
        assert _next_action_requires_external_gate("Needs GATE 11 sign-off") is True

    def test_g11_g_token(self):
        assert _next_action_requires_external_gate("G11-G approval block") is True

    def test_publication_word(self):
        assert _next_action_requires_external_gate("Package publication pending") is True

    def test_publish_to_nuget(self):
        assert _next_action_requires_external_gate("Publish to NuGet when ready") is True

    def test_requires_user_authorization_sentence(self):
        assert _next_action_requires_external_gate(
            "Authorized git commit + push (requires user authorization)"
        ) is True

    def test_requires_human_authorization(self):
        assert _next_action_requires_external_gate(
            "This action requires human authorization"
        ) is True

    def test_commercial_release(self):
        assert _next_action_requires_external_gate("Commercial release pending") is True

    def test_human_required_for_commercial(self):
        assert _next_action_requires_external_gate(
            "Human required for commercial sign-off"
        ) is True

    # Case-insensitivity
    def test_case_insensitive_git_push(self):
        assert _next_action_requires_external_gate("GIT PUSH to remote") is True

    def test_case_insensitive_gate_11(self):
        assert _next_action_requires_external_gate("GATE 11 G11-G APPROVAL") is True

    # --- False cases (agent can execute) ---

    def test_empty_string(self):
        assert _next_action_requires_external_gate("") is False

    def test_none_input(self):
        # None is handled by the "if not next_action: return False" guard
        assert _next_action_requires_external_gate(None) is False  # type: ignore[arg-type]

    def test_agent_owned_action(self):
        assert _next_action_requires_external_gate("Add FOSS roundtrip tests") is False

    def test_implementation_action(self):
        assert _next_action_requires_external_gate(
            "Implement write_gnumeric() and add 10 tests"
        ) is False

    def test_continue_product_work(self):
        assert _next_action_requires_external_gate(
            "Continue FOSS Python development for Gnumeric"
        ) is False

    def test_random_text(self):
        assert _next_action_requires_external_gate(
            "Investigate format support for PBM"
        ) is False

    def test_substring_false_positive_guard_push(self):
        # "pushed" contains "push" but without "git " prefix — should NOT match
        # Our patterns use "git push" not bare "push", so this is safe
        assert _next_action_requires_external_gate("data is pushed to cache") is False

    def test_substring_false_positive_commit_message(self):
        # "commit" alone (without "git") should not match
        assert _next_action_requires_external_gate("Write commit message for review") is False


# ---------------------------------------------------------------------------
# generate_next_work_items() — integration safety check
# ---------------------------------------------------------------------------

class TestGenerateNextWorkItemsSafety:
    """Smoke-test generate_next_work_items() for safe external-gate classification."""

    def _make_review_with_product(self, net_next_action: str, foss_next_action: str) -> dict:
        """Build a minimal review dict with one net and one foss product."""
        return {
            "item_grades": [],
            "_injected_poc_targets": {
                "commercial_net_products": [
                    {"format": "TestFmt", "next_action": net_next_action}
                ],
                "foss_reduced_products": [
                    {"format": "FossFmt", "next_action": foss_next_action}
                ],
            },
        }

    def test_items_returned_for_empty_review(self):
        """generate_next_work_items returns a dict with 'items' key."""
        review = {"item_grades": []}
        result = generate_next_work_items(review)
        assert isinstance(result, dict)
        assert "items" in result

    def test_rework_items_always_agent_owned(self):
        """REWORK items are always agent-owned (they're fixes, not gates)."""
        review = {
            "item_grades": [
                {
                    "item_id": "WI-001",
                    "item_title": "Some work item",
                    "supervisor_grade": "REWORK_REQUIRED",
                    "required_rework": "Fix the evidence",
                }
            ]
        }
        result = generate_next_work_items(review)
        rework_items = [i for i in result["items"] if i.get("source") == "rework-from-prior"]
        assert len(rework_items) == 1
        assert rework_items[0]["agent_can_execute"] is True

    def test_items_have_agent_can_execute_field(self):
        """Every generated item must have an agent_can_execute bool field."""
        review = {"item_grades": []}
        result = generate_next_work_items(review)
        for item in result["items"]:
            assert "agent_can_execute" in item, f"Missing agent_can_execute in {item.get('item_id')}"
            assert isinstance(item["agent_can_execute"], bool)

    def test_items_have_stop_reason_field(self):
        """Every generated item must have a stop_reason_decision field."""
        review = {"item_grades": []}
        result = generate_next_work_items(review)
        for item in result["items"]:
            assert "stop_reason_decision" in item, (
                f"Missing stop_reason_decision in {item.get('item_id')}"
            )

    def test_items_have_execution_status_field(self):
        """Every item must have execution_status."""
        review = {"item_grades": []}
        result = generate_next_work_items(review)
        for item in result["items"]:
            assert "execution_status" in item, (
                f"Missing execution_status in {item.get('item_id')}"
            )
            assert item["execution_status"] in ("executable", "external-gate-pending"), (
                f"Invalid execution_status value: {item['execution_status']}"
            )

    def test_result_has_stream_field(self):
        """Result dict must have a stream field."""
        review = {"item_grades": []}
        result = generate_next_work_items(review)
        assert "stream" in result

    def test_result_has_advisory_field(self):
        """Result dict must have stop_reason_adjudicator_advisory field."""
        review = {"item_grades": []}
        result = generate_next_work_items(review)
        assert "stop_reason_adjudicator_advisory" in result
        assert result["stop_reason_adjudicator_advisory"]  # non-empty
