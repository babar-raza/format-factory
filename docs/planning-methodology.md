# Planning Methodology

**Document type:** Local Planning and Execution Standard
**Created:** 2026-05-08 (memory-planning-methodology-and-agent-handoff sprint)
**Visibility:** internal
**Authority:** This document is the local standard for creating, reviewing, hardening, and executing plans through agents in the format-factory repo. It supplements AGENTS.md and GOVERNANCE.md.

---

## 1. Purpose

This document captures the repo-local standard for:

- writing plans that agents can execute without hidden context.
- challenging and hardening weak plans before execution.
- converting prose plans into execution-ready agent prompts.
- creating single-go autonomous handoffs with internal gates.
- separating sprint streams (MAIN, SECONDARY, MEMORY, CLOSURE).
- preserving discovered architectural gaps in durable local artifacts.
- enabling fresh-chat continuity without relying on conversation history.

---

## 2. Core Principles

1. Evidence, gates, taskcards, and status repair are necessary infrastructure, not waste. They are the foundation of trustworthy format knowledge.
2. Plans must be challenged before execution. Every plan has a hardening step.
3. The source of truth is repo files and evidence bundles, not agent summaries alone.
4. If a missing architecture layer is discovered, it must be implemented (if authorized) or captured in backlog, roadmap, taskcards, and memory.
5. Every sprint must have exact scope boundaries: allowed paths, forbidden paths, allowed actions, stop conditions.
6. Every prompt must distinguish authorized work from prohibited work. Hard prohibitions are non-negotiable.
7. Product source must not start from scattered evidence when a compiled Format Understanding Layer is required (see docs/format-understanding-layer.md).
8. LLMs may assist under governance, but verified facts, citations, DEC-034, oracle results, and human approvals remain the authority.
9. No cleanup commands (`git stash`, `git reset`, `git restore`, `git checkout --`, `git clean`) as a default or catch-all. If unrelated dirty work exists, classify it and stop or produce a blocker bundle; do not hide it to satisfy clean-tree pressure.
10. No pushing without SCM Agent policy authorization (AGENTS.md §AG4.2) — execute when credentials and branch policy allow; classify EXTERNAL_BLOCKER otherwise.
11. No gate self-approval without evidence. Gates 1-10: agent-owned policy gates (AGENTS.md §AG5). Gate 11 G11-G: Babar Raza only.

### Git Safety Requirements

Execution plans must require exact-path staging only, a dirty-state classification before edits, and a `git-safety-policy-check.md` metadata report. New evidence bundles must use sprint-specific metadata directories under `.local/`; root `bundle-metadata/` is reserved only for legacy inspection and must not be used for new sprint bundles. Final execution responses must include `NO_STASH_RESET_RESTORE_CLEAN_USED: YES`.

---

## 3. Plan Quality Test

A plan is NOT ready for execution if it is missing any of these:

1. Current-state verification (reads repo files, not just memory or summary).
2. Source/evidence references (specific files or bundle paths, not "see the evidence").
3. Exact allowed paths (list of files and dirs the agent may create or modify).
4. Exact forbidden paths (list of files and dirs the agent must not touch).
5. Validation commands (exact command lines to run, expected output).
6. Acceptance criteria (machine-testable, not vague).
7. Taskcard updates (which taskcards change status, how).
8. Evidence bundle requirements (contract path, metadata count, final path format).
9. Final status labels (e.g., PASS, FAIL, BLOCKED, NEEDS_REPAIR).
10. Rollback or blocker behavior (what to do if a check fails).
11. Self-challenge questions (minimum 10, answered yes/no).
12. Final evidence bundle path instruction (must end with EVIDENCE_BUNDLE: absolute path).

---

## 4. Plan Hardening Process

When asked to harden a plan, the agent must:

1. Read all files the plan references. Do not rely on summaries.
2. Verify current repo state (git status, git log, current-state consistency checker).
3. Identify: obsolete content, stale state, contradictions, missing steps, and overbroad claims.
4. Separate: symptoms (surface failures), root causes (structural issues), and structural weaknesses (gaps that will recur).
5. Preserve what works. Do not rewrite for the sake of rewriting.
6. Redesign what is structurally weak. Avoid superficial patches.
7. Convert vague steps ("update the file") into executable tasks ("append the following YAML block to AGENTS.md under Section AB").
8. Add validation and evidence requirements to every section.
9. Add stop conditions: if check X fails, stop and record BLOCKED.
10. If a discovered gap is out of scope, add it to ROADMAP.md, master-plan.md backlog, a taskcard (proposed_pending_human_approval), and relevant memory file.

---

## 5. Sprint Types

| Sprint Type | Purpose | Commits Allowed | Gates Changed | Product Source |
|---|---|---|---|---|
| MAIN SPRINT | Execute gate work, advance format pipeline | YES | YES (human approval) | YES (Phase 3+) |
| SECONDARY SPRINT | Execute authorized secondary plans (e.g., S-F2F) | YES | NO | NO |
| MEMORY SPRINT | Capture decisions, strategy, and architecture into durable local artifacts | YES | NO | NO |
| CLOSURE HYGIENE | Normalize contracts, fix stale state, build clean closure bundles | YES | NO | NO |
| INDEPENDENT VERIFICATION | Verify prior sprint claims without adding new work (DEC-034) | YES | NO | NO |
| UNBLOCKING PATCH | Minimal targeted fix for a specific blocker, scoped exactly | YES | NO | NO |
| PLAN MODE | Produce a hardened, challenged plan -- no execution, no repo changes | NO | NO | NO |
| EXECUTION MODE | Execute an authorized plan with gates, validation, and evidence bundle | YES | context-dependent | context-dependent |

Key rules:
- Do not mix sprint streams. A MEMORY SPRINT must not contain gate changes or product source.
- Every sprint must declare its type at the top of the prompt.
- SECONDARY SPRINTs require explicit human authorization naming the sprint (e.g., "execute S-F2F-02").

---

## 6. Prompt Anatomy

Every execution prompt must include these sections in this order:

1. **MODE** -- PLAN MODE ONLY or EXECUTION MODE.
2. **Sprint type** -- one of the sprint types above.
3. **Sprint name** -- unique human-readable name.
4. **Project and repo path** -- absolute path, no abbreviations.
5. **Primary evidence input** -- path to the previous bundle or primary input file.
6. **Goal** -- 1-5 sentences, specific, no vague placeholders.
7. **Human authorization** -- explicit list of what is authorized.
8. **Not authorized** -- explicit list of what is forbidden in prose.
9. **Hard prohibitions** -- explicit list of forbidden paths and actions.
10. **Read first** -- exact file paths the agent must read before acting.
11. **Current-state verification** -- specific checks to perform, metadata file to create.
12. **Execution sections** -- labeled A, B, C... each with: goal, required content, files to create/modify, validation.
13. **Validation section** -- exact commands, expected output, acceptance criteria.
14. **Taskcard updates** -- which taskcards change and to what status.
15. **Evidence contract** -- path, required fields, required repo files, required metadata files, forbidden patterns.
16. **Search audit** -- exact terms to search, classification rules (PASS/FAIL).
17. **Commit rules** -- allowed-to-stage list, do-not-stage list, commit message.
18. **Evidence bundle rules** -- output path pattern, exclusions, pre-final-response checks.
19. **Self-challenge** -- minimum 17 yes/no questions.
20. **Final response format** -- numbered list of required final response items, plus final line: EVIDENCE_BUNDLE: <absolute Windows path to zip>.

---

## 7. Single-Go Execution Handoff

A single-go execution handoff is a prompt that lets an agent self-manage an end-to-end plan without manual slice-by-slice copy-pasting. The key design principles:

1. **Internal gates.** The prompt includes all gates internally. If a gate fails (e.g., YAML validation fails), the agent records the failure and stops -- it does not skip ahead.
2. **Stop conditions.** Every section has a stop condition. Example: "If BUNDLE_VALIDATION: FAIL, stop and print BLOCKED_EVIDENCE_BUNDLE: <path>. Do not proceed to commit."
3. **Self-contained.** The prompt includes all needed context: file paths, validation commands, evidence contract path, commit message.
4. **Evidence before commit.** The agent must build and validate the evidence bundle before the commit section. No commit without a passing bundle.
5. **Labeled outputs.** The agent must print labeled status for each section (e.g., GATE7_FUZZ_TEST: PASS 18/18) so progress is auditable.
6. **Final line always prints evidence path.** The last line must be EVIDENCE_BUNDLE: <absolute path> (or BLOCKER_EVIDENCE_BUNDLE: <absolute path> if blocked).

When converting a prose plan to a single-go handoff:
- Replace "check if X exists" with: "run `ls X` and confirm it exists; if absent, stop with MISSING_FILE: X."
- Replace "update the YAML" with: "append the following block to file Y at line Z (after section header H)."
- Replace "validate the bundle" with: "run `python tools/evidence/validate_evidence_bundle.py --bundle <path> --contract <path>`. Expected: BUNDLE_VALIDATION: PASS."

---

## 8. Backlog Capture Rule

Any architectural gap, missing capability, or structural weakness that is identified during a sprint but is NOT authorized in the current sprint scope must be captured in:

1. ROADMAP.md (add to Infrastructure Milestones or future phases).
2. plans/master-plan.md (Gap Register or Backlog section).
3. taskcards/ (new taskcard with status: proposed_pending_human_approval).
4. memory/ (add to appropriate memory file or create new one).

The gap must NOT remain only in chat or only in an evidence bundle.

See AGENTS.md Section AB and GOVERNANCE.md Section 21 for the governing rule.

---

## 9. Fresh-Chat Usage

When starting a new chat session (or after context compaction), the agent should:

1. Ask the human to confirm which repo state to work from.
2. Read (in order): plans/master-plan.md, ROADMAP.md, AGENTS.md, GOVERNANCE.md, docs/planning-methodology.md, docs/agent-execution-handoff-standard.md, memory/00-index.md, memory/09-current-state-before-phase1.md, memory/11-prompting-and-agent-style-rules.md, and the latest evidence bundle summary.
3. Run the current-state consistency checker: python tools/evidence/check_current_state_consistency.py.
4. Identify current sprint state from master-plan.md Section 33 (Run Commit Ledger).
5. Produce the next prompt only after reading these files. Do not produce a prompt from summary alone.

See docs/fresh-chat-continuity-brief.md for a human-facing guide.

---

## 10. Style Rules

All methodology docs, prompts, and instructions in this repo must:

1. Be direct. State what to do, not what might be considered.
2. Be LLM-consumable. Each instruction is an atomic, self-contained action.
3. Avoid vague placeholders in square brackets where possible. Use descriptive instructions instead.
4. Avoid reliance on hidden context. If context is needed, include the file path and section reference.
5. Avoid em dashes. Use commas, colons, semicolons, or periods instead.
6. Include an explicit evidence bundle path requirement. The final line of every evidence-producing sprint response must be: EVIDENCE_BUNDLE: <absolute Windows path to zip>.
7. Challenge agent claims. Do not trust summaries until referenced files are read.
8. Do not skip gates or evidence. Gates and evidence are not waste -- they are the quality foundation.
9. Do not over-engineer. Add complexity only when a concrete problem requires it.
10. Include stop conditions. Every section of an execution prompt must say what to do if it fails.
