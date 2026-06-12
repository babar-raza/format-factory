"""Tests for validate_claude_commands.py — command file validator."""

import sys
import textwrap
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"
sys.path.insert(0, str(TOOLS_DIR))

from validate_claude_commands import (
    validate_command_file,
    validate_all,
    cross_reference_registry,
    _parse_frontmatter,
    REQUIRED_SECTIONS,
)


# ── Frontmatter parsing ──────────────────────────────────────────────

def test_parse_frontmatter_present():
    content = "---\nversion: \"1.0\"\nlast-updated: \"2026-06-03\"\n---\n# Title"
    fm, body = _parse_frontmatter(content)
    assert fm["version"] == "1.0"
    assert body.startswith("# Title")


def test_parse_frontmatter_absent():
    content = "# Title\nBody text"
    fm, body = _parse_frontmatter(content)
    assert fm == {}
    assert "# Title" in body


# ── Single file validation ────────────────────────────────────────────

def _write_full_command(tmp_path: Path, extra: str = "") -> Path:
    """Write a command file with all required sections."""
    p = tmp_path / "test-command.md"
    p.write_text(textwrap.dedent(f"""\
        ---
        version: "1.0"
        last-updated: "2026-06-03"
        ---

        # /test-command

        Test command description paragraph that explains the purpose.

        ## Usage

        ```
        /test-command
        ```

        ## Steps

        1. Read files
        2. Do work
        3. Report results

        ## Allowed Paths

        - `src/python/test/`

        ## Forbidden Paths

        - `registry/format-registry.yaml`

        ## Stop Conditions

        - Ledger missing

        ## Evidence Required

        - Test results

        ## Validation

        Complete when tests pass.

        ## Rollback

        1. Revert changes

        ## Transcript

        Emit a skill invocation transcript to reports/.

        ## Sample Invocation

        ```
        /test-command
        ```

        ## Changelog

        - 1.0 (2026-06-03): Initial

        {extra}
    """), encoding="utf-8")
    return p


def test_full_command_passes(tmp_path):
    p = _write_full_command(tmp_path)
    result = validate_command_file(p)
    assert result["valid"] is True
    assert len(result["errors"]) == 0
    assert result["section_count"] == len(REQUIRED_SECTIONS)


def test_missing_allowed_paths_fails(tmp_path):
    p = tmp_path / "bad.md"
    p.write_text(textwrap.dedent("""\
        ---
        version: "1.0"
        last-updated: "2026-06-03"
        ---

        # /bad-command

        Description paragraph.

        ## Required Inputs

        - format_id

        ## Steps

        1. Do step one
        2. Do step two

        ## Forbidden Paths

        - `registry/`

        ## Stop Conditions

        - Something

        ## Output Format

        Report results.

        ## Changelog

        - 1.0: init
    """), encoding="utf-8")
    result = validate_command_file(p)
    assert result["valid"] is False
    assert any("Allowed paths" in e for e in result["errors"])


def test_short_file_fails(tmp_path):
    p = tmp_path / "short.md"
    p.write_text("# /short\nToo short.", encoding="utf-8")
    result = validate_command_file(p)
    assert result["valid"] is False
    assert any("too short" in e for e in result["errors"])


def test_missing_frontmatter_warns(tmp_path):
    p = _write_full_command(tmp_path)
    content = p.read_text(encoding="utf-8")
    # Remove frontmatter
    body_start = content.find("---", 3)
    p.write_text(content[body_start + 3:], encoding="utf-8")
    result = validate_command_file(p)
    assert any("frontmatter" in w.lower() or "version" in w.lower() for w in result["warnings"])


def test_transcript_keyword_detected(tmp_path):
    p = _write_full_command(tmp_path)
    result = validate_command_file(p)
    assert "transcript_requirement" in result["sections_found"]


def test_transcript_keyword_missing_warns(tmp_path):
    p = tmp_path / "no-xscript.md"
    p.write_text(textwrap.dedent("""\
        ---
        version: "1.0"
        last-updated: "2026-06-03"
        ---

        # /no-xscript

        Description paragraph for the command.

        ## Required Inputs

        - format_id

        ## Steps

        1. Step one
        2. Step two

        ## Allowed Paths

        - `src/python/test/`

        ## Forbidden Paths

        - `registry/`

        ## Stop Conditions

        - Ledger missing

        ## Output Format

        Report results.

        ## Changelog

        - 1.0: init
    """), encoding="utf-8")
    result = validate_command_file(p)
    assert "transcript_requirement" in result["sections_missing"]


# ── Validate all ──────────────────────────────────────────────────────

def test_validate_all_finds_files(tmp_path):
    cmd_dir = tmp_path / ".claude" / "commands"
    cmd_dir.mkdir(parents=True)
    _write_full_command(cmd_dir)
    (cmd_dir / "_readme.md").write_text("# Readme\n", encoding="utf-8")
    # Create minimal registry
    reg = tmp_path / "registry.yaml"
    reg.write_text("registry_id: test\nskills: []\n", encoding="utf-8")
    result = validate_all(cmd_dir, reg)
    assert "test-command.md" in result["commands"]
    assert "_readme.md" not in result["commands"]


# ── Cross-reference ───────────────────────────────────────────────────

def test_orphan_command_detected(tmp_path):
    cmd_results = {"orphan-skill.md": {"valid": True}}
    reg = tmp_path / "registry.yaml"
    import yaml as _yaml
    reg.write_text(_yaml.dump({
        "skills": [{"skill_id": "other", "command_file": ".claude/commands/other.md"}]
    }), encoding="utf-8")
    errors, warnings = cross_reference_registry(cmd_results, reg)
    assert any("Orphan" in w for w in warnings)


def test_missing_command_from_registry_errors(tmp_path):
    cmd_results = {}
    reg = tmp_path / "registry.yaml"
    import yaml as _yaml
    reg.write_text(_yaml.dump({
        "skills": [{"skill_id": "active-skill", "status": "active",
                     "command_file": ".claude/commands/active-skill.md"}]
    }), encoding="utf-8")
    errors, warnings = cross_reference_registry(cmd_results, reg)
    assert any("missing command" in e.lower() for e in errors)


def test_missing_draft_command_only_warns(tmp_path):
    cmd_results = {}
    reg = tmp_path / "registry.yaml"
    import yaml as _yaml
    reg.write_text(_yaml.dump({
        "skills": [{"skill_id": "draft-skill", "status": "draft",
                     "command_file": ".claude/commands/draft-skill.md"}]
    }), encoding="utf-8")
    errors, warnings = cross_reference_registry(cmd_results, reg)
    assert len(errors) == 0
    assert any("draft" in w.lower() for w in warnings)
