---
memory_package: format-factory-chat-memory
version: 1.0
created_at: 2026-05-03
intended_location: /memory
source: ChatGPT conversation memory plus inspected Phase 0 evidence bundles through run015
visibility: internal
publish_allowed: false
notes: Place this folder at repo root as /memory. These files are for agent context and must not supersede plans/master-plan.md.
---

# 00 â€” Memory Index

## Purpose

This index helps an agent understand the complete picture without reading a single huge transcript.

The memory package captures:

- the origin of the project
- the userâ€™s standing governance rules
- the architecture decisions
- the reason for each Phase 0 hardening run
- the evidence-bundle review pattern
- the current state before Phase 1
- future memory synchronization rules

## Files

| File | Purpose |
|---|---|
| `01-project-origin-and-intent.md` | Why the project exists and what â€œfile format hackingâ€ means here. |
| `02-standing-operating-rules.md` | Non-negotiable rules the user established for ChatGPT and agents. |
| `03-architecture-and-product-tracks.md` | Acquisition layer, OSS Python, OSS .NET, commercial .NET, tiers. |
| `04-phase0-evolution-and-bundle-reviews.md` | Chronological account of plan versions and evidence bundle inspections. |
| `05-decision-register-expanded.md` | Expanded decision log with rationale and consequences. |
| `06-gap-risk-and-healing-history.md` | Gap, risk, and healing history through run014. |
| `07-agent-governance-model.md` | Claude/Codex, AGENTS.md, commands, skills, gates, bundles. |
| `08-specification-cache-amendment.md` | Requirement to cache specifications/materials locally on disk. |
| `09-current-state-before-phase1.md` | Current repo/project state after run015: Phase 0 accepted, Phase 1A FODS scoring complete. |
| `10-memory-maintenance-protocol.md` | How agents should maintain `/memory` over time. |
| `11-prompting-and-agent-style-rules.md` | Prompt mode labels, execution handoffs, bundle requirements. |
| `12-glossary.md` | Project terminology. |
| `11-format-understanding-and-llm-strategy.md` | Format Understanding Layer, LLM/embedding strategy, non-XML backlog, non-Aspose registry, discovered-gap capture rule (memory sprint 2026-05-08). Updated 2026-05-09 with AI direction refinement notes. |
| `12-planning-and-agent-handoff-methodology.md` | Planning methodology, execution handoff standard, user preferences for prompts and plans. Updated with methodology index and prompt README links (linkage sprint 2026-05-08). Updated 2026-05-09 with ChatGPT supervision and parallel sprint handling rules. |
| `13-chatgpt-initial-project-analysis-20260509.md` | ChatGPT first project-level analysis (2026-05-09). Project purpose, user requirement, standing, strengths, gaps, intended path, next-level AI interpretation, bottom-line assessment. Required reading for AI/LLM, Phase 4, or multi-stream sprint work. |
| `14-ai-supervision-and-three-pilot-direction-20260509.md` | AI supervision rules and three-pilot direction agreed in 2026-05-09 session. User confirmation, end goal, AI roles, ChatGPT supervisory workflow, parallel sprint rules, stream notes, LLM design refinement required. Required reading for Phase 4, AI strategy, and sprint driving. |
| `15-ai-modules-and-state-management-architecture-20260509.md` | Detailed AI module, embedding retrieval, agent role, source generation, Format Factory State Manager, community component, and no-drift architecture direction. Required reading for LLM/embedding work, state management work, no-drift work, agent workflow design, Phase 4 source generation, playbook replay, and review queue design. |

## Local Methodology Entry Points (added linkage sprint 2026-05-08)

These files provide the local bridge for fresh-chat continuity. Future agents should start
from the methodology index before generating plans or prompts.

| File | Purpose |
|------|---------|
| [docs/agent-methodology-index.md](../docs/agent-methodology-index.md) | Start here for all plan and prompt work. Links all methodology docs, templates, commands, and enforcement rules. |
| [docs/prompts/README.md](../docs/prompts/README.md) | Index of all 8 prompt templates. Rules for using templates. |
| [.claude/commands/_readme.md](../.claude/commands/_readme.md) | Command registry. Lists all active methodology commands (/plan-hardening, /execution-handoff, /evidence-review-next-prompt, /memory-sprint). |

## Priority reading for a new agent

A new agent should read in this order:

```text
plans/master-plan.md
AGENTS.md
GOVERNANCE.md
docs/agent-methodology-index.md
memory/00-index.md
memory/12-planning-and-agent-handoff-methodology.md
memory/09-current-state-before-phase1.md
docs/fresh-chat-continuity-brief.md
```

Then it should read only the memory files relevant to the task.

### Additional priority files by task type

| Task type | Additional required reading |
|-----------|----------------------------|
| AI/LLM/embedding strategy | memory/13-chatgpt-initial-project-analysis-20260509.md, memory/14-ai-supervision-and-three-pilot-direction-20260509.md, memory/11-format-understanding-and-llm-strategy.md |
| State management and no-drift work | memory/15-ai-modules-and-state-management-architecture-20260509.md, memory/12-planning-and-agent-handoff-methodology.md, docs/current-state-and-evidence-authority.md |
| Agent workflow design | memory/15-ai-modules-and-state-management-architecture-20260509.md, memory/12-planning-and-agent-handoff-methodology.md, docs/agent-execution-handoff-standard.md |
| Playbook replay and review queue design | memory/15-ai-modules-and-state-management-architecture-20260509.md, docs/playbook-layer.md, memory/14-ai-supervision-and-three-pilot-direction-20260509.md |
| Phase 4 product source planning | memory/13-chatgpt-initial-project-analysis-20260509.md, memory/14-ai-supervision-and-three-pilot-direction-20260509.md |
| Phase 4 source generation | memory/15-ai-modules-and-state-management-architecture-20260509.md, memory/11-format-understanding-and-llm-strategy.md, docs/format-understanding-layer.md |
| Three-pilot proof planning | memory/14-ai-supervision-and-three-pilot-direction-20260509.md |
| Sprint evidence review and next-prompt generation | memory/14-ai-supervision-and-three-pilot-direction-20260509.md, memory/12-planning-and-agent-handoff-methodology.md |

## Memory stream update history

| Run | Stream | Files updated |
|-----|--------|---------------|
| run019 | Main execution | 00-index.md, 04-phase0-evolution-and-bundle-reviews.md, 05-decision-register-expanded.md, 06-gap-risk-and-healing-history.md, 09-current-state-before-phase1.md, 10-memory-maintenance-protocol.md (run018 committed 0c97256; TC-0007 tooling implemented; TC-0009 Gate 2 evidence draft; master-plan v2.15) |
| run017 | Main execution | 00-index.md, 04-phase0-evolution-and-bundle-reviews.md, 05-decision-register-expanded.md, 06-gap-risk-and-healing-history.md, 09-current-state-before-phase1.md, 10-memory-maintenance-protocol.md (Gate 1 approval by Babar Raza; Phase 2 started; acquisition-packs/fods/ skeleton; TC-0009 created; master-plan.md v2.13) |
| run016 | Main execution | 02-standing-operating-rules.md, 07-agent-governance-model.md, 09-current-state-before-phase1.md, 10-memory-maintenance-protocol.md, 11-prompting-and-agent-style-rules.md (DEC-034 governance rule; AGENTS.md Section V; run016 verification sprint recorded) |
| run014 | Main execution | 00-index.md, 04-phase0-evolution-and-bundle-reviews.md, 09-current-state-before-phase1.md (run014 closure-readiness sprint recorded; master-plan.md v2.10; stale file-count and bundle references fixed) |
| run013 | Main execution | 00-index.md, 03-architecture-and-product-tracks.md, 04-phase0-evolution-and-bundle-reviews.md, 05-decision-register-expanded.md, 06-gap-risk-and-healing-history.md, 07-agent-governance-model.md, 09-current-state-before-phase1.md, 10-memory-maintenance-protocol.md (stale pending-propagation notes removed; run011/run013 status recorded) |
| run012 | Memory stream | 00-index.md, 03-architecture-and-product-tracks.md, 04-phase0-evolution-and-bundle-reviews.md, 05-decision-register-expanded.md, 06-gap-risk-and-healing-history.md, 07-agent-governance-model.md, 08-specification-cache-amendment.md, 09-current-state-before-phase1.md, 10-memory-maintenance-protocol.md |
| memory-sprint-2026-05-08 | Memory sprint | 00-index.md, 11-format-understanding-and-llm-strategy.md (NEW), AGENTS.md Sections AB+AC, GOVERNANCE.md Sections 21+22, docs/format-understanding-layer.md (NEW), docs/llm-and-embedding-strategy.md (NEW), docs/format-representation-model.md (NEW), docs/non-aspose-format-candidate-registry-plan.md (NEW), plans/master-plan.md Section 37 (NEW), ROADMAP.md Architecture Backlog (NEW), taskcards/FUL-001--FUL-004 (NEW), taskcards/LLM-001 (NEW), taskcards/EMB-001 (NEW), taskcards/REP-001 (NEW), taskcards/REP-003 (NEW), taskcards/NAC-001 (NEW), taskcards/GOV-001 (NEW) |
| memory-planning-methodology-2026-05-08 | Memory methodology sprint | 00-index.md (UPDATED), 12-planning-and-agent-handoff-methodology.md (NEW), docs/planning-methodology.md (NEW), docs/agent-execution-handoff-standard.md (NEW), docs/plan-hardening-checklist.md (NEW), docs/fresh-chat-continuity-brief.md (NEW), docs/prompts/ (8 templates NEW), AGENTS.md Section AD (NEW), GOVERNANCE.md Section 23 (NEW), taskcards/GOV-002 (NEW), .claude/commands/ (4 files NEW) |
| memory-methodology-linkage-2026-05-08 | Memory methodology linkage sprint | 00-index.md (UPDATED), 12-planning-and-agent-handoff-methodology.md (UPDATED), docs/agent-methodology-index.md (NEW), docs/prompts/README.md (NEW), README.md (UPDATED -- agent methodology section), .claude/commands/_readme.md (UPDATED -- methodology commands table), AGENTS.md AD0/AD8-AD10 (ADDED), GOVERNANCE.md Section 23.0/23.7-23.8/24 (ADDED), tools/governance/check_methodology_links.py (NEW), tests/governance/test_methodology_links.py (NEW), taskcards/GOV-003 (NEW) |
| memory-ai-direction-sync-2026-05-09 | ChatGPT AI supervision and sprint rules memory sync | 00-index.md (UPDATED -- new file rows, priority tables, stream history), 10-memory-maintenance-protocol.md (UPDATED -- 2026-05-09 entry), 11-format-understanding-and-llm-strategy.md (UPDATED -- AI direction refinement section), 12-planning-and-agent-handoff-methodology.md (UPDATED -- ChatGPT supervision rules, parallel sprint handling), 13-chatgpt-initial-project-analysis-20260509.md (NEW), 14-ai-supervision-and-three-pilot-direction-20260509.md (NEW), docs/fresh-chat-continuity-brief.md (UPDATED -- 2026-05-09 section), docs/agent-methodology-index.md (UPDATED -- new memory context refs), docs/prompts/README.md (UPDATED -- ChatGPT prompt note), ROADMAP.md (UPDATED -- 2026-05-09 AI direction note), taskcards/GOV-004 (NEW), tools/evidence/contracts/memory-ai-direction-sync-20260509.yaml (NEW) |
| memory-ai-state-management-sync-2026-05-09 | AI module and state-management architecture memory sync | 15-ai-modules-and-state-management-architecture-20260509.md (NEW), 00-index.md (UPDATED), 10-memory-maintenance-protocol.md (UPDATED), 11-format-understanding-and-llm-strategy.md (UPDATED), 12-planning-and-agent-handoff-methodology.md (UPDATED), 14-ai-supervision-and-three-pilot-direction-20260509.md (UPDATED), docs/fresh-chat-continuity-brief.md (UPDATED), docs/agent-methodology-index.md (UPDATED), docs/prompts/README.md (UPDATED), docs/llm-and-embedding-strategy.md (UPDATED), ROADMAP.md (UPDATED), taskcards/GOV-005 (NEW), tools/evidence/contracts/memory-ai-state-management-sync-20260509.yaml (NEW). No LLM modules, embeddings, vector DB, state manager code, orchestration components, product source, gate changes, playbook replay, or push. |
| run010 | Memory stream | Memory integration prompted by addition of /memory folder; AGENTS.md Section U added in run010 repo execution (not a /memory file edit â€” see run010 bundle) |

## Warning

Never act from this memory package alone. Always cross-check the actual repo state and the current master plan.

The source layout (`src/net/{format}`, `src/python/{format}`) was propagated to `plans/master-plan.md` v2.8 in run011 and verified in run013. Stale "pending propagation" notes have been removed. However, **no `src/` folders may be created in Phase 0** â€” source folder creation requires a Phase 4+ prompt with Gate 9 passed.
