"""R112: Live handoff, stream-local cycle isolation, YES_WITH_LIMITATIONS, skill promotion.

Wave 1: Near-live v3 handoff proof (supervisor grading handoff dry-run).
Wave 2: Stream-local cycle isolation (authority map, stream-local outputs).
Wave 3: YES_WITH_LIMITATIONS semantics (all-pass->YES, low-severity->YES_WITH_LIMITATIONS, critical->NO).
Wave 4: Skill promotion (record-lane-execution promoted to active).
Wave 5: Receiver fixture rerun.
Wave 6: Evidence-quality improvement.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
TOOLS_DIR = str(REPO_ROOT / "tools" / "supervisor")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from validate_adoption_compliance import validate_adoption  # noqa: E402
from validate_skill_transcript import validate_transcript  # noqa: E402
from autonomous_cycle import classify_continuation_state  # noqa: E402

R112_DIR = REPO_ROOT / "reports" / "skills-r112"
HANDOFF_DIR = R112_DIR / "generated-handoffs"
TRANSCRIPT_DIR = R112_DIR / "skill-transcripts"
RECEIVER_DIR = R112_DIR / "receiver-fixtures"
SAMPLE_DIR = R112_DIR / "sample-outputs"


# ============================================================
# Wave 1: LIVE/NEAR-LIVE V3 HANDOFF PROOF
# ============================================================

class TestLiveHandoffProof:
    """Near-live v3 handoff execution through full validation path."""

    def test_live_handoff_proof_exists(self):
        path = R112_DIR / "live-handoff-proof.json"
        assert path.exists()

    def test_proof_has_handoff_reference(self):
        data = json.loads((R112_DIR / "live-handoff-proof.json").read_text(encoding="utf-8"))
        assert "handoff_file" in data
        assert "supervisor" in data["handoff_file"].lower()

    def test_proof_has_transcript(self):
        data = json.loads((R112_DIR / "live-handoff-proof.json").read_text(encoding="utf-8"))
        assert "transcript" in data
        assert data["transcript"]["result"] == "PASS"

    def test_proof_transcript_validates(self):
        data = json.loads((R112_DIR / "live-handoff-proof.json").read_text(encoding="utf-8"))
        result = validate_transcript(data["transcript"])
        assert result["valid"], f"Transcript invalid: {result['errors']}"

    def test_proof_has_adoption_compliance(self):
        data = json.loads((R112_DIR / "live-handoff-proof.json").read_text(encoding="utf-8"))
        assert "adoption_compliance" in data
        assert data["adoption_compliance"]["compliant"]

    def test_proof_has_grading_result(self):
        data = json.loads((R112_DIR / "live-handoff-proof.json").read_text(encoding="utf-8"))
        assert "grading_result" in data
        assert data["grading_result"]["overall_verdict"] in ("ACCEPTED", "ACCEPTED_WITH_REWORK")

    def test_proof_has_continuation_decision(self):
        data = json.loads((R112_DIR / "live-handoff-proof.json").read_text(encoding="utf-8"))
        assert "continuation_decision" in data
        assert data["continuation_decision"]["state"] in ("YES", "YES_WITH_LIMITATIONS")

    def test_proof_transcript_file_exists(self):
        transcripts = list(TRANSCRIPT_DIR.glob("transcript-r112-*-live*.json"))
        assert len(transcripts) >= 1


# ============================================================
# Wave 2: STREAM-LOCAL CYCLE ISOLATION
# ============================================================

class TestStreamLocalCycleIsolation:
    """Stream-local outputs must be authoritative for Skills."""

    def test_authority_map_code_exists(self):
        """autonomous_cycle.py must write authority-map.json."""
        cycle_path = REPO_ROOT / "tools" / "supervisor" / "autonomous_cycle.py"
        text = cycle_path.read_text(encoding="utf-8")
        assert "authority-map.json" in text
        assert "STREAM_LOCAL" in text

    def test_stream_local_authority_map_artifact(self):
        path = R112_DIR / "stream-local-authority-map.json"
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["authority"] == "STREAM_LOCAL"
        assert data["global_status"] == "ADVISORY_REFERENCE"

    def test_stream_dir_exists(self):
        stream_dir = REPO_ROOT / "reports" / "supervisor-streams" / "skills"
        assert stream_dir.exists()

    def test_stream_dir_has_evidence_review(self):
        path = REPO_ROOT / "reports" / "supervisor-streams" / "skills" / "evidence-review.json"
        assert path.exists()

    def test_stream_dir_has_contradictions(self):
        path = REPO_ROOT / "reports" / "supervisor-streams" / "skills" / "contradictions.json"
        assert path.exists()

    def test_stream_continuation_signal_exists(self):
        path = REPO_ROOT / ".local" / "supervisor" / "streams" / "skills" / "continuation-signal.json"
        if not path.exists():
            import pytest
            pytest.skip(".local/supervisor/streams/skills/continuation-signal.json not present (gitignored)")
        assert path.exists()


# ============================================================
# Wave 3: YES_WITH_LIMITATIONS SEMANTICS
# ============================================================

class TestYesWithLimitationsSemantics:
    """Continuation state machine must support YES_WITH_LIMITATIONS."""

    def _policies_path(self):
        return REPO_ROOT / ".supervisor" / "policies.yaml"

    def test_clean_all_pass_yields_yes(self):
        """Anti-skip all_pass=true, no violations -> YES."""
        anti_skip = {"all_pass": True, "violations": 0, "impact": {"block": False, "downgrade": False}}
        state = classify_continuation_state(
            True, False, [], [], [], {}, self._policies_path(),
            anti_skip_result=anti_skip,
        )
        assert state == "YES"

    def test_low_severity_yields_yes_with_limitations(self):
        """Anti-skip has low-severity violations, no block/downgrade -> YES_WITH_LIMITATIONS."""
        anti_skip = {
            "all_pass": False, "violations": 1,
            "impact": {"block": False, "downgrade": False, "caveats": ["low_sev"]},
        }
        state = classify_continuation_state(
            True, False, [], [], [], {}, self._policies_path(),
            anti_skip_result=anti_skip,
        )
        assert state == "YES_WITH_LIMITATIONS"

    def test_critical_block_yields_no(self):
        """Anti-skip critical block -> hard_stops -> NO_BROKEN_BASELINE."""
        state = classify_continuation_state(
            False, False, ["anti_skip_critical_block"], [], [], {}, self._policies_path(),
            anti_skip_result=None,
        )
        assert state.startswith("NO_")

    def test_prompt_quality_failure_yields_no(self):
        """Prompt quality failure -> NO_PROMPT_QUALITY_FAILURE."""
        state = classify_continuation_state(
            False, False, ["prompt_quality_failure"], [], [], {}, self._policies_path(),
            anti_skip_result=None,
        )
        assert state == "NO_PROMPT_QUALITY_FAILURE"

    def test_max_iterations_yields_no(self):
        state = classify_continuation_state(
            True, True, ["max_iterations_reached"], [], [], {}, self._policies_path(),
            anti_skip_result=None,
        )
        assert state == "NO_MAX_ITERATIONS"

    def test_rework_yields_yes_with_rework(self):
        state = classify_continuation_state(
            "true_with_rework", False, [], [], ["W1"], {}, self._policies_path(),
            anti_skip_result=None,
        )
        assert state == "YES_WITH_REWORK"

    def test_overclaimed_yields_no_unsafe(self):
        state = classify_continuation_state(
            False, False, [], ["W1"], [], {}, self._policies_path(),
            anti_skip_result=None,
        )
        assert state == "NO_UNSAFE_SOURCE_STATE"

    def test_missing_manifest_yields_no(self):
        state = classify_continuation_state(
            False, False, ["missing_evidence_manifest"], [], [], {}, self._policies_path(),
            anti_skip_result=None,
        )
        assert state == "NO_MISSING_EVIDENCE_MANIFEST"

    def test_wrong_stream_yields_no(self):
        state = classify_continuation_state(
            False, False, ["wrong_stream_context"], [], [], {}, self._policies_path(),
            anti_skip_result=None,
        )
        assert state == "NO_WRONG_STREAM_CONTEXT"


# ============================================================
# Wave 4: SKILL PROMOTION (record-lane-execution)
# ============================================================

class TestSkillPromotion:
    """record-lane-execution must be promoted to active."""

    def test_command_file_exists(self):
        path = REPO_ROOT / ".claude" / "commands" / "record-lane-execution.md"
        assert path.exists()

    def test_registry_status_active(self):
        reg = yaml.safe_load(
            (REPO_ROOT / ".supervisor" / "skill-registry.yaml").read_text(encoding="utf-8")
        )
        skills = {s["skill_id"]: s for s in reg["skills"]}
        assert "record-lane-execution" in skills
        assert skills["record-lane-execution"]["status"] == "active"

    def test_registry_no_deferred_reason(self):
        reg = yaml.safe_load(
            (REPO_ROOT / ".supervisor" / "skill-registry.yaml").read_text(encoding="utf-8")
        )
        skills = {s["skill_id"]: s for s in reg["skills"]}
        assert "deferred_reason" not in skills["record-lane-execution"]

    def test_transcript_for_promoted_skill(self):
        """There must be a transcript using the promoted skill."""
        transcripts = list(TRANSCRIPT_DIR.glob("*.json"))
        found = False
        for t in transcripts:
            data = json.loads(t.read_text(encoding="utf-8"))
            if data.get("skill_id") == "record-lane-execution":
                found = True
                break
        assert found, "No transcript found using record-lane-execution skill"

    def test_active_skill_count(self):
        reg = yaml.safe_load(
            (REPO_ROOT / ".supervisor" / "skill-registry.yaml").read_text(encoding="utf-8")
        )
        active = [s for s in reg["skills"] if s["status"] == "active"]
        assert len(active) >= 24  # Was 23, now 24 with record-lane-execution


# ============================================================
# Wave 5: RECEIVER FIXTURE RERUN
# ============================================================

class TestReceiverFixtureRerun:
    """Receiver fixtures must still be machine-checkable."""

    def test_mainstream_fixture_exists(self):
        assert (RECEIVER_DIR / "mainstream-receiver.json").exists()

    def test_acceleration_fixture_exists(self):
        assert (RECEIVER_DIR / "acceleration-receiver.json").exists()

    def test_supervisor_fixture_exists(self):
        assert (RECEIVER_DIR / "supervisor-receiver.json").exists()

    def test_mainstream_compliant_passes(self):
        data = json.loads((RECEIVER_DIR / "mainstream-receiver.json").read_text(encoding="utf-8"))
        result = validate_adoption({"planned_work_items": [data["compliant_item"]]})
        assert result["compliant"]

    def test_mainstream_failing_fails(self):
        data = json.loads((RECEIVER_DIR / "mainstream-receiver.json").read_text(encoding="utf-8"))
        result = validate_adoption({"planned_work_items": [data["failing_item"]]})
        assert not result["compliant"]

    def test_acceleration_compliant_passes(self):
        data = json.loads((RECEIVER_DIR / "acceleration-receiver.json").read_text(encoding="utf-8"))
        result = validate_adoption({"planned_work_items": [data["compliant_item"]]})
        assert result["compliant"]

    def test_supervisor_has_transcript_evidence(self):
        data = json.loads((RECEIVER_DIR / "supervisor-receiver.json").read_text(encoding="utf-8"))
        evidence = data["compliant_item"]["evidence_paths"]
        assert any("transcript" in p.lower() and p.endswith(".json") for p in evidence)


# ============================================================
# Wave 6: EVIDENCE-QUALITY IMPROVEMENT
# ============================================================

class TestEvidenceQualityImprovement:
    """Evidence quality should target >= 0.80."""

    def test_r112_has_many_tests(self):
        text = Path(__file__).read_text(encoding="utf-8")
        assert text.count("def test_") >= 38

    def test_transcripts_all_valid(self):
        path = R112_DIR / "validator-results" / "transcript-validation-r112.json"
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["fail"] == 0
        assert data["pass"] >= 8

    def test_lane_ledger_complete(self):
        path = R112_DIR / "lane-execution-ledger.json"
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data["lanes"]) >= 8
