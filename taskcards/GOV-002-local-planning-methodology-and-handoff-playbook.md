---
taskcard_id: GOV-002
title: Local Planning Methodology and Agent Handoff Playbook
status: completed_pending_independent_verification
created: 2026-05-08
sprint: memory-planning-methodology-and-agent-handoff
visibility: internal
relationship_to_main_sprint: governance -- applies to all sprint types
relationship_to_product_source: none -- methodology only
---

# GOV-002 -- Local Planning Methodology and Agent Handoff Playbook

## Purpose

Create durable local methodology docs, prompt templates, and execution handoff standards
so the format-factory project can preserve and reuse the planning style established in
this chat session. A fresh chat window must be able to continue with the same approach
without needing the full original conversation.

## Problem Statement

Planning patterns, execution handoff structures, and user preferences developed during
chat sessions were not stored as durable repo artifacts. Each new session risked
inconsistent execution style, missing plan hardening, or lost user preferences.

## Scope

- docs/planning-methodology.md (core principles, sprint types, prompt anatomy, style rules)
- docs/agent-execution-handoff-standard.md (execution standard, handoff structure)
- docs/plan-hardening-checklist.md (22-item checklist)
- docs/fresh-chat-continuity-brief.md (fresh chat orientation guide)
- docs/prompts/ (8 prompt templates)
- memory/12-planning-and-agent-handoff-methodology.md (user preferences captured in memory)
- .claude/commands/ (4 command files: plan-hardening, execution-handoff, evidence-review-next-prompt, memory-sprint)
- AGENTS.md Section AD (planning and handoff methodology rules)
- GOVERNANCE.md Section 23 (planning and handoff governance)

## Out of Scope

- Product source
- Gate changes
- LLM endpoint calls
- Embeddings or vector DB

## Acceptance Criteria

1. docs/planning-methodology.md exists and covers all 10 required sections.
2. docs/agent-execution-handoff-standard.md exists and covers all 18 required sections.
3. docs/plan-hardening-checklist.md exists with 22-item checklist.
4. docs/fresh-chat-continuity-brief.md exists with all 8 required sections.
5. All 8 prompt templates exist in docs/prompts/.
6. memory/12-planning-and-agent-handoff-methodology.md exists.
7. memory/00-index.md updated.
8. 4 .claude/commands/ files created.
9. AGENTS.md Section AD added.
10. GOVERNANCE.md Section 23 added.
11. Evidence bundle validates (BUNDLE_VALIDATION: PASS, minimum 60 metadata).
12. No product source created.
13. No LLM call made.
14. No embeddings or vector DB.
15. No gate status changes.

## Status

completed_pending_independent_verification

Independent verification requirement: DEC-034. A separate session must verify the content
of each created doc against the acceptance criteria above.
