"""
check_methodology_links.py
Deterministic local check for methodology doc accessibility and cross-link integrity.

Read-only. No network. No LLM calls. No file writes.

Exit 0: METHODOLOGY_LINK_CHECK: PASS
Exit 1: METHODOLOGY_LINK_CHECK: FAIL

Run from repo root:
    python tools/governance/check_methodology_links.py
"""
import sys
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def check(label, result, detail=""):
    """Print a check result. Return True if passed."""
    status = "PASS" if result else "FAIL"
    suffix = f" -- {detail}" if detail else ""
    print(f"  [{status}] {label}{suffix}")
    return result


def file_contains(path, text):
    """Return True if path exists and contains text (case-sensitive)."""
    try:
        content = (REPO_ROOT / path).read_text(encoding="utf-8")
        return text in content
    except Exception:
        return False


def file_exists(path):
    """Return True if path exists as a file."""
    return (REPO_ROOT / path).is_file()


def no_em_dash(path):
    """Return True if path exists and contains no em dash (U+2014)."""
    try:
        content = (REPO_ROOT / path).read_text(encoding="utf-8")
        return "\u2014" not in content
    except Exception:
        return True  # file not found -- separate check handles existence


def no_unresolved_placeholder(path):
    """Return True if path has no unresolved TBD/TODO/PLACEHOLDER markers.
    Exempts required literal final line syntax like <absolute Windows path to zip>.
    """
    exempt_patterns = [
        r"<absolute Windows path to zip>",
        r"<absolute Windows path>",
    ]
    bad_patterns = [
        r"\[PLACEHOLDER\]",
        r"\[TODO\]",
        r"<fill this>",
        r"\bTBD\b",
        r"\bTODO\b",
    ]
    try:
        content = (REPO_ROOT / path).read_text(encoding="utf-8")
        # Remove exempt patterns before checking
        cleaned = content
        for ep in exempt_patterns:
            cleaned = re.sub(ep, "", cleaned)
        for bp in bad_patterns:
            if re.search(bp, cleaned):
                return False
        return True
    except Exception:
        return True  # missing file handled separately


def run_checks():
    failures = []

    def require(label, result, detail=""):
        passed = check(label, result, detail)
        if not passed:
            failures.append(label)
        return passed

    print("\n=== Methodology Required Files ===")
    required_files = [
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
        "tools/governance/check_methodology_links.py",
    ]
    for f in required_files:
        require(f"File exists: {f}", file_exists(f))

    print("\n=== README.md Cross-Links ===")
    require(
        "README.md links docs/agent-methodology-index.md",
        file_contains("README.md", "docs/agent-methodology-index.md"),
    )
    require(
        "README.md links docs/fresh-chat-continuity-brief.md",
        file_contains("README.md", "docs/fresh-chat-continuity-brief.md"),
    )
    require(
        "README.md links docs/prompts/README.md",
        file_contains("README.md", "docs/prompts/README.md"),
    )

    print("\n=== AGENTS.md Cross-Links ===")
    require(
        "AGENTS.md references docs/agent-methodology-index.md",
        file_contains("AGENTS.md", "docs/agent-methodology-index.md"),
    )
    require(
        "AGENTS.md references docs/plan-hardening-checklist.md",
        file_contains("AGENTS.md", "docs/plan-hardening-checklist.md"),
    )
    require(
        "AGENTS.md references docs/agent-execution-handoff-standard.md",
        file_contains("AGENTS.md", "docs/agent-execution-handoff-standard.md"),
    )

    print("\n=== GOVERNANCE.md Cross-Links ===")
    require(
        "GOVERNANCE.md references docs/agent-methodology-index.md",
        file_contains("GOVERNANCE.md", "docs/agent-methodology-index.md"),
    )
    require(
        "GOVERNANCE.md references docs/plan-hardening-checklist.md",
        file_contains("GOVERNANCE.md", "docs/plan-hardening-checklist.md"),
    )

    print("\n=== memory/00-index.md Cross-Links ===")
    require(
        "memory/00-index.md references memory/12",
        file_contains("memory/00-index.md", "12-planning-and-agent-handoff-methodology.md"),
    )
    require(
        "memory/00-index.md references docs/agent-methodology-index.md",
        file_contains("memory/00-index.md", "docs/agent-methodology-index.md"),
    )

    print("\n=== docs/agent-methodology-index.md Internal Links ===")
    idx = "docs/agent-methodology-index.md"
    methodology_links = [
        "planning-methodology.md",
        "agent-execution-handoff-standard.md",
        "plan-hardening-checklist.md",
        "fresh-chat-continuity-brief.md",
        "prompts/README.md",
        "prompts/plan-hardening-prompt-template.md",
        "prompts/execution-handoff-prompt-template.md",
        "prompts/independent-verification-prompt-template.md",
        "prompts/evidence-bundle-review-prompt-template.md",
        "prompts/memory-sprint-prompt-template.md",
        "prompts/closure-hygiene-prompt-template.md",
        "prompts/unblocking-patch-prompt-template.md",
        "prompts/fresh-chat-bootstrap-prompt.md",
    ]
    for link in methodology_links:
        require(
            f"agent-methodology-index.md links {link}",
            file_contains(idx, link),
        )
    require(
        "agent-methodology-index.md links .claude/commands/plan-hardening.md",
        file_contains(idx, "plan-hardening.md"),
    )
    require(
        "agent-methodology-index.md links .claude/commands/execution-handoff.md",
        file_contains(idx, "execution-handoff.md"),
    )
    require(
        "agent-methodology-index.md links .claude/commands/evidence-review-next-prompt.md",
        file_contains(idx, "evidence-review-next-prompt.md"),
    )
    require(
        "agent-methodology-index.md links .claude/commands/memory-sprint.md",
        file_contains(idx, "memory-sprint.md"),
    )
    require(
        "agent-methodology-index.md links tools/governance/check_methodology_links.py",
        file_contains(idx, "check_methodology_links.py"),
    )

    print("\n=== docs/prompts/README.md Internal Links ===")
    prompts_readme = "docs/prompts/README.md"
    template_files = [
        "plan-hardening-prompt-template.md",
        "execution-handoff-prompt-template.md",
        "independent-verification-prompt-template.md",
        "evidence-bundle-review-prompt-template.md",
        "memory-sprint-prompt-template.md",
        "closure-hygiene-prompt-template.md",
        "unblocking-patch-prompt-template.md",
        "fresh-chat-bootstrap-prompt.md",
    ]
    for tf in template_files:
        require(
            f"docs/prompts/README.md links {tf}",
            file_contains(prompts_readme, tf),
        )

    print("\n=== .claude/commands/_readme.md Lists Commands ===")
    cmd_readme = ".claude/commands/_readme.md"
    require(
        "_readme.md lists /plan-hardening",
        file_contains(cmd_readme, "plan-hardening"),
    )
    require(
        "_readme.md lists /execution-handoff",
        file_contains(cmd_readme, "execution-handoff"),
    )
    require(
        "_readme.md lists /evidence-review-next-prompt",
        file_contains(cmd_readme, "evidence-review-next-prompt"),
    )
    require(
        "_readme.md lists /memory-sprint",
        file_contains(cmd_readme, "memory-sprint"),
    )

    print("\n=== Command Cross-References ===")
    require(
        "plan-hardening.md references plan-hardening-checklist.md",
        file_contains(".claude/commands/plan-hardening.md", "plan-hardening-checklist.md"),
    )
    require(
        "execution-handoff.md references agent-execution-handoff-standard.md",
        file_contains(".claude/commands/execution-handoff.md", "agent-execution-handoff-standard.md"),
    )
    require(
        "evidence-review-next-prompt.md references planning-methodology.md",
        file_contains(".claude/commands/evidence-review-next-prompt.md", "planning-methodology.md"),
    )
    require(
        "memory-sprint.md references planning-methodology.md",
        file_contains(".claude/commands/memory-sprint.md", "planning-methodology.md"),
    )

    print("\n=== No Em Dash in Methodology Docs ===")
    em_dash_files = [
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
    ]
    for f in em_dash_files:
        require(f"No em dash in {f}", no_em_dash(f))

    print("\n=== No Unresolved Placeholders in Methodology Docs ===")
    placeholder_files = [
        "docs/agent-methodology-index.md",
        "docs/prompts/README.md",
        "docs/planning-methodology.md",
        "docs/agent-execution-handoff-standard.md",
        "docs/plan-hardening-checklist.md",
        "docs/fresh-chat-continuity-brief.md",
        "memory/12-planning-and-agent-handoff-methodology.md",
    ]
    for f in placeholder_files:
        require(f"No unresolved placeholder in {f}", no_unresolved_placeholder(f))

    print()
    if failures:
        print(f"FAILED CHECKS ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        print()
        print("METHODOLOGY_LINK_CHECK: FAIL")
        return 1
    else:
        print("METHODOLOGY_LINK_CHECK: PASS")
        return 0


if __name__ == "__main__":
    sys.exit(run_checks())
