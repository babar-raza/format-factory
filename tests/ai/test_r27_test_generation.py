"""Lane H tests — AI test generation and evidence review.

Tests for proposal validation, reviewer, rejection, and evidence review helper.
"""

import pytest
from pathlib import Path

from tools.ai.schemas.models import ArtifactAuthorityStateValue
from tools.ai.test_generation.proposal import (
    EvidenceReviewHelper,
    ProposalReviewer,
    GeneratedTestProposal,
)


class TestProposalValidation:
    def test_valid_proposal(self):
        proposal = GeneratedTestProposal(
            proposal_id="tp-001",
            source_requirement_ids=["REQ-001"],
            proposed_test_name="test_fods_xml_parsing",
            target_file="tests/test_fods.py",
            test_code="def test_fods(): assert True",
        )
        errors = proposal.validate()
        assert errors == []

    def test_missing_proposal_id(self):
        proposal = GeneratedTestProposal(
            proposed_test_name="test_x",
            target_file="tests/test_x.py",
            test_code="def test_x(): pass",
            source_requirement_ids=["R1"],
        )
        errors = proposal.validate()
        assert "missing proposal_id" in errors

    def test_missing_source_ids(self):
        proposal = GeneratedTestProposal(
            proposal_id="tp-001",
            proposed_test_name="test_x",
            target_file="tests/test_x.py",
            test_code="def test_x(): pass",
        )
        errors = proposal.validate()
        assert any("source" in e for e in errors)

    def test_wrong_initial_authority(self):
        proposal = GeneratedTestProposal(
            proposal_id="tp-001",
            source_requirement_ids=["R1"],
            proposed_test_name="test_x",
            target_file="tests/test_x.py",
            test_code="def test_x(): pass",
            authority_state=ArtifactAuthorityStateValue.authoritative_after_gate,
        )
        errors = proposal.validate()
        assert any("ai_draft" in e for e in errors)


class TestProposalReviewer:
    def test_accept_valid(self):
        reviewer = ProposalReviewer()
        proposal = GeneratedTestProposal(
            proposal_id="tp-001",
            source_requirement_ids=["R1"],
            proposed_test_name="test_x",
            target_file="tests/test_x.py",
            test_code="def test_x(): pass",
        )
        accepted, errors = reviewer.review(proposal)
        assert accepted is True
        assert reviewer.accepted_count == 1

    def test_reject_invalid(self):
        reviewer = ProposalReviewer()
        proposal = GeneratedTestProposal()  # all fields missing
        accepted, errors = reviewer.review(proposal)
        assert accepted is False
        assert reviewer.rejected_count == 1

    def test_explicit_rejection(self):
        reviewer = ProposalReviewer()
        proposal = GeneratedTestProposal(
            proposal_id="tp-001",
            source_requirement_ids=["R1"],
            proposed_test_name="test_x",
            target_file="tests/test_x.py",
            test_code="def test_x(): pass",
        )
        reviewer.reject(proposal, "not relevant")
        assert proposal.authority_state == ArtifactAuthorityStateValue.rejected

    def test_accepted_metadata(self):
        reviewer = ProposalReviewer()
        proposal = GeneratedTestProposal(
            proposal_id="tp-001",
            source_requirement_ids=["R1"],
            proposed_test_name="test_x",
            target_file="tests/test_x.py",
            test_code="def test_x(): pass",
        )
        reviewer.review(proposal)
        meta = reviewer.get_accepted_metadata()
        assert len(meta) == 1
        assert meta[0]["proposal_id"] == "tp-001"


class TestEvidenceReviewHelper:
    def test_missing_directory(self, tmp_path):
        helper = EvidenceReviewHelper()
        findings = helper.review_directory(tmp_path / "nonexistent")
        assert any(f["type"] == "missing_directory" for f in findings)
        assert all(f["authority_state"] == "ai_draft" for f in findings)

    def test_empty_directory(self, tmp_path):
        helper = EvidenceReviewHelper()
        findings = helper.review_directory(tmp_path)
        assert any(f["type"] == "no_markdown_reports" for f in findings)
