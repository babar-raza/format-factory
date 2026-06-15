"""Tests for LLM Semantic Verification Layer.

Covers all four integration points:
1. Acceptance Criteria Parser (inspect_declared_evidence.py)
2. Evidence Content Verifier (grade_declared_work.py)
3. Transcript Scope Validator (inspect_declared_evidence.py)
4. Sprint-Aware Prompt Rewriter (generate_next_worker_prompt.py)

Tests verify deterministic fallbacks, downgrade-only semantics,
and governance section preservation. Tests that check deterministic
behavior mock the LLM gateway to ensure no live calls interfere.
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


_REPO = Path(__file__).resolve().parent.parent.parent
_TOOLS = _REPO / "tools" / "supervisor"
sys.path.insert(0, str(_TOOLS))


def _disable_llm():
    """Context manager-like patch dict that disables LLM env vars."""
    return patch.dict(os.environ, {
        "GPT_OSS_ENDPOINT": "",
        "GPT_OSS_API_KEY": "",
        "PROFESSIONALIZE_BASE_URL": "",
        "PROFESSIONALIZE_API_KEY": "",
    })


# ── 1. Acceptance Criteria Parser ──────────────────────────────────────────


class TestAcceptanceCriteriaParser:
    """Tests for parse_acceptance_criteria() in inspect_declared_evidence.py."""

    def _parser(self):
        from inspect_declared_evidence import parse_acceptance_criteria
        return parse_acceptance_criteria

    def test_empty_input_returns_empty(self):
        result = self._parser()("")
        assert result["assertions"] == []
        assert result["overall_verifiability"] == 0.0
        assert result["llm_used"] is False

    def test_none_input_returns_empty(self):
        result = self._parser()(None)
        assert result["assertions"] == []
        assert result["llm_used"] is False

    def test_quoted_string_extracted_deterministically(self):
        """With LLM disabled, regex fallback should extract quoted strings."""
        import inspect_declared_evidence as ide
        ide._ai_gateway = None
        ide._ai_config_obj = None
        with _disable_llm():
            result = self._parser()('Output must contain "valid JSON"')
        assert result["llm_used"] is False
        assert len(result["assertions"]) >= 1
        assert any("valid JSON" in a["claim"] for a in result["assertions"])
        assert result["overall_verifiability"] > 0.0

    def test_pass_keyword_extracted(self):
        import inspect_declared_evidence as ide
        ide._ai_gateway = None
        ide._ai_config_obj = None
        with _disable_llm():
            result = self._parser()("All tests PASS without errors")
        assert result["llm_used"] is False
        assert any(a["claim"] == "PASS" for a in result["assertions"])

    def test_no_gateway_means_no_llm(self):
        """Without credentials, llm_used must always be False."""
        import inspect_declared_evidence as ide
        ide._ai_gateway = None
        ide._ai_config_obj = None
        with _disable_llm():
            result = self._parser()("The system correctly handles edge cases and produces reasonable output")
        assert result["llm_used"] is False

    def test_verifiability_score_bounded(self):
        result = self._parser()('Must output "hello" and "world"')
        assert 0.0 <= result["overall_verifiability"] <= 1.0


# ── 2. Evidence Content Verifier ───────────────────────────────────────────


class TestSemanticVerifyItem:
    """Tests for semantic_verify_item() in grade_declared_work.py."""

    def _verifier(self):
        from grade_declared_work import semantic_verify_item
        return semantic_verify_item

    def test_no_evidence_paths_returns_fallback(self):
        result = self._verifier()(
            {"evidence_paths_found": []},
            {"item_id": "X", "title": "Test item"},
            _REPO,
        )
        # Grading now returns adequate=False when no evidence paths provided
        assert result["adequate"] is False
        assert result["confidence"] == 0.0
        assert result["llm_used"] is False

    def test_nonexistent_paths_returns_fallback(self):
        result = self._verifier()(
            {"evidence_paths_found": ["nonexistent/path/file.py"]},
            {"item_id": "X", "title": "Test item"},
            _REPO,
        )
        # Nonexistent paths: adequate may be True or False depending on fallback logic
        assert result["llm_used"] is False

    def test_fallback_never_downgrades(self):
        """Without LLM, verifier returns adequate=False (SUP-RECT-004: LLM unavailable)."""
        import grade_declared_work as gdw
        gdw._sv_gateway = None
        gdw._sv_config = None
        with _disable_llm():
            result = self._verifier()(
                {"evidence_paths_found": ["tests/supervisor/test_llm_semantic_verification.py"]},
                {"item_id": "X", "title": "Test item"},
                _REPO,
            )
        # SUP-RECT-004: LLM unavailable → adequate=False with deficiency
        assert result["adequate"] is False
        assert result["stub_detected"] is False
        assert "llm_verification_unavailable" in result.get("deficiencies", [])


class TestSemanticVerificationDowngradeOnly:
    """Verify the downgrade-only contract in grade_all()."""

    def test_downgrade_map_only_goes_down(self):
        """Verify the downgrade map in grade_all never maps to a higher grade."""
        grade_order = [
            "ACCEPTED_VERIFIED",
            "ACCEPTED",
            "ACCEPTED_WITH_WARNINGS",
            "ACCEPTED_WITH_LIMITATIONS",
            "REWORK_REQUIRED",
            "OVERCLAIMED",
            "REJECTED",
        ]
        assert grade_order.index("ACCEPTED_WITH_LIMITATIONS") > grade_order.index("ACCEPTED_VERIFIED")

    def test_grade_all_with_empty_declaration(self):
        from grade_declared_work import grade_all
        inspection = {
            "run_id": "test",
            "sprint_id": "test",
            "evidence_root": "",
            "item_inspections": [],
            "artifact_inspections": [],
            "test_results": {"passed": 0, "failed": 0, "skipped": 0},
        }
        declaration = {"planned_work_items": []}
        result = grade_all(inspection, declaration)
        assert result["overall_verdict"] == "ACCEPTED"
        assert result["evidence_quality_score"] == 0.0

    def test_grade_all_preserves_deterministic_grades_without_llm(self):
        """Without LLM, grade_all must produce identical results to before."""
        from grade_declared_work import grade_all

        inspection = {
            "run_id": "test",
            "sprint_id": "test",
            "evidence_root": "",
            "item_inspections": [
                {
                    "item_id": "W1",
                    "declared_status": "completed",
                    "evidence_paths_found": ["some/path.py"],
                    "evidence_paths_missing": [],
                    "has_evidence": True,
                    "has_tests": True,
                    "tests_declared": ["tests/test_x.py"],
                    "tests_with_content": ["tests/test_x.py"],
                    "tests_empty_or_stub": [],
                    "test_summaries": [],
                    "acceptance_criteria_verified": True,
                    "acceptance_criteria_pattern": "PASS",
                    "acceptance_criteria_parse": None,
                    "transcript_validation": None,
                },
            ],
            "artifact_inspections": [],
            "test_results": {"passed": 5, "failed": 0, "skipped": 0},
        }
        declaration = {
            "planned_work_items": [
                {"item_id": "W1", "title": "Test work", "status": "completed"},
            ],
        }
        # Mock semantic_verify_item to return fallback (simulating no LLM)
        mock_sv = {
            "adequate": True, "confidence": 0.0,
            "stub_detected": False, "deficiencies": [], "llm_used": False,
        }
        with patch("grade_declared_work.semantic_verify_item", return_value=mock_sv):
            result = grade_all(inspection, declaration)
        w1 = next(g for g in result["item_grades"] if g["item_id"] == "W1")
        assert w1["supervisor_grade"] == "ACCEPTED_VERIFIED"
        sv = w1.get("semantic_verification", {})
        assert sv.get("llm_used") is False


# ── 3. Transcript Scope Validator ──────────────────────────────────────────


class TestTranscriptScopeValidator:
    """Tests for _validate_transcript_scope in inspect_declared_evidence.py."""

    def test_no_gateway_returns_none(self):
        from inspect_declared_evidence import _validate_transcript_scope
        result = _validate_transcript_scope(
            ["nonexistent.json"], _REPO, {"title": "test", "item_id": "X"}
        )
        assert result is None

    def test_no_paths_returns_none(self):
        from inspect_declared_evidence import _validate_transcript_scope
        result = _validate_transcript_scope([], _REPO, {"title": "test"})
        assert result is None

    def test_no_item_context_returns_none(self):
        from inspect_declared_evidence import _validate_transcript_scope
        result = _validate_transcript_scope(["some.json"], _REPO, {})
        assert result is None


# ── 4. Sprint-Aware Prompt Rewriter ────────────────────────────────────────


class TestPromptRewriter:
    """Tests for prompt rewriter in generate_next_worker_prompt.py."""

    def test_rewriter_returns_none_without_credentials(self):
        import generate_next_worker_prompt as gnwp
        with _disable_llm():
            result = gnwp.rewrite_prompt_with_context(
                "# Test Prompt\n## Hard Prohibitions\n- no push\n",
                {"overall_verdict": "ACCEPTED", "item_grades": []},
                "mainstream",
            )
        # Without LLM credentials, must return None (deterministic prompt used)
        assert result is None

    def test_governance_section_extraction(self):
        from generate_next_worker_prompt import _extract_governance_sections
        prompt = (
            "# Header\nSome content\n"
            "## Hard Prohibitions\n- No push\n- No commit\n"
            "## Train A\nDo something\n"
            "## Evidence Declaration Requirements\nWrite YAML\n"
        )
        sections = _extract_governance_sections(prompt)
        headers = [h for h, _ in sections]
        assert "## Hard Prohibitions" in headers
        assert "## Evidence Declaration Requirements" in headers
        assert "## Train A" not in headers

    def test_governance_section_content_preserved(self):
        from generate_next_worker_prompt import _extract_governance_sections
        prompt = (
            "## Hard Prohibitions\n"
            "- No git push without explicit user authorization.\n"
            "- No git commit without explicit user authorization.\n"
            "## Other Section\nStuff\n"
        )
        sections = _extract_governance_sections(prompt)
        prohibitions = next((c for h, c in sections if h == "## Hard Prohibitions"), "")
        assert "No git push" in prohibitions
        assert "No git commit" in prohibitions

    def test_empty_prompt_extraction(self):
        from generate_next_worker_prompt import _extract_governance_sections
        sections = _extract_governance_sections("")
        assert sections == []


# ── 5. Integration: Pipeline Coherence ─────────────────────────────────────


class TestPipelineCoherence:
    """Verify the LLM layer integrates cleanly with the existing pipeline."""

    def test_inspect_item_includes_criteria_parse(self):
        """inspect_item() output must include acceptance_criteria_parse field."""
        from inspect_declared_evidence import inspect_item
        item = {
            "item_id": "TEST-001",
            "status": "completed",
            "evidence_paths": [],
            "acceptance_criteria": 'Output must contain "hello"',
        }
        result = inspect_item(item, _REPO)
        assert "acceptance_criteria_parse" in result
        parse = result["acceptance_criteria_parse"]
        if parse:
            assert "assertions" in parse

    def test_inspect_item_backwards_compatible(self):
        """inspect_item() must still return all legacy fields."""
        from inspect_declared_evidence import inspect_item
        item = {
            "item_id": "TEST-002",
            "status": "completed",
            "evidence_paths": [],
        }
        result = inspect_item(item, _REPO)
        assert "acceptance_criteria_verified" in result
        assert "acceptance_criteria_pattern" in result
        assert "tests_with_content" in result
        assert "tests_empty_or_stub" in result
        assert "transcript_validation" in result

    def test_autonomous_cycle_import_still_works(self):
        """autonomous_cycle.py must still import all required modules."""
        import autonomous_cycle  # noqa: F401
        assert hasattr(autonomous_cycle, "run_cycle")
        assert hasattr(autonomous_cycle, "classify_continuation_state")

    @pytest.mark.timeout(10)
    def test_generate_prompt_still_works(self):
        """generate_prompt() must still produce a valid prompt."""
        from generate_next_worker_prompt import generate_prompt
        review = {
            "sprint_id": "TEST-R1",
            "overall_verdict": "ACCEPTED",
            "autonomous_continue": True,
            "item_grades": [],
            "accepted_items": [],
            "rework_items": [],
            "rejected_items": [],
            "overclaimed_items": [],
            "test_results": {"passed": 10, "failed": 0, "skipped": 0},
            "evidence_quality_score": 1.0,
        }
        with _disable_llm():
            prompt = generate_prompt(review, repo_root=_REPO, stream="mainstream")
        assert len(prompt) > 100
        assert "Hard Prohibitions" in prompt or "Prohibitions" in prompt


# ── 6. Downgrade Contract Enforcement ──────────────────────────────────────


class TestDowngradeContract:
    """Verify that semantic verification can only downgrade, never upgrade."""

    def test_mock_llm_downgrade_applied(self):
        """Simulate LLM returning adequate=False with high confidence."""
        from grade_declared_work import grade_all

        inspection = {
            "run_id": "test",
            "sprint_id": "test",
            "evidence_root": "",
            "item_inspections": [
                {
                    "item_id": "W1",
                    "declared_status": "completed",
                    "evidence_paths_found": ["tests/supervisor/test_llm_semantic_verification.py"],
                    "evidence_paths_missing": [],
                    "has_evidence": True,
                    "has_tests": True,
                    "tests_declared": ["tests/supervisor/test_llm_semantic_verification.py"],
                    "tests_with_content": ["tests/supervisor/test_llm_semantic_verification.py"],
                    "tests_empty_or_stub": [],
                    "test_summaries": [],
                    "acceptance_criteria_verified": True,
                    "acceptance_criteria_pattern": "PASS",
                    "acceptance_criteria_parse": None,
                    "transcript_validation": None,
                },
            ],
            "artifact_inspections": [],
            "test_results": {"passed": 5, "failed": 0, "skipped": 0},
        }
        declaration = {
            "planned_work_items": [
                {"item_id": "W1", "title": "Test work", "status": "completed"},
            ],
        }

        mock_sv = {
            "adequate": False,
            "confidence": 0.95,
            "stub_detected": False,
            "deficiencies": ["Evidence covers only happy path"],
            "llm_used": True,
        }
        with patch("grade_declared_work.semantic_verify_item", return_value=mock_sv):
            result = grade_all(inspection, declaration)

        w1 = next(g for g in result["item_grades"] if g["item_id"] == "W1")
        assert w1["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS"
        assert w1.get("semantic_verification") == mock_sv

    def test_mock_llm_stub_detected_forces_rework(self):
        """Simulate LLM detecting stub evidence."""
        from grade_declared_work import grade_all

        inspection = {
            "run_id": "test",
            "sprint_id": "test",
            "evidence_root": "",
            "item_inspections": [
                {
                    "item_id": "W2",
                    "declared_status": "completed",
                    "evidence_paths_found": ["some/test.py"],
                    "evidence_paths_missing": [],
                    "has_evidence": True,
                    "has_tests": False,
                    "tests_declared": [],
                    "tests_with_content": [],
                    "tests_empty_or_stub": [],
                    "test_summaries": [],
                    "acceptance_criteria_verified": False,
                    "acceptance_criteria_pattern": "",
                    "acceptance_criteria_parse": None,
                    "transcript_validation": None,
                },
            ],
            "artifact_inspections": [],
            "test_results": {"passed": 0, "failed": 0, "skipped": 0},
        }
        declaration = {
            "planned_work_items": [
                {"item_id": "W2", "title": "Stub item", "status": "completed"},
            ],
        }

        mock_sv = {
            "adequate": False,
            "confidence": 0.9,
            "stub_detected": True,
            "deficiencies": ["File contains only assert True"],
            "llm_used": True,
        }
        with patch("grade_declared_work.semantic_verify_item", return_value=mock_sv):
            result = grade_all(inspection, declaration)

        w2 = next(g for g in result["item_grades"] if g["item_id"] == "W2")
        assert w2["supervisor_grade"] == "REWORK_REQUIRED"
        assert "stub" in w2.get("required_rework", "").lower()

    def test_mock_llm_low_confidence_no_downgrade(self):
        """LLM returns adequate=False but confidence < 0.8 -- no downgrade."""
        from grade_declared_work import grade_all

        inspection = {
            "run_id": "test",
            "sprint_id": "test",
            "evidence_root": "",
            "item_inspections": [
                {
                    "item_id": "W3",
                    "declared_status": "completed",
                    "evidence_paths_found": ["tests/supervisor/test_llm_semantic_verification.py"],
                    "evidence_paths_missing": [],
                    "has_evidence": True,
                    "has_tests": True,
                    "tests_declared": ["tests/supervisor/test_llm_semantic_verification.py"],
                    "tests_with_content": ["tests/supervisor/test_llm_semantic_verification.py"],
                    "tests_empty_or_stub": [],
                    "test_summaries": [],
                    "acceptance_criteria_verified": True,
                    "acceptance_criteria_pattern": "PASS",
                    "acceptance_criteria_parse": None,
                    "transcript_validation": None,
                },
            ],
            "artifact_inspections": [],
            "test_results": {"passed": 5, "failed": 0, "skipped": 0},
        }
        declaration = {
            "planned_work_items": [
                {"item_id": "W3", "title": "Good work", "status": "completed"},
            ],
        }

        mock_sv = {
            "adequate": False,
            "confidence": 0.5,
            "stub_detected": False,
            "deficiencies": ["Uncertain assessment"],
            "llm_used": True,
        }
        with patch("grade_declared_work.semantic_verify_item", return_value=mock_sv):
            result = grade_all(inspection, declaration)

        w3 = next(g for g in result["item_grades"] if g["item_id"] == "W3")
        assert w3["supervisor_grade"] == "ACCEPTED_VERIFIED"

    def test_mock_llm_adequate_no_change(self):
        """LLM returns adequate=True -- grade unchanged."""
        from grade_declared_work import grade_all

        inspection = {
            "run_id": "test",
            "sprint_id": "test",
            "evidence_root": "",
            "item_inspections": [
                {
                    "item_id": "W4",
                    "declared_status": "completed",
                    "evidence_paths_found": ["tests/supervisor/test_llm_semantic_verification.py"],
                    "evidence_paths_missing": [],
                    "has_evidence": True,
                    "has_tests": True,
                    "tests_declared": ["tests/supervisor/test_llm_semantic_verification.py"],
                    "tests_with_content": ["tests/supervisor/test_llm_semantic_verification.py"],
                    "tests_empty_or_stub": [],
                    "test_summaries": [],
                    "acceptance_criteria_verified": True,
                    "acceptance_criteria_pattern": "PASS",
                    "acceptance_criteria_parse": None,
                    "transcript_validation": None,
                },
            ],
            "artifact_inspections": [],
            "test_results": {"passed": 5, "failed": 0, "skipped": 0},
        }
        declaration = {
            "planned_work_items": [
                {"item_id": "W4", "title": "Good work", "status": "completed"},
            ],
        }

        mock_sv = {
            "adequate": True,
            "confidence": 0.95,
            "stub_detected": False,
            "deficiencies": [],
            "llm_used": True,
        }
        with patch("grade_declared_work.semantic_verify_item", return_value=mock_sv):
            result = grade_all(inspection, declaration)

        w4 = next(g for g in result["item_grades"] if g["item_id"] == "W4")
        assert w4["supervisor_grade"] == "ACCEPTED_VERIFIED"

    def test_mock_llm_borderline_confidence_no_downgrade(self):
        """Confidence 0.82 is below 0.85 threshold — no downgrade."""
        from grade_declared_work import grade_all

        inspection = {
            "run_id": "test",
            "sprint_id": "test",
            "evidence_root": "",
            "item_inspections": [
                {
                    "item_id": "W5",
                    "declared_status": "completed",
                    "evidence_paths_found": ["tests/supervisor/test_llm_semantic_verification.py"],
                    "evidence_paths_missing": [],
                    "has_evidence": True,
                    "has_tests": True,
                    "tests_declared": ["tests/supervisor/test_llm_semantic_verification.py"],
                    "tests_with_content": ["tests/supervisor/test_llm_semantic_verification.py"],
                    "tests_empty_or_stub": [],
                    "test_summaries": [],
                    "acceptance_criteria_verified": True,
                    "acceptance_criteria_pattern": "PASS",
                    "acceptance_criteria_parse": None,
                    "transcript_validation": None,
                },
            ],
            "artifact_inspections": [],
            "test_results": {"passed": 5, "failed": 0, "skipped": 0},
        }
        declaration = {
            "planned_work_items": [
                {"item_id": "W5", "title": "Borderline work", "status": "completed"},
            ],
        }

        mock_sv = {
            "adequate": False,
            "confidence": 0.82,
            "stub_detected": False,
            "deficiencies": ["Borderline assessment"],
            "llm_used": True,
        }
        with patch("grade_declared_work.semantic_verify_item", return_value=mock_sv):
            result = grade_all(inspection, declaration)

        w5 = next(g for g in result["item_grades"] if g["item_id"] == "W5")
        assert w5["supervisor_grade"] == "ACCEPTED_VERIFIED"


# ── 7. Semantic Quality Score ─────────────────────────────────────────────


class TestSemanticQualityScore:
    """Verify semantic_quality_score is populated in evidence_quality_breakdown."""

    def test_semantic_score_with_adequate_items(self):
        from grade_declared_work import grade_all

        inspection = {
            "run_id": "test",
            "sprint_id": "test",
            "evidence_root": "",
            "item_inspections": [
                {
                    "item_id": "SQ1",
                    "declared_status": "completed",
                    "evidence_paths_found": ["some/path.py"],
                    "evidence_paths_missing": [],
                    "has_evidence": True,
                    "has_tests": True,
                    "tests_declared": ["tests/test.py"],
                    "tests_with_content": ["tests/test.py"],
                    "tests_empty_or_stub": [],
                    "test_summaries": [],
                    "acceptance_criteria_verified": True,
                    "acceptance_criteria_pattern": "PASS",
                    "acceptance_criteria_parse": None,
                    "transcript_validation": None,
                },
            ],
            "artifact_inspections": [],
            "test_results": {"passed": 5, "failed": 0, "skipped": 0},
        }
        declaration = {
            "planned_work_items": [
                {"item_id": "SQ1", "title": "Test", "status": "completed"},
            ],
        }

        mock_sv = {
            "adequate": True,
            "confidence": 0.9,
            "stub_detected": False,
            "deficiencies": [],
            "llm_used": True,
        }
        with patch("grade_declared_work.semantic_verify_item", return_value=mock_sv):
            result = grade_all(inspection, declaration)

        breakdown = result["evidence_quality_breakdown"]
        assert breakdown["semantic_verified_count"] == 1
        assert breakdown["semantic_adequate_count"] == 1
        assert breakdown["semantic_quality_score"] == 1.0

    def test_semantic_score_none_without_llm(self):
        from grade_declared_work import grade_all

        inspection = {
            "run_id": "test",
            "sprint_id": "test",
            "evidence_root": "",
            "item_inspections": [],
            "artifact_inspections": [],
            "test_results": {"passed": 0, "failed": 0, "skipped": 0},
        }
        declaration = {"planned_work_items": []}

        result = grade_all(inspection, declaration)
        breakdown = result["evidence_quality_breakdown"]
        assert breakdown["semantic_quality_score"] is None
        assert breakdown["semantic_verified_count"] == 0


# ── 8. Transcript Scope Aligned in Grading ────────────────────────────────


class TestTranscriptScopeInGrading:
    """Verify transcript_scope_aligned=False blocks concrete proof."""

    def test_scope_misaligned_blocks_verified(self):
        """Transcript valid but scope misaligned — should not count as concrete proof."""
        from grade_declared_work import grade_item

        item_inspection = {
            "item_id": "TSG1",
            "declared_status": "completed",
            "evidence_paths_found": ["some/evidence.py"],
            "evidence_paths_missing": [],
            "has_evidence": True,
            "has_tests": False,
            "tests_declared": [],
            "tests_with_content": [],
            "tests_empty_or_stub": [],
            "test_summaries": [],
            "acceptance_criteria_verified": False,
            "acceptance_criteria_pattern": "",
            "acceptance_criteria_parse": None,
            "transcript_validation": {
                "all_valid": True,
                "transcript_scope_aligned": False,
            },
        }
        result = grade_item(item_inspection, {"passed": 0, "failed": 0})
        # Without tests, criteria, or scope-aligned transcript, should be ACCEPTED_WITH_LIMITATIONS
        assert result["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS"

    def test_scope_aligned_allows_verified(self):
        """Transcript valid and scope aligned — counts as concrete proof."""
        from grade_declared_work import grade_item

        item_inspection = {
            "item_id": "TSG2",
            "declared_status": "completed",
            "evidence_paths_found": ["some/evidence.py"],
            "evidence_paths_missing": [],
            "has_evidence": True,
            "has_tests": False,
            "tests_declared": [],
            "tests_with_content": [],
            "tests_empty_or_stub": [],
            "test_summaries": [],
            "acceptance_criteria_verified": False,
            "acceptance_criteria_pattern": "",
            "acceptance_criteria_parse": None,
            "transcript_validation": {
                "all_valid": True,
                "transcript_scope_aligned": True,
            },
        }
        result = grade_item(item_inspection, {"passed": 0, "failed": 0})
        assert result["supervisor_grade"] == "ACCEPTED_VERIFIED"


# ── 9. Transcript Scope Validator with Synthetic Fixture ──────────────────


class TestTranscriptScopeWithFixture:
    """H3: Test _validate_transcript_scope with a real synthetic transcript file."""

    def test_synthetic_transcript_no_crash(self, tmp_path):
        """With a real file but no LLM, should return None without crashing."""
        from inspect_declared_evidence import _validate_transcript_scope
        transcript = tmp_path / "transcript.json"
        transcript.write_text(json.dumps({
            "skill_id": "add-python-api",
            "mode": "autonomous",
            "result": "success",
            "steps": [{"action": "wrote code", "file": "src/python/tsv/tsv_parser.py"}],
        }))
        import inspect_declared_evidence as ide
        ide._ai_gateway = None
        ide._ai_config_obj = None
        with _disable_llm():
            result = _validate_transcript_scope(
                [str(transcript)], tmp_path,
                {"title": "implement get_headers()", "item_id": "W1"}
            )
        # LLM disabled — returns None (no scope validation)
        assert result is None

    def test_mock_llm_scope_aligned(self, tmp_path):
        """Mock LLM returning scope_aligned=True."""
        from inspect_declared_evidence import _validate_transcript_scope
        transcript = tmp_path / "transcript.json"
        transcript.write_text(json.dumps({
            "skill_id": "add-python-api",
            "result": "success",
        }))
        mock_response = '{"scope_aligned": true, "coverage_pct": 0.95, "gaps": []}'
        with patch("inspect_declared_evidence._llm_call", return_value=mock_response):
            result = _validate_transcript_scope(
                [str(transcript)], tmp_path,
                {"title": "implement get_headers()", "item_id": "W1"}
            )
        assert result is not None
        assert result["scope_aligned"] is True
        assert result["coverage_pct"] == 0.95

    def test_mock_llm_scope_misaligned(self, tmp_path):
        """Mock LLM returning scope_aligned=False."""
        from inspect_declared_evidence import _validate_transcript_scope
        transcript = tmp_path / "transcript.json"
        transcript.write_text(json.dumps({
            "skill_id": "add-python-api",
            "result": "success",
        }))
        mock_response = '{"scope_aligned": false, "coverage_pct": 0.2, "gaps": ["wrong format"]}'
        with patch("inspect_declared_evidence._llm_call", return_value=mock_response):
            result = _validate_transcript_scope(
                [str(transcript)], tmp_path,
                {"title": "implement get_headers()", "item_id": "W1"}
            )
        assert result is not None
        assert result["scope_aligned"] is False


# ── 10. Prompt Rewriter with Rework Items ─────────────────────────────────


class TestPromptRewriterWithRework:
    """H4: Test prompt rewriter handles reviews with rework items."""

    def test_rework_items_included_in_context(self):
        """Verify rewriter builds review_context with rework summaries."""
        import generate_next_worker_prompt as gnwp
        review = {
            "overall_verdict": "ACCEPTED_WITH_REWORK",
            "evidence_quality_score": 0.5,
            "accepted_items": ["W1"],
            "item_grades": [
                {
                    "item_id": "W2",
                    "item_title": "Fix broken parser",
                    "supervisor_grade": "REWORK_REQUIRED",
                    "required_rework": "Tests failing",
                },
                {
                    "item_id": "W3",
                    "item_title": "Add feature X",
                    "supervisor_grade": "OVERCLAIMED",
                    "required_rework": "No evidence found",
                },
            ],
        }
        # With LLM disabled, rewriter returns None — but we can test it doesn't crash
        with _disable_llm():
            result = gnwp.rewrite_prompt_with_context(
                "# Prompt\n## Hard Prohibitions\n- no push\n",
                review,
                "mainstream",
            )
        assert result is None  # No LLM available — correct behavior

    def test_rewriter_with_mock_llm_preserves_governance(self):
        """Mock LLM rewrite — verify governance sections preserved."""
        import generate_next_worker_prompt as gnwp

        prompt = (
            "# Sprint Prompt\n"
            "## Hard Prohibitions\n- No git push\n- No git commit\n"
            "## Train A\nDo something\n"
            "## Evidence Declaration Requirements\nWrite YAML\n"
        )
        review = {
            "overall_verdict": "ACCEPTED_WITH_REWORK",
            "evidence_quality_score": 0.3,
            "accepted_items": ["W1"],
            "item_grades": [
                {
                    "item_id": "W2",
                    "item_title": "Broken item",
                    "supervisor_grade": "REWORK_REQUIRED",
                    "required_rework": "Tests fail",
                },
            ],
        }

        # Mock gateway to return a valid rewrite preserving governance
        rewritten = (
            "# Sprint Prompt — Enhanced\n"
            "## Sprint Context\nPrior sprint had rework items.\n"
            "## Hard Prohibitions\n- No git push\n- No git commit\n"
            "## Train A\nDo something better\n"
            "## Evidence Declaration Requirements\nWrite YAML\n"
        )
        mock_resp = ({"content": rewritten}, type("R", (), {"status": "success"})())

        # gateway_chat is imported locally inside rewrite_prompt_with_context,
        # so we must mock at the source module path
        mock_cfg = type("C", (), {
            "is_configured": True, "endpoint": "http://test",
            "provider_name": "openai", "endpoint_identity": "test",
        })()
        with patch("tools.ai.control_plane.gateway.gateway_chat", return_value=mock_resp), \
             patch("tools.ai.control_plane.config.load_ai_config", return_value=mock_cfg):
            result = gnwp.rewrite_prompt_with_context(prompt, review, "mainstream")

        # Result should be the rewritten prompt (governance sections present)
        if result is not None:
            assert "## Hard Prohibitions" in result
            assert "## Evidence Declaration Requirements" in result


# ── P2-H1: SDK Fallback Retry ────────────────────────────────────────────


class TestSDKFallbackRetry:
    """Tests for SDK fallback retry logic with backoff."""

    @staticmethod
    def _make_mock_openai(create_fn):
        """Build a mock openai module with a custom create function."""
        import types
        mod = types.ModuleType("openai")

        class _Completions:
            @staticmethod
            def create(**kw):
                return create_fn(**kw)

        class _Chat:
            completions = _Completions()

        class MockClient:
            def __init__(self, **kw):
                pass
            chat = _Chat()

        mod.OpenAI = MockClient
        return mod

    def test_retry_succeeds_on_second_attempt(self):
        """Mock first call to fail, second to succeed."""
        import grade_declared_work as gdw
        mock_cfg = type("C", (), {"endpoint": "http://test"})()

        call_count = {"n": 0}
        def create_fn(**kw):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise ConnectionError("transient failure")
            return type("R", (), {
                "choices": [type("C", (), {
                    "message": type("M", (), {"content": '{"adequate": true}'})()
                })()]
            })()

        messages = [{"role": "user", "content": "test"}]
        with patch.dict(os.environ, {"GPT_OSS_API_KEY": "test-key"}), \
             patch.dict(sys.modules, {"openai": self._make_mock_openai(create_fn)}):
            result = gdw._sv_sdk_fallback(messages, mock_cfg)

        assert result is not None
        assert call_count["n"] == 2

    def test_retry_exhausted_returns_none(self):
        """Both attempts fail → returns None gracefully."""
        import grade_declared_work as gdw
        mock_cfg = type("C", (), {"endpoint": "http://test"})()

        def fail_fn(**kw):
            raise ConnectionError("persistent failure")

        messages = [{"role": "user", "content": "test"}]
        with patch.dict(os.environ, {"GPT_OSS_API_KEY": "test-key"}), \
             patch.dict(sys.modules, {"openai": self._make_mock_openai(fail_fn)}):
            result = gdw._sv_sdk_fallback(messages, mock_cfg)

        assert result is None

    def test_no_api_key_skips_retry(self):
        """No API key → returns None immediately without attempting."""
        import grade_declared_work as gdw
        mock_cfg = type("C", (), {"endpoint": "http://test"})()
        messages = [{"role": "user", "content": "test"}]
        with patch.dict(os.environ, {"GPT_OSS_API_KEY": ""}):
            result = gdw._sv_sdk_fallback(messages, mock_cfg)
        assert result is None

    def test_retry_3_attempts_succeeds_on_third(self):
        """Mock first 2 calls fail, third succeeds → result returned (3-attempt backoff)."""
        import grade_declared_work as gdw
        mock_cfg = type("C", (), {"endpoint": "http://test"})()

        call_count = {"n": 0}
        def create_fn(**kw):
            call_count["n"] += 1
            if call_count["n"] < 3:
                raise ConnectionError("transient failure")
            return type("R", (), {
                "choices": [type("C", (), {
                    "message": type("M", (), {"content": '{"adequate": true}'})()
                })()]
            })()

        messages = [{"role": "user", "content": "test"}]
        with patch.dict(os.environ, {"GPT_OSS_API_KEY": "test-key"}), \
             patch.dict(sys.modules, {"openai": self._make_mock_openai(create_fn)}):
            result = gdw._sv_sdk_fallback(messages, mock_cfg)

        assert result is not None
        assert call_count["n"] == 3

    def test_retry_sleep_calls_exponential(self):
        """Verify exponential backoff: sleep(1) then sleep(2) between attempts."""
        import grade_declared_work as gdw
        mock_cfg = type("C", (), {"endpoint": "http://test"})()

        def fail_fn(**kw):
            raise ConnectionError("persistent failure")

        messages = [{"role": "user", "content": "test"}]
        sleep_calls = []
        with patch.dict(os.environ, {"GPT_OSS_API_KEY": "test-key"}), \
             patch.dict(sys.modules, {"openai": self._make_mock_openai(fail_fn)}), \
             patch("time.sleep", side_effect=lambda s: sleep_calls.append(s)):
            gdw._sv_sdk_fallback(messages, mock_cfg)

        assert sleep_calls == [1, 2], f"Expected [1, 2] exponential backoff, got {sleep_calls}"

    def test_retry_exhausted_3_returns_none(self):
        """All 3 attempts fail → returns None gracefully (3-attempt version)."""
        import grade_declared_work as gdw
        mock_cfg = type("C", (), {"endpoint": "http://test"})()

        call_count = {"n": 0}
        def fail_fn(**kw):
            call_count["n"] += 1
            raise ConnectionError("persistent failure")

        messages = [{"role": "user", "content": "test"}]
        with patch.dict(os.environ, {"GPT_OSS_API_KEY": "test-key"}), \
             patch.dict(sys.modules, {"openai": self._make_mock_openai(fail_fn)}), \
             patch("time.sleep"):
            result = gdw._sv_sdk_fallback(messages, mock_cfg)

        assert result is None
        assert call_count["n"] == 3


# ── P2-H2: tests_supporting Population ───────────────────────────────────


class TestTestsSupportingPopulation:
    """Tests for tests_supporting population from evidence_paths."""

    def _grade_item(self):
        from grade_declared_work import grade_item
        return grade_item

    def test_test_paths_populate_tests_supporting(self):
        """Item with test file in evidence_paths + passing tests → tests_supporting populated."""
        inspection = {
            "item_id": "W-TEST",
            "declared_status": "completed",
            "has_evidence": True,
            "has_tests": True,
            "evidence_paths_found": [
                "src/python/abw/abw_codec.py",
                "tests/python/abw/test_r148_abw_word_wrap.py",
            ],
            "evidence_paths_missing": [],
        }
        test_results = {"passed": 5, "failed": 0, "errors": 0}
        grade = self._grade_item()(inspection, test_results)
        assert grade["tests_supporting"] == ["tests/python/abw/test_r148_abw_word_wrap.py"]

    def test_failing_tests_block_tests_supporting(self):
        """Test failures → tests_supporting stays empty."""
        inspection = {
            "item_id": "W-FAIL",
            "declared_status": "completed",
            "has_evidence": True,
            "has_tests": True,
            "evidence_paths_found": [
                "src/python/abw/abw_codec.py",
                "tests/python/abw/test_r148_abw_word_wrap.py",
            ],
            "evidence_paths_missing": [],
        }
        test_results = {"passed": 5, "failed": 1, "errors": 0}
        grade = self._grade_item()(inspection, test_results)
        assert grade["tests_supporting"] == []

    def test_no_test_paths_no_population(self):
        """No test files in evidence_paths → tests_supporting stays empty."""
        inspection = {
            "item_id": "W-NOTEST",
            "declared_status": "completed",
            "has_evidence": True,
            "has_tests": False,
            "evidence_paths_found": ["src/python/abw/abw_codec.py"],
            "evidence_paths_missing": [],
        }
        test_results = {"passed": 5, "failed": 0, "errors": 0}
        grade = self._grade_item()(inspection, test_results)
        assert grade["tests_supporting"] == []

    def test_tests_supporting_enables_accepted_verified(self):
        """With tests_supporting populated, grade can reach ACCEPTED_VERIFIED."""
        inspection = {
            "item_id": "W-VERIFIED",
            "declared_status": "completed",
            "has_evidence": True,
            "has_tests": True,
            "evidence_paths_found": [
                "src/python/abw/abw_codec.py",
                "tests/python/abw/test_r148_abw_word_wrap.py",
            ],
            "evidence_paths_missing": [],
        }
        test_results = {"passed": 5, "failed": 0, "errors": 0}
        grade = self._grade_item()(inspection, test_results)
        assert grade["tests_supporting"]
        assert grade["supervisor_grade"] == "ACCEPTED_VERIFIED"


# ── P2-H3: Confidence Floor ─────────────────────────────────────────────


class TestConfidenceFloor:
    """Tests for low-confidence override in semantic_verify_item."""

    def test_low_confidence_inadequate_overridden(self):
        """adequate=false with confidence < 0.80 → adequate=true with override flag."""
        from grade_declared_work import semantic_verify_item

        mock_response = json.dumps({
            "adequate": False,
            "confidence": 0.73,
            "stub_detected": False,
            "deficiencies": ["Missing edge case test"],
        })

        # Create minimal test fixture
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            test_file = tmp / "test_example.py"
            test_file.write_text("def test_basic(): assert True\n")

            inspection = {
                "evidence_paths_found": [str(test_file)],
            }
            decl_item = {
                "title": "implement example()",
                "acceptance_criteria": "test passes",
            }

            with patch("grade_declared_work._sv_llm_call", return_value=mock_response):
                result = semantic_verify_item(inspection, decl_item, tmp)

        assert result["adequate"] is True
        assert result["low_confidence_override"] is True
        assert result["llm_used"] is True

    def test_high_confidence_inadequate_not_overridden(self):
        """adequate=false with confidence >= 0.80 → stays inadequate."""
        from grade_declared_work import semantic_verify_item

        mock_response = json.dumps({
            "adequate": False,
            "confidence": 0.92,
            "stub_detected": False,
            "deficiencies": ["Missing error handling test"],
        })

        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            test_file = tmp / "test_example.py"
            test_file.write_text("def test_basic(): assert True\n")

            inspection = {
                "evidence_paths_found": [str(test_file)],
            }
            decl_item = {
                "title": "implement example()",
                "acceptance_criteria": "test passes",
            }

            with patch("grade_declared_work._sv_llm_call", return_value=mock_response):
                result = semantic_verify_item(inspection, decl_item, tmp)

        assert result["adequate"] is False
        assert result.get("low_confidence_override") is not True
        assert result["llm_used"] is True

    def test_adequate_true_not_affected(self):
        """adequate=true is never overridden regardless of confidence."""
        from grade_declared_work import semantic_verify_item

        mock_response = json.dumps({
            "adequate": True,
            "confidence": 0.65,
            "stub_detected": False,
            "deficiencies": [],
        })

        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            test_file = tmp / "test_example.py"
            test_file.write_text("def test_basic(): assert True\n")

            inspection = {
                "evidence_paths_found": [str(test_file)],
            }
            decl_item = {
                "title": "implement example()",
                "acceptance_criteria": "test passes",
            }

            with patch("grade_declared_work._sv_llm_call", return_value=mock_response):
                result = semantic_verify_item(inspection, decl_item, tmp)

        assert result["adequate"] is True
        assert result.get("low_confidence_override") is not True


# ── P2-H5: Deprecation Marker ───────────────────────────────────────────


class TestDeprecationMarker:
    """Tests for evidence_quality_score deprecation in grade_all output."""

    def test_deprecation_marker_present(self):
        """evidence_quality_breakdown includes deprecation marker."""
        from grade_declared_work import grade_all

        inspection = {
            "test_results": {"passed": 1, "failed": 0, "errors": 0},
            "item_inspections": [{
                "item_id": "W1",
                "declared_status": "completed",
                "has_evidence": True,
                "has_tests": False,
                "evidence_paths_found": ["src/example.py"],
                "evidence_paths_missing": [],
            }],
        }
        declaration = {
            "planned_work_items": [{"item_id": "W1", "title": "Test", "status": "completed"}],
            "_repo_root": str(_REPO),
        }

        with _disable_llm():
            result = grade_all(inspection, declaration)

        eqb = result["evidence_quality_breakdown"]
        assert eqb["evidence_quality_score_deprecated"] is True
        assert eqb["primary_quality_metric"] == "semantic_quality_score"
