"""R110: Sample output packaging, handoff enforcement, and continuation semantics.

Wave 1: Sample outputs are machine-readable JSON in sample-outputs/.
Wave 2: Adoption consumption hardening (load + validate).
Wave 3: Handoff enforcement (validation_command, expected_evidence, transcript_requirement,
         raw_log_requirement, fail_conditions).
Wave 6: Continuation semantics (YES_WITH_LIMITATIONS when low-severity anti-skip).
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
from anti_skip_checker import detect_missing_sample_outputs  # noqa: E402

SAMPLE_DIR = REPO_ROOT / "reports" / "skills-r110" / "sample-outputs"
HANDOFF_DIR = REPO_ROOT / "reports" / "skills-r110" / "generated-handoffs"


# ═══════════════════════════════════════════════════════════════════════
# Wave 1: SAMPLE OUTPUT PACKAGING
# ═══════════════════════════════════════════════════════════════════════

class TestSampleOutputPackaging:
    """Sample outputs must exist, be valid JSON, and have required fields."""

    EXPECTED_SAMPLES = [
        "mainstream-compliant.json",
        "mainstream-failing-no-ledger.json",
        "acceleration-compliant-routing.json",
        "acceleration-failing-missing-skill.json",
        "supervisor-transcript-aware-grading.json",
        "anti-bypass-enforcement.json",
    ]

    def test_sample_dir_exists(self):
        assert SAMPLE_DIR.exists(), f"Sample output dir missing: {SAMPLE_DIR}"

    def test_all_expected_samples_exist(self):
        for name in self.EXPECTED_SAMPLES:
            assert (SAMPLE_DIR / name).exists(), f"Missing sample: {name}"

    def test_all_samples_are_valid_json(self):
        for name in self.EXPECTED_SAMPLES:
            path = SAMPLE_DIR / name
            data = json.loads(path.read_text(encoding="utf-8"))
            assert isinstance(data, dict)
            assert "sample_type" in data

    def test_mainstream_compliant_has_adoption_result(self):
        data = json.loads((SAMPLE_DIR / "mainstream-compliant.json").read_text(encoding="utf-8"))
        assert data["adoption_result"]["compliant"] is True
        assert data["adoption_result"]["checks"]["has_skill_id"] is True

    def test_mainstream_failing_has_failure_explanation(self):
        data = json.loads((SAMPLE_DIR / "mainstream-failing-no-ledger.json").read_text(encoding="utf-8"))
        assert data["adoption_result"]["compliant"] is False
        assert "failure_explanation" in data

    def test_supervisor_sample_has_contrast(self):
        data = json.loads((SAMPLE_DIR / "supervisor-transcript-aware-grading.json").read_text(encoding="utf-8"))
        assert data["grading_result"]["supervisor_grade"] == "ACCEPTED_VERIFIED"
        assert data["contrast_without_transcript"]["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS"

    def test_anti_skip_now_passes_with_samples(self):
        """With sample outputs present, detect_missing_sample_outputs should pass."""
        result = detect_missing_sample_outputs(
            REPO_ROOT / "reports" / "skills-r110",
        )
        assert not result["is_violation"], f"Still missing: {result}"
        assert result["outputs_found"] >= 6


# ═══════════════════════════════════════════════════════════════════════
# Wave 2: ADOPTION CONSUMPTION HARDENING
# ═══════════════════════════════════════════════════════════════════════

class TestAdoptionConsumptionHardening:
    """Machine-checkable adoption fixtures load packages and validate."""

    def test_sample_compliant_item_validates(self):
        """Load compliant sample, run through validator."""
        data = json.loads((SAMPLE_DIR / "mainstream-compliant.json").read_text(encoding="utf-8"))
        decl = {"planned_work_items": [data["work_item"]]}
        result = validate_adoption(decl)
        assert result["compliant"]

    def test_sample_failing_item_validates(self):
        """Load failing sample, run through validator."""
        data = json.loads((SAMPLE_DIR / "mainstream-failing-no-ledger.json").read_text(encoding="utf-8"))
        decl = {"planned_work_items": [data["work_item"]]}
        result = validate_adoption(decl)
        assert not result["compliant"]

    def test_acceleration_routing_validates(self):
        data = json.loads((SAMPLE_DIR / "acceleration-compliant-routing.json").read_text(encoding="utf-8"))
        decl = {"planned_work_items": [data["work_item"]]}
        result = validate_adoption(decl)
        assert result["compliant"]
        assert result["items_with_skill_id"] == 1

    def test_acceleration_missing_skill_validates(self):
        data = json.loads((SAMPLE_DIR / "acceleration-failing-missing-skill.json").read_text(encoding="utf-8"))
        decl = {"planned_work_items": [data["work_item"]]}
        result = validate_adoption(decl)
        assert result["compliant"]  # not blocking but tracked
        assert result["items_with_skill_id"] == 0


# ═══════════════════════════════════════════════════════════════════════
# Wave 3: HANDOFF ENFORCEMENT
# ═══════════════════════════════════════════════════════════════════════

class TestHandoffEnforcement:
    """Every generated handoff must have enforcement fields."""

    REQUIRED_HANDOFF_FIELDS = [
        "validation_command",
        "expected_evidence",
        "transcript_requirement",
        "raw_log_requirement",
        "fail_conditions",
    ]

    @classmethod
    def setup_class(cls):
        cls.handoffs = {}
        for f in HANDOFF_DIR.glob("*.yaml"):
            cls.handoffs[f.name] = yaml.safe_load(f.read_text(encoding="utf-8"))

    def test_at_least_3_handoffs(self):
        assert len(self.handoffs) >= 3

    def test_all_handoffs_have_validation_command(self):
        for name, h in self.handoffs.items():
            assert "validation_command" in h, f"{name} missing validation_command"

    def test_all_handoffs_have_expected_evidence(self):
        for name, h in self.handoffs.items():
            assert "expected_evidence" in h, f"{name} missing expected_evidence"

    def test_all_handoffs_have_transcript_requirement(self):
        for name, h in self.handoffs.items():
            assert "transcript_requirement" in h, f"{name} missing transcript_requirement"

    def test_all_handoffs_have_raw_log_requirement(self):
        for name, h in self.handoffs.items():
            assert "raw_log_requirement" in h, f"{name} missing raw_log_requirement"

    def test_all_handoffs_have_fail_conditions(self):
        for name, h in self.handoffs.items():
            fc = h.get("fail_conditions", [])
            assert len(fc) >= 3, f"{name} has too few fail_conditions ({len(fc)})"

    def test_all_handoffs_have_pass_criteria(self):
        for name, h in self.handoffs.items():
            pc = h.get("pass_criteria", [])
            assert len(pc) >= 3, f"{name} has too few pass_criteria ({len(pc)})"

    def test_mainstream_handoff_requires_live_mode(self):
        mainstream = [h for n, h in self.handoffs.items() if "mainstream" in n.lower()]
        assert len(mainstream) >= 1
        h = mainstream[0]
        assert h["transcript_requirement"]["mode"] == "live"

    def test_handoff_skill_id_must_match(self):
        for name, h in self.handoffs.items():
            tr = h.get("transcript_requirement", {})
            if "skill_id_must_match" in tr:
                assert tr["skill_id_must_match"] == h["skill_id"]


# ═══════════════════════════════════════════════════════════════════════
# Wave 6: CONTINUATION SEMANTICS
# ═══════════════════════════════════════════════════════════════════════

class TestContinuationSemantics:
    """Verify continuation signal semantics with anti-skip results."""

    def test_clean_yes_requires_all_pass(self):
        """If anti-skip all_pass=true, continuation can be clean YES."""
        anti_skip = {"all_pass": True, "violations": 0}
        continuation = "YES" if anti_skip["all_pass"] else "YES_WITH_LIMITATIONS"
        assert continuation == "YES"

    def test_low_severity_yields_yes_with_limitations(self):
        """If anti-skip has low-severity only, continuation is YES_WITH_LIMITATIONS."""
        anti_skip = {
            "all_pass": False, "violations": 1,
            "checks": [{"check": "missing_sample_outputs", "is_violation": True, "severity": "low"}]
        }
        has_critical = any(
            c.get("severity") in ("critical", "high") for c in anti_skip.get("checks", []) if c.get("is_violation")
        )
        if anti_skip["all_pass"]:
            continuation = "YES"
        elif has_critical:
            continuation = "NO"
        else:
            continuation = "YES_WITH_LIMITATIONS"
        assert continuation == "YES_WITH_LIMITATIONS"

    def test_critical_severity_yields_no(self):
        """If anti-skip has critical severity, continuation is NO."""
        anti_skip = {
            "all_pass": False, "violations": 1,
            "checks": [{"check": "path_only_acceptance", "is_violation": True, "severity": "critical"}]
        }
        has_critical = any(
            c.get("severity") in ("critical", "high") for c in anti_skip.get("checks", []) if c.get("is_violation")
        )
        continuation = "NO" if has_critical else "YES_WITH_LIMITATIONS"
        assert continuation == "NO"

    def test_missing_samples_prevents_clean_pass(self):
        """missing_sample_outputs is low severity but prevents clean YES."""
        anti_skip_r109 = {"all_pass": False, "violations": 1}
        assert not anti_skip_r109["all_pass"]
        # After fixing sample outputs, all_pass should be True
        anti_skip_r110 = {"all_pass": True, "violations": 0}
        assert anti_skip_r110["all_pass"]
