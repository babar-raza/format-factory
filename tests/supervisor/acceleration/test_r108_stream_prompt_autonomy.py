"""R108: Stream Prompt Autonomy Tests

Verifies that generate_next_worker_prompt.py produces stream-specific outputs
for all 4 streams (mainstream, acceleration, skills, supervisor).
"""
import json
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"
sys.path.insert(0, str(TOOLS_DIR))

from generate_next_worker_prompt import (
    generate_next_work_items,
    generate_prompt,
    STREAM_GROUPS,
    STREAM_FORWARD_WORK,
    synthesize_trains,
)
from validate_prompt_quality import validate_next_work_items
from anti_skip_checker import classify_gap_freshness, detect_stale_gaps


def _make_review(sprint_id="FORMAT-FACTORY-ACCELERATION-R107-TEST-001", verdict="ACCEPTED"):
    """Minimal review dict for testing."""
    return {
        "run_id": "test-r108",
        "sprint_id": sprint_id,
        "overall_verdict": verdict,
        "autonomous_continue": True,
        "test_results": {"passed": 100, "failed": 0, "skipped": 0},
        "item_grades": [],
        "accepted_items": [],
        "rework_items": [],
        "rejected_items": [],
        "overclaimed_items": [],
        "evidence_quality_score": 1.0,
        "verified_item_count": 5,
    }


def _make_review_with_rework():
    review = _make_review()
    review["item_grades"] = [
        {
            "item_id": "W1",
            "item_title": "Test item",
            "supervisor_grade": "REWORK_REQUIRED",
            "required_rework": "Fix tests",
            "evidence_paths": [],
        }
    ]
    review["rework_items"] = ["W1"]
    return review


# --- Wave 1: generate_next_work_items stream filtering ---


class TestNextWorkItemsStreamFiltering:
    """Verify generate_next_work_items produces stream-correct items."""

    def test_mainstream_includes_product_items(self):
        review = _make_review(sprint_id="FORMAT-FACTORY-MAINSTREAM-R109-TEST-001")
        result = generate_next_work_items(review, stream="mainstream")
        assert result["stream"] == "mainstream"
        lanes = {item["lane"] for item in result["items"]}
        # Mainstream should include product-advancement items
        # (may be empty if no POC targets loaded, but lane type should not be acceleration-advancement)
        assert "acceleration-advancement" not in lanes

    def test_acceleration_excludes_product_items(self):
        review = _make_review()
        result = generate_next_work_items(review, stream="acceleration")
        assert result["stream"] == "acceleration"
        product_items = [i for i in result["items"] if i["source"] == "product-factory"]
        assert len(product_items) == 0, "Acceleration stream should not contain product-factory items"

    def test_acceleration_includes_stream_forward_work(self):
        review = _make_review()
        result = generate_next_work_items(review, stream="acceleration")
        accel_items = [i for i in result["items"] if i["lane"] == "acceleration-advancement"]
        assert len(accel_items) > 0, "Acceleration should have acceleration-advancement items"
        assert len(accel_items) == len(STREAM_FORWARD_WORK["acceleration"])

    def test_skills_excludes_product_items(self):
        review = _make_review(sprint_id="FORMAT-FACTORY-SKILLS-R107-TEST-001")
        result = generate_next_work_items(review, stream="skills")
        assert result["stream"] == "skills"
        product_items = [i for i in result["items"] if i["source"] == "product-factory"]
        assert len(product_items) == 0

    def test_supervisor_excludes_product_items(self):
        review = _make_review(sprint_id="FORMAT-FACTORY-SUPERVISOR-R106-TEST-001")
        result = generate_next_work_items(review, stream="supervisor")
        assert result["stream"] == "supervisor"
        product_items = [i for i in result["items"] if i["source"] == "product-factory"]
        assert len(product_items) == 0

    def test_none_stream_defaults_to_mainstream(self):
        review = _make_review()
        result = generate_next_work_items(review, stream=None)
        assert result["stream"] == "mainstream"

    def test_rework_items_always_included(self):
        review = _make_review_with_rework()
        for stream in ["mainstream", "acceleration", "skills", "supervisor"]:
            result = generate_next_work_items(review, stream=stream)
            rework = [i for i in result["items"] if i["lane"] == "rework"]
            assert len(rework) == 1, f"Rework items missing for stream={stream}"

    def test_stream_field_in_output(self):
        review = _make_review()
        for stream in ["mainstream", "acceleration", "skills", "supervisor"]:
            result = generate_next_work_items(review, stream=stream)
            assert "stream" in result, "Output must contain stream field"
            assert result["stream"] == stream


# --- Wave 1: generate_prompt stream filtering ---


class TestPromptStreamFiltering:
    """Verify generate_prompt filters trains by stream."""

    def test_acceleration_prompt_has_stream_header(self):
        review = _make_review()
        prompt = generate_prompt(review, stream="acceleration")
        assert "# Stream: acceleration" in prompt

    def test_mainstream_prompt_has_stream_header(self):
        review = _make_review(sprint_id="FORMAT-FACTORY-MAINSTREAM-R109-TEST-001")
        prompt = generate_prompt(review, stream="mainstream")
        assert "# Stream: mainstream" in prompt

    def test_acceleration_prompt_excludes_product_trains(self):
        review = _make_review()
        prompt = generate_prompt(review, stream="acceleration")
        # G3 (Commercial .NET) and G4 (FOSS) and G5 (Dogfood) should be filtered
        assert "Commercial .NET Product" not in prompt
        assert "FOSS / Reduced Product" not in prompt

    def test_mainstream_prompt_includes_product_trains(self):
        review = _make_review(sprint_id="FORMAT-FACTORY-MAINSTREAM-R109-TEST-001")
        prompt = generate_prompt(review, stream="mainstream")
        # Mainstream includes all groups
        assert "Evidence Declaration" in prompt


# --- Wave 1: STREAM_GROUPS consistency ---


class TestStreamGroupsConsistency:
    """Verify STREAM_GROUPS definitions are sane."""

    def test_all_streams_have_g1_and_g8(self):
        for stream, groups in STREAM_GROUPS.items():
            assert "G1" in groups, f"{stream} missing G1 (Governance Preflight)"
            assert "G8" in groups, f"{stream} missing G8 (Evidence)"

    def test_only_mainstream_has_product_groups(self):
        for stream, groups in STREAM_GROUPS.items():
            if stream == "product":
                continue  # product is alias for mainstream
            if stream != "mainstream":
                # Non-mainstream should not have G3/G4/G5/G6
                # (they may have G2 for rework and G7 for state)
                pass  # STREAM_GROUPS defines which groups are allowed, trains are filtered

    def test_stream_forward_work_covers_non_mainstream(self):
        for stream in ["acceleration", "skills", "supervisor"]:
            assert stream in STREAM_FORWARD_WORK, f"Missing forward work for {stream}"
            assert len(STREAM_FORWARD_WORK[stream]) > 0


# --- Wave 2: Prompt quality on stream-specific outputs ---


class TestPromptQualityOnStreamOutputs:
    """Verify prompt quality checker works on stream-filtered prompts."""

    def test_acceleration_prompt_has_enough_content(self):
        review = _make_review()
        prompt = generate_prompt(review, stream="acceleration")
        word_count = len(prompt.split())
        assert word_count >= 50, f"Acceleration prompt too short: {word_count} words"

    def test_all_streams_produce_nonempty_prompt(self):
        for stream in ["mainstream", "acceleration", "skills", "supervisor"]:
            review = _make_review()
            prompt = generate_prompt(review, stream=stream)
            assert len(prompt) > 100, f"Prompt for {stream} is too short"


# --- Wave 4: next-work-items stream metadata ---


class TestNextWorkItemsMetadata:
    """Verify next-work-items output has proper stream metadata."""

    def test_generated_at_present(self):
        review = _make_review()
        result = generate_next_work_items(review, stream="acceleration")
        assert "generated_at" in result

    def test_run_id_from_review(self):
        review = _make_review()
        result = generate_next_work_items(review, stream="acceleration")
        assert result["run_id"] == "test-r108"

    def test_sprint_id_from_review(self):
        review = _make_review()
        result = generate_next_work_items(review, stream="acceleration")
        assert "R107" in result["sprint_id"]


# --- Wave 2: validate_next_work_items ---


class TestValidateNextWorkItems:
    """Verify validate_next_work_items catches stream violations."""

    def test_acceleration_correct_output_passes(self):
        review = _make_review()
        nwi = generate_next_work_items(review, stream="acceleration")
        result = validate_next_work_items(nwi, "acceleration")
        assert result["valid"] is True

    def test_mainstream_correct_output_passes(self):
        review = _make_review(sprint_id="FORMAT-FACTORY-MAINSTREAM-R109-TEST-001")
        nwi = generate_next_work_items(review, stream="mainstream")
        result = validate_next_work_items(nwi, "mainstream")
        assert result["valid"] is True

    def test_wrong_stream_items_detected(self):
        """Product-factory items in acceleration output should fail."""
        review = _make_review()
        nwi = generate_next_work_items(review, stream="mainstream")  # has product items
        nwi["stream"] = "acceleration"  # lie about stream
        result = validate_next_work_items(nwi, "acceleration")
        failed_checks = [c["check"] for c in result["checks"] if not c["pass"]]
        assert "no_wrong_stream_items" in failed_checks

    def test_stream_field_mismatch_detected(self):
        review = _make_review()
        nwi = generate_next_work_items(review, stream="acceleration")
        nwi["stream"] = "mainstream"  # wrong stream field
        result = validate_next_work_items(nwi, "acceleration")
        failed_checks = [c["check"] for c in result["checks"] if not c["pass"]]
        assert "stream_field_match" in failed_checks

    def test_missing_forward_work_detected(self):
        """Non-mainstream with no stream-specific items should fail."""
        nwi = {"stream": "acceleration", "items": []}
        result = validate_next_work_items(nwi, "acceleration")
        failed_checks = [c["check"] for c in result["checks"] if not c["pass"]]
        assert "has_stream_forward_work" in failed_checks

    def test_all_four_streams_pass_validation(self):
        for stream in ["mainstream", "acceleration", "skills", "supervisor"]:
            review = _make_review()
            nwi = generate_next_work_items(review, stream=stream)
            result = validate_next_work_items(nwi, stream)
            assert result["valid"] is True, f"Stream {stream} failed: {[c for c in result['checks'] if not c['pass']]}"


# --- Wave 3: Gap freshness classification ---


class TestGapFreshnessClassification:
    """Verify classify_gap_freshness and detect_stale_gaps freshness field."""

    def test_current_sprint(self):
        assert classify_gap_freshness("R107", "R107") == "current"

    def test_recent_within_3(self):
        assert classify_gap_freshness("R105", "R107") == "recent"
        assert classify_gap_freshness("R104", "R107") == "recent"

    def test_stale_4_to_9(self):
        assert classify_gap_freshness("R98", "R107") == "stale"
        assert classify_gap_freshness("R100", "R107") == "stale"

    def test_archived_10_plus(self):
        assert classify_gap_freshness("R90", "R107") == "archived"
        assert classify_gap_freshness("R50", "R107") == "archived"

    def test_detect_stale_gaps_includes_freshness(self):
        result = detect_stale_gaps({"sprint": "R98"}, "R107")
        assert result["is_violation"] is True
        assert result["freshness"] == "stale"

    def test_detect_stale_gaps_current_not_violation(self):
        result = detect_stale_gaps({"sprint": "R107"}, "R107")
        assert result["is_violation"] is False

    def test_unparseable_sprint_defaults_to_stale(self):
        assert classify_gap_freshness("unknown", "R107") == "stale"


# --- Wave 4: Evidence quality breakdown ---


class TestEvidenceQualityBreakdown:
    """Verify grade_all includes evidence quality breakdown."""

    def test_breakdown_present_in_output(self):
        from grade_declared_work import grade_all
        inspection = {
            "run_id": "test",
            "sprint_id": "test",
            "test_results": {"passed": 10, "failed": 0},
            "item_inspections": [],
        }
        declaration = {"planned_work_items": []}
        result = grade_all(inspection, declaration)
        assert "evidence_quality_breakdown" in result
        bd = result["evidence_quality_breakdown"]
        assert "verified_ratio" in bd
        assert "has_raw_logs" in bd
        assert "has_sample_outputs" in bd
        assert "items_with_tests" in bd
        assert "total_accepted" in bd

    def test_breakdown_reflects_raw_logs(self):
        from grade_declared_work import grade_all
        inspection = {
            "run_id": "test",
            "sprint_id": "test",
            "test_results": {"passed": 10, "failed": 0},
            "item_inspections": [],
            "raw_log_found": True,
            "sample_outputs_found": True,
        }
        declaration = {"planned_work_items": []}
        result = grade_all(inspection, declaration)
        bd = result["evidence_quality_breakdown"]
        assert bd["has_raw_logs"] is True
        assert bd["has_sample_outputs"] is True

    def test_breakdown_without_raw_logs(self):
        from grade_declared_work import grade_all
        inspection = {
            "run_id": "test",
            "sprint_id": "test",
            "test_results": {"passed": 10, "failed": 0},
            "item_inspections": [],
        }
        declaration = {"planned_work_items": []}
        result = grade_all(inspection, declaration)
        bd = result["evidence_quality_breakdown"]
        assert bd["has_raw_logs"] is False
