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

# 07 — Agent Governance Model

## Actors

| Actor | Role |
|---|---|
| Human | Project owner, mediator, approval authority |
| ChatGPT | Strategic reviewer, prompt author, bundle inspector, memory sync source |
| Claude in VS Code | Primary repo execution agent |
| Codex | Optional reviewer or implementation agent |
| Local LLMs | Future privacy-sensitive or batch helper |
| `llm.professionalize.com` | Future remote endpoint for selected tasks |

## Governance files

| File | Role |
|---|---|
| `plans/master-plan.md` | Single operational authority |
| `AGENTS.md` | Agent operating contract |
| `GOVERNANCE.md` | Human/release/legal governance |
| `docs/gates.md` | Gate requirements |
| `docs/governance/release-control.md` | Visibility and release policy |
| `docs/python-foss/specification-cache.md` | Spec-cache policy |
| `memory/` | Historical context and rationale |

## Agent startup checklist

Every agent should:

1. read `plans/master-plan.md`
2. read `AGENTS.md`
3. read `GOVERNANCE.md`
4. identify current phase
5. inspect git status
6. inspect forbidden paths
7. check whether artifacts already exist
8. read relevant memory files
9. confirm taskcard scope
10. perform work only within allowed phase

## Evidence bundle protocol

Every execution run must create a clean zip with:

- relevant repo files under `repo/`
- audit files under `bundle-metadata/`
- no `.git/`
- no raw `.local/`
- no `.env`
- no `ocal/`
- no secrets
- no LLM prompts/responses

The final line must be:

```text
EVIDENCE_BUNDLE: <absolute Windows path>
```

## Agent self-challenge

Before final output, agents must answer:

1. Did I accidentally perform later-phase work?
2. Did I create forbidden paths?
3. Did I mark something complete without human approval?
4. Did I leave contradictions?
5. Did I create or expose secrets?
6. Did I update master plan/gap register as required?
7. Did I create a clean bundle?
8. Did I avoid committing?

## Commands and skills

Phase 0 created `.claude/commands/_readme.md` only.

Planned Phase 1 commands include:

- `/score-format`
- `/create-taskcard`
- `/check-gate`
- `/create-acquisition-pack`
- `/reproduce-master-plan`
- `/build-evidence-bundle`
- `/check-release-boundary`

Commands and skills must be versioned and logged.

## Memory integration

Agents should use `/memory` to understand the history and rationale, but must not treat memory files as more authoritative than the master plan.

If `/memory` conflicts with `plans/master-plan.md`, log a gap and ask for guidance or prepare a correction plan.

For the full memory usage rules, see `AGENTS.md` Section U (Memory Usage and Maintenance).

## Run stream model

Phase 0 has used two concurrent stream types:

**Main execution stream** (run001–run009, run011, run013):

- Modifies governance files, taskcards, master plan.
- Produces repo-changing artifacts.
- Must produce an evidence bundle.
- run011 propagated the format-first source layout to master-plan.md v2.8.
- run013 verified propagation, cleaned stale memory notes, added repeatability section to llm-endpoint-strategy.md.

**Memory stream** (run010, run012):

- Modifies only `/memory` files.
- Does not modify governance files unless explicitly required.
- Captures history, decisions, and expectations for agent context.
- Must not override or supersede anything in the main execution stream.
- Produces an evidence bundle (memory-only scope).

**Reconciliation rule:** When a main execution run and a memory stream run are concurrent (as with run009 + run010), a follow-up main execution run (run011) must reconcile any pending propagation items before Phase 1 begins.

**Reconciliation status (run013):** All pending propagation items from run012 have been resolved. The product source layout (`src/net/{format}`, `src/python/{format}`) is now in `plans/master-plan.md` v2.8+. Stale "pending propagation" notes removed from all `/memory` files.

## Authority hierarchy (confirmed run010)

| Priority | Source | Role |
|----------|--------|------|
| 1 | `plans/master-plan.md` | Single operational authority |
| 2 | `AGENTS.md`, `GOVERNANCE.md` | Agent and human operating contracts |
| 3 | Repo files, taskcards | Implementation artifacts |
| 4 | Evidence bundles | Audit trail |
| 5 | `/memory` | Historical context and rationale only |

## DEC-034: Independent verification before human review (run016)

Recorded as DEC-034 in `plans/master-plan.md`. Any agent-produced request for human review must first pass an independent agent verification sprint in a separate execution session. See AGENTS.md Section V for the full rule. GOVERNANCE.md Section 15 covers the human-side governance of this requirement.
