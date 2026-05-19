"""R29 Lane D — AI synthesis/evaluator/requirements production hardening tests.

Extends R28 tests with:
- Malformed citation syntax
- Citation source hash mismatch
- Missing verified facts
- Contradictory generated requirement
- Authority escalation attempt
- Evaluator threshold boundary behavior
- Multi-format contamination
- Requirements reviewer rejection
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from tools.ai.synthesis.citation_verifier import (
    CitationResult,
    VerificationReport,
    verify_all_citations,
    verify_single_citation,
)
from tools.ai.synthesis.contradiction_detector import (
    check_output_contradictions,
)
from tools.ai.synthesis.evaluator import (
    EvaluationCriteria,
    EvaluationResult,
    evaluate_synthesis,
)
from tools.ai.synthesis.runner import SynthesisResult
from tools.ai.requirements.generator import (
    GeneratedRequirement,
    validate_requirement,
    review_requirement,
    generate_requirements_from_synthesis,
    write_requirements_packet,
    REQUIREMENT_SCHEMA,
)


class TestCitationMalformedSyntax:
    """Citations with malformed or missing fields."""

    def test_empty_citation_dict(self):
        result = verify_single_citation({}, 0)
        assert not result.valid
        assert "missing_source_field" in result.errors

    def test_citation_missing_text(self):
        result = verify_single_citation({"source": "specs/fods.md"}, 0)
        assert not result.valid
        assert "missing_text_field" in result.errors

    def test_citation_missing_source(self):
        result = verify_single_citation({"text": "some text"}, 0)
        assert not result.valid
        assert "missing_source_field" in result.errors

    def test_citation_empty_strings(self):
        result = verify_single_citation({"source": "", "text": ""}, 0)
        assert not result.valid

    def test_citation_with_none_values(self):
        result = verify_single_citation({"source": None, "text": None}, 0)
        assert not result.valid

    def test_all_citations_empty_list(self):
        report = verify_all_citations([])
        assert report.total == 0
        assert not report.all_valid  # Empty = not valid


class TestCitationHashMismatch:
    """Citation verification hash behavior."""

    def test_same_citation_produces_same_hash(self):
        cit = {"source": "specs/fods.md", "text": "cell element"}
        r1 = verify_single_citation(cit, 0, source_texts={"specs/fods.md": "cell element content"})
        r2 = verify_single_citation(cit, 0, source_texts={"specs/fods.md": "cell element content"})
        assert r1.verification_hash == r2.verification_hash
        assert r1.verification_hash != ""

    def test_different_text_different_hash(self):
        cit1 = {"source": "specs/fods.md", "text": "cell element"}
        cit2 = {"source": "specs/fods.md", "text": "row element"}
        r1 = verify_single_citation(cit1, 0, source_texts={"specs/fods.md": "cell element row element"})
        r2 = verify_single_citation(cit2, 0, source_texts={"specs/fods.md": "cell element row element"})
        assert r1.verification_hash != r2.verification_hash

    def test_text_not_found_in_source(self):
        cit = {"source": "specs/fods.md", "text": "fabricated content"}
        r = verify_single_citation(cit, 0, source_texts={"specs/fods.md": "actual content"})
        assert r.source_exists
        assert not r.text_found_in_source
        assert "text_not_found_in_source" in r.errors


class TestContradictionEdgeCases:
    """Contradiction detector edge cases."""

    def test_none_output(self):
        report = check_output_contradictions(None)
        assert report is not None

    def test_empty_string_output(self):
        report = check_output_contradictions("")
        assert report is not None

    def test_no_contradiction_in_consistent_text(self):
        report = check_output_contradictions("FODS supports flat XML storage for spreadsheets.")
        assert report.status in ("no_contradictions", "blocked_no_facts_source", "no_facts_loaded")


class TestEvaluatorThresholdBoundary:
    """Evaluator threshold and boundary behavior."""

    def _make_result(self, **overrides) -> SynthesisResult:
        r = SynthesisResult(task_id=overrides.pop("task_id", "test-eval"))
        r.output_hash = "abc123"
        r.schema_valid = True
        r.citations = []
        r.citation_verified = False
        r.contradiction_check_status = "no_contradictions"
        r.errors = []
        for k, v in overrides.items():
            setattr(r, k, v)
        return r

    def test_all_checks_pass(self):
        r = self._make_result()
        ev = evaluate_synthesis(r)
        assert ev.passed
        assert ev.score == 1.0

    def test_single_failure_drops_score(self):
        r = self._make_result(schema_valid=False)
        ev = evaluate_synthesis(r)
        assert not ev.passed
        assert ev.score < 1.0

    def test_error_count_boundary(self):
        """Exactly at max_error_count should pass."""
        r = self._make_result(errors=["one"])
        criteria = EvaluationCriteria(max_error_count=1)
        ev = evaluate_synthesis(r, criteria)
        assert ev.checks.get("errors_within_limit") is True

    def test_error_count_over_boundary(self):
        """One over max_error_count should fail."""
        r = self._make_result(errors=["one", "two"])
        criteria = EvaluationCriteria(max_error_count=1)
        ev = evaluate_synthesis(r, criteria)
        assert ev.checks.get("errors_within_limit") is False

    def test_citations_required_but_missing(self):
        r = self._make_result(citation_verified=False, citations=[])
        criteria = EvaluationCriteria(require_citations=True, min_citation_count=1)
        ev = evaluate_synthesis(r, criteria)
        assert not ev.passed
        assert "citations_insufficient:0" in ev.failures

    def test_contradiction_detected_fails(self):
        r = self._make_result(contradiction_check_status="contradictions_found")
        ev = evaluate_synthesis(r)
        assert not ev.passed
        assert any("contradiction" in f for f in ev.failures)

    def test_missing_output_hash_fails(self):
        r = self._make_result(output_hash="")
        ev = evaluate_synthesis(r)
        assert not ev.passed
        assert "missing_output_hash" in ev.failures


class TestAuthorityEscalationGuard:
    """Ensure AI outputs cannot self-escalate authority."""

    def test_requirement_starts_as_ai_draft(self):
        req = GeneratedRequirement(
            req_id="REQ-TEST-001",
            text="Test requirement",
            format_id="test",
        )
        assert req.authority_state == "ai_draft"

    def test_review_accept_sets_verifier_reviewed(self):
        req = GeneratedRequirement(
            req_id="REQ-TEST-001",
            text="Test requirement",
            format_id="test",
        )
        review_requirement(req, accept=True, reason="verified")
        assert req.authority_state == "verifier_reviewed"
        assert req.verifier_status == "accepted"

    def test_review_reject_keeps_ai_draft(self):
        req = GeneratedRequirement(
            req_id="REQ-TEST-001",
            text="Test requirement",
            format_id="test",
        )
        review_requirement(req, accept=False, reason="not verified")
        assert req.authority_state == "ai_draft"
        assert req.verifier_status == "rejected"

    def test_cannot_set_authoritative_via_generation(self):
        """Generation must always produce ai_draft."""
        output = {
            "requirements": [
                {"id": "REQ-ATTACK-001", "text": "backdoor", "authority_state": "authoritative_after_gate"}
            ]
        }
        reqs = generate_requirements_from_synthesis(output, "test")
        assert len(reqs) == 1
        assert reqs[0].authority_state == "ai_draft"

    def test_invalid_priority_rejected(self):
        req = GeneratedRequirement(
            req_id="REQ-TEST-001",
            text="Test",
            format_id="test",
            source_chunk_hash="abc",
            priority="ADMIN_OVERRIDE",
        )
        errors = validate_requirement(req)
        assert any("invalid priority" in e for e in errors)


class TestMultiFormatContamination:
    """Requirements must not mix format IDs."""

    def test_requirements_from_one_format(self):
        output = {
            "requirements": [
                {"id": "REQ-FODS-001", "text": "spreadsheet cells", "source_chunk_hash": "abc"},
                {"id": "REQ-FODS-002", "text": "row grouping", "source_chunk_hash": "def"},
            ]
        }
        reqs = generate_requirements_from_synthesis(output, "fods")
        for r in reqs:
            assert r.format_id == "fods"

    def test_requirements_packet_single_format(self, tmp_path):
        reqs = [
            GeneratedRequirement(req_id="REQ-FODS-001", text="cell", format_id="fods", source_chunk_hash="abc"),
            GeneratedRequirement(req_id="REQ-FODS-002", text="row", format_id="fods", source_chunk_hash="def"),
        ]
        for r in reqs:
            r.compute_hash()
        out = write_requirements_packet(reqs, tmp_path / "packet.json")
        import json
        data = json.loads(out.read_text())
        assert data["format"] == "fods"
        assert data["authority_state"] == "ai_draft"
        assert data["count"] == 2


class TestRequirementsValidationEdgeCases:
    """Edge cases in requirement validation."""

    def test_missing_all_fields(self):
        req = GeneratedRequirement(req_id="", text="", format_id="")
        errors = validate_requirement(req)
        assert len(errors) >= 3

    def test_valid_requirement_no_errors(self):
        req = GeneratedRequirement(
            req_id="REQ-FODS-001",
            text="FODS cells must support text content",
            format_id="fods",
            source_chunk_hash="abc123",
            priority="SPEC",
        )
        errors = validate_requirement(req)
        assert errors == []

    def test_all_valid_priorities_accepted(self):
        for p in REQUIREMENT_SCHEMA["valid_priorities"]:
            req = GeneratedRequirement(
                req_id="REQ-TEST", text="test", format_id="test",
                source_chunk_hash="x", priority=p,
            )
            errors = validate_requirement(req)
            assert not any("invalid priority" in e for e in errors), f"Priority {p} rejected"

    def test_generation_from_empty_synthesis(self):
        reqs = generate_requirements_from_synthesis({}, "test")
        assert reqs == []

    def test_generation_skips_non_dict_entries(self):
        output = {"requirements": ["not a dict", 42, None]}
        reqs = generate_requirements_from_synthesis(output, "test")
        assert reqs == []
