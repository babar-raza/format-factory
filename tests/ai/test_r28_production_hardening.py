"""R28 Lane C — AI production hardening tests.

Tests for citation verifier, contradiction detector, evaluator,
and deeper negative tests for existing modules.
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.ai.synthesis.citation_verifier import (
    CitationResult,
    VerificationReport,
    verify_all_citations,
    verify_single_citation,
)
from tools.ai.synthesis.contradiction_detector import (
    ContradictionReport,
    check_output_contradictions,
)
from tools.ai.synthesis.evaluator import (
    EvaluationCriteria,
    EvaluationResult,
    evaluate_synthesis,
)
from tools.ai.synthesis.runner import SynthesisResult, run_synthesis
from tools.ai.schemas.models import AITaskContract, ArtifactAuthorityStateValue
from tools.ai.agentic.scoped_runner import (
    AgenticTaskContract,
    ScopedRunner,
    FORBIDDEN_OPERATIONS,
)
from tools.ai.retrieval.namespace_manager import (
    CrossNamespaceError,
    IndexManifest,
    NamespaceManager,
)
from tools.ai.telemetry.drain import (
    map_spool_to_agent_metrics,
    validate_drain_payload,
)
from tools.ai.validators.risk_controls import run_all_risk_checks


# ============================================================
# Citation Verifier Tests
# ============================================================


class TestCitationVerifier:
    def test_valid_citation_with_source_texts(self):
        cit = {"source": "spec.md", "text": "FODS uses XML"}
        result = verify_single_citation(
            cit, 0, source_texts={"spec.md": "FODS uses XML for spreadsheets"}
        )
        assert result.valid
        assert result.source_exists
        assert result.text_found_in_source

    def test_citation_text_not_found(self):
        cit = {"source": "spec.md", "text": "invented claim"}
        result = verify_single_citation(
            cit, 0, source_texts={"spec.md": "real content only"}
        )
        assert not result.valid
        assert result.source_exists
        assert not result.text_found_in_source

    def test_citation_missing_source(self):
        cit = {"source": "", "text": "some text"}
        result = verify_single_citation(cit, 0)
        assert not result.valid
        assert "missing_source_field" in result.errors

    def test_citation_missing_text(self):
        cit = {"source": "spec.md", "text": ""}
        result = verify_single_citation(cit, 0)
        assert not result.valid
        assert "missing_text_field" in result.errors

    def test_citation_source_not_in_texts(self):
        cit = {"source": "nonexistent.md", "text": "claim"}
        result = verify_single_citation(cit, 0, source_texts={"other.md": "content"})
        assert not result.valid
        assert "no_verification_context" in result.errors

    def test_verify_all_empty(self):
        report = verify_all_citations([])
        assert report.total == 0
        assert not report.all_valid

    def test_verify_all_mixed(self):
        citations = [
            {"source": "a.md", "text": "correct"},
            {"source": "b.md", "text": "wrong"},
        ]
        sources = {"a.md": "correct claim here", "b.md": "different content"}
        report = verify_all_citations(citations, source_texts=sources)
        assert report.total == 2
        assert report.verified == 1
        assert report.failed == 1

    def test_verification_hash_computed(self):
        cit = {"source": "spec.md", "text": "some text"}
        result = verify_single_citation(
            cit, 0, source_texts={"spec.md": "some text here"}
        )
        assert result.verification_hash
        assert len(result.verification_hash) == 16


# ============================================================
# Contradiction Detector Tests
# ============================================================


class TestContradictionDetector:
    def test_no_contradictions(self):
        facts = [
            {"id": "f1", "assertion": "FODS uses XML", "negation": "FODS does not use XML"}
        ]
        output = {"content": "FODS is an XML format"}
        report = check_output_contradictions(output, facts=facts)
        assert report.clean
        assert report.facts_checked == 1

    def test_contradiction_detected(self):
        facts = [
            {"id": "f1", "assertion": "FODS uses XML", "negation": "fods does not use xml"}
        ]
        output = {"content": "FODS does not use XML"}
        report = check_output_contradictions(output, facts=facts)
        assert not report.clean
        assert len(report.contradictions) == 1
        assert report.contradictions[0].fact_id == "f1"

    def test_no_facts_source(self):
        report = check_output_contradictions({"content": "anything"})
        assert report.status == "blocked_no_facts_source"

    def test_empty_facts_list(self):
        report = check_output_contradictions({"x": "y"}, facts=[])
        assert report.status == "blocked_no_facts" or report.status == "no_contradictions"

    def test_string_output(self):
        facts = [{"id": "f1", "assertion": "A", "negation": "not a"}]
        report = check_output_contradictions("not a claim", facts=facts)
        assert len(report.contradictions) == 1

    def test_facts_without_negation_skipped(self):
        facts = [{"id": "f1", "assertion": "X is Y"}]
        report = check_output_contradictions({"x": "z"}, facts=facts)
        assert report.clean

    def test_report_to_dict(self):
        facts = [{"id": "f1", "assertion": "A", "negation": "not a"}]
        report = check_output_contradictions("not a", facts=facts)
        d = report.to_dict()
        assert d["contradiction_count"] == 1
        assert d["contradictions"][0]["fact_id"] == "f1"


# ============================================================
# Evaluator Tests
# ============================================================


class TestEvaluator:
    def _make_result(self, **kwargs) -> SynthesisResult:
        r = SynthesisResult(task_id="test-eval")
        r.schema_valid = kwargs.get("schema_valid", True)
        r.errors = kwargs.get("errors", [])
        r.citation_verified = kwargs.get("citation_verified", False)
        r.citations = kwargs.get("citations", [])
        r.contradiction_check_status = kwargs.get("contradiction_check_status", "no_contradictions")
        r.output_hash = kwargs.get("output_hash", "abc123")
        return r

    def test_all_pass_default_criteria(self):
        result = self._make_result()
        ev = evaluate_synthesis(result)
        assert ev.passed
        assert ev.score == 1.0

    def test_schema_invalid_fails(self):
        result = self._make_result(schema_valid=False)
        ev = evaluate_synthesis(result)
        assert not ev.passed
        assert "schema_invalid" in ev.failures

    def test_too_many_errors_fails(self):
        result = self._make_result(errors=["e1", "e2"])
        ev = evaluate_synthesis(result)
        assert not ev.passed

    def test_citation_criteria(self):
        criteria = EvaluationCriteria(require_citations=True, min_citation_count=2)
        result = self._make_result(
            citation_verified=True,
            citations=[{"s": "a", "t": "b"}, {"s": "c", "t": "d"}],
        )
        ev = evaluate_synthesis(result, criteria)
        assert ev.passed

    def test_citation_insufficient(self):
        criteria = EvaluationCriteria(require_citations=True, min_citation_count=3)
        result = self._make_result(citation_verified=True, citations=[{"s": "a"}])
        ev = evaluate_synthesis(result, criteria)
        assert not ev.passed

    def test_contradiction_fails(self):
        result = self._make_result(contradiction_check_status="contradictions_found:2")
        ev = evaluate_synthesis(result)
        assert not ev.passed

    def test_missing_hash_fails(self):
        result = self._make_result(output_hash="")
        ev = evaluate_synthesis(result)
        assert not ev.passed

    def test_score_partial(self):
        result = self._make_result(schema_valid=False, output_hash="abc")
        ev = evaluate_synthesis(result)
        assert 0 < ev.score < 1.0


# ============================================================
# Deeper Negative Tests for Existing Modules
# ============================================================


class TestSynthesisRunnerDeepNegative:
    def _contract(self, **kwargs) -> AITaskContract:
        defaults = {
            "task_id": "neg-test",
            "task_type": "synthesis",
            "role": "structured_extraction",
        }
        defaults.update(kwargs)
        return AITaskContract(**defaults)

    def test_empty_json_output(self):
        result = run_synthesis(self._contract(), "{}")
        assert result.is_valid
        assert result.structured_output == {}

    def test_nested_json_arrays_accepted(self):
        raw = json.dumps({"items": [1, 2, 3], "nested": {"a": "b"}})
        result = run_synthesis(self._contract(), raw)
        assert result.is_valid

    def test_extremely_large_output_hashed(self):
        raw = json.dumps({"data": "x" * 100000})
        result = run_synthesis(self._contract(), raw)
        assert result.output_hash
        assert len(result.output_hash) == 16

    def test_unicode_output(self):
        raw = json.dumps({"text": "日本語テスト 中文 العربية"})
        result = run_synthesis(self._contract(), raw)
        assert result.is_valid

    def test_authority_never_escalated_even_on_success(self):
        raw = json.dumps({"status": "authoritative"})
        result = run_synthesis(self._contract(), raw)
        assert result.authority_state == ArtifactAuthorityStateValue.ai_draft


class TestAgenticRunnerDeepNegative:
    def test_every_forbidden_op_rejected(self):
        runner = ScopedRunner()
        for op in FORBIDDEN_OPERATIONS:
            contract = AgenticTaskContract(
                task_id="forbidden-test",
                path_allowlist=["tools/"],
                operation_allowlist=[op],
            )
            errors = contract.validate()
            assert any("forbidden" in e for e in errors), f"{op} not caught"

    def test_empty_path_allowlist_rejected(self):
        contract = AgenticTaskContract(
            task_id="no-paths",
            operation_allowlist=["read"],
        )
        errors = contract.validate()
        assert "missing path_allowlist" in errors

    def test_task_fn_exception_caught(self):
        runner = ScopedRunner()
        contract = AgenticTaskContract(
            task_id="exc-test",
            path_allowlist=["tools/"],
            operation_allowlist=["read"],
        )
        def failing_fn(c, r):
            raise ValueError("boom")
        result = runner.run(contract, model_id="qwen2-7b", task_fn=failing_fn)
        assert result.status == "error"
        assert not result.discarded

    def test_non_qwen_model_always_rejected(self):
        runner = ScopedRunner()
        contract = AgenticTaskContract(
            task_id="model-test",
            path_allowlist=["tools/"],
            operation_allowlist=["read"],
        )
        for model in ["gpt-4", "claude-3", "llama-70b", "mistral-7b"]:
            result = runner.run(contract, model_id=model)
            assert result.discarded, f"{model} not rejected"
            assert result.status == "model_rejected"


class TestNamespaceManagerDeepNegative:
    def test_stale_on_empty_hashes(self):
        mgr = NamespaceManager(store_root=Path(tempfile.mkdtemp()))
        manifest = IndexManifest(
            format_id="fods",
            chunk_hashes=["h1", "h2"],
            embedding_model_fingerprint="fp1",
        )
        mgr.create_namespace("fods", manifest)
        is_stale, reason = mgr.detect_stale_index("fods", [], "fp1")
        assert is_stale
        assert reason == "chunk_hashes_changed"

    def test_stale_on_model_change(self):
        mgr = NamespaceManager(store_root=Path(tempfile.mkdtemp()))
        manifest = IndexManifest(
            format_id="fods",
            chunk_hashes=["h1"],
            embedding_model_fingerprint="fp1",
        )
        mgr.create_namespace("fods", manifest)
        is_stale, reason = mgr.detect_stale_index("fods", ["h1"], "fp2")
        assert is_stale
        assert reason == "embedding_model_changed"

    def test_cross_namespace_error_message(self):
        mgr = NamespaceManager()
        with pytest.raises(CrossNamespaceError, match="forbidden"):
            mgr.reject_cross_namespace_query("fods", "fodt")


class TestDrainDeepNegative:
    def test_secret_in_nested_payload(self):
        payload = map_spool_to_agent_metrics({
            "timestamp": "2026-01-01",
            "sprint_id": "test",
            "model": "sk-secret-key-here",
        })
        errors = validate_drain_payload(payload)
        assert any("secret" in e for e in errors)

    def test_bearer_in_payload(self):
        payload = map_spool_to_agent_metrics({
            "timestamp": "2026-01-01",
            "sprint_id": "test",
            "endpoint_identity": "Bearer abc123",
        })
        errors = validate_drain_payload(payload)
        assert any("secret" in e for e in errors)

    def test_valid_payload_passes(self):
        payload = map_spool_to_agent_metrics({
            "timestamp": "2026-01-01",
            "sprint_id": "test",
            "model": "gpt-oss-turbo",
        })
        errors = validate_drain_payload(payload)
        assert not errors


class TestRiskControlsDeepNegative:
    def test_all_checks_return_dict(self):
        repo = Path(".")
        results = run_all_risk_checks(repo)
        assert len(results) == 6
        for r in results:
            assert "check" in r
            assert "passed" in r
