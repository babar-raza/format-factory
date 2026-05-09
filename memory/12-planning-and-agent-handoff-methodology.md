---
memory_package: format-factory-chat-memory
version: 1.0
created_at: 2026-05-08
intended_location: /memory
source: Memory sprint -- planning methodology and agent handoff (2026-05-08)
visibility: internal
publish_allowed: false
notes: These are user preferences and planning standards recorded from the working session. Must not supersede plans/master-plan.md for operational state.
---

# 12 -- Planning and Agent Handoff Methodology

## User Preferences for Prompts and Plans

1. **Detailed and systematic.** Prompts must be detailed, systematic, and LLM-consumable. Each step must be an atomic, executable instruction.

2. **Challenge plans before execution.** Every plan must be challenged and normalized before execution. The plan hardening checklist (docs/plan-hardening-checklist.md) must pass.

3. **Single-go execution when requested.** When the user asks for a single-go execution prompt, the agent must produce one complete prompt that the agent can self-manage end-to-end with internal gates. No manual slice-by-slice copy-pasting.

4. **No manual steps where agent can act.** The agent must perform all feasible steps itself. Do not use placeholders like "(human to do this part)" for work the agent can do.

5. **Evidence bundles with exact final path.** Every evidence-producing sprint must end with: EVIDENCE_BUNDLE: <absolute Windows path to zip>. This is required, not optional.

6. **Inspect files before acting.** Every referenced file or evidence artifact must be read before new work is produced. Do not trust summaries alone.

7. **All discovered gaps captured.** Any missing architecture or structural gap must be captured in backlog, memory, taskcards, and roadmap. It must not remain only in chat.

8. **No em dash.** The user has a broad style preference against em dashes. Use commas, colons, semicolons, or periods instead in all docs and prompts.

9. **Local continuity.** A fresh chat session must be able to continue work by reading local repo files. No hidden context. No reliance on conversation history.

10. **Local reusable templates.** Prompt templates and methodology docs are stored locally in docs/prompts/ and docs/. These are the source of truth for future session prompts.

11. **Current-state verification before decisions.** Before any planning or execution, the agent must read current repo files, run the consistency checker, and verify git status.

12. **Source of truth from repo and evidence.** Agent summaries are challenged against actual file content. An evidence bundle is not a replacement for reading the files.

13. **No broad cleanup or stash.** git stash -u, git reset --hard, and git clean -fd are not used as default behavior. If cleanup is needed, scope it exactly.

14. **Preserve gates, evidence, and taskcards.** These are not waste. They are the quality foundation.

15. **Tangible outputs for product sprints.** When the sprint scope is product progress (gate work), the primary output must be product artifacts, not only meta-work.

16. **No push unless explicitly authorized.** Every session defaults to no push, even after a commit.

## Planning Style Summary

- PLAN MODE prompts: challenge, harden, do not execute. Final line: NEXT_PROMPT_READY: yes.
- EXECUTION MODE prompts: execute, validate, bundle, commit. Final line: EVIDENCE_BUNDLE: <path>.
- MEMORY SPRINT prompts: capture decisions, update memory and governance, bundle. No gate changes.
- INDEPENDENT VERIFICATION prompts: verify prior sprint claims, DEC-034. Do not re-execute.
- CLOSURE HYGIENE prompts: normalize contracts, no new scope.

## Prompt Evolution Pattern

1. Human provides a goal or plan draft.
2. Agent reads all referenced files and current repo state.
3. Agent hardens the plan using docs/plan-hardening-checklist.md.
4. Human approves or revises the hardened plan.
5. Agent converts the plan to a single-go execution handoff.
6. Agent executes, validates, and builds evidence bundle.
7. Human inspects bundle. Agent provides next prompt only after inspection.
8. Cycle repeats.

## Key Doc Paths

- Methodology entry point: docs/agent-methodology-index.md (START HERE for plan and prompt work)
- Planning methodology: docs/planning-methodology.md
- Execution handoff standard: docs/agent-execution-handoff-standard.md
- Plan hardening checklist: docs/plan-hardening-checklist.md
- Fresh-chat continuity brief: docs/fresh-chat-continuity-brief.md
- Prompt template index: docs/prompts/README.md
- Prompt templates: docs/prompts/ (8 templates)
- Commands: .claude/commands/ (plan-hardening.md, execution-handoff.md, evidence-review-next-prompt.md, memory-sprint.md)
- Command registry: .claude/commands/_readme.md
- Methodology link checker: tools/governance/check_methodology_links.py

## Local Bridge for Fresh-Chat Continuity

These three files are the local bridge for a fresh chat session to find all methodology tools
without needing conversation history:

1. docs/agent-methodology-index.md -- links everything (entry point)
2. docs/prompts/README.md -- template selection guide
3. .claude/commands/_readme.md -- active command registry

A future agent starting fresh should read docs/agent-methodology-index.md first,
then follow the links to the relevant docs, templates, and commands for the current task.

## ChatGPT Supervision Rules (added 2026-05-09)

ChatGPT serves as the external supervisor for this project. These rules govern how ChatGPT-driven
sprints must be handled by agents in VS Code.

### ChatGPT supervisory workflow

For every sprint, ChatGPT will:

1. Inspect the provided evidence bundle first.
2. Challenge the prior agent summary.
3. Reconstruct actual state from files and reports.
4. Identify contradictions, stale state, and missing proof.
5. Decide whether the sprint needs closure, repair, verification, or next-scope execution.
6. Produce a detailed, comprehensive, exact prompt for the VS Code agent.
7. Require the agent to produce a new evidence bundle.
8. Use that evidence bundle to plan the next step.

### Sprint prompt requirements

Every sprint prompt from ChatGPT must tell agents exactly:

- What files to read before acting.
- What to verify (expected output, hashes, counts, statuses).
- What to fix (exact file paths, exact change descriptions).
- What not to touch (forbidden files and patterns).
- What evidence to produce (metadata files, minimum counts, contract path).
- How to report completion (exact final response format).

Agents must not shorten, reinterpret, or skip these requirements.
Agents must not convert execution prompts into informal plans unless the prompt says PLAN MODE.

### Parallel sprint handling

The user may run multiple sprints in parallel when they are independent streams.

For each active stream, agents must classify the stream before staging any files:

- MAIN_SPRINT_OWNED
- SECONDARY_SPRINT_OWNED
- MEMORY_SPRINT_OWNED
- UNKNOWN_REQUIRES_STOP

If multiple active streams touch shared authority files (master-plan, registry, AGENTS.md,
GOVERNANCE.md, memory/, evidence contracts, or taskcards), a reconciliation sprint is required
before major new scope.

### Agents must inspect evidence bundles before advancing

An agent summary is not sufficient authorization to start the next sprint. The human or ChatGPT
must inspect the actual bundle contents and challenge the summary against real file state.

Agents must produce `EVIDENCE_BUNDLE: <absolute Windows path>` as the final line of every
execution sprint.

### Prompts are requested only when needed, but must be comprehensive when given

The user does not need constant prompt suggestions. Prompts are generated only when requested.
But once requested, the prompt must be comprehensive, execution-ready, and fully specific.
It must not rely on agent in-context memory or prior chat history.

## State-Aware Agent Handoff Rules (added 2026-05-09)

Future prompts for AI, embedding, state-management, orchestration, no-drift, playbook replay,
review queue, and Phase 4 source generation work must read
`memory/15-ai-modules-and-state-management-architecture-20260509.md`.

When Format Factory State Manager outputs exist, agents must use them during preflight and
closeout. Until then, agents must continue reconstructing state from the registry, master plan,
taskcards, FUL files, evidence bundles, tests, and current-state consistency checks.

Future execution prompts should include:

- state preflight from authority files
- dirty-file stream classification before staging
- explicit design-versus-implementation distinction
- no-drift closeout after edits
- evidence state summary in bundle metadata
- current-state consistency confirmation
- claim linting for stale or unsupported status claims

Agent state should be checkpointed through approved systems such as LangGraph when implemented and
authorized. Checkpointing must support bounded sprint prompts, human-in-the-loop stops, repair loops,
review queues, files-read records, blocked-item records, and evidence bundle references.

Sprint closeout must include evidence state and current-state consistency: bundle path, validation
result, command outputs, fingerprints when available, final verdict, changed file list, and
confirmation that registry and master-plan claims still align with actual repo state.
