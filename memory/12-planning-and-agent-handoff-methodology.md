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

- Planning methodology: docs/planning-methodology.md
- Execution handoff standard: docs/agent-execution-handoff-standard.md
- Plan hardening checklist: docs/plan-hardening-checklist.md
- Fresh-chat continuity brief: docs/fresh-chat-continuity-brief.md
- Prompt templates: docs/prompts/ (8 templates)
- Commands: .claude/commands/ (plan-hardening.md, execution-handoff.md, evidence-review-next-prompt.md, memory-sprint.md)
