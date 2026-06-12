"""Lane C tests — GPT-OSS synthesis controls.

Tests for synthesis runner, citation verification, contradiction checking,
structured output validation, and authority lifecycle enforcement.
"""

import json

from tools.ai.schemas.models import AIRole, AITaskContract, ArtifactAuthorityStateValue
from tools.ai.synthesis.runner import (
    check_contradictions,
    run_synthesis,
    validate_structured_output,
    validate_task_contract,
    verify_citations,
)


class TestValidTaskContract:
    def test_valid_contract(self):
        contract = AITaskContract(task_id="t1", task_type="spec_extraction", role=AIRole.structured_extraction)
        assert validate_task_contract(contract) == []

    def test_missing_task_id(self):
        contract = AITaskContract(task_id="", task_type="x", role=AIRole.structured_extraction)
        errors = validate_task_contract(contract)
        assert "task_id is required" in errors


class TestStructuredOutputValidation:
    def test_valid_output(self):
        schema = {"required_fields": ["name", "value"]}
        output = {"name": "test", "value": 42}
        valid, errors = validate_structured_output(output, schema)
        assert valid is True

    def test_missing_field(self):
        schema = {"required_fields": ["name", "value"]}
        output = {"name": "test"}
        valid, errors = validate_structured_output(output, schema)
        assert valid is False
        assert any("value" in e for e in errors)

    def test_no_schema(self):
        valid, errors = validate_structured_output({"x": 1}, None)
        assert valid is True

    def test_non_dict_output(self):
        valid, errors = validate_structured_output("string", {"required_fields": []})
        assert valid is False


class TestCitationVerification:
    def test_valid_citations(self):
        citations = [{"source": "spec.md", "text": "section 4.2"}]
        valid, errors = verify_citations(citations)
        assert valid is True

    def test_missing_source(self):
        citations = [{"text": "hello"}]
        valid, errors = verify_citations(citations)
        assert valid is False

    def test_empty_citations(self):
        valid, errors = verify_citations([])
        assert valid is False

    def test_citation_text_not_in_source(self):
        citations = [{"source": "spec.md", "text": "nonexistent text"}]
        snippets = {"spec.md": "this is the real content"}
        valid, errors = verify_citations(citations, snippets)
        assert valid is False

    def test_hallucinated_citation_rejected(self):
        citations = [{"source": "fake.md", "text": "made up"}]
        snippets = {"spec.md": "real content"}
        valid, errors = verify_citations(citations, snippets)
        assert valid is True  # source not in snippets, no verification possible


class TestContradictionCheck:
    def test_missing_verified_facts(self):
        status = check_contradictions({"key": "val"}, None)
        assert status == "blocked_missing_verified_facts"

    def test_nonexistent_path(self, tmp_path):
        status = check_contradictions({"key": "val"}, tmp_path / "nope.yaml")
        assert status == "blocked_missing_verified_facts"

    def test_no_contradictions(self, tmp_path):
        import yaml
        facts_file = tmp_path / "verified-facts.yaml"
        facts_file.write_text(yaml.dump({"facts": [
            {"id": "f1", "assertion": "fods uses xml", "negation": "fods does not use xml"}
        ]}))
        status = check_contradictions({"format": "fods", "uses": "xml"}, facts_file)
        assert status == "no_contradictions"


class TestRunSynthesis:
    def test_valid_extraction(self):
        contract = AITaskContract(task_id="t1", task_type="spec_extraction", role=AIRole.structured_extraction)
        raw = json.dumps({"name": "test", "value": 42})
        schema = {"required_fields": ["name", "value"]}
        result = run_synthesis(contract, raw, output_schema=schema)
        assert result.schema_valid is True
        assert result.authority_state == ArtifactAuthorityStateValue.ai_draft

    def test_malformed_json_rejected(self):
        contract = AITaskContract(task_id="t1", task_type="x", role=AIRole.structured_extraction)
        result = run_synthesis(contract, "not json{{{")
        assert "malformed_json_output" in result.errors

    def test_authority_never_escalated(self):
        contract = AITaskContract(task_id="t1", task_type="x", role=AIRole.structured_extraction)
        result = run_synthesis(contract, json.dumps({"x": 1}))
        assert result.authority_state == ArtifactAuthorityStateValue.ai_draft

    def test_missing_citation_error(self):
        contract = AITaskContract(
            task_id="t1", task_type="x", role=AIRole.structured_extraction,
            require_citation=True,
        )
        raw = json.dumps({"data": "test"})
        result = run_synthesis(contract, raw)
        assert any("no citations" in e for e in result.errors)
