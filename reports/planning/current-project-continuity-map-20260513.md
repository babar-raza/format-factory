# Current Project Continuity Map
# Date: 2026-05-13
# Sprint: CHATGPT-MEMORY-LOCAL-SYNC-20260513

## Purpose

This map provides a navigable overview of Format Factory project state, decisions, evidence, memory,
and next actions as of 2026-05-13. It is designed for fresh-chat continuity and inter-session handoff.

---

## 1. Major Decisions

| Decision | ID | Status | Resolution | Date |
|----------|-----|--------|-----------|------|
| .NET packaging model | DEC-033 | RESOLVED | Option B: .NET Commercial Only | 2026-05-12 |
| Independent verification requirement | DEC-034 | ACTIVE | Required before any gate human review | ongoing |
| Commercial product direction | memory/21 | RESOLVED | C7+ load-edit-save-convert | 2026-05-13 |
| AI usage authorization | memory/23 | RESOLVED | Accelerator authorized, not authority | 2026-05-13 |
| Gate 11 approval | registry | DEFERRED | NOT APPROVED — in_progress | ongoing |
| FODS/FODT Gates 1-10 | registry | ALL PASSED | See registry/format-registry.yaml | 2026-05-08 |

---

## 2. Current Source Status

### Python FOSS (src/python/)
| Format | Status | Key Files |
|--------|--------|-----------|
| FODS | Phase 4 COMPLETE (TC-0050) | src/python/fods/ — parser.py, neutral_model.py, constants.py, exceptions.py, __init__.py |
| FODT | Phase 4 COMPLETE (TC-0052) | src/python/fodt/ — same structure |

### .NET Commercial (src/net/)
| Format | Status | Capability | Tests |
|--------|--------|-----------|-------|
| FODS | C4-C6-vertical-slice | Load/Save/Edit DOM | 42/42 PASS |
| FODT | C4-C6-vertical-slice | Load/Save/Edit DOM | 43/43 PASS |

Key .NET files:
- src/net/fods/FodsDocument.cs, FodsWriter.cs, Model/FodsSheet.cs, FodsRow.cs, FodsCell.cs
- src/net/fodt/FodtDocument.cs, FodtWriter.cs, Model/FodtBody.cs, FodtParagraph.cs

---

## 3. Evidence Bundle Chain

| Bundle File | Sprint | Status | Notes |
|-------------|--------|--------|-------|
| .local/commercial-load-save-vertical-slice-swarm-20260513.zip | COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001 | BUNDLE_VALIDATION: PASS | Latest primary bundle |
| .local/dec034-gate11-tier0-commercial-iv-swarm-20260513.zip | DEC034-GATE11-TIER0-COMMERCIAL-IV-SWARM-001 | PASS | |
| .local/gate11-approval-release-readiness-swarm-20260513.zip | GATE11-APPROVAL-AND-RELEASE-READINESS-SWARM-001 | PASS | Gate 11 deferred |
| .local/gate11-tier0-commercial-accel003-repair-swarm-20260513.zip | GATE11-TIER0-COMMERCIAL-AND-ACCEL003-REPAIR-SWARM-001 | PASS | |

Note: Evidence bundles are in .local/ (gitignored). They are not pushed to remote.

---

## 4. Memory Files

| File | Topic | Sprint |
|------|-------|--------|
| memory/24-chatgpt-session-memory-sync-20260513.md | Full session continuity (THIS sync) | CHATGPT-MEMORY-LOCAL-SYNC |
| memory/23-ai-usage-operating-model-20260513.md | AI usage policy | AI-USAGE-LOCAL-DOC-SYNC |
| memory/22-commercial-load-save-vertical-slice-20260513.md | Vertical slice result | COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001 |
| memory/21-commercial-product-direction-reset-20260513.md | Commercial product direction | COMMERCIAL-REQUIREMENTS-DOC-SYNC |
| memory/20-gate11-approval-release-readiness-20260513.md | Gate 11 deferred | GATE11-APPROVAL-AND-RELEASE-READINESS-SWARM-001 |
| memory/19-dec034-gate11-tier0-commercial-iv-20260513.md | DEC-034 IV | DEC034-GATE11-TIER0-COMMERCIAL-IV-SWARM-001 |
| memory/18-gate11-tier0-dotnet-and-accel003-repair-20260513.md | Gate 11 Tier 0 .NET | GATE11-TIER0-COMMERCIAL-AND-ACCEL003-REPAIR-SWARM-001 |
| memory/17-dec033-option-b-gate11-and-github-pat-20260512.md | DEC-033 Option B | DEC033-OPTION-B-GATE11-COMMERCIAL-SWARM-001 |
| memory/16-controlled-swarm-execution-and-acceleration-20260512.md | Swarm model | POST-FODT-GATE10-CONTROLLED-SWARM-001 |

---

## 5. Plans

| Plan | Version | Purpose |
|------|---------|---------|
| plans/master-plan.md | v2.47 | Operational authority — all sprint states, next action |
| plans/secondary/ | various | Secondary sprints (S-F2F-00 through S-F2F-08) |

---

## 6. Active Taskcards

### Completed Taskcards (relevant recent)
- TC-0050: FODS Phase 4 Python — COMPLETED
- TC-0052: FODT Phase 4 Python — COMPLETED
- TC-0044: FODS Gate 10 — COMPLETED
- TC-0049: FODT Gate 10 — COMPLETED

### In-Progress Taskcards
- taskcards/FODS-GATE11-commercial-readiness.md — commercial_readiness_in_progress
- taskcards/FODT-COMMERCIAL-EDIT-SAVE-VERTICAL-SLICE.md — C7 roadmap

### Commercial Implementation Taskcards (from COMMERCIAL-REQUIREMENTS-DOC-SYNC)
10 taskcards for C3-C10 implementation path — see taskcards/ directory.

### AI Taskcards (from AI-USAGE-LOCAL-DOC-SYNC)
- AI-USAGE-OPERATING-MODEL, AI-SPEC-RETRIEVAL-RAG-POLICY, AI-COMMERCIAL-DEVELOPMENT-PATTERNS
- AI-USAGE-LEDGER-AND-METRICS, AI-VALIDATION-GATES

---

## 7. Skills/Commands Plan

Current skills (via .claude/commands/):
- /plan-hardening — plan review and hardening
- /execution-handoff — execution handoff standard
- /evidence-review-next-prompt — evidence review and next prompt
- /memory-sprint — memory sync sprint

Planned skills (tools/skills/ — NOT YET IMPLEMENTED):
- Format context resolver
- Local spec retrieval
- Requirements generation pipeline
- Verifier review
- Implementation prompt generator
- Evidence contract generator

Reference: .claude/commands/_readme.md, docs/prompts/README.md

---

## 8. Generated Requirements Direction

| Location | Format | Status |
|----------|--------|--------|
| generated-requirements/fods/ | FODS | generated, schema-validated, verifier-reviewed — pending IV |
| generated-requirements/fodt/ | FODT | generated, schema-validated, verifier-reviewed — pending IV |

Files present:
- commercial-requirements.yaml
- object-model-requirements.yaml (MODIFIED — dirty, not staged)
- save-edit-requirements.yaml
- conversion-requirements.yaml
- verifier-review.yaml (MODIFIED — dirty, not staged)
- traceability-map.yaml

Note: object-model-requirements.yaml and verifier-review.yaml have unstaged modifications.
These must NOT be touched by this sprint (prohibited directory).

Next step: Independent verification sprint to accept requirement IDs as ACCEPTED_FOR_VERTICAL_SLICE.

---

## 9. AI Governance Docs

| Document | Purpose |
|----------|---------|
| docs/ai-usage-operating-model.md | Core policy — allowed/prohibited uses, ledger, workflow |
| docs/ai-usage-operating-model.yaml | Machine-readable policy |
| docs/ai-assisted-commercial-development.md | Patterns A-F for src/net/{format}/ implementation |
| docs/ai-assisted-commercial-development.yaml | Machine-readable patterns |
| docs/spec-retrieval-and-rag-policy.md | RAG guardrails, provenance, embedding policy |
| docs/spec-retrieval-and-rag-policy.yaml | Machine-readable |
| docs/agent-swarm-ai-orchestration.md | AI lane governance in controlled swarms |

---

## 10. Next Recommended Work

Priority 1: AI-generated requirements independent verification
- Sprint type: DEC-034 IV sprint
- Files: generated-requirements/fods/, generated-requirements/fodt/
- Action: Verify against schema and spec; accept requirement IDs; update verifier-review.yaml
- Unblocks: Next .NET implementation swarm (entity expansion)
- Requires human authorization

Priority 2: .NET entity expansion
- Expand FODS: row/column operations, cell styles, multi-sheet navigation
- Expand FODT: lists, tables, text styles, headings
- Follow accepted requirement IDs
- Advance capability toward C7 (same-format save with full entity model)

Priority 3: Skill system implementation
- Build tools/skills/ requirements generation pipeline
- Enables scaling to future formats without manual spec extraction
- Pre-condition for FODP, ODS, ODT, and other format acquisitions

---

## Local Documents Referenced

The following docs were checked for existence:
- docs/commercial-product-capability-model.md — PRESENT
- docs/commercial-dotnet-architecture.md — PRESENT
- docs/ai-usage-operating-model.md — PRESENT
- docs/ai-assisted-commercial-development.md — PRESENT
- docs/spec-retrieval-and-rag-policy.md — PRESENT
- docs/agent-swarm-ai-orchestration.md — PRESENT
- memory/21-commercial-product-direction-reset-20260513.md — PRESENT
- memory/22-commercial-load-save-vertical-slice-20260513.md — PRESENT
- memory/23-ai-usage-operating-model-20260513.md — PRESENT
- memory/24-chatgpt-session-memory-sync-20260513.md — CREATED (this sprint)
- generated-requirements/ — PRESENT
- tools/requirements/ — CHECK (may not be present)
- tools/skills/ — NOT PRESENT (backlog)
