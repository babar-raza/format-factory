---
taskcard_id: GOV-003
title: Methodology Linkage and Local Enforcement
status: completed_pending_independent_verification
created: 2026-05-08
sprint: memory-methodology-linkage-and-enforcement
visibility: internal
relationship_to_main_sprint: governance -- applies to all sprint types
relationship_to_product_source: none -- methodology only
---

# GOV-003 -- Methodology Linkage and Local Enforcement

## Purpose

Make all methodology documents created by GOV-002 easy for agents to find, linked from
repo entry points, listed in command documentation, enforced through governance rules,
and validated by a deterministic local check. Close the methodology work permanently
by ensuring it is discoverable from a fresh chat or local agent session.

## Problem Statement

After GOV-002 created the methodology docs, prompt templates, and commands, they were not
yet linked from README.md, not indexed in .claude/commands/_readme.md, had no central
entry-point index, had no prompt template README, had no cross-link from AGENTS.md or
GOVERNANCE.md to the index, and had no automated check verifying the link structure.
A fresh agent would not be able to discover the methodology without manual search.

## Scope

- docs/agent-methodology-index.md (NEW -- central entry point)
- docs/prompts/README.md (NEW -- template index)
- README.md (UPDATED -- Agent Methodology and Fresh Chat Start section)
- .claude/commands/_readme.md (UPDATED -- Implemented Methodology Commands table)
- AGENTS.md (UPDATED -- AD0, AD8-AD10 rules referencing methodology index)
- GOVERNANCE.md (UPDATED -- Sections 23.0, 23.7-23.8, Section 24)
- memory/00-index.md (UPDATED -- methodology entry points table, priority reading updated)
- memory/12-planning-and-agent-handoff-methodology.md (UPDATED -- key doc paths + local bridge section)
- tools/governance/check_methodology_links.py (NEW -- deterministic link checker)
- tests/governance/test_methodology_links.py (NEW -- 14 governance tests)
- .claude/settings.json (UPDATED -- tools/governance/**, tests/governance/** allowed)
- taskcards/GOV-003-methodology-linkage-and-local-enforcement.md (this file)
- tools/evidence/contracts/memory-methodology-linkage-and-enforcement.yaml

## Out of Scope

- Product source
- Gate changes
- MAIN SPRINT execution
- SECONDARY SPRINT execution (S-F2F-02 or later)
- LLM endpoint calls
- Embeddings or vector DB
- Spec downloads

## Files Created

- docs/agent-methodology-index.md
- docs/prompts/README.md
- tools/governance/check_methodology_links.py
- tests/governance/test_methodology_links.py
- taskcards/GOV-003-methodology-linkage-and-local-enforcement.md
- tools/evidence/contracts/memory-methodology-linkage-and-enforcement.yaml

## Files Updated

- README.md (Agent Methodology section added)
- .claude/commands/_readme.md (Implemented Methodology Commands table added)
- AGENTS.md (AD0, AD8-AD10 added)
- GOVERNANCE.md (Section 23.0, 23.7-23.8, Section 24 added)
- memory/00-index.md (methodology entry points table, priority reading, stream history)
- memory/12-planning-and-agent-handoff-methodology.md (key doc paths + local bridge)
- .claude/settings.json (tools/governance/**, tests/governance/** allowed)

## Validation Command

```
python tools/governance/check_methodology_links.py
```

Expected output: METHODOLOGY_LINK_CHECK: PASS

```
PYTHONPATH="C:/Users/prora/AppData/Roaming/Python/Python313/site-packages" python -m pytest tests/governance/test_methodology_links.py -v
```

Expected output: 14 passed

## Acceptance Criteria

1. docs/agent-methodology-index.md exists and links all methodology docs, templates, and commands.
2. README.md links docs/agent-methodology-index.md.
3. .claude/commands/_readme.md lists /plan-hardening, /execution-handoff, /evidence-review-next-prompt, /memory-sprint with methodology doc and template links.
4. docs/prompts/README.md exists and lists all 8 templates.
5. AGENTS.md references docs/agent-methodology-index.md (AD0 rule).
6. GOVERNANCE.md references docs/agent-methodology-index.md (Section 23.0, 24).
7. memory/00-index.md links methodology index and memory/12.
8. tools/governance/check_methodology_links.py exists, syntax valid, passes.
9. tests/governance/test_methodology_links.py: 14/14 PASS.
10. METHODOLOGY_LINK_CHECK: PASS.
11. No product source created.
12. No LLM call made.
13. No embeddings or vector DB.
14. No gate status changes.
15. Final evidence bundle created and validates.

## Evidence Requirements

- Sprint: memory-methodology-linkage-and-enforcement
- Contract: tools/evidence/contracts/memory-methodology-linkage-and-enforcement.yaml
- Bundle: .local/evidence-bundles/memory-methodology-linkage-and-enforcement-YYYYMMDD-HHMMSS.zip
- Minimum metadata: 75

## Status

completed_pending_independent_verification

Independent verification requirement: DEC-034. A separate session must verify the content
of each created doc and the link checker results against the acceptance criteria above.
