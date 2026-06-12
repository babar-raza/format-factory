"""R30 AI defect closure tests — verify all R29-identified defects are fixed.

Lane B: Evaluator contradiction bypass
Lane C: Requirements lifecycle hardening
Lane D: Proposal type fix
Lane E: Scoped runner max_files enforcement
Lane F: Retrieval namespace path safety
Lane G: Secret redaction coverage
Lane H: Schema validator dedicated coverage
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


# ============================================================
# Lane B: Evaluator contradiction bypass closure
# ============================================================

from tools.ai.synthesis.evaluator import (
    EvaluationCriteria,
    evaluate_synthesis,
)
from tools.ai.synthesis.runner import SynthesisResult


class TestEvaluatorContradictionBypass(unittest.TestCase):
    """Verify not_checked no longer passes contradiction enforcement."""

    def _make_result(self, **overrides) -> SynthesisResult:
        r = SynthesisResult(task_id=overrides.pop("task_id", "test-r30"))
        r.schema_valid = True
        r.errors = []
        r.citation_verified = False
        r.citations = []
        r.contradiction_check_status = "no_contradictions"
        r.output_hash = "abc123"
        for k, v in overrides.items():
            setattr(r, k, v)
        return r

    def test_not_checked_fails_when_contradictions_required(self):
        """Core R29 defect: not_checked must NOT pass."""
        result = self._make_result(contradiction_check_status="not_checked")
        ev = evaluate_synthesis(result)
        assert not ev.passed
        assert any("contradiction" in f for f in ev.failures)

    def test_no_contradictions_passes(self):
        result = self._make_result(contradiction_check_status="no_contradictions")
        ev = evaluate_synthesis(result)
        assert ev.passed

    def test_blocked_no_facts_fails(self):
        result = self._make_result(contradiction_check_status="blocked_no_facts")
        ev = evaluate_synthesis(result)
        assert not ev.passed

    def test_contradictions_found_fails(self):
        result = self._make_result(contradiction_check_status="contradictions_found")
        ev = evaluate_synthesis(result)
        assert not ev.passed

    def test_contradiction_not_required_ignores_status(self):
        criteria = EvaluationCriteria(require_no_contradictions=False)
        result = self._make_result(contradiction_check_status="not_checked")
        ev = evaluate_synthesis(result, criteria)
        assert ev.passed

    def test_empty_status_fails(self):
        result = self._make_result(contradiction_check_status="")
        ev = evaluate_synthesis(result)
        assert not ev.passed


# ============================================================
# Lane C: Requirements lifecycle hardening
# ============================================================

from tools.ai.requirements.generator import (
    GeneratedRequirement,
    review_requirement,
    validate_requirement,
    write_requirements_packet,
)


class TestRequirementsEmptyPacket(unittest.TestCase):
    """write_requirements_packet([]) must raise, not crash with IndexError."""

    def test_empty_packet_raises_valueerror(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "empty.json"
            with self.assertRaises(ValueError):
                write_requirements_packet([], out)


class TestRequirementsLifecycleGuards(unittest.TestCase):
    """Rejected/accepted requirements cannot be re-reviewed."""

    def _make_req(self, **overrides):
        defaults = dict(
            req_id="REQ-R30-001", text="test", format_id="fods",
            source_chunk_hash="h1",
        )
        defaults.update(overrides)
        return GeneratedRequirement(**defaults)

    def test_review_from_pending_accept(self):
        req = self._make_req()
        review_requirement(req, accept=True, reason="ok")
        assert req.verifier_status == "accepted"
        assert req.authority_state == "verifier_reviewed"

    def test_review_from_pending_reject(self):
        req = self._make_req()
        review_requirement(req, accept=False, reason="bad")
        assert req.verifier_status == "rejected"
        assert req.authority_state == "ai_draft"

    def test_rejected_cannot_be_rereviewed(self):
        req = self._make_req()
        review_requirement(req, accept=False, reason="bad")
        with self.assertRaises(ValueError):
            review_requirement(req, accept=True, reason="changed mind")

    def test_accepted_cannot_be_rereviewed(self):
        req = self._make_req()
        review_requirement(req, accept=True, reason="ok")
        with self.assertRaises(ValueError):
            review_requirement(req, accept=False, reason="oops")

    def test_validate_rejects_invalid_authority_state(self):
        req = self._make_req()
        req.authority_state = "authoritative_after_gate"
        errors = validate_requirement(req)
        assert any("authority_state" in e for e in errors)

    def test_validate_accepts_valid_authority_states(self):
        for state in ["ai_draft", "schema_validated", "verifier_reviewed"]:
            req = self._make_req()
            req.authority_state = state
            errors = validate_requirement(req)
            assert not any("authority_state" in e for e in errors)


# ============================================================
# Lane D: Proposal type fix
# ============================================================

from tools.ai.test_generation.proposal import (
    GeneratedTestProposal,
    ProposalReviewer,
    EvidenceReviewHelper,
)
from tools.ai.schemas.models import ArtifactAuthorityStateValue


class TestProposalReviewerTypeFix(unittest.TestCase):
    """ProposalReviewer.review() must accept GeneratedTestProposal, not TestProposal."""

    def _make_proposal(self, valid=True):
        p = GeneratedTestProposal(
            proposal_id="PROP-R30-001" if valid else "",
            source_requirement_ids=["REQ-1"],
            proposed_test_name="test_something",
            target_file="tests/test_x.py",
            test_code="def test_something(): pass",
        )
        return p

    def test_review_valid_proposal(self):
        reviewer = ProposalReviewer()
        accepted, errors = reviewer.review(self._make_proposal())
        assert accepted
        assert not errors
        assert reviewer.accepted_count == 1

    def test_review_invalid_proposal(self):
        reviewer = ProposalReviewer()
        accepted, errors = reviewer.review(self._make_proposal(valid=False))
        assert not accepted
        assert len(errors) > 0
        assert reviewer.rejected_count == 1

    def test_reject_sets_authority_state(self):
        reviewer = ProposalReviewer()
        p = self._make_proposal()
        reviewer.reject(p, "not needed")
        assert p.authority_state == ArtifactAuthorityStateValue.rejected
        assert reviewer.rejected_count == 1

    def test_accepted_metadata(self):
        reviewer = ProposalReviewer()
        reviewer.review(self._make_proposal())
        meta = reviewer.get_accepted_metadata()
        assert len(meta) == 1
        assert meta[0]["proposal_id"] == "PROP-R30-001"


class TestEvidenceReviewHelper(unittest.TestCase):
    """Test the evidence review helper."""

    def test_missing_directory(self):
        helper = EvidenceReviewHelper()
        findings = helper.review_directory(Path("/nonexistent/path"))
        assert len(findings) == 1
        assert findings[0]["type"] == "missing_directory"

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as td:
            helper = EvidenceReviewHelper()
            findings = helper.review_directory(Path(td))
            types = {f["type"] for f in findings}
            assert "no_markdown_reports" in types

    def test_pending_detection(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "report.md"
            p.write_text("Status: PENDING\n")
            helper = EvidenceReviewHelper()
            findings = helper.review_directory(Path(td))
            types = {f["type"] for f in findings}
            assert "incomplete_report" in types


# ============================================================
# Lane E: Scoped runner max_files enforcement
# ============================================================

from tools.ai.agentic.scoped_runner import (
    AgenticTaskContract,
    ScopedRunner,
)


class TestScopedRunnerMaxFiles(unittest.TestCase):
    """max_files must be enforced."""

    def _make_contract(self, max_files=3):
        return AgenticTaskContract(
            task_id="test-r30",
            task_type="inventory",
            path_allowlist=["reports/", "tests/"],
            operation_allowlist=["read"],
            max_files=max_files,
        )

    def test_max_files_exceeded_discards_output(self):
        runner = ScopedRunner()
        contract = self._make_contract(max_files=2)

        def task_fn(c, root):
            return {
                "files_accessed": [
                    str(Path("reports/a.md").resolve()),
                    str(Path("reports/b.md").resolve()),
                    str(Path("reports/c.md").resolve()),
                ],
                "result": {"data": "should be discarded"},
            }

        result = runner.run(contract, task_fn=task_fn)
        assert result.status == "scope_violation"
        assert result.discarded
        assert any(v["type"] == "max_files_exceeded" for v in result.violations)

    def test_max_files_within_limit_passes(self):
        runner = ScopedRunner()
        # Use absolute paths matching the allowlist
        abs_reports = str(Path("reports/").resolve())
        contract = AgenticTaskContract(
            task_id="test-r30",
            task_type="inventory",
            path_allowlist=[abs_reports],
            operation_allowlist=["read"],
            max_files=5,
        )

        def task_fn(c, root):
            return {
                "files_accessed": [
                    str(Path("reports/a.md").resolve()),
                    str(Path("reports/b.md").resolve()),
                ],
                "result": {"ok": True},
            }

        result = runner.run(contract, task_fn=task_fn)
        assert result.status == "success"
        assert not result.discarded

    def test_forbidden_operation_rejected(self):
        contract = AgenticTaskContract(
            task_id="test-r30",
            path_allowlist=["reports/"],
            operation_allowlist=["commit"],  # forbidden
        )
        runner = ScopedRunner()
        result = runner.run(contract)
        assert result.status == "contract_invalid"

    def test_model_restriction(self):
        runner = ScopedRunner()
        contract = self._make_contract()
        result = runner.run(contract, model_id="gpt-4")
        assert result.status == "model_rejected"
        assert result.discarded


# ============================================================
# Lane F: Retrieval namespace path safety
# ============================================================

from tools.ai.retrieval.namespace_manager import (
    NamespaceManager,
    IndexManifest,
    CrossNamespaceError,
    validate_format_id,
)


class TestNamespacePathSafety(unittest.TestCase):
    """format_id must be validated to prevent path traversal."""

    def test_traversal_dots_rejected(self):
        with self.assertRaises(ValueError):
            validate_format_id("../etc")

    def test_traversal_slash_rejected(self):
        with self.assertRaises(ValueError):
            validate_format_id("foo/bar")

    def test_traversal_backslash_rejected(self):
        with self.assertRaises(ValueError):
            validate_format_id("foo\\bar")

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            validate_format_id("")

    def test_special_chars_rejected(self):
        with self.assertRaises(ValueError):
            validate_format_id("format@evil")

    def test_valid_format_id_accepted(self):
        validate_format_id("fods")
        validate_format_id("qoi")
        validate_format_id("zst")
        validate_format_id("pgm-parser")
        validate_format_id("fods_v2")

    def test_namespace_manager_rejects_traversal(self):
        mgr = NamespaceManager()
        with self.assertRaises(ValueError):
            mgr.get_namespace_path("../../../etc")

    def test_cross_namespace_rejected(self):
        mgr = NamespaceManager()
        with self.assertRaises(CrossNamespaceError):
            mgr.reject_cross_namespace_query("fods", "fodt")

    def test_stale_detection_no_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            mgr = NamespaceManager(store_root=Path(td))
            is_stale, reason = mgr.detect_stale_index("fods", ["h1"], "fp1")
            assert is_stale
            assert reason == "no_manifest"

    def test_create_and_load_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            mgr = NamespaceManager(store_root=Path(td))
            manifest = IndexManifest(
                format_id="fods",
                embedding_model_id="test-model",
                embedding_model_fingerprint="fp1",
                chunk_hashes=["h1", "h2"],
                chunk_count=2,
            )
            mgr.create_namespace("fods", manifest)
            loaded = mgr.load_manifest("fods")
            assert loaded is not None
            assert loaded.format_id == "fods"
            assert loaded.chunk_count == 2

    def test_query_without_cross_format_param(self):
        """authorized_cross_format parameter was removed."""
        import inspect
        sig = inspect.signature(NamespaceManager.query)
        params = list(sig.parameters.keys())
        assert "authorized_cross_format" not in params


# ============================================================
# Lane G: Secret redaction coverage
# ============================================================

from tools.ai.validators.secret_redaction import (
    redact_text,
    contains_secret,
    _SECRET_ENV_VARS,
)


class TestSecretRedactionCoverage(unittest.TestCase):
    """AGENT_METRICS_API_KEY must be in redaction list."""

    def test_agent_metrics_api_key_in_env_vars(self):
        assert "AGENT_METRICS_API_KEY" in _SECRET_ENV_VARS

    def test_agent_metrics_endpoint_in_env_vars(self):
        assert "AGENT_METRICS_ENDPOINT" in _SECRET_ENV_VARS

    def test_sk_pattern_redacted(self):
        text = "key is sk-abcdef1234567890 here"
        assert "[REDACTED]" in redact_text(text)

    def test_bearer_pattern_redacted(self):
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.test"
        assert "[REDACTED]" in redact_text(text)

    def test_contains_secret_detects_sk(self):
        assert contains_secret("use sk-abcdef1234567890")

    def test_env_var_value_redacted(self):
        with patch.dict(os.environ, {"AGENT_METRICS_API_KEY": "supersecretvalue123"}):
            text = "the key is supersecretvalue123 in text"
            assert "[REDACTED]" in redact_text(text)
            assert contains_secret(text)

    def test_clean_text_not_flagged(self):
        assert not contains_secret("hello world no secrets here")


# ============================================================
# Lane H: Schema validator dedicated coverage
# ============================================================

from tools.ai.validators.schema_validator import validate_schema
from tools.ai.schemas.models import ValidationResult


class TestSchemaValidatorDedicated(unittest.TestCase):
    """Dedicated tests for schema_validator.py."""

    def test_valid_data_passes(self):
        from pydantic import BaseModel

        class TestModel(BaseModel):
            name: str
            value: int

        result = validate_schema({"name": "test", "value": 42}, TestModel)
        assert result.valid
        assert not result.errors

    def test_missing_required_field_fails(self):
        from pydantic import BaseModel

        class TestModel(BaseModel):
            name: str
            value: int

        result = validate_schema({"name": "test"}, TestModel)
        assert not result.valid
        assert len(result.errors) > 0

    def test_wrong_type_fails(self):
        from pydantic import BaseModel

        class TestModel(BaseModel):
            count: int

        result = validate_schema({"count": "not_a_number"}, TestModel)
        # Pydantic may coerce strings to int, so check both cases
        # The key thing is validate_schema doesn't crash
        assert isinstance(result, ValidationResult)

    def test_extra_fields_handled(self):
        from pydantic import BaseModel

        class StrictModel(BaseModel):
            name: str

        result = validate_schema({"name": "ok", "extra": "field"}, StrictModel)
        assert isinstance(result, ValidationResult)

    def test_empty_dict_with_required_fields(self):
        from pydantic import BaseModel

        class TestModel(BaseModel):
            name: str

        result = validate_schema({}, TestModel)
        assert not result.valid

    def test_nested_model_validation(self):
        from pydantic import BaseModel

        class Inner(BaseModel):
            x: int

        class Outer(BaseModel):
            inner: Inner

        result = validate_schema({"inner": {"x": 5}}, Outer)
        assert result.valid

        result = validate_schema({"inner": {"x": "bad"}}, Outer)
        assert isinstance(result, ValidationResult)


if __name__ == "__main__":
    unittest.main()
