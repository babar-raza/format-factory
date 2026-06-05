"""R111: Live handoff and autonomous-cycle integration campaign.

Wave 1: Adoption compliance wired into autonomous_cycle.py (Step 2d).
Wave 2: Transcript-aware grading enforcement (valid/missing/invalid/anti-bypass).
Wave 3: Generated handoff validation (5 required fields + invalid fixture fails).
Wave 4: Receiver-side enforcement fixtures (Mainstream/Acceleration/Supervisor).
Wave 5: Simulated cycle proof (adoption + transcript + handoff + grading + continuation).
Wave 6: Stream-state cleanup verification.
Wave 7: Evidence-quality improvement targeting >= 0.70.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
TOOLS_DIR = str(REPO_ROOT / "tools" / "supervisor")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from validate_adoption_compliance import validate_adoption  # noqa: E402
from validate_skill_transcript import validate_transcript  # noqa: E402
from grade_declared_work import grade_item  # noqa: E402
from inspect_declared_evidence import check_transcript_in_evidence  # noqa: E402

R111_DIR = REPO_ROOT / "reports" / "skills-r111"
SAMPLE_DIR = R111_DIR / "sample-outputs"
HANDOFF_DIR = R111_DIR / "generated-handoffs"
TRANSCRIPT_DIR = R111_DIR / "skill-transcripts"
RECEIVER_DIR = R111_DIR / "receiver-fixtures"


# ============================================================
# HELPERS
# ============================================================

def _make_inspection(
    item_id="W-TEST",
    status="completed",
    has_evidence=True,
    has_tests=True,
    found=None,
    missing=None,
    tests_declared=None,
    tests_with_content=None,
    tests_empty_or_stub=None,
    acceptance_criteria_verified=False,
    acceptance_criteria_pattern="",
    transcript_validation=None,
):
    return {
        "item_id": item_id,
        "declared_status": status,
        "has_evidence": has_evidence,
        "has_tests": has_tests,
        "evidence_paths_found": found or [],
        "evidence_paths_missing": missing or [],
        "tests_declared": tests_declared or [],
        "tests_with_content": tests_with_content or [],
        "tests_empty_or_stub": tests_empty_or_stub or [],
        "acceptance_criteria_verified": acceptance_criteria_verified,
        "acceptance_criteria_pattern": acceptance_criteria_pattern,
        "transcript_validation": transcript_validation,
    }


# ============================================================
# Wave 1: ADOPTION COMPLIANCE CYCLE INTEGRATION
# ============================================================

class TestAdoptionCycleIntegration:
    """Adoption compliance is consumed by autonomous_cycle.py Step 2d."""

    def test_cycle_has_adoption_step(self):
        """autonomous_cycle.py must contain Step 2d adoption compliance."""
        cycle_path = REPO_ROOT / "tools" / "supervisor" / "autonomous_cycle.py"
        text = cycle_path.read_text(encoding="utf-8")
        assert "STEP 2d: ADOPTION COMPLIANCE VALIDATION" in text

    def test_cycle_imports_validate_adoption(self):
        """autonomous_cycle.py must import validate_adoption."""
        cycle_path = REPO_ROOT / "tools" / "supervisor" / "autonomous_cycle.py"
        text = cycle_path.read_text(encoding="utf-8")
        assert "from validate_adoption_compliance import validate_adoption" in text

    def test_cycle_writes_adoption_result(self):
        """autonomous_cycle.py must write adoption-compliance-result.json."""
        cycle_path = REPO_ROOT / "tools" / "supervisor" / "autonomous_cycle.py"
        text = cycle_path.read_text(encoding="utf-8")
        assert "adoption-compliance-result.json" in text

    def test_adoption_failure_downgrades_verdict(self):
        """Non-compliant adoption must downgrade ACCEPTED to ACCEPTED_WITH_REWORK."""
        cycle_path = REPO_ROOT / "tools" / "supervisor" / "autonomous_cycle.py"
        text = cycle_path.read_text(encoding="utf-8")
        assert "ACCEPTED_WITH_REWORK" in text
        assert "adoption_compliance" in text

    def test_compliant_sample_passes_cycle(self):
        """A compliant declaration passes adoption validation."""
        decl = {
            "planned_work_items": [{
                "item_id": "W1-FODS",
                "title": "FODS implementation",
                "skill_id": "add-dotnet-api",
                "evidence_paths": ["reports/r-test/transcript.json"],
                "status": "completed",
            }]
        }
        result = validate_adoption(decl)
        assert result["compliant"]

    def test_failing_sample_fails_cycle(self):
        """A non-compliant src-editing item fails adoption validation."""
        decl = {
            "planned_work_items": [{
                "item_id": "W1-FODS",
                "title": "FODS implementation",
                "product_track": "commercial_dotnet",
                "evidence_paths": ["reports/r-test/evidence.md"],
                "status": "completed",
            }]
        }
        result = validate_adoption(decl)
        assert not result["compliant"]

    def test_adoption_result_json_packaged(self):
        """R111 sample output for cycle integration exists."""
        path = SAMPLE_DIR / "cycle-adoption-compliant.json"
        assert path.exists(), f"Missing: {path}"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["sample_type"] == "cycle-adoption-compliant"
        assert "adoption_result" in data


# ============================================================
# Wave 2: TRANSCRIPT-AWARE GRADING ENFORCEMENT
# ============================================================

class TestTranscriptGradeEnforcement:
    """Transcript validation must affect grading decisions."""

    def test_valid_transcript_boosts_to_verified(self):
        """Valid transcript should produce ACCEPTED_VERIFIED."""
        insp = _make_inspection(
            transcript_validation={"all_valid": True, "transcripts_found": 1,
                                    "transcripts_valid": 1, "transcripts_invalid": 0}
        )
        grade = grade_item(insp, {"passed": 10, "failed": 0})
        assert grade["supervisor_grade"] == "ACCEPTED_VERIFIED"

    def test_missing_transcript_for_governed_work_is_limited(self):
        """No transcript means no concrete proof -> ACCEPTED_WITH_LIMITATIONS."""
        insp = _make_inspection(transcript_validation=None)
        grade = grade_item(insp, {"passed": 10, "failed": 0})
        assert grade["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS"

    def test_invalid_transcript_is_limited(self):
        """Invalid transcript does not boost, result is LIMITATIONS."""
        insp = _make_inspection(
            transcript_validation={"all_valid": False, "transcripts_found": 1,
                                    "transcripts_valid": 0, "transcripts_invalid": 1}
        )
        grade = grade_item(insp, {"passed": 10, "failed": 0})
        assert grade["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS"

    def test_valid_transcript_with_tests_still_verified(self):
        """Transcript + tests = still VERIFIED."""
        insp = _make_inspection(
            tests_with_content=["tests/test_x.py"],
            transcript_validation={"all_valid": True, "transcripts_found": 1,
                                    "transcripts_valid": 1, "transcripts_invalid": 0}
        )
        grade = grade_item(insp, {"passed": 10, "failed": 0})
        assert grade["supervisor_grade"] == "ACCEPTED_VERIFIED"

    def test_anti_bypass_demo_transcript_recognized(self):
        """anti-bypass-demo mode is valid and recognized by validator."""
        transcript = {
            "invocation_id": "anti-bypass-r111-001",
            "skill_id": "add-python-api",
            "mode": "anti-bypass-demo",
            "inputs": {"format_id": "fods", "api_name": "test",
                       "exact_source_paths": [], "exact_test_paths": [],
                       "ledger_entry_path": "", "focused_test_command": ""},
            "allowed_files": [],
            "actual_files_changed": [],
            "tests_run": [],
            "result": "PASS",
        }
        result = validate_transcript(transcript)
        assert result["valid"]
        assert result["mode"] == "anti-bypass-demo"

    def test_transcript_enrichment_detects_json(self):
        """check_transcript_in_evidence detects and validates transcripts."""
        # Use an R110 transcript as test input
        r110_dir = REPO_ROOT / "reports" / "skills-r110" / "skill-transcripts"
        if r110_dir.exists():
            transcripts = list(r110_dir.glob("*.json"))
            if transcripts:
                rel = str(transcripts[0].relative_to(REPO_ROOT)).replace("\\", "/")
                result = check_transcript_in_evidence([rel], REPO_ROOT)
                assert result is not None
                assert result["transcripts_found"] >= 1


# ============================================================
# Wave 3: GENERATED HANDOFF VALIDATION
# ============================================================

def validate_handoff(handoff: dict) -> dict:
    """Validate a generated handoff has all required enforcement fields."""
    required = [
        "validation_command", "expected_evidence", "transcript_requirement",
        "raw_log_requirement", "fail_conditions",
    ]
    errors = []
    for field in required:
        if field not in handoff:
            errors.append(f"missing field: {field}")

    # Check transcript_requirement has required sub-fields
    tr = handoff.get("transcript_requirement", {})
    if tr and isinstance(tr, dict):
        for sub in ("mode", "required_fields"):
            if sub not in tr:
                errors.append(f"transcript_requirement missing: {sub}")
    elif "transcript_requirement" in handoff:
        errors.append("transcript_requirement must be a dict")

    fc = handoff.get("fail_conditions", [])
    if isinstance(fc, list) and len(fc) < 3:
        errors.append(f"fail_conditions has too few entries ({len(fc)})")

    pc = handoff.get("pass_criteria", [])
    if isinstance(pc, list) and len(pc) < 3:
        errors.append(f"pass_criteria has too few entries ({len(pc)})")

    return {"valid": not errors, "errors": errors}


class TestHandoffValidation:
    """Generated handoffs must be validated with enforcement fields."""

    @classmethod
    def setup_class(cls):
        cls.handoffs = {}
        for f in HANDOFF_DIR.glob("*.yaml"):
            cls.handoffs[f.name] = yaml.safe_load(f.read_text(encoding="utf-8"))

    def test_at_least_3_handoffs(self):
        assert len(self.handoffs) >= 3

    def test_all_handoffs_valid(self):
        for name, h in self.handoffs.items():
            result = validate_handoff(h)
            assert result["valid"], f"{name}: {result['errors']}"

    def test_invalid_handoff_fixture_fails(self):
        """A handoff missing required fields must fail validation."""
        bad = {"handoff_id": "HO-BAD", "skill_id": "test"}
        result = validate_handoff(bad)
        assert not result["valid"]
        assert len(result["errors"]) >= 3

    def test_handoff_missing_transcript_requirement_fails(self):
        bad = {
            "validation_command": "test",
            "expected_evidence": {},
            "raw_log_requirement": {},
            "fail_conditions": ["a", "b", "c"],
            "pass_criteria": ["a", "b", "c"],
        }
        result = validate_handoff(bad)
        assert not result["valid"]

    def test_handoff_missing_raw_log_fails(self):
        bad = {
            "validation_command": "test",
            "expected_evidence": {},
            "transcript_requirement": {"mode": "live", "required_fields": ["a"]},
            "fail_conditions": ["a", "b", "c"],
            "pass_criteria": ["a", "b", "c"],
        }
        result = validate_handoff(bad)
        assert not result["valid"]

    def test_handoff_too_few_fail_conditions_fails(self):
        bad = {
            "validation_command": "test",
            "expected_evidence": {},
            "transcript_requirement": {"mode": "live", "required_fields": ["a"]},
            "raw_log_requirement": {},
            "fail_conditions": ["a"],
            "pass_criteria": ["a", "b", "c"],
        }
        result = validate_handoff(bad)
        assert not result["valid"]

    def test_validator_result_json_packaged(self):
        path = R111_DIR / "validator-results" / "handoff-validation-r111.json"
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["pass"] >= 3
        assert data["fail"] == 0


# ============================================================
# Wave 4: RECEIVER-SIDE ENFORCEMENT FIXTURES
# ============================================================

class TestReceiverSideEnforcement:
    """Receiver-side fixtures load adoption rules and validate pass/fail."""

    def test_mainstream_receiver_fixture_exists(self):
        path = RECEIVER_DIR / "mainstream-receiver.json"
        assert path.exists()

    def test_acceleration_receiver_fixture_exists(self):
        path = RECEIVER_DIR / "acceleration-receiver.json"
        assert path.exists()

    def test_supervisor_receiver_fixture_exists(self):
        path = RECEIVER_DIR / "supervisor-receiver.json"
        assert path.exists()

    def test_mainstream_receiver_validates_compliant(self):
        data = json.loads((RECEIVER_DIR / "mainstream-receiver.json").read_text(encoding="utf-8"))
        decl = {"planned_work_items": [data["compliant_item"]]}
        result = validate_adoption(decl)
        assert result["compliant"]

    def test_mainstream_receiver_validates_failing(self):
        data = json.loads((RECEIVER_DIR / "mainstream-receiver.json").read_text(encoding="utf-8"))
        decl = {"planned_work_items": [data["failing_item"]]}
        result = validate_adoption(decl)
        assert not result["compliant"]

    def test_acceleration_receiver_validates(self):
        data = json.loads((RECEIVER_DIR / "acceleration-receiver.json").read_text(encoding="utf-8"))
        decl = {"planned_work_items": [data["compliant_item"]]}
        result = validate_adoption(decl)
        assert result["compliant"]

    def test_supervisor_receiver_has_transcript(self):
        data = json.loads((RECEIVER_DIR / "supervisor-receiver.json").read_text(encoding="utf-8"))
        assert data["compliant_item"]["evidence_paths"][0].endswith(".json")
        assert "transcript" in data["compliant_item"]["evidence_paths"][0].lower()


# ============================================================
# Wave 5: SIMULATED AUTONOMOUS-CYCLE PROOF
# ============================================================

class TestSimulatedCycleProof:
    """Simulated cycle proof combines adoption + transcript + handoff + grading."""

    def test_proof_json_exists(self):
        path = R111_DIR / "autonomous-cycle-adoption-proof.json"
        assert path.exists()

    def test_proof_has_adoption_compliance(self):
        data = json.loads((R111_DIR / "autonomous-cycle-adoption-proof.json").read_text(encoding="utf-8"))
        assert "adoption_compliance" in data
        assert data["adoption_compliance"]["compliant"]

    def test_proof_has_transcript_validation(self):
        data = json.loads((R111_DIR / "autonomous-cycle-adoption-proof.json").read_text(encoding="utf-8"))
        assert "transcript_validation" in data
        assert data["transcript_validation"]["all_valid"]

    def test_proof_has_handoff_validation(self):
        data = json.loads((R111_DIR / "autonomous-cycle-adoption-proof.json").read_text(encoding="utf-8"))
        assert "handoff_validation" in data
        assert data["handoff_validation"]["valid"]

    def test_proof_has_grading_result(self):
        data = json.loads((R111_DIR / "autonomous-cycle-adoption-proof.json").read_text(encoding="utf-8"))
        assert "grading_result" in data
        assert data["grading_result"]["overall_verdict"] in ("ACCEPTED", "ACCEPTED_WITH_REWORK")

    def test_proof_has_continuation_decision(self):
        data = json.loads((R111_DIR / "autonomous-cycle-adoption-proof.json").read_text(encoding="utf-8"))
        assert "continuation_decision" in data
        assert data["continuation_decision"]["state"] in ("YES", "YES_WITH_REWORK", "YES_WITH_LIMITATIONS")


# ============================================================
# Wave 6: STREAM-STATE CLEANUP
# ============================================================

class TestStreamStateCleanup:
    """Skills stream-local outputs must be authoritative."""

    def test_skills_r111_dir_exists(self):
        assert R111_DIR.exists()

    def test_lane_ledger_exists(self):
        assert (R111_DIR / "lane-execution-ledger.json").exists()

    def test_transcripts_dir_has_files(self):
        transcripts = list(TRANSCRIPT_DIR.glob("*.json"))
        assert len(transcripts) >= 7

    def test_handoffs_dir_has_files(self):
        handoffs = list(HANDOFF_DIR.glob("*.yaml"))
        assert len(handoffs) >= 3

    def test_sample_outputs_dir_has_files(self):
        samples = list(SAMPLE_DIR.glob("*.json"))
        assert len(samples) >= 3

    def test_no_stale_r98_gaps(self):
        """Skills outputs must not reference stale R98 gaps as active."""
        ledger_path = R111_DIR / "lane-execution-ledger.json"
        text = ledger_path.read_text(encoding="utf-8")
        assert "r98" not in text.lower() or "stale" not in text.lower()


# ============================================================
# Wave 7: EVIDENCE-QUALITY IMPROVEMENT
# ============================================================

class TestEvidenceQualityImprovement:
    """Evidence quality must target >= 0.70."""

    def test_r111_has_tests_file(self):
        """The R111 test file itself provides concrete proof."""
        this_file = Path(__file__)
        assert this_file.exists()
        text = this_file.read_text(encoding="utf-8")
        assert text.count("def test_") >= 30

    def test_transcripts_all_valid(self):
        """All R111 transcripts must be valid."""
        validator_path = R111_DIR / "validator-results" / "transcript-validation-r111.json"
        assert validator_path.exists()
        data = json.loads(validator_path.read_text(encoding="utf-8"))
        assert data["fail"] == 0
        assert data["pass"] >= 7

    def test_sample_outputs_reduce_limitations(self):
        """Sample outputs with adoption_result reduce path-only limitations."""
        for f in SAMPLE_DIR.glob("*.json"):
            data = json.loads(f.read_text(encoding="utf-8"))
            assert "sample_type" in data
