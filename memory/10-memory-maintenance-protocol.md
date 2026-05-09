---
memory_package: format-factory-chat-memory
version: 1.0
created_at: 2026-05-03
intended_location: /memory
source: ChatGPT conversation memory plus inspected Phase 0 evidence bundles through run013
visibility: internal
publish_allowed: false
notes: Place this folder at repo root as /memory. These files are for agent context and must not supersede plans/master-plan.md.
---

# 10 — Memory Maintenance Protocol

## Purpose

The `/memory` folder exists so agents can understand the history and rationale that is not fully visible from current source files alone.

This is especially important because the plan evolved through multiple review/healing loops.

## Authority hierarchy

| Priority | Source |
|---|---|
| 1 | `plans/master-plan.md` |
| 2 | `AGENTS.md` and `GOVERNANCE.md` |
| 3 | current repo files and taskcards |
| 4 | evidence bundles |
| 5 | `/memory` context files |

If `/memory` conflicts with the master plan, the agent must log a gap and not silently choose either side.

## When to update memory

Update `/memory` after:

- phase acceptance
- gate transition
- major decision
- major gap discovery
- major healing run
- architecture amendment
- product track change
- new prompt policy
- specification cache policy change
- release control change

## How to update memory

1. Preserve chronology.
2. Add dates/run IDs when known.
3. Record the reason behind decisions, not only the final result.
4. Keep current state in `09-current-state-before-phase1.md` or its future equivalent.
5. Do not erase historical mistakes; summarize them as resolved healing records.
6. Do not include secrets, private keys, API tokens, or raw prompt/response caches.
7. Do not paste large copyrighted specification text into memory.
8. Keep memory as internal documentation.

## Suggested future memory versions

When more work occurs, create a new package or update files with version numbers:

```text
memory-package-v1-phase0.md files
memory-package-v2-phase1a.md files
memory-package-v3-gate1.md files
```

Do not rely on memory from ChatGPT alone. The agent should maintain local memory from repo artifacts and evidence bundles.

## Agent maintenance task

**COMPLETED run010.** `AGENTS.md` was updated in run010 with Section U (Memory Usage and Maintenance):

- U2: Agents must read relevant `/memory` files before complex work, phase transitions, governance changes.
- U3: Minimal required files for general work (README, 00-index, 02-standing-operating-rules, 09-current-state).
- U4: Task-type table for additional files.
- U5: Contradiction rule — log gap, do not silently override.
- U6: Maintenance triggers — update after major events.
- U7: Content restrictions — no secrets, no raw prompts, no copyrighted spec text.
- U8: Evidence bundle rule for memory changes.
- U9: TC-0008 placeholder for future /sync-memory command.

This task is complete. The memory package is now formally integrated into the agent operating contract.

## ChatGPT supervisory analysis and sprint-driving rules (added 2026-05-09)

When ChatGPT provides architectural direction, sprint supervision rule changes, or active-stream
conclusions, the memory package must be updated with a dedicated memory sprint.

The update must:
- Record ChatGPT analysis in a separate named memory file (do not embed in 00-index directly).
- Record user decisions and confirmed directions in a separate named memory file.
- Update 00-index and 10 (this file) with dated entries.
- Update 11 and 12 if LLM strategy or planning methodology changed.
- Update discoverability docs (fresh-chat-continuity-brief, agent-methodology-index).

Memory files must distinguish between:
1. **Verified repo state** -- from actual file inspection and evidence bundles.
2. **ChatGPT analysis** -- reasoning and assessment from the AI supervision session.
3. **User decisions** -- confirmed by the user in the supervision session.
4. **Recommended next prompt** -- what ChatGPT recommends the next sprint should be.
5. **Pending execution** -- work recommended but not yet performed.

These must never be mixed. A ChatGPT recommendation is not the same as a completed sprint.

## Stream separation and reconciliation (added run012)

When a main execution stream run and a memory stream run are concurrent:

1. The memory stream run must not modify any file that the main execution stream owns unless explicitly required.
2. Any pending propagation captured in memory must be labeled "pending-propagation" with the specific master-plan section it must target.
3. A reconciliation main execution run (e.g., run011) must occur before Phase 1 to push all pending-propagation items into `plans/master-plan.md`.

**Pending propagation as of run012 — RESOLVED run013:**

| Item | Captured in | Propagated to | By |
|------|------------|----------------------|----|
| `src/net/{format}` layout | `memory/03`, `memory/09` | `plans/master-plan.md` v2.8 product source layout section | run011 ✅ |
| `src/python/{format}` layout | `memory/03`, `memory/09` | `plans/master-plan.md` v2.8 product source layout section | run011 ✅ |
| .NET FOSS packaging question | `memory/03` | `plans/master-plan.md` as DEC-033 (deferred, must resolve before Gate 10 .NET release) | run011 ✅ |

All pending propagation items from run012 are resolved. run013 verified the propagation and cleaned stale notes from `/memory` files. Agents may now read the source layout from `plans/master-plan.md` directly.

**run016 memory update:** Memory files 02, 07, 09, 10, 11 updated. Trigger: governance change (DEC-034 added — independent verification before human review). Changes: new governance rule, DEC-034 reference, run016 run history entry, verification sprint pattern documented.

**run017 memory update:** Memory files 00-index, 04, 05, 06, 09, 10 updated. Trigger: gate transition (Gate 1 approved by Babar Raza, 2026-05-04) + phase start (Phase 2 active). Changes: run017 run history entries, DEC-042/DEC-043 added to decision register, G-001/G-002 marked resolved, G-HEAL-016/G-HEAL-017 added, 09-current-state fully rewritten to reflect Phase 2 active and acquisition-packs/fods/ existence.

**run019 memory update:** Memory files 00-index, 04, 09, 10 updated. Trigger: infrastructure taskcard completion (TC-0007) + Gate 2 evidence draft (TC-0009). Changes: run018/run019 run history entries; 09-current-state updated with Gate 2 draft status, TC-0007 status, new commits, next actions; 04-phase0-evolution updated with run018/run019 status.

**run027 memory update:** External MEMORY.md updated. Trigger: gate status change (Gate 3 → sample_corpus_verified_pending_human_review) + architecture change (Hybrid Spec Retrieval Strategy). Changes: Phase 3 State section updated; TC-0015/TC-0016 added; run027 commit noted.

**run028 memory update:** Memory files 03, 05, 09, 10 updated (+ external MEMORY.md). Trigger: gate transition (Gate 3 PASSED by Babar Raza, 2026-05-05) + major planning milestone (Gate 4 planning package created). Changes: 03 — Hybrid Spec Retrieval Strategy section added; 05 — decisions D-046 through D-049 added (Gate 2 PASSED, Gate 3 PASSED, Hybrid Retrieval, Gate 4 planning); 09 — complete rewrite to current state (run028); 10 — this entry.

**run029 memory update:** Memory files 05, 09, 10 updated (+ external MEMORY.md). Trigger: gate milestone (Gate 4 prototype created 4/4 PASS). Changes: 05 — D-050 added (Gate 4 prototype created and validated); 09 — TC-0014/TC-0017/TC-0018 statuses updated; TC-0019 row added; Prototypes row updated; latest commit updated to 5c93b88; run history rows for run028/run029 added; evidence bundle entry for run029 added; 10 — this entry.

**run030 memory update:** Memory files 09, 10 updated (+ external MEMORY.md). Trigger: gate milestone (TC-0018 DEC-034 verification PASS) + architecture change (Spec Workbench v1 created). Changes: 09 — latest commit updated to ea20cde; Uncommitted → run030; Gate 4 status → prototype_verified_pending_human_review; TC-0017 completed; TC-0018 verification_passed; TC-0020/TC-0021 rows added; master-plan version → 2.26; Next required actions updated; 10 — this entry; external MEMORY.md — run030 added to run history, Phase 3 State updated, Gate 4 status updated, TC-0020/TC-0021 added, Spec Workbench artifacts noted.

**memory-ai-direction-sync-2026-05-09 memory update:** Memory files 00, 10, 11, 12 updated; memory files 13 and 14 created. Trigger: ChatGPT supervisory analysis of run050 and S-F2F-02B bundles; AI direction decisions captured. Changes: 00-index -- new file rows, priority tables by task type, stream history entry; 10 -- this entry; 11 -- AI direction refinement section added; 12 -- ChatGPT supervision rules and parallel sprint handling added; 13 (NEW) -- ChatGPT initial project analysis from 2026-05-09 conversation; 14 (NEW) -- AI supervision rules and three-pilot direction. No gate status changes. No product source. No LLM calls. No embeddings. No playbook replay. No push.
