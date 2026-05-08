"""
test_methodology_links.py
Unit tests for check_methodology_links.py.

Run from repo root:
    python -m pytest tests/governance/test_methodology_links.py -v
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CHECKER = REPO_ROOT / "tools" / "governance" / "check_methodology_links.py"


def run_checker():
    """Run the methodology link checker and return (returncode, stdout)."""
    result = subprocess.run(
        [sys.executable, str(CHECKER)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    return result.returncode, result.stdout + result.stderr


class TestMethodologyLinkChecker:
    def test_checker_script_exists(self):
        assert CHECKER.exists(), f"Checker not found: {CHECKER}"

    def test_checker_syntax_valid(self):
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(CHECKER)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_required_methodology_files_exist(self):
        required = [
            "docs/agent-methodology-index.md",
            "docs/prompts/README.md",
            "docs/planning-methodology.md",
            "docs/agent-execution-handoff-standard.md",
            "docs/plan-hardening-checklist.md",
            "docs/fresh-chat-continuity-brief.md",
            "docs/prompts/plan-hardening-prompt-template.md",
            "docs/prompts/execution-handoff-prompt-template.md",
            "docs/prompts/independent-verification-prompt-template.md",
            "docs/prompts/evidence-bundle-review-prompt-template.md",
            "docs/prompts/memory-sprint-prompt-template.md",
            "docs/prompts/closure-hygiene-prompt-template.md",
            "docs/prompts/unblocking-patch-prompt-template.md",
            "docs/prompts/fresh-chat-bootstrap-prompt.md",
            "memory/12-planning-and-agent-handoff-methodology.md",
            ".claude/commands/plan-hardening.md",
            ".claude/commands/execution-handoff.md",
            ".claude/commands/evidence-review-next-prompt.md",
            ".claude/commands/memory-sprint.md",
        ]
        for f in required:
            assert (REPO_ROOT / f).is_file(), f"Missing required file: {f}"

    def test_readme_links_methodology_index(self):
        content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        assert "docs/agent-methodology-index.md" in content

    def test_readme_links_fresh_chat_brief(self):
        content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        assert "docs/fresh-chat-continuity-brief.md" in content

    def test_agents_md_references_methodology_index(self):
        content = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        assert "docs/agent-methodology-index.md" in content

    def test_governance_md_references_methodology_index(self):
        content = (REPO_ROOT / "GOVERNANCE.md").read_text(encoding="utf-8")
        assert "docs/agent-methodology-index.md" in content

    def test_memory_index_references_memory_12(self):
        content = (REPO_ROOT / "memory/00-index.md").read_text(encoding="utf-8")
        assert "12-planning-and-agent-handoff-methodology.md" in content

    def test_memory_index_references_methodology_index(self):
        content = (REPO_ROOT / "memory/00-index.md").read_text(encoding="utf-8")
        assert "docs/agent-methodology-index.md" in content

    def test_command_readme_lists_all_four_commands(self):
        content = (REPO_ROOT / ".claude/commands/_readme.md").read_text(encoding="utf-8")
        for cmd in ["plan-hardening", "execution-handoff", "evidence-review-next-prompt", "memory-sprint"]:
            assert cmd in content, f"Command not listed in _readme.md: {cmd}"

    def test_prompts_readme_links_all_templates(self):
        content = (REPO_ROOT / "docs/prompts/README.md").read_text(encoding="utf-8")
        templates = [
            "plan-hardening-prompt-template.md",
            "execution-handoff-prompt-template.md",
            "independent-verification-prompt-template.md",
            "evidence-bundle-review-prompt-template.md",
            "memory-sprint-prompt-template.md",
            "closure-hygiene-prompt-template.md",
            "unblocking-patch-prompt-template.md",
            "fresh-chat-bootstrap-prompt.md",
        ]
        for t in templates:
            assert t in content, f"Template not listed in prompts/README.md: {t}"

    def test_methodology_index_links_all_templates(self):
        content = (REPO_ROOT / "docs/agent-methodology-index.md").read_text(encoding="utf-8")
        templates = [
            "plan-hardening-prompt-template.md",
            "execution-handoff-prompt-template.md",
            "independent-verification-prompt-template.md",
            "evidence-bundle-review-prompt-template.md",
            "memory-sprint-prompt-template.md",
            "closure-hygiene-prompt-template.md",
            "unblocking-patch-prompt-template.md",
            "fresh-chat-bootstrap-prompt.md",
        ]
        for t in templates:
            assert t in content, f"Template not linked in agent-methodology-index.md: {t}"

    def test_no_em_dash_in_methodology_docs(self):
        files = [
            "docs/agent-methodology-index.md",
            "docs/prompts/README.md",
            "docs/planning-methodology.md",
            "docs/fresh-chat-continuity-brief.md",
        ]
        for f in files:
            content = (REPO_ROOT / f).read_text(encoding="utf-8")
            assert "\u2014" not in content, f"Em dash found in {f}"

    def test_checker_passes(self):
        returncode, output = run_checker()
        assert "METHODOLOGY_LINK_CHECK: PASS" in output, f"Checker failed:\n{output}"
        assert returncode == 0, f"Checker returned non-zero: {returncode}\n{output}"
