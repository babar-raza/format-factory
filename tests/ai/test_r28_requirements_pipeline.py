"""R28 Lane E — AI-generated requirements pipeline tests."""

import json
import sys
import tempfile
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.ai.requirements.generator import (
    GeneratedRequirement,
    REQUIREMENT_SCHEMA,
    generate_requirements_from_synthesis,
    review_requirement,
    validate_requirement,
    write_requirements_packet,
)


class TestRequirementValidation:
    def test_valid_requirement(self):
        req = GeneratedRequirement(
            req_id="REQ-FODS-GEN-001",
            text="Parser shall handle empty spreadsheets",
            format_id="fods",
            source_chunk_hash="abc123",
        )
        errors = validate_requirement(req)
        assert not errors

    def test_missing_req_id(self):
        req = GeneratedRequirement(req_id="", text="test", format_id="fods", source_chunk_hash="h")
        errors = validate_requirement(req)
        assert "missing req_id" in errors

    def test_missing_text(self):
        req = GeneratedRequirement(req_id="R1", text="", format_id="fods", source_chunk_hash="h")
        errors = validate_requirement(req)
        assert "missing text" in errors

    def test_missing_provenance(self):
        req = GeneratedRequirement(req_id="R1", text="test", format_id="fods")
        errors = validate_requirement(req)
        assert any("provenance" in e for e in errors)

    def test_invalid_priority(self):
        req = GeneratedRequirement(
            req_id="R1", text="test", format_id="fods",
            source_chunk_hash="h", priority="INVALID",
        )
        errors = validate_requirement(req)
        assert any("priority" in e for e in errors)

    def test_all_valid_priorities_accepted(self):
        for p in REQUIREMENT_SCHEMA["valid_priorities"]:
            req = GeneratedRequirement(
                req_id="R1", text="test", format_id="fods",
                source_chunk_hash="h", priority=p,
            )
            errors = validate_requirement(req)
            assert not any("priority" in e for e in errors)


class TestRequirementReview:
    def test_accept(self):
        req = GeneratedRequirement(req_id="R1", text="t", format_id="fods", source_chunk_hash="h")
        reviewed = review_requirement(req, accept=True, reason="meets spec")
        assert reviewed.verifier_status == "accepted"
        assert reviewed.authority_state == "verifier_reviewed"

    def test_reject(self):
        req = GeneratedRequirement(req_id="R1", text="t", format_id="fods", source_chunk_hash="h")
        reviewed = review_requirement(req, accept=False, reason="too vague")
        assert reviewed.verifier_status == "rejected"
        assert reviewed.authority_state == "ai_draft"


class TestRequirementGeneration:
    def test_generate_from_synthesis(self):
        synthesis = {
            "requirements": [
                {"id": "REQ-1", "text": "Parse XML", "source_chunk_hash": "h1", "source": "spec.md"},
                {"id": "REQ-2", "text": "Handle errors", "source_chunk_hash": "h2", "source": "spec.md"},
            ]
        }
        reqs = generate_requirements_from_synthesis(synthesis, "fods")
        assert len(reqs) == 2
        assert all(r.format_id == "fods" for r in reqs)
        assert all(r.priority == "AI_PROPOSAL" for r in reqs)
        assert all(r.generation_hash for r in reqs)

    def test_empty_synthesis(self):
        reqs = generate_requirements_from_synthesis({}, "fods")
        assert len(reqs) == 0

    def test_non_dict_items_skipped(self):
        synthesis = {"requirements": ["not a dict", 42, None]}
        reqs = generate_requirements_from_synthesis(synthesis, "fods")
        assert len(reqs) == 0


class TestRequirementPacket:
    def test_write_packet(self):
        reqs = [
            GeneratedRequirement(
                req_id="R1", text="test req", format_id="fods",
                source_chunk_hash="h1",
            ),
        ]
        reqs[0].compute_hash()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reqs.json"
            write_requirements_packet(reqs, path)
            assert path.exists()
            data = json.loads(path.read_text())
            assert data["count"] == 1
            assert data["authority_state"] == "ai_draft"
            assert len(data["requirements"]) == 1

    def test_packet_provenance_preserved(self):
        reqs = [
            GeneratedRequirement(
                req_id="R1", text="test", format_id="fods",
                source_chunk_hash="abc123", source_path="spec.md",
            ),
        ]
        reqs[0].compute_hash()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reqs.json"
            write_requirements_packet(reqs, path)
            data = json.loads(path.read_text())
            assert data["requirements"][0]["source_chunk_hash"] == "abc123"
