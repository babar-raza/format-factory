---
memory_package: format-factory-chat-memory
version: 1.0
created_at: 2026-05-03
intended_location: /memory
source: ChatGPT conversation memory plus inspected Phase 0 evidence bundles through run008
visibility: internal
publish_allowed: false
notes: Place this folder at repo root as /memory. These files are for agent context and must not supersede plans/master-plan.md.
---

# Agent Prompt — Integrate `/memory` into AGENTS.md

Use this prompt after extracting the memory package into the repository root as `/memory`.

```text
MODE:
PLAN MODE ONLY.

Project:
format-factory

Repo path:
C:\Users\prora\OneDrive\Documents\GitHub\format-factory

Task:
Plan how to amend AGENTS.md so agents consistently use and maintain the new /memory folder.

Important:
This is plan mode only. Do not edit files. Do not create bundles. Do not commit. Do not proceed to Phase 1. Do not score FODS. Do not create acquisition packs, samples, schemas, prototypes, product source, CI workflows, reports, or commercial folders.

Context:
The human has extracted a new /memory folder into the repo root. The /memory folder contains Markdown files generated from the ChatGPT conversation. These files preserve project history, decision rationale, phase evolution, bundle review lessons, current state, and future memory-maintenance protocol.

Authority rule:
plans/master-plan.md remains the single operational authority. /memory is context and rationale. If /memory conflicts with plans/master-plan.md, the agent must log a gap and treat the master plan as the operational authority until the contradiction is resolved.

Read first:
1. plans/master-plan.md
2. AGENTS.md
3. GOVERNANCE.md
4. memory/README.md
5. memory/00-index.md
6. memory/02-standing-operating-rules.md
7. memory/09-current-state-before-phase1.md
8. memory/10-memory-maintenance-protocol.md

Your task:
Produce a plan for amending AGENTS.md so it includes a Memory Usage and Maintenance section.

The plan must specify exact AGENTS.md changes, but do not apply them.

Required AGENTS.md additions:

1. Memory folder purpose
   - /memory contains historical context, rationale, project evolution, and ChatGPT conversation memory.
   - /memory does not supersede plans/master-plan.md.

2. When agents must read memory
   - before complex planning
   - before Phase transitions
   - before changing governance files
   - before changing master plan
   - before resolving contradictions
   - before starting a new long-running task from old context

3. Minimal required memory files for general work
   - memory/README.md
   - memory/00-index.md
   - memory/02-standing-operating-rules.md
   - memory/09-current-state-before-phase1.md

4. Additional memory files by task type
   - architecture work: memory/03-architecture-and-product-tracks.md
   - governance work: memory/07-agent-governance-model.md
   - spec cache work: memory/08-specification-cache-amendment.md
   - Phase 0 review: memory/04-phase0-evolution-and-bundle-reviews.md
   - prompt writing: memory/11-prompting-and-agent-style-rules.md
   - gap/risk review: memory/06-gap-risk-and-healing-history.md

5. Memory contradiction rule
   - if /memory conflicts with master plan, AGENTS.md, GOVERNANCE.md, or current repo state, log a gap.
   - do not silently update files based only on memory.
   - ask for a correction plan or create a plan-mode proposal.

6. Memory maintenance rule
   - after major plan evolution, phase acceptance, gate transition, major decision, or healing run, update /memory or create a taskcard to update it.
   - do not store secrets, raw LLM prompts, raw LLM responses, or copyrighted spec excerpts in /memory.

7. Evidence bundle rule
   - if memory is changed in execution mode, include changed memory files in the evidence/source bundle.
   - include a memory-sync-report.md in bundle metadata.

8. Agent self-challenge additions
   - Did I read the relevant memory files?
   - Did I treat memory as context, not authority?
   - Did I log contradictions between memory and master plan?
   - Did I update memory or create a memory-update taskcard when required?

9. Future command suggestion
   - propose a future /sync-memory command or taskcard, but do not implement it.

Required output:
1. Verdict on whether AGENTS.md needs amendment.
2. Exact proposed section heading and placement in AGENTS.md.
3. Proposed text to add to AGENTS.md.
4. Any related changes needed in GOVERNANCE.md or plans/master-plan.md.
5. Gap log entries if memory integration creates unresolved gaps.
6. Risk review.
7. Fix This Plan Before Execution section.
8. Final recommendation:
   READY_FOR_MEMORY_INTEGRATION_EXECUTION
   or
   NEEDS_MORE_PLAN_HARDENING

Plan mode rules:
Do not edit any repo file. Do not create evidence bundle. Do not commit.
```
