---
report_type: governance_sync
title: Assistant Supervision Methodology Sync Report
sprint: CHATGPT-MEMORY-LOCAL-SYNC-20260513-ADDENDUM
date: "2026-05-13"
visibility: internal
publish_allowed: false
---

# Assistant Supervision Methodology Sync Report

**Sprint:** CHATGPT-MEMORY-LOCAL-SYNC-20260513-ADDENDUM
**Date:** 2026-05-13
**Scope:** Transfer ChatGPT execution methodology, supervision style, and design standards into local repo memory

---

## 1. What Methodology Was Captured

The following working methodology was captured from the ChatGPT session that preceded this sync:

- **Evidence-first reasoning:** Never accept sprint claims without inspecting the evidence bundle and source files.
- **Challenge-agent-claims behavior:** Actively challenge PASS/complete/ready/commercial-ready claims against actual artifacts.
- **Ready-to-send prompt generation:** All next-step recommendations must include a complete, pasteable prompt — not vague guidance.
- **Controlled swarm execution:** Prefer larger governed multi-lane swarms over serial micro-sprints.
- **System design preference:** Build reusable systems, pipelines, and contracts rather than one-off patches.
- **AI acceleration with governance:** Use AI for retrieval, requirements, code, tests, gaps — but validate every output before accepting it.
- **Generated-requirements-first:** Human requirements → governed AI generation → schema validation → verifier review → accepted requirement IDs → implementation.
- **Gate and readiness discipline:** Use precise language about prototype/vertical-slice/commercial-product; Gate 11 requires C7+ evidence and human approval.
- **Local memory and continuity:** Sync durable decisions to local memory; local repo always wins over external AI memory.
- **Communication style:** Direct, honest, no flattery, clear verdicts, practical implications, ready-to-send prompts.

---

## 2. Files Created

| File | Purpose |
|------|---------|
| `docs/assistant-supervision-methodology.md` | Primary supervision methodology document (15 sections) |
| `docs/assistant-supervision-methodology.yaml` | Machine-readable version of the same |
| `docs/project-execution-standards.md` | Concise execution standards reference (10 sections) |
| `docs/project-execution-standards.yaml` | Machine-readable version of the same |
| `memory/25-assistant-supervision-methodology-20260513.md` | Compact durable memory version |
| `taskcards/ASSISTANT-SUPERVISION-METHODOLOGY.md` | Taskcard for methodology maintenance |
| `taskcards/PROJECT-EXECUTION-STANDARDS.md` | Taskcard for standards maintenance |
| `reports/governance/assistant-supervision-methodology-sync-20260513.md` | This report |
| `reports/governance/assistant-supervision-methodology-sync-20260513.yaml` | Machine-readable version |
| `.local/chatgpt-memory-local-sync-20260513-metadata/assistant-supervision-methodology-sync-report.md` | Local metadata summary |

---

## 3. Files Updated

| File | Change |
|------|--------|
| `docs/fresh-chat-project-bootstrap.md` | Added "Expected assistant working style" section |
| `docs/fresh-chat-project-bootstrap.yaml` | Added `assistant_working_style_files` and `assistant_working_style_summary` fields |
| `memory/00-index.md` | Added entry for memory/25; added addendum to memory stream update history |
| `AGENTS.md` | Added AF15 (ready-to-send prompts required for next steps) |
| `GOVERNANCE.md` | Added 26.13 (supervision methodology and execution standards) |

---

## 4. Files Intentionally Not Updated

| File | Reason |
|------|--------|
| `plans/master-plan.md` | No gate status or operational state change in this addendum sprint |
| `registry/format-registry.yaml` | No gate status change |
| `src/net/` or `src/python/` | Product source not in scope |
| `tests/` | Test changes not in scope |
| Any acquisition pack | Not in scope |

---

## 5. Governance Rules Already Present

The following suggested rules were already present in AGENTS.md or GOVERNANCE.md before this sprint:

| Rule | Existing location |
|------|------------------|
| Future agents must inspect evidence before accepting sprint claims | AD2, AD9 (AGENTS.md) |
| Future agents must preserve controlled swarm safety rules | Section AE (AGENTS.md), Section 25 (GOVERNANCE.md) |
| Future agents must sync durable decisions to local memory | U6 (AGENTS.md) |
| Future agents must treat AI output as proposal until validated | AC4, AF12 (AGENTS.md), 26.10 (GOVERNANCE.md) |
| Future agents must not overstate commercial readiness | AF9, AF10, AF11 (AGENTS.md), 26.8, 26.9 (GOVERNANCE.md) |

---

## 6. Governance Rules Added

| Rule | Location |
|------|---------|
| AF15: Ready-to-send prompts are required for next steps | AGENTS.md (NEW) |
| 26.13: Supervision methodology and execution standards | GOVERNANCE.md (NEW) |

---

## 7. Remaining Gaps

- The methodology documents reference `docs/agent-methodology-index.md` links that should be
  verified against the new methodology files. Adding the new docs to that index is recommended
  in a subsequent sprint.
- GOV-006 (documentation information architecture) should eventually incorporate these new docs
  into the broader taxonomy.

---

## 8. How Future Chats Should Use the Methodology

A new ChatGPT or Claude session should:

1. Paste `docs/fresh-chat-project-bootstrap.md` as context.
2. Read `docs/assistant-supervision-methodology.md` before reviewing evidence or planning.
3. Read `docs/project-execution-standards.md` before writing execution prompts.
4. Read `memory/25-assistant-supervision-methodology-20260513.md` for the compact summary.
5. Apply the methodology when reviewing sprint evidence, challenging agent claims, and generating next prompts.

---

## 9. How Local Agents Should Use the Methodology

A Claude Code or other local agent should:

1. Read `docs/fresh-chat-project-bootstrap.md` at session start.
2. Apply evidence-first review (Section 3 of methodology) before accepting any sprint claim.
3. Produce ready-to-send prompts per Section 6 of the methodology.
4. Follow controlled swarm structure per Section 7 when executing multi-lane sprints.
5. Follow execution standards lifecycle (10 steps) per `docs/project-execution-standards.md`.

---

## 10. How This Prevents Drift

Without this methodology documented locally:
- Future agents would accept sprint claims without evidence inspection.
- Future agents would provide vague advice instead of complete prompts.
- The controlled swarm model would not be passed on consistently.
- AI governance expectations would be lost at session boundaries.
- Gate readiness language would drift (prototype ≠ commercial product).

With this methodology documented locally:
- Any new session that reads the bootstrap files gets the full methodology.
- Agents that deviate from evidence-first review violate documented governance (GOVERNANCE.md 26.13).
- Prompt generation standards are codified and enforceable.
- The methodology is version-controlled and improves incrementally.
