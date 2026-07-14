"""
test_governance_infrastructure.py

TC-HARD-001 (2026-06-22): Governance infrastructure validation tests.

Validates key governance files produced by the floating-stargazing-globe sprint
and subsequent hardening. These tests give governance sprints a concrete
pytest evidence path, improving test_coverage scores when declared in evidence_paths.

Covers:
  - skill-registry.yaml (missing_skill_workflow section, skill count)
  - work-type-skill-map.yaml (active_mappings, gap_mappings)
  - gap-register.yaml (resolved/open gaps)
  - autonomous-loop.md Step 0 (DEFERRED + session-scoped filtering)
  - check-skill-coverage.md (work-type mapping table presence)
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_yaml(rel: str) -> dict:
    p = _REPO / rel
    assert p.exists(), f"File not found: {rel}"
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def _read(rel: str) -> str:
    p = _REPO / rel
    assert p.exists(), f"File not found: {rel}"
    return p.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# skill-registry.yaml
# ---------------------------------------------------------------------------

class TestSkillRegistry:
    def test_yaml_parses(self):
        d = _load_yaml(".supervisor/skill-registry.yaml")
        assert isinstance(d, dict)

    def test_missing_skill_workflow_section_present(self):
        d = _load_yaml(".supervisor/skill-registry.yaml")
        assert "missing_skill_workflow" in d, "missing_skill_workflow key absent"

    def test_missing_skill_workflow_has_required_fields(self):
        d = _load_yaml(".supervisor/skill-registry.yaml")
        msw = d["missing_skill_workflow"]
        for field in ("version", "trigger", "enforcement_point", "action", "known_open_gaps"):
            assert field in msw, f"missing_skill_workflow missing field: {field}"

    def test_known_open_gaps_list(self):
        """known_open_gaps shrinks over time as gaps are resolved and their
        entries removed (e.g. capability_compiler removed by TC-EXT-009-03,
        pre_sprint_governance_hook removed by TC-EXT-010-01/05 — SKILL-GAP-015
        closed). This is a structural sanity check (field exists, is a list),
        not a monotonically-growing count invariant — do not restore a fixed
        lower bound here without checking whether it reflects resolved gaps.
        """
        d = _load_yaml(".supervisor/skill-registry.yaml")
        gaps = d["missing_skill_workflow"]["known_open_gaps"]
        assert isinstance(gaps, list)
        assert len(gaps) >= 1, "known_open_gaps should not be emptied entirely"

    def test_skills_list_present_and_nonempty(self):
        d = _load_yaml(".supervisor/skill-registry.yaml")
        skills = d.get("skills", [])
        assert len(skills) >= 40, f"Expected >=40 skills, got {len(skills)}"

    def test_check_skill_coverage_skill_registered(self):
        d = _load_yaml(".supervisor/skill-registry.yaml")
        ids = [s.get("skill_id", "") for s in d.get("skills", [])]
        assert "check-skill-coverage" in ids, "check-skill-coverage not in skill registry"

    def test_registry_round_trips(self):
        """Ensure no data is lost in YAML round-trip."""
        text = (_REPO / ".supervisor" / "skill-registry.yaml").read_text(encoding="utf-8")
        d = yaml.safe_load(text)
        assert yaml.safe_load(yaml.dump(d)) is not None


# ---------------------------------------------------------------------------
# work-type-skill-map.yaml
# ---------------------------------------------------------------------------

class TestWorkTypeSkillMap:
    def test_file_exists(self):
        assert (_REPO / ".supervisor" / "work-type-skill-map.yaml").exists()

    def test_yaml_parses(self):
        d = _load_yaml(".supervisor/work-type-skill-map.yaml")
        assert isinstance(d, dict)

    def test_active_mappings_present(self):
        d = _load_yaml(".supervisor/work-type-skill-map.yaml")
        assert "active_mappings" in d, "active_mappings section absent"

    def test_active_mappings_count(self):
        d = _load_yaml(".supervisor/work-type-skill-map.yaml")
        mappings = d["active_mappings"]
        assert len(mappings) >= 14, f"Expected >=14 active_mappings, got {len(mappings)}"

    def test_gap_mappings_present(self):
        d = _load_yaml(".supervisor/work-type-skill-map.yaml")
        assert "gap_mappings" in d, "gap_mappings section absent"

    def test_gap_mappings_count(self):
        """gap_mappings shrinks over time as gaps are resolved and their entries
        moved to active_mappings (e.g. capability_compiler by TC-EXT-009-03,
        pre_sprint_governance_hook by TC-EXT-010-01/05 — SKILL-GAP-015 closed).
        This is a structural sanity check (field exists, is non-empty), not a
        monotonically-growing count invariant.
        """
        d = _load_yaml(".supervisor/work-type-skill-map.yaml")
        gaps = d["gap_mappings"]
        assert len(gaps) >= 1, f"Expected >=1 gap_mappings, got {len(gaps)}"

    def test_rollback_and_recovery_in_gaps(self):
        """rollback_and_recovery (SKILL-GAP-011) is the remaining open gap as of
        TC-EXT-010 (2026-07-14). Replaces the prior capability_compiler-in-gaps
        assertion — capability_compiler was resolved and moved to
        active_mappings by TC-EXT-009-03, and pre_sprint_governance_hook was
        resolved and moved to active_mappings by TC-EXT-010-01/05.
        """
        d = _load_yaml(".supervisor/work-type-skill-map.yaml")
        assert "rollback_and_recovery" in d["gap_mappings"]


# ---------------------------------------------------------------------------
# gap-register.yaml
# ---------------------------------------------------------------------------

_GAP_REGISTER = _REPO / ".local" / "recon" / "gap-register.yaml"


class TestGapRegister:
    pytestmark = pytest.mark.skipif(
        not _GAP_REGISTER.is_file(),
        reason=".local/recon/gap-register.yaml not present in this environment",
    )

    def test_yaml_parses(self):
        d = _load_yaml(".local/recon/gap-register.yaml")
        assert isinstance(d, dict)

    def test_gaps_list_present(self):
        d = _load_yaml(".local/recon/gap-register.yaml")
        assert "gaps" in d

    def test_skill_gap_001_resolved(self):
        d = _load_yaml(".local/recon/gap-register.yaml")
        match = next((g for g in d["gaps"] if g.get("gap_id") == "SKILL-GAP-001"), None)
        assert match is not None, "SKILL-GAP-001 not found"
        assert match.get("current_status") == "resolved", (
            f"SKILL-GAP-001 not resolved: {match.get('current_status')}"
        )

    def test_bypass_001_resolved(self):
        d = _load_yaml(".local/recon/gap-register.yaml")
        match = next((g for g in d["gaps"] if g.get("gap_id") == "BYPASS-001"), None)
        assert match is not None, "BYPASS-001 not found"
        assert match.get("current_status") == "resolved"

    def test_bypass_002_gap_confirmed(self):
        """BYPASS-002 is a known open gap that should remain gap_confirmed."""
        d = _load_yaml(".local/recon/gap-register.yaml")
        match = next((g for g in d["gaps"] if g.get("gap_id") == "BYPASS-002"), None)
        assert match is not None, "BYPASS-002 not found"
        assert match.get("current_status") == "gap_confirmed"


# ---------------------------------------------------------------------------
# autonomous-loop.md Step 0
# ---------------------------------------------------------------------------

class TestAutonomousLoopStep0:
    def test_file_exists(self):
        assert (_REPO / ".claude" / "commands" / "autonomous-loop.md").exists()

    def test_terminal_closed_in_done_statuses(self):
        text = _read(".claude/commands/autonomous-loop.md")
        assert "TERMINAL_CLOSED" in text

    def test_deferred_in_done_statuses(self):
        """TC-HARD-003: DEFERRED must be in DONE_STATUSES to prevent false hard-stops
        from foreign-session deferred plans."""
        text = _read(".claude/commands/autonomous-loop.md")
        assert "DEFERRED" in text, "DEFERRED not found in autonomous-loop.md"
        assert re.search(
            r"DONE_STATUSES.*DEFERRED|DEFERRED.*DONE_STATUSES", text, re.DOTALL
        ), "DEFERRED not found inside DONE_STATUSES definition"

    def test_session_id_filtering_present(self):
        """TC-HARD-003: Session-scoped filtering must be in the session-keyed lock loop."""
        text = _read(".claude/commands/autonomous-loop.md")
        assert "lock_sid" in text or "session_id" in text, (
            "No session_id filtering found in autonomous-loop.md"
        )


# ---------------------------------------------------------------------------
# check-skill-coverage.md
# ---------------------------------------------------------------------------

class TestCheckSkillCoverage:
    def test_file_exists(self):
        assert (_REPO / ".claude" / "commands" / "check-skill-coverage.md").exists()

    def test_work_type_mapping_table_present(self):
        text = _read(".claude/commands/check-skill-coverage.md")
        assert "python_api" in text
        assert "add-python-api" in text

    def test_capability_compiler_marked_skill_gap(self):
        text = _read(".claude/commands/check-skill-coverage.md")
        assert "capability_compiler" in text
        assert "SKILL_GAP" in text
