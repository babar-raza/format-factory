---
espanso_provenance:
  source_trigger: ":ffreadme"
  source_block: 27
  source_line_range: [27941, 29445]
  gap_id: GAP-ESP-001
  extraction_date: "2026-07-03"
  capability_id: readme-root-governance
prompt_id: ESP-PROMPT-2
title: "Root README Forensic Governance"
version: "1.0"
status: ACTIVE
mutating: true
context_profile: full
---

# Root README Forensic Investigation and Preservation-First Enhancement

**IMPORTANT:** This prompt governs `README.md` at the repository root ONLY.
Per-format READMEs (`src/python/{format}/README.md`, `src/net/{format}/README.md`) are governed
by `/sync-readmes`, not this protocol.

## Short-Context View

Improve the root `README.md` in-place using verified repository evidence.
**Do not replace from scratch.** Remove or rewrite a section only when evidence proves it is false, obsolete, duplicated, contradictory, or misleading. Preserve all human-authored structure, wording, diagrams, tables, commands, links, and maintainer notes.

---

## Full Protocol

### When to Use
- Root `README.md` is stale, inaccurate, or missing major features
- Capability count, command list, or format list is out of date
- Architecture diagrams do not match current structure
- Installation/quickstart instructions reference outdated paths

### When NOT to Use
- For format-specific READMEs — use `/sync-readmes` instead
- When no evidence of inaccuracy exists (avoid unnecessary churn)
- During a sprint whose primary goal is product code — README updates are closeout work

### Prerequisites
- Repository root: `C:\Users\prora\OneDrive\Documents\GitHub\format-factory`
- Must read current `README.md` before any mutation
- Must gather evidence from live system before any claim update

### Execution Protocol

```
PHASE 1: BIND REPOSITORY STATE
  → Confirm HEAD, branch, working tree state
  → Read README.md completely
  → Record all existing sections, headings, diagrams, tables, commands

PHASE 2: GATHER EVIDENCE
  → Capability count: registry/.governance/capabilities/registry.yaml
  → Format list: registry/format-registry.yaml
  → Command list: .claude/commands/command-registry.yaml
  → Skill count: .supervisor/skill-registry.yaml
  → Gate status: registry/format-registry.yaml (gate_status fields)
  → Architecture: .supervisor/prompts/ (what prompt assets exist)
  → Test counts: run pytest --collect-only -q 2>/dev/null | tail -3
  → Python packages: src/python/ directory listing
  → .NET projects: src/net/ directory listing

PHASE 3: CLAIM VERIFICATION
  For each factual claim in README.md:
  → Locate the source of truth
  → Verify whether the claim is accurate
  → Mark: ACCURATE | OUTDATED | FALSE | MISSING | MISLEADING

PHASE 4: PRESERVATION INVENTORY
  Record sections to PRESERVE unchanged:
  → Human-authored architectural explanations
  → Project history and design rationale
  → Maintainer notes and warnings
  → Links verified as valid
  → Examples that still work
  → Diagrams that match reality

PHASE 5: MUTATION PLAN
  For each OUTDATED / FALSE / MISSING / MISLEADING finding:
  → Specify exact change (update number, fix path, add section, remove stale content)
  → Provide evidence reference (file path, line, test result)
  → Classify: safe to auto-apply | requires human review

PHASE 6: APPLY CHANGES
  Rules:
  → Update counts when evidence shows different numbers
  → Fix paths that no longer exist
  → Add missing commands/features that have been shipped
  → Remove claims proven false by repository inspection
  → DO NOT rewrite sections that are accurate and human-authored
  → DO NOT change the overall structure unless a section belongs elsewhere

PHASE 7: VERIFY
  → Re-read updated README.md
  → Confirm all links are relative and valid
  → Confirm no evidence-backed claim was removed
  → Confirm no new unverified claim was added
```

### Preservation Rules (non-negotiable)
A section may only be removed or rewritten when repository evidence proves it is:
- False (the described feature/command does not exist)
- Obsolete (feature removed or renamed)
- Duplicated (exact same content appears elsewhere)
- Contradictory (conflicts with another verified section)
- Unsupported (no evidence it was ever true)
- Misleading (technically true but practically wrong)

### Forbidden Actions
- Replacing README from scratch
- Removing human-authored context without evidence it is false
- Adding claims not backed by current repository evidence
- Changing the project name, tagline, or vision without user instruction
- Committing without user approval (README changes are high-visibility)

### Evidence Requirements
- List of sections changed with before/after comparison
- Source of evidence for each factual claim updated
- Preservation inventory showing what was kept and why

### Completion Gate
- All factual claims verified against current repository
- Only evidence-backed changes applied
- README reads accurately for the current system state
- No human-authored context silently removed
