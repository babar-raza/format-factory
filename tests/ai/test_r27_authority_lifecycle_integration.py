"""Lane D tests — authority lifecycle integration.

Tests for state records, transition evidence, terminal states,
and no-skip enforcement.
"""


from tools.ai.schemas.models import (
    ArtifactAuthorityState,
    ArtifactAuthorityStateValue,
)
from tools.ai.validators.authority_lifecycle import (
    can_transition,
    count_by_state,
    is_terminal,
    read_state_records,
    transition_with_evidence,
    validate_transition_chain,
    write_state_record,
)


class TestNoSkipEnforcement:
    def test_no_skip_draft_to_authoritative(self):
        """Cannot skip from ai_draft directly to authoritative_after_gate."""
        assert can_transition(
            ArtifactAuthorityStateValue.ai_draft,
            ArtifactAuthorityStateValue.authoritative_after_gate,
        ) is False

    def test_valid_sequential_chain(self):
        chain = [
            ArtifactAuthorityStateValue.ai_draft,
            ArtifactAuthorityStateValue.schema_validated,
            ArtifactAuthorityStateValue.source_cited,
        ]
        assert validate_transition_chain(chain) == []

    def test_invalid_skip_chain(self):
        chain = [
            ArtifactAuthorityStateValue.ai_draft,
            ArtifactAuthorityStateValue.source_verified,  # skips schema_validated and source_cited
        ]
        errors = validate_transition_chain(chain)
        assert len(errors) > 0


class TestTerminalStates:
    def test_rejected_is_terminal(self):
        assert is_terminal(ArtifactAuthorityStateValue.rejected) is True

    def test_superseded_is_terminal(self):
        assert is_terminal(ArtifactAuthorityStateValue.superseded) is True

    def test_draft_is_not_terminal(self):
        assert is_terminal(ArtifactAuthorityStateValue.ai_draft) is False


class TestTransitionWithEvidence:
    def test_requires_evidence_path(self):
        artifact = ArtifactAuthorityState(artifact_id="a1")
        success, err = transition_with_evidence(
            artifact, ArtifactAuthorityStateValue.schema_validated, "", "reason"
        )
        assert success is False
        assert "evidence_path" in err

    def test_valid_transition_with_evidence(self):
        artifact = ArtifactAuthorityState(artifact_id="a1")
        success, err = transition_with_evidence(
            artifact, ArtifactAuthorityStateValue.schema_validated,
            "reports/test.md", "schema check passed"
        )
        assert success is True
        assert artifact.current_state == ArtifactAuthorityStateValue.schema_validated
        assert len(artifact.transitions) == 1
        assert artifact.transitions[0]["evidence_path"] == "reports/test.md"

    def test_cannot_transition_from_terminal(self):
        artifact = ArtifactAuthorityState(
            artifact_id="a1",
            current_state=ArtifactAuthorityStateValue.rejected,
        )
        success, err = transition_with_evidence(
            artifact, ArtifactAuthorityStateValue.schema_validated,
            "reports/test.md", "retry"
        )
        assert success is False
        assert "terminal" in err

    def test_accepted_planning_not_source(self):
        """accepted_for_planning cannot jump to accepted_for_source_requirements."""
        artifact = ArtifactAuthorityState(
            artifact_id="a1",
            current_state=ArtifactAuthorityStateValue.accepted_for_planning,
        )
        success, err = transition_with_evidence(
            artifact, ArtifactAuthorityStateValue.accepted_for_source_requirements,
            "reports/test.md", "skip tests"
        )
        assert success is False


class TestStateRecordIO:
    def test_write_and_read(self, tmp_path):
        state_file = tmp_path / "artifact-states.jsonl"
        artifact = ArtifactAuthorityState(artifact_id="a1")
        write_state_record(artifact, state_file)
        records = read_state_records(state_file)
        assert len(records) == 1
        assert records[0]["artifact_id"] == "a1"
        assert records[0]["current_state"] == "ai_draft"

    def test_count_by_state(self, tmp_path):
        state_file = tmp_path / "artifact-states.jsonl"
        a1 = ArtifactAuthorityState(artifact_id="a1")
        a2 = ArtifactAuthorityState(
            artifact_id="a2",
            current_state=ArtifactAuthorityStateValue.rejected,
        )
        write_state_record(a1, state_file)
        write_state_record(a2, state_file)
        counts = count_by_state(state_file)
        assert counts["ai_draft"] == 1
        assert counts["rejected"] == 1

    def test_read_nonexistent_file(self, tmp_path):
        records = read_state_records(tmp_path / "nope.jsonl")
        assert records == []
