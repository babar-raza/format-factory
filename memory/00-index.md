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

# 00 — Memory Index

## Purpose

This index helps an agent understand the complete picture without reading a single huge transcript.

The memory package captures:

- the origin of the project
- the user’s standing governance rules
- the architecture decisions
- the reason for each Phase 0 hardening run
- the evidence-bundle review pattern
- the current state before Phase 1
- future memory synchronization rules

## Files

| File | Purpose |
|---|---|
| `01-project-origin-and-intent.md` | Why the project exists and what “file format hacking” means here. |
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

## Priority reading for a new agent

A new agent should read in this order:

```text
plans/master-plan.md
AGENTS.md
GOVERNANCE.md
memory/README.md
memory/00-index.md
memory/09-current-state-before-phase1.md
memory/02-standing-operating-rules.md
memory/04-phase0-evolution-and-bundle-reviews.md
```

Then it should read only the memory files relevant to the task.

## Memory stream update history

| Run | Stream | Files updated |
|-----|--------|---------------|
| run017 | Main execution | 00-index.md, 04-phase0-evolution-and-bundle-reviews.md, 05-decision-register-expanded.md, 06-gap-risk-and-healing-history.md, 09-current-state-before-phase1.md, 10-memory-maintenance-protocol.md (Gate 1 approval by Babar Raza; Phase 2 started; acquisition-packs/fods/ skeleton; TC-0009 created; master-plan.md v2.13) |
| run016 | Main execution | 02-standing-operating-rules.md, 07-agent-governance-model.md, 09-current-state-before-phase1.md, 10-memory-maintenance-protocol.md, 11-prompting-and-agent-style-rules.md (DEC-034 governance rule; AGENTS.md Section V; run016 verification sprint recorded) |
| run014 | Main execution | 00-index.md, 04-phase0-evolution-and-bundle-reviews.md, 09-current-state-before-phase1.md (run014 closure-readiness sprint recorded; master-plan.md v2.10; stale file-count and bundle references fixed) |
| run013 | Main execution | 00-index.md, 03-architecture-and-product-tracks.md, 04-phase0-evolution-and-bundle-reviews.md, 05-decision-register-expanded.md, 06-gap-risk-and-healing-history.md, 07-agent-governance-model.md, 09-current-state-before-phase1.md, 10-memory-maintenance-protocol.md (stale pending-propagation notes removed; run011/run013 status recorded) |
| run012 | Memory stream | 00-index.md, 03-architecture-and-product-tracks.md, 04-phase0-evolution-and-bundle-reviews.md, 05-decision-register-expanded.md, 06-gap-risk-and-healing-history.md, 07-agent-governance-model.md, 08-specification-cache-amendment.md, 09-current-state-before-phase1.md, 10-memory-maintenance-protocol.md |
| run010 | Memory stream | Memory integration prompted by addition of /memory folder; AGENTS.md Section U added in run010 repo execution (not a /memory file edit — see run010 bundle) |

## Warning

Never act from this memory package alone. Always cross-check the actual repo state and the current master plan.

The source layout (`src/net/{format}`, `src/python/{format}`) was propagated to `plans/master-plan.md` v2.8 in run011 and verified in run013. Stale "pending propagation" notes have been removed. However, **no `src/` folders may be created in Phase 0** — source folder creation requires a Phase 4+ prompt with Gate 9 passed.
