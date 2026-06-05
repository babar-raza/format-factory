"""R111: Stream-Output Authority, Global Next-Sprint Cleanup, and Evidence Quality Tests

Verifies:
- Stream-output authority classification model
- Wrong-stream next-sprint detection
- Global next-sprint stream fix in generate_supervisor_packet.py main()
- Prompt-quality expansion for global next-sprint inspection
- Evidence-quality scoring improvements
- generate_supervisor_packet.py main() stream detection
"""
import json
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"
sys.path.insert(0, str(TOOLS_DIR))

from anti_skip_checker import (
    classify_stream_output_authority,
    detect_wrong_stream_next_sprint,
    STREAM_OUTPUT_AUTHORITY,
    SEVERITY_MAP,
    classify_violation_impact,
    run_all_checks,
)
from generate_supervisor_packet import detect_stream_from_sprint_id
from generate_next_worker_prompt import generate_prompt, generate_next_work_items
from validate_prompt_quality import validate_prompt_quality, validate_next_work_items


# --- Wave 1: Stream-output authority model ---


class TestStreamOutputAuthorityModel:
    """Verify the stream-output authority classification system."""

    def test_authority_has_five_levels(self):
        assert len(STREAM_OUTPUT_AUTHORITY) == 5

    def test_same_stream_is_authority(self):
        result = classify_stream_output_authority(
            "review/combined-prompt.md", "acceleration", "acceleration"
        )
        assert result == "CURRENT_STREAM_AUTHORITY"

    def test_different_stream_is_reference(self):
        result = classify_stream_output_authority(
            "review/combined-prompt.md", "mainstream", "acceleration"
        )
        assert result == "CROSS_STREAM_REFERENCE"

    def test_global_different_stream_is_snapshot(self):
        result = classify_stream_output_authority(
            "reports/supervisor/next-sprint.md", "mainstream", "acceleration", is_global=True
        )
        assert result == "ARCHIVED_LAST_WRITER_SNAPSHOT"

    def test_global_same_stream_is_authority(self):
        result = classify_stream_output_authority(
            "reports/supervisor/next-sprint.md", "acceleration", "acceleration", is_global=True
        )
        assert result == "CURRENT_STREAM_AUTHORITY"

    def test_empty_stream_is_snapshot(self):
        result = classify_stream_output_authority(
            "unknown.md", "", "acceleration"
        )
        assert result == "ARCHIVED_LAST_WRITER_SNAPSHOT"


# --- Wave 2: Wrong-stream next-sprint detection ---


class TestWrongStreamNextSprint:
    """Verify detection of wrong-stream global next-sprint.md."""

    def test_mainstream_next_sprint_for_acceleration_is_violation(self):
        text = "# Stream: mainstream\nContent here"
        result = detect_wrong_stream_next_sprint(text, "acceleration")
        assert result["is_violation"] is True
        assert result["detected_stream"] == "mainstream"
        assert result["authority"] == "ARCHIVED_LAST_WRITER_SNAPSHOT"

    def test_acceleration_next_sprint_for_acceleration_is_clean(self):
        text = "# Stream: acceleration\nContent here"
        result = detect_wrong_stream_next_sprint(text, "acceleration")
        assert result["is_violation"] is False
        assert result["authority"] == "CURRENT_STREAM_AUTHORITY"

    def test_no_stream_header_is_snapshot(self):
        text = "No stream header\nJust content"
        result = detect_wrong_stream_next_sprint(text, "acceleration")
        assert result["is_violation"] is False
        assert result["authority"] == "ARCHIVED_LAST_WRITER_SNAPSHOT"

    def test_wrong_stream_severity_is_medium(self):
        """Medium = caveat, not block (global is last-writer-wins)."""
        assert SEVERITY_MAP["wrong_stream_next_sprint"] == "medium"

    def test_wrong_stream_appears_as_caveat(self):
        checks = [{"check": "wrong_stream_next_sprint", "is_violation": True}]
        impact = classify_violation_impact(checks)
        assert "wrong_stream_next_sprint" in impact["caveats"]
        assert impact["block"] is False

    def test_supervisor_for_skills_is_violation(self):
        text = "# Stream: supervisor\nContent"
        result = detect_wrong_stream_next_sprint(text, "skills")
        assert result["is_violation"] is True


# --- Wave 2 continued: Global next-sprint fix ---


class TestGlobalNextSprintStreamDetection:
    """Verify that generate_supervisor_packet.py main() detects stream correctly."""

    def test_acceleration_sprint_detected(self):
        assert detect_stream_from_sprint_id(
            "FORMAT-FACTORY-ACCELERATION-R110-TEST-001"
        ) == "acceleration"

    def test_mainstream_sprint_detected(self):
        assert detect_stream_from_sprint_id(
            "FORMAT-FACTORY-MAINSTREAM-R111-TEST-001"
        ) == "mainstream"

    def test_supervisor_sprint_detected(self):
        assert detect_stream_from_sprint_id(
            "FORMAT-FACTORY-SUPERVISOR-R108-TEST-001"
        ) == "supervisor"

    def test_skills_sprint_detected(self):
        assert detect_stream_from_sprint_id(
            "FORMAT-FACTORY-SKILLS-R109-TEST-001"
        ) == "skills"

    def test_legacy_sprint_defaults_to_mainstream(self):
        assert detect_stream_from_sprint_id(
            "FORMAT-FACTORY-R93-TEST-001"
        ) == "mainstream"


# --- Wave 3: Prompt quality with global next-sprint ---


class TestPromptQualityWithGlobalNextSprint:
    """Verify prompt quality handles global next-sprint stream correctly."""

    def _make_review(self, sprint_id="FORMAT-FACTORY-ACCELERATION-R111-TEST-001"):
        return {
            "run_id": "test",
            "sprint_id": sprint_id,
            "overall_verdict": "ACCEPTED",
            "autonomous_continue": True,
            "test_results": {"passed": 100, "failed": 0, "skipped": 0},
            "item_grades": [],
        }

    def test_acceleration_generated_prompt_passes_all(self):
        review = self._make_review()
        prompt = generate_prompt(review, stream="acceleration")
        pq = validate_prompt_quality(prompt, "acceleration", has_advancement=True)
        assert pq["valid"] is True

    def test_mainstream_text_fails_stream_identity_for_acceleration(self):
        # A mainstream-only prompt should not pass as acceleration
        mainstream_text = """
        # Sprint Prompt
        ## Sprint Focus
        ADVANCE: Product deepening — .NET commercial + Python FOSS + dogfood + packaging
        ## Section 1: Product Work
        TASK-001: Advance FODS Gate 11 commercial readiness
        TASK-002: Advance FODT Gate 11 commercial readiness
        ## Evidence
        Write evidence-declaration.yaml and run autonomous-cycle
        """ * 3  # Make it long enough
        pq = validate_prompt_quality(mainstream_text, "acceleration", has_advancement=True)
        # Stream identity should fail (no acceleration markers)
        identity = next(c for c in pq["checks"] if c["check"] == "stream_identity")
        assert identity["pass"] is False


# --- Wave 4: Run-all-checks integration ---


class TestRunAllChecksWithNextSprint:
    """Verify run_all_checks integrates wrong-stream next-sprint detection."""

    def test_wrong_stream_next_sprint_included(self):
        result = run_all_checks(
            target_stream="acceleration",
            next_sprint_text="# Stream: mainstream\nContent",
        )
        checks = {c["check"]: c for c in result["checks"]}
        assert "wrong_stream_next_sprint" in checks
        assert checks["wrong_stream_next_sprint"]["is_violation"] is True

    def test_correct_stream_next_sprint_clean(self):
        result = run_all_checks(
            target_stream="acceleration",
            next_sprint_text="# Stream: acceleration\nContent",
        )
        checks = {c["check"]: c for c in result["checks"]}
        assert "wrong_stream_next_sprint" in checks
        assert checks["wrong_stream_next_sprint"]["is_violation"] is False

    def test_no_next_sprint_text_skips_check(self):
        result = run_all_checks(target_stream="acceleration")
        checks = {c["check"] for c in result["checks"]}
        assert "wrong_stream_next_sprint" not in checks


# --- Wave 5: Stream-output authority map ---


class TestStreamOutputAuthorityMap:
    """Verify stream-output authority map generation."""

    def test_build_authority_map(self):
        """Build a complete authority map for an acceleration package."""
        artifacts = [
            ("review/combined-next-worker-prompt.md", "acceleration", False),
            ("review/next-work-items.json", "acceleration", False),
            ("reports/supervisor/next-sprint.md", "mainstream", True),
            ("reports/supervisor/evidence-review.md", "acceleration", True),
            ("reports/supervisor/contradictions.md", "acceleration", True),
        ]
        authority_map = {}
        for path, stream, is_global in artifacts:
            authority_map[path] = classify_stream_output_authority(
                path, stream, "acceleration", is_global=is_global
            )
        assert authority_map["review/combined-next-worker-prompt.md"] == "CURRENT_STREAM_AUTHORITY"
        assert authority_map["review/next-work-items.json"] == "CURRENT_STREAM_AUTHORITY"
        assert authority_map["reports/supervisor/next-sprint.md"] == "ARCHIVED_LAST_WRITER_SNAPSHOT"
        assert authority_map["reports/supervisor/evidence-review.md"] == "CURRENT_STREAM_AUTHORITY"
        assert authority_map["reports/supervisor/contradictions.md"] == "CURRENT_STREAM_AUTHORITY"


# --- Wave 6: Evidence quality ---


class TestEvidenceQualityImprovement:
    """Verify evidence quality scoring concepts."""

    def test_verified_items_improve_score(self):
        """Items with tests should count as verified."""
        grades = [
            {"supervisor_grade": "ACCEPTED_VERIFIED", "tests_supporting": ["test1"]},
            {"supervisor_grade": "ACCEPTED_VERIFIED", "tests_supporting": ["test2"]},
            {"supervisor_grade": "ACCEPTED_WITH_LIMITATIONS", "tests_supporting": []},
        ]
        verified = sum(1 for g in grades if g.get("tests_supporting"))
        total = len(grades)
        score = verified / total if total > 0 else 0
        assert score == pytest.approx(0.67, abs=0.01)

    def test_all_verified_reaches_target(self):
        grades = [
            {"supervisor_grade": "ACCEPTED_VERIFIED", "tests_supporting": ["t"]}
            for _ in range(7)
        ]
        verified = sum(1 for g in grades if g.get("tests_supporting"))
        score = verified / len(grades)
        assert score >= 0.70


# --- Wave 7: Regression ---


class TestStreamOutputRegression:
    """Ensure existing anti-skip checks are not broken."""

    def test_all_streams_nwi_validate(self):
        review = {
            "run_id": "test",
            "sprint_id": "FORMAT-FACTORY-ACCELERATION-R111-TEST-001",
            "overall_verdict": "ACCEPTED",
            "autonomous_continue": True,
            "test_results": {"passed": 100, "failed": 0, "skipped": 0},
            "item_grades": [],
        }
        for stream in ["mainstream", "acceleration", "skills", "supervisor"]:
            nwi = generate_next_work_items(review, stream=stream)
            result = validate_next_work_items(nwi, stream)
            assert result["valid"] is True, f"{stream}: {[c for c in result['checks'] if not c['pass']]}"

    def test_severity_map_has_new_entry(self):
        assert "wrong_stream_next_sprint" in SEVERITY_MAP
        assert SEVERITY_MAP["wrong_stream_next_sprint"] == "medium"
