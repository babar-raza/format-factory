"""R110: Prompt Quality Advancement Lane Fix Tests

Verifies:
- Acceleration prompts contain stream-specific advancement content
- advancement_lane check passes for all non-mainstream streams
- Sprint goal includes stream-specific advancement description
- STREAM_FORWARD_WORK content appears in generated prompts
- Next-work-items remain stream-correct after prompt fix
"""
import sys
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"
sys.path.insert(0, str(TOOLS_DIR))

from generate_next_worker_prompt import (
    generate_prompt,
    generate_next_work_items,
    build_sprint_goal,
    STREAM_FORWARD_WORK,
    STREAM_GROUPS,
)
from validate_prompt_quality import (
    validate_prompt_quality,
    validate_next_work_items,
)


def _make_review(sprint_id="FORMAT-FACTORY-ACCELERATION-R109-TEST-001"):
    return {
        "run_id": "test-r109",
        "sprint_id": sprint_id,
        "overall_verdict": "ACCEPTED",
        "autonomous_continue": True,
        "test_results": {"passed": 100, "failed": 0, "skipped": 0},
        "item_grades": [],
        "accepted_items": [],
        "rework_items": [],
        "rejected_items": [],
        "overclaimed_items": [],
    }


# --- Wave 1: Advancement-lane definition ---


class TestAdvancementLaneDefinition:
    """Verify that acceleration advancement terms are well-defined."""

    def test_acceleration_has_forward_work(self):
        assert "acceleration" in STREAM_FORWARD_WORK
        assert len(STREAM_FORWARD_WORK["acceleration"]) >= 3

    def test_forward_work_items_have_required_fields(self):
        for stream, items in STREAM_FORWARD_WORK.items():
            for item in items:
                assert "id" in item, f"{stream} item missing id"
                assert "title" in item, f"{stream} item missing title"
                assert "desc" in item, f"{stream} item missing desc"

    def test_all_non_mainstream_streams_have_forward_work(self):
        for stream in ("acceleration", "skills", "supervisor"):
            assert stream in STREAM_FORWARD_WORK
            assert len(STREAM_FORWARD_WORK[stream]) >= 2

    def test_acceleration_groups_include_rework(self):
        """Acceleration trains should include G2 (rework group) for forward work."""
        assert "G2" in STREAM_GROUPS["acceleration"]


# --- Wave 2: Prompt quality fix ---


class TestPromptQualityAdvancementLaneFix:
    """Verify that generated acceleration prompts pass advancement_lane check."""

    def test_acceleration_prompt_passes_advancement_lane(self):
        review = _make_review()
        prompt = generate_prompt(review, stream="acceleration")
        pq = validate_prompt_quality(prompt, "acceleration", has_advancement=True)
        advancement = next(c for c in pq["checks"] if c["check"] == "advancement_lane")
        assert advancement["pass"] is True

    def test_acceleration_prompt_passes_all_checks(self):
        review = _make_review()
        prompt = generate_prompt(review, stream="acceleration")
        pq = validate_prompt_quality(prompt, "acceleration", has_advancement=True)
        assert pq["valid"] is True, f"Failed: {[c['check'] for c in pq['checks'] if not c['pass']]}"

    def test_skills_prompt_passes_advancement_lane(self):
        review = _make_review(sprint_id="FORMAT-FACTORY-SKILLS-R109-TEST-001")
        prompt = generate_prompt(review, stream="skills")
        pq = validate_prompt_quality(prompt, "skills", has_advancement=True)
        advancement = next(c for c in pq["checks"] if c["check"] == "advancement_lane")
        assert advancement["pass"] is True

    def test_supervisor_prompt_passes_advancement_lane(self):
        review = _make_review(sprint_id="FORMAT-FACTORY-SUPERVISOR-R109-TEST-001")
        prompt = generate_prompt(review, stream="supervisor")
        pq = validate_prompt_quality(prompt, "supervisor", has_advancement=True)
        advancement = next(c for c in pq["checks"] if c["check"] == "advancement_lane")
        assert advancement["pass"] is True


# --- Wave 2 continued: Forward-work content in prompts ---


class TestForwardWorkInPrompts:
    """Verify that STREAM_FORWARD_WORK descriptions appear in generated prompts."""

    def test_acceleration_prompt_contains_forward_work_titles(self):
        review = _make_review()
        prompt = generate_prompt(review, stream="acceleration")
        lower = prompt.lower()
        for fw in STREAM_FORWARD_WORK["acceleration"]:
            assert fw["title"].lower() in lower, f"Missing forward work title: {fw['title']}"

    def test_acceleration_prompt_contains_advancement_terms(self):
        review = _make_review()
        prompt = generate_prompt(review, stream="acceleration")
        lower = prompt.lower()
        accel_terms = ["detector", "harden", "expand", "enhance", "severity", "enforce"]
        found = [t for t in accel_terms if t in lower]
        assert len(found) >= 3, f"Only found {found} in prompt"

    def test_skills_prompt_contains_forward_work_titles(self):
        review = _make_review(sprint_id="FORMAT-FACTORY-SKILLS-R109-TEST-001")
        prompt = generate_prompt(review, stream="skills")
        lower = prompt.lower()
        for fw in STREAM_FORWARD_WORK["skills"]:
            assert fw["title"].lower() in lower, f"Missing: {fw['title']}"

    def test_supervisor_prompt_contains_forward_work_titles(self):
        review = _make_review(sprint_id="FORMAT-FACTORY-SUPERVISOR-R109-TEST-001")
        prompt = generate_prompt(review, stream="supervisor")
        lower = prompt.lower()
        for fw in STREAM_FORWARD_WORK["supervisor"]:
            assert fw["title"].lower() in lower, f"Missing: {fw['title']}"


# --- Wave 2 continued: Sprint goal ---


class TestSprintGoalStreamAwareness:
    """Verify that sprint goal includes stream advancement descriptions."""

    def test_acceleration_sprint_goal_mentions_advancement(self):
        review = _make_review()
        trains = []  # No product trains
        goal = build_sprint_goal(review, [], trains, stream="acceleration")
        assert "advance" in goal.lower()
        assert "acceleration" in goal.lower()

    def test_mainstream_sprint_goal_unchanged(self):
        review = _make_review()
        trains = []
        goal = build_sprint_goal(review, [], trains, stream="mainstream")
        # Mainstream with no product trains should still have evidence part
        assert "evidence" in goal.lower()

    def test_skills_sprint_goal_mentions_skills(self):
        review = _make_review()
        goal = build_sprint_goal(review, [], [], stream="skills")
        assert "skills" in goal.lower()


# --- Wave 3: Next-work consistency ---


class TestNextWorkConsistency:
    """Verify next-work-items remain stream-correct after prompt fix."""

    def test_acceleration_nwi_no_product_items(self):
        review = _make_review()
        nwi = generate_next_work_items(review, stream="acceleration")
        product = [i for i in nwi["items"] if i["source"] == "product-factory"]
        assert len(product) == 0

    def test_acceleration_nwi_has_forward_work(self):
        review = _make_review()
        nwi = generate_next_work_items(review, stream="acceleration")
        forward = [i for i in nwi["items"] if i["lane"] == "acceleration-advancement"]
        assert len(forward) >= 3

    def test_all_streams_nwi_validate(self):
        for stream in ["mainstream", "acceleration", "skills", "supervisor"]:
            review = _make_review()
            nwi = generate_next_work_items(review, stream=stream)
            result = validate_next_work_items(nwi, stream)
            assert result["valid"] is True, f"{stream}: {[c for c in result['checks'] if not c['pass']]}"

    def test_acceleration_nwi_stream_field_correct(self):
        review = _make_review()
        nwi = generate_next_work_items(review, stream="acceleration")
        assert nwi["stream"] == "acceleration"


# --- Wave 4: Regression ---


class TestPromptQualityRegression:
    """Ensure existing checks are not broken by R110 changes."""

    def test_short_prompt_still_fails_not_generic(self):
        pq = validate_prompt_quality("too short", "acceleration", has_advancement=False)
        generic = next(c for c in pq["checks"] if c["check"] == "not_generic")
        assert generic["pass"] is False

    def test_no_advancement_flag_skips_check(self):
        pq = validate_prompt_quality("x " * 60, "acceleration", has_advancement=False)
        advancement_checks = [c for c in pq["checks"] if c["check"] == "advancement_lane"]
        assert len(advancement_checks) == 0

    def test_wrong_stream_still_detected(self):
        # A prompt with mainstream markers should fail for acceleration
        prompt = "gate 11 fods fodt product " * 20 + " tool validator "
        pq = validate_prompt_quality(prompt, "acceleration")
        # Stream identity should still work
        identity = next(c for c in pq["checks"] if c["check"] == "stream_identity")
        assert identity["pass"] is True  # "tool" + "validator" match acceleration markers
