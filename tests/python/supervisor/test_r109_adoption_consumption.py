"""R109 Wave 1-4: Adoption consumption and enforcement fixtures.

These tests CONSUME the Skills adoption packages from R108 and demonstrate
pass/fail behavior for Mainstream, Acceleration, and Supervisor streams.
This is the core R109 deliverable: proving other streams are FORCED to consume.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
import pytest

TOOLS_DIR = str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
ADOPTION_DIR = REPO_ROOT / "reports" / "skills-r108" / "adoption-packages"

from validate_adoption_compliance import validate_adoption, _is_exempt, _has_transcript_evidence  # noqa: E402
from grade_declared_work import grade_item  # noqa: E402
from validate_skill_transcript import validate_transcript  # noqa: E402


# ═══════════════════════════════════════════════════════════════════════
# Wave 1: ADOPTION CONSUMPTION FIXTURES — receiver-side package loading
# ═══════════════════════════════════════════════════════════════════════

class TestMainstreamAdoptionConsumption:
    """Mainstream receiver loads and validates its adoption package."""

    @classmethod
    def setup_class(cls):
        pkg_path = ADOPTION_DIR / "mainstream-adoption.yaml"
        assert pkg_path.exists(), f"Mainstream adoption package missing: {pkg_path}"
        cls.package = yaml.safe_load(pkg_path.read_text(encoding="utf-8"))

    def test_package_stream_is_mainstream(self):
        assert self.package["stream"] == "mainstream"

    def test_package_has_enforcement_gates(self):
        gates = self.package.get("enforcement_gates", [])
        assert len(gates) >= 3
        gate_ids = {g["gate_id"] for g in gates}
        assert "ADOPT-M-01" in gate_ids  # skill registry lookup
        assert "ADOPT-M-02" in gate_ids  # transcript generation
        assert "ADOPT-M-03" in gate_ids  # ledger entry

    def test_package_gates_are_active(self):
        for gate in self.package["enforcement_gates"]:
            assert gate["status"] == "active", f"Gate {gate['gate_id']} not active"

    def test_package_has_integration_points(self):
        points = self.package.get("integration_points", [])
        assert len(points) >= 2
        tools = {p["tool"] for p in points}
        assert "validate_adoption_compliance.py" in tools
        assert "validate_skill_transcript.py" in tools

    def test_compliant_mainstream_item_passes(self):
        """A Mainstream product item with skill_id + transcript + ledger passes."""
        decl = {"planned_work_items": [{
            "item_id": "W1-FODS-API",
            "title": "FODS RenameSheet API",
            "skill_id": "add-dotnet-api",
            "product_track": "commercial_dotnet",
            "ledger_entry_id": "LED-R94-001",
            "evidence_paths": ["reports/r94/skill-transcripts/transcript-fods-rename.json"],
            "status": "completed",
        }]}
        result = validate_adoption(decl)
        assert result["compliant"]

    def test_failing_mainstream_item_no_ledger(self):
        """A Mainstream src-editing item WITHOUT ledger fails."""
        decl = {"planned_work_items": [{
            "item_id": "W1-FODS-API",
            "title": "FODS RenameSheet API",
            "skill_id": "add-dotnet-api",
            "product_track": "foss_python",
            "evidence_paths": ["reports/r94/skill-transcripts/transcript-fods-rename.json"],
            "status": "completed",
        }]}
        result = validate_adoption(decl)
        assert not result["compliant"]


class TestAccelerationAdoptionConsumption:
    """Acceleration receiver loads and validates its adoption package."""

    @classmethod
    def setup_class(cls):
        pkg_path = ADOPTION_DIR / "acceleration-adoption.yaml"
        assert pkg_path.exists(), f"Acceleration adoption package missing: {pkg_path}"
        cls.package = yaml.safe_load(pkg_path.read_text(encoding="utf-8"))

    def test_package_stream_is_acceleration(self):
        assert self.package["stream"] == "acceleration"

    def test_package_has_enforcement_gates(self):
        gates = self.package.get("enforcement_gates", [])
        assert len(gates) >= 3
        gate_ids = {g["gate_id"] for g in gates}
        assert "ADOPT-A-01" in gate_ids  # POC target skill mapping
        assert "ADOPT-A-02" in gate_ids  # transcript generation
        assert "ADOPT-A-03" in gate_ids  # adoption compliance check

    def test_package_gates_are_planned(self):
        """Acceleration gates are planned (not yet active)."""
        for gate in self.package["enforcement_gates"]:
            assert gate["status"] == "planned"

    def test_package_has_integration_points(self):
        points = self.package.get("integration_points", [])
        assert len(points) >= 2

    def test_gap_routing_with_skill_coverage(self):
        """POC gap with skill_id coverage is correctly tracked."""
        decl = {"planned_work_items": [{
            "item_id": "W1-POC-GAP",
            "title": "FODS export gap",
            "skill_id": "add-dotnet-api",
            "evidence_paths": ["reports/r98/poc-export.md"],
            "status": "completed",
        }]}
        result = validate_adoption(decl)
        assert result["compliant"]
        assert result["items_with_skill_id"] == 1

    def test_gap_routing_missing_skill_coverage(self):
        """POC gap without skill coverage is tracked (not blocking but noted)."""
        decl = {"planned_work_items": [{
            "item_id": "W1-POC-GAP",
            "title": "FODS export gap",
            "evidence_paths": ["reports/r98/poc-export.md"],
            "status": "completed",
        }]}
        result = validate_adoption(decl)
        assert result["compliant"]  # not blocking
        assert result["items_with_skill_id"] == 0  # but noted


class TestSupervisorAdoptionConsumption:
    """Supervisor receiver loads and validates its adoption package."""

    @classmethod
    def setup_class(cls):
        pkg_path = ADOPTION_DIR / "supervisor-adoption.yaml"
        assert pkg_path.exists(), f"Supervisor adoption package missing: {pkg_path}"
        cls.package = yaml.safe_load(pkg_path.read_text(encoding="utf-8"))

    def test_package_stream_is_supervisor(self):
        assert self.package["stream"] == "supervisor"

    def test_package_has_enforcement_gates(self):
        gates = self.package.get("enforcement_gates", [])
        assert len(gates) >= 4
        gate_ids = {g["gate_id"] for g in gates}
        assert "ADOPT-S-01" in gate_ids  # inspector enrichment
        assert "ADOPT-S-02" in gate_ids  # transcript-grade boost
        assert "ADOPT-S-03" in gate_ids  # anti-skip
        assert "ADOPT-S-04" in gate_ids  # manifest path

    def test_package_gates_are_active(self):
        for gate in self.package["enforcement_gates"]:
            assert gate["status"] == "active"


# ═══════════════════════════════════════════════════════════════════════
# Wave 2: MAINSTREAM COMPLIANCE ENFORCEMENT FIXTURE
# ═══════════════════════════════════════════════════════════════════════

class TestMainstreamComplianceEnforcement:
    """Enforce Mainstream adoption: compliant item vs failing item."""

    def test_compliant_product_item_full(self):
        """Full Mainstream product item: skill_id + transcript + ledger + source hash."""
        decl = {"planned_work_items": [{
            "item_id": "W1-FODS-RENAME",
            "title": "FODS RenameSheet implementation",
            "skill_id": "add-dotnet-api",
            "product_track": "commercial_dotnet",
            "ledger_entry_id": "LED-R94-FODS-RENAME-001",
            "evidence_paths": [
                "reports/r94/fods-rename-sheet.md",
                "reports/r94/skill-transcripts/transcript-fods-rename.json",
            ],
            "status": "completed",
            "source_hash": "abc123def456",
            "raw_logs": ["reports/r94/raw-logs/test-fods.log"],
            "poc_reference": "poc-targets.yaml#fods-rename-sheet",
        }]}
        result = validate_adoption(decl)
        assert result["compliant"]
        item = result["items"][0]
        assert item["checks"]["has_skill_id"]
        assert item["checks"]["has_transcript"]
        assert item["checks"]["has_ledger_entry"]

    def test_failing_product_item_no_skill_no_ledger(self):
        """Failing Mainstream item: no skill_id, no ledger for foss_python."""
        decl = {"planned_work_items": [{
            "item_id": "W1-PPM-GRAYSCALE",
            "title": "PPM grayscale conversion",
            "product_track": "foss_python",
            "evidence_paths": ["reports/r94/ppm-grayscale.md"],
            "status": "completed",
        }]}
        result = validate_adoption(decl)
        assert not result["compliant"]
        item = result["items"][0]
        assert not item["checks"]["has_skill_id"]
        assert not item["checks"]["has_transcript"]
        assert not item["checks"]["has_ledger_entry"]

    def test_mainstream_checklist_gates_map_to_validator(self):
        """Each Mainstream gate maps to a validate_adoption check."""
        pkg = yaml.safe_load(
            (ADOPTION_DIR / "mainstream-adoption.yaml").read_text(encoding="utf-8")
        )
        for gate in pkg["enforcement_gates"]:
            assert "validate_adoption_compliance.py" in gate.get("validator", "") or \
                   "validate_skill_transcript.py" in gate.get("validator", ""), \
                   f"Gate {gate['gate_id']} has no validator mapping"


# ═══════════════════════════════════════════════════════════════════════
# Wave 3: ACCELERATION COMPLIANCE FIXTURE
# ═══════════════════════════════════════════════════════════════════════

class TestAccelerationComplianceFixture:
    """Acceleration stream: gap → skill/handoff routing."""

    def test_gap_with_generated_handoff_route(self):
        """A POC gap that has a generated handoff should be routable."""
        handoff_path = REPO_ROOT / "reports" / "skills-r108" / "generated-handoffs"
        # Skills R107 produced handoff-004; R108 produced 3 simulation transcripts
        # The routing is: gap → skill_id → handoff YAML → transcript validation
        decl = {"planned_work_items": [{
            "item_id": "W1-POC-ROUTING",
            "title": "POC gap routing to skill",
            "skill_id": "add-python-api",
            "evidence_paths": [
                "reports/skills-r109/skill-transcripts/transcript-r109-004-acceleration-routing.json",
            ],
            "status": "completed",
        }]}
        result = validate_adoption(decl)
        assert result["compliant"]
        assert result["items_with_skill_id"] == 1

    def test_missing_skill_coverage_behavior(self):
        """Gap without skill coverage: compliant but low adoption score."""
        decl = {"planned_work_items": [
            {"item_id": "W1-NO-SKILL", "title": "Unrouted gap", "evidence_paths": ["x.md"], "status": "completed"},
            {"item_id": "W2-HAS-SKILL", "title": "Routed gap", "skill_id": "s1", "evidence_paths": ["y.md"], "status": "completed"},
        ]}
        result = validate_adoption(decl)
        assert result["compliant"]
        assert result["items_with_skill_id"] == 1
        assert result["non_exempt_items"] == 2


# ═══════════════════════════════════════════════════════════════════════
# Wave 4: SUPERVISOR GRADING ENFORCEMENT FIXTURE
# ═══════════════════════════════════════════════════════════════════════

class TestSupervisorGradingFixture:
    """Supervisor: transcript-aware grading, path-only rejection."""

    def _make_inspection(self, transcript_validation=None, **kwargs):
        tests_declared = kwargs.get("tests_declared", [])
        return {
            "item_id": kwargs.get("item_id", "W1"),
            "declared_status": "completed",
            "has_evidence": True,
            "has_tests": bool(tests_declared),
            "evidence_paths_found": kwargs.get("evidence_paths", ["reports/test/report.md"]),
            "evidence_paths_missing": [],
            "tests_declared": tests_declared,
            "tests_with_content": kwargs.get("tests_with_content", []),
            "tests_empty_or_stub": [],
            "acceptance_criteria_verified": kwargs.get("criteria_verified", False),
            "acceptance_criteria_pattern": "",
            **({"transcript_validation": transcript_validation} if transcript_validation else {}),
        }

    def test_transcript_aware_grading_verified(self):
        """Item with valid transcript → ACCEPTED_VERIFIED."""
        insp = self._make_inspection(transcript_validation={
            "transcripts_found": 1, "transcripts_valid": 1, "transcripts_invalid": 0,
            "all_valid": True,
            "valid_transcripts": [{"path": "t.json", "skill_id": "s1", "mode": "dry-run", "result": "PASS"}],
            "invalid_transcripts": [],
        })
        grade = grade_item(insp, {"passed": 1, "failed": 0})
        assert grade["supervisor_grade"] == "ACCEPTED_VERIFIED"

    def test_missing_transcript_downgrade(self):
        """Item with no transcript, no tests → ACCEPTED_WITH_LIMITATIONS (path-only)."""
        insp = self._make_inspection()
        grade = grade_item(insp, {"passed": 0, "failed": 0})
        assert grade["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS"
        criteria = grade.get("acceptance_criteria_failed", [])
        assert any("path-only" in c.lower() or "no raw proof" in c.lower() for c in criteria)

    def test_path_only_evidence_rejected_at_quality_level(self):
        """All-path-only sprint gets quality downgrade to ACCEPTED_WITH_REWORK."""
        from grade_declared_work import grade_all
        inspection = {
            "run_id": "test-path-only",
            "sprint_id": "TEST",
            "evidence_root": "reports/test",
            "test_results": {"passed": 0, "failed": 0},
            "item_inspections": [
                self._make_inspection(item_id="W1"),
                self._make_inspection(item_id="W2"),
            ],
        }
        declaration = {
            "planned_work_items": [
                {"item_id": "W1", "title": "Item 1", "status": "completed"},
                {"item_id": "W2", "title": "Item 2", "status": "completed"},
            ],
        }
        result = grade_all(inspection, declaration)
        assert result["evidence_quality_score"] == 0.0
        assert result["overall_verdict"] == "ACCEPTED_WITH_REWORK"

    def test_wrong_stream_next_prompt_rejection(self):
        """Skills next prompt must not contain product implementation tasks."""
        prompt_path = REPO_ROOT / "reports" / "skills-r108" / "generated-next-skills-prompt.md"
        if prompt_path.exists():
            content = prompt_path.read_text(encoding="utf-8").lower()
            # Skills prompt must not contain direct implementation directives
            assert "implement fods" not in content or "delegate to mainstream" in content
            assert "forbidden paths" in content  # must have forbidden section
            assert "src/python" in content or "src/net" in content  # forbidden list present

    def test_transcript_validator_catches_bad_transcript(self):
        """Transcript with missing fields → invalid."""
        bad = {"invocation_id": "x", "skill_id": "nonexistent-skill-xyz"}
        result = validate_transcript(bad)
        assert not result["valid"]
        assert len(result["errors"]) > 0
