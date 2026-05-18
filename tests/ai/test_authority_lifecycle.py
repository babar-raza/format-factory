"""Tests for artifact authority lifecycle validator."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.ai.schemas.models import ArtifactAuthorityStateValue
from tools.ai.validators.authority_lifecycle import can_transition, validate_transition_chain


class TestAuthorityLifecycle:
    def test_valid_first_step(self):
        assert can_transition(
            ArtifactAuthorityStateValue.ai_draft,
            ArtifactAuthorityStateValue.schema_validated,
        ) is True

    def test_invalid_skip(self):
        assert can_transition(
            ArtifactAuthorityStateValue.ai_draft,
            ArtifactAuthorityStateValue.authoritative_after_gate,
        ) is False

    def test_rejection_always_valid(self):
        for state in ArtifactAuthorityStateValue:
            if state in (
                ArtifactAuthorityStateValue.rejected,
                ArtifactAuthorityStateValue.superseded,
                ArtifactAuthorityStateValue.authoritative_after_gate,
            ):
                continue
            assert can_transition(state, ArtifactAuthorityStateValue.rejected) is True

    def test_no_transition_from_rejected(self):
        for state in ArtifactAuthorityStateValue:
            assert can_transition(ArtifactAuthorityStateValue.rejected, state) is False

    def test_valid_chain(self):
        chain = [
            ArtifactAuthorityStateValue.ai_draft,
            ArtifactAuthorityStateValue.schema_validated,
            ArtifactAuthorityStateValue.source_cited,
            ArtifactAuthorityStateValue.source_verified,
        ]
        errors = validate_transition_chain(chain)
        assert errors == []

    def test_invalid_chain_with_skip(self):
        chain = [
            ArtifactAuthorityStateValue.ai_draft,
            ArtifactAuthorityStateValue.source_verified,
        ]
        errors = validate_transition_chain(chain)
        assert len(errors) == 1
        assert "Invalid transition" in errors[0]

    def test_full_happy_path(self):
        chain = [
            ArtifactAuthorityStateValue.ai_draft,
            ArtifactAuthorityStateValue.schema_validated,
            ArtifactAuthorityStateValue.source_cited,
            ArtifactAuthorityStateValue.source_verified,
            ArtifactAuthorityStateValue.contradiction_checked,
            ArtifactAuthorityStateValue.evaluator_passed,
            ArtifactAuthorityStateValue.accepted_for_planning,
            ArtifactAuthorityStateValue.accepted_for_tests,
            ArtifactAuthorityStateValue.accepted_for_source_requirements,
            ArtifactAuthorityStateValue.authoritative_after_gate,
        ]
        errors = validate_transition_chain(chain)
        assert errors == []
