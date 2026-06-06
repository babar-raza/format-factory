"""
tests/supervisor/test_commit_push_external_gate.py

Lane 2 — Sprint FORMAT-FACTORY-AUTONOMY-NO-MANUAL-PROMPT-CHAIN-REPAIR-001

Regression tests: product items with commit/push/Gate next_action must NEVER
produce agent_can_execute=True in generate_next_work_items() output.
These tests guard against AF-004 (next-work-items unsafe wording) regressions.
"""

import sys
from pathlib import Path
from unittest.mock import patch

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from generate_next_worker_prompt import (
    _next_action_requires_external_gate,
    generate_next_work_items,
    _make_task_adjudication_fields,
)


# ---------------------------------------------------------------------------
# Regression: _make_task_adjudication_fields with [external-gate] label
# ---------------------------------------------------------------------------

class TestMakeTaskAdjudicationExternalGate:
    """_make_task_adjudication_fields("[external-gate]", ...) must NOT set agent_can_execute=True."""

    def test_external_gate_label_agent_can_execute_false(self):
        fields = _make_task_adjudication_fields("[external-gate]", "Commit and push FODS")
        assert fields["agent_can_execute"] is False

    def test_external_gate_label_execution_status(self):
        fields = _make_task_adjudication_fields("[external-gate]", "Gate 11 approval")
        assert fields["execution_status"] == "external-gate-pending"

    def test_agent_owned_label_agent_can_execute_true(self):
        fields = _make_task_adjudication_fields("[agent-owned]", "Implement write_gnumeric()")
        assert fields["agent_can_execute"] is True

    def test_agent_owned_label_execution_status(self):
        fields = _make_task_adjudication_fields("[agent-owned]", "Implement probe_abw()")
        assert fields["execution_status"] == "executable"

    def test_stop_reason_present_for_external_gate(self):
        fields = _make_task_adjudication_fields("[external-gate]", "Commit + push")
        assert "stop_reason_decision" in fields
        assert fields["stop_reason_decision"]  # non-empty

    def test_stop_reason_present_for_agent_owned(self):
        fields = _make_task_adjudication_fields("[agent-owned]", "Add tests")
        assert "stop_reason_decision" in fields


# ---------------------------------------------------------------------------
# AF-004 regression: exact next_action strings from poc-targets.yaml
# ---------------------------------------------------------------------------

COMMIT_PUSH_STRINGS = [
    "Authorized git commit + push (requires user authorization)",
    "Authorized git commit + push (requires explicit user authorization)",
    "git commit && git push",
    "git push origin main",
    "Commit and push when Gate 11 G11-G is approved",
    "Requires Gate 11 approval before commit + push",
    "Gate 11 G11-G approval, then git push",
    "Publication: publish to NuGet after gate approval",
    "Human required for commercial release sign-off",
    "Commercial release requires explicit user authorization",
    "Publish to NuGet requires user authorization",
    "NuGet publish — requires human authorization",
]


class TestCommitPushStringsAreExternalGate:
    """Every commit/push/Gate string from real poc-targets.yaml must classify as external-gate."""

    def test_authorized_git_commit_push(self):
        assert _next_action_requires_external_gate(
            "Authorized git commit + push (requires user authorization)"
        ) is True

    def test_authorized_git_commit_push_explicit(self):
        assert _next_action_requires_external_gate(
            "Authorized git commit + push (requires explicit user authorization)"
        ) is True

    def test_git_commit_and_push_shell(self):
        assert _next_action_requires_external_gate("git commit && git push") is True

    def test_git_push_origin_main(self):
        assert _next_action_requires_external_gate("git push origin main") is True

    def test_gate_11_g11g_then_push(self):
        assert _next_action_requires_external_gate(
            "Commit and push when Gate 11 G11-G is approved"
        ) is True

    def test_gate_11_approval_before_commit(self):
        assert _next_action_requires_external_gate(
            "Requires Gate 11 approval before commit + push"
        ) is True

    def test_g11g_then_git_push(self):
        assert _next_action_requires_external_gate(
            "Gate 11 G11-G approval, then git push"
        ) is True

    def test_nuget_publication(self):
        assert _next_action_requires_external_gate(
            "Publication: publish to NuGet after gate approval"
        ) is True

    def test_human_required_commercial(self):
        assert _next_action_requires_external_gate(
            "Human required for commercial release sign-off"
        ) is True

    def test_commercial_release_explicit_auth(self):
        assert _next_action_requires_external_gate(
            "Commercial release requires explicit user authorization"
        ) is True

    def test_publish_to_nuget_user_auth(self):
        assert _next_action_requires_external_gate(
            "Publish to NuGet requires user authorization"
        ) is True

    def test_nuget_publish_human_auth(self):
        assert _next_action_requires_external_gate(
            "NuGet publish — requires human authorization"
        ) is True


# ---------------------------------------------------------------------------
# Integration: generate_next_work_items() with mocked poc_targets
# ---------------------------------------------------------------------------

def _fake_poc_targets_commit_push(_repo_root):
    """Fake poc_targets with commit/push next_action for both product types."""
    return {
        "commercial_net_products": [
            {
                "format": "FODS",
                "next_action": "Authorized git commit + push (requires user authorization)",
            },
            {
                "format": "FODT",
                "next_action": "Gate 11 G11-G approval, then publish to NuGet",
            },
        ],
        "foss_reduced_products": [
            {
                "format": "Gnumeric",
                "next_action": "Continue implementing export_to_html",  # agent-owned
            },
            {
                "format": "ABW",
                "next_action": "Commit + push ABW package when approved",  # external-gate
            },
        ],
    }


def _fake_poc_targets_all_agent(_repo_root):
    """Fake poc_targets with only agent-owned next_actions."""
    return {
        "commercial_net_products": [
            {"format": "FODS", "next_action": "Add FODS binary writer tests"},
        ],
        "foss_reduced_products": [
            {"format": "Gnumeric", "next_action": "Implement probe_gnumeric roundtrip"},
        ],
    }


class TestGenerateNextWorkItemsCommitPushGate:
    """Integration tests: commit/push items must not be agent_can_execute=True."""

    def test_commit_push_net_product_not_agent_executable(self):
        review = {"item_grades": []}
        with patch(
            "generate_next_worker_prompt.load_poc_targets",
            side_effect=_fake_poc_targets_commit_push,
        ):
            result = generate_next_work_items(review)

        product_items = [i for i in result["items"] if i.get("source") == "product-factory"]
        fods = next((i for i in product_items if "FODS" in i["item_id"]), None)
        assert fods is not None, "FODS product item missing"
        assert fods["agent_can_execute"] is False, (
            f"FODS (commit+push) must NOT be agent_can_execute=True; got {fods}"
        )

    def test_gate_11_net_product_not_agent_executable(self):
        review = {"item_grades": []}
        with patch(
            "generate_next_worker_prompt.load_poc_targets",
            side_effect=_fake_poc_targets_commit_push,
        ):
            result = generate_next_work_items(review)

        product_items = [i for i in result["items"] if i.get("source") == "product-factory"]
        fodt = next((i for i in product_items if "FODT" in i["item_id"]), None)
        assert fodt is not None, "FODT product item missing"
        assert fodt["agent_can_execute"] is False, (
            f"FODT (Gate11+NuGet) must NOT be agent_can_execute=True; got {fodt}"
        )

    def test_agent_owned_foss_product_is_executable(self):
        """Gnumeric has agent-owned next_action → must be agent_can_execute=True."""
        review = {"item_grades": []}
        with patch(
            "generate_next_worker_prompt.load_poc_targets",
            side_effect=_fake_poc_targets_commit_push,
        ):
            result = generate_next_work_items(review)

        product_items = [i for i in result["items"] if i.get("source") == "product-factory"]
        gnumeric = next((i for i in product_items if "GNUMERIC" in i["item_id"]), None)
        assert gnumeric is not None, "Gnumeric FOSS item missing"
        assert gnumeric["agent_can_execute"] is True, (
            f"Gnumeric (agent-owned) must be agent_can_execute=True; got {gnumeric}"
        )

    def test_commit_push_foss_product_not_agent_executable(self):
        """ABW has commit+push next_action → must be agent_can_execute=False."""
        review = {"item_grades": []}
        with patch(
            "generate_next_worker_prompt.load_poc_targets",
            side_effect=_fake_poc_targets_commit_push,
        ):
            result = generate_next_work_items(review)

        product_items = [i for i in result["items"] if i.get("source") == "product-factory"]
        abw = next((i for i in product_items if "ABW" in i["item_id"]), None)
        assert abw is not None, "ABW FOSS item missing"
        assert abw["agent_can_execute"] is False, (
            f"ABW (commit+push) must NOT be agent_can_execute=True; got {abw}"
        )

    def test_all_agent_owned_are_executable(self):
        """When all next_actions are agent-owned, all products must be agent_can_execute=True."""
        review = {"item_grades": []}
        with patch(
            "generate_next_worker_prompt.load_poc_targets",
            side_effect=_fake_poc_targets_all_agent,
        ):
            result = generate_next_work_items(review)

        product_items = [i for i in result["items"] if i.get("source") == "product-factory"]
        assert len(product_items) >= 1
        for item in product_items:
            assert item["agent_can_execute"] is True, (
                f"Agent-owned item {item['item_id']} must be executable; got {item}"
            )

    def test_execution_status_external_gate_pending_for_commit_push(self):
        """External-gate items must have execution_status='external-gate-pending'."""
        review = {"item_grades": []}
        with patch(
            "generate_next_worker_prompt.load_poc_targets",
            side_effect=_fake_poc_targets_commit_push,
        ):
            result = generate_next_work_items(review)

        product_items = [i for i in result["items"] if i.get("source") == "product-factory"]
        fods = next((i for i in product_items if "FODS" in i["item_id"]), None)
        assert fods["execution_status"] == "external-gate-pending", (
            f"FODS must be external-gate-pending; got {fods['execution_status']}"
        )

    def test_execution_status_executable_for_agent_owned(self):
        """Agent-owned items must have execution_status='executable'."""
        review = {"item_grades": []}
        with patch(
            "generate_next_worker_prompt.load_poc_targets",
            side_effect=_fake_poc_targets_all_agent,
        ):
            result = generate_next_work_items(review)

        product_items = [i for i in result["items"] if i.get("source") == "product-factory"]
        assert all(i["execution_status"] == "executable" for i in product_items), (
            f"All agent-owned items must be 'executable': {[i['execution_status'] for i in product_items]}"
        )
