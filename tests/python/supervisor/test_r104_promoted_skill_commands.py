"""Tests for Skills R104 promoted skill command files.

Validates that the 5 newly promoted skills have complete command files
that pass the command validator with all 12 required sections.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from validate_claude_commands import validate_command_file, validate_all, REQUIRED_SECTIONS


PROMOTED_SKILLS = [
    "validate-skill-transcript.md",
    "validate-product-code-ledger.md",
    "build-context-pack.md",
    "select-poc-gap.md",
    "materialize-declaration-review.md",
]

COMMANDS_DIR = REPO_ROOT / ".claude" / "commands"


class TestPromotedSkillCommandFiles:
    """Positive tests: each promoted skill command file passes validation."""

    @pytest.mark.parametrize("cmd_file", PROMOTED_SKILLS)
    def test_promoted_command_file_passes(self, cmd_file):
        path = COMMANDS_DIR / cmd_file
        assert path.exists(), f"Command file not found: {path}"
        result = validate_command_file(path)
        assert result["valid"], f"{cmd_file} failed: {result['errors']}"

    @pytest.mark.parametrize("cmd_file", PROMOTED_SKILLS)
    def test_promoted_command_has_all_12_sections(self, cmd_file):
        path = COMMANDS_DIR / cmd_file
        result = validate_command_file(path)
        assert result["section_count"] == 12, (
            f"{cmd_file} missing sections: {result['sections_missing']}"
        )

    @pytest.mark.parametrize("cmd_file", PROMOTED_SKILLS)
    def test_promoted_command_has_frontmatter(self, cmd_file):
        path = COMMANDS_DIR / cmd_file
        result = validate_command_file(path)
        assert "version" in result["frontmatter"], f"{cmd_file} missing version frontmatter"
        assert "last-updated" in result["frontmatter"], f"{cmd_file} missing last-updated"


class TestPromotedSkillRegistryConsistency:
    """Verify promoted skills are active in registry."""

    def test_registry_has_promoted_skills_as_active(self):
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not available")

        registry_path = REPO_ROOT / ".supervisor" / "skill-registry.yaml"
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        skills = {s["skill_id"]: s for s in data.get("skills", [])}

        promoted_ids = [
            "validate-skill-transcript",
            "validate-product-code-ledger",
            "build-context-pack",
            "select-poc-gap",
            "materialize-declaration-review",
        ]

        for sid in promoted_ids:
            assert sid in skills, f"Skill {sid} not in registry"
            assert skills[sid]["status"] == "active", (
                f"Skill {sid} should be active, got {skills[sid]['status']}"
            )

    def test_deferred_skills_remain_non_active(self):
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not available")

        registry_path = REPO_ROOT / ".supervisor" / "skill-registry.yaml"
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        skills = {s["skill_id"]: s for s in data.get("skills", [])}

        # R112: record-lane-execution promoted to active; check-mcp-status remains deferred
        deferred = ["check-mcp-status"]
        for sid in deferred:
            assert sid in skills, f"Skill {sid} not in registry"
            assert skills[sid]["status"] in ("draft", "deferred"), (
                f"Skill {sid} should be draft or deferred, got {skills[sid]['status']}"
            )
        # Verify record-lane-execution is now active (promoted in R112)
        assert skills["record-lane-execution"]["status"] == "active", (
            f"record-lane-execution should be active after R112 promotion"
        )

    def test_total_active_skills_at_least_18(self):
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not available")

        registry_path = REPO_ROOT / ".supervisor" / "skill-registry.yaml"
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        active = [s for s in data.get("skills", []) if s.get("status") == "active"]
        assert len(active) >= 18, f"Expected at least 18 active skills, got {len(active)}"


class TestCommandValidatorNegative:
    """Negative tests: ensure validator catches problems."""

    def test_missing_allowed_paths_in_stub_fails(self, tmp_path):
        stub = tmp_path / "bad-skill.md"
        stub.write_text(
            "---\nversion: '1.0'\nlast-updated: '2026-06-03'\n---\n"
            "# /bad-skill\n\nA skill with missing sections.\n\n"
            "## Required Inputs\n- something\n\n"
            "## What This Skill Does\n1. Step one\n2. Step two\n\n"
            "## Forbidden Paths\n- nothing\n\n"
            "## Stop Conditions\n- none\n\n"
            "## Evidence Output\nSome output.\n\n"
            "## Validation\nRun it.\n\n"
            "## Rollback\nUndo it.\n\n"
            "Mentions transcript somewhere.\n\n"
            "## Sample Invocation\n```bash\nrun it\n```\n\n"
            "## Changelog\n- v1.0\n",
            encoding="utf-8",
        )
        result = validate_command_file(stub)
        assert not result["valid"], "Should fail due to missing Allowed Paths"
        assert "allowed_paths" in result["sections_missing"]

    def test_too_short_file_fails(self, tmp_path):
        stub = tmp_path / "short.md"
        stub.write_text("# /short\n\nToo short.\n", encoding="utf-8")
        result = validate_command_file(stub)
        assert not result["valid"]
        assert any("too short" in e.lower() for e in result["errors"])

    def test_nonexistent_file_fails(self, tmp_path):
        result = validate_command_file(tmp_path / "does-not-exist.md")
        assert not result["valid"]
        assert any("cannot read" in e.lower() for e in result["errors"])
