# Prompt Templates

**Document type:** Template Index and Usage Guide
**Created:** 2026-05-08 (memory-methodology-linkage-and-enforcement sprint)
**Visibility:** internal
**Parent:** [docs/agent-methodology-index.md](../agent-methodology-index.md)

---

## Purpose

These templates provide structured starting points for each type of sprint or planning
session in the format-factory project. They encode the canonical prompt anatomy, required
sections, and enforcement rules so that every session produces consistent results.

---

## Rules for Using Templates

1. Do not use vague placeholders. Adapt each section from actual repo state. Read the files referenced before filling in values.
2. Adapt from repo truth. File paths, commit hashes, gate statuses, and allowed/forbidden paths must come from reading the current repo state.
3. Include exact read-first list. Every execution prompt must specify the exact files to read in phase A before any action.
4. Include allowed and forbidden paths. Every execution prompt must list exactly which files may be created or modified and which must not be touched.
5. Include evidence contract and bundle requirements. Every execution sprint must specify a contract file (min_metadata_count, required_repo_files, required_metadata_files, forbidden_patterns).
6. Include self-challenge. Every execution sprint must end with a self-challenge section (minimum 17 yes/no questions) before the final response format.
7. Include final response format. The last line must be: EVIDENCE_BUNDLE: <absolute Windows path to zip>

---

## Template Table

| Template | Purpose | Mode | Final Line |
|----------|---------|------|------------|
| [plan-hardening-prompt-template.md](plan-hardening-prompt-template.md) | Review and harden a draft plan against repo truth before execution. | PLAN MODE | NEXT_PROMPT_READY: yes |
| [execution-handoff-prompt-template.md](execution-handoff-prompt-template.md) | Full single-go execution sprint from evidence input to bundle output. | EXECUTION MODE | EVIDENCE_BUNDLE: <absolute Windows path to zip> |
| [independent-verification-prompt-template.md](independent-verification-prompt-template.md) | DEC-034 verification of a prior sprint's claims in a separate session. | EXECUTION MODE | EVIDENCE_BUNDLE: <absolute Windows path to zip> |
| [evidence-bundle-review-prompt-template.md](evidence-bundle-review-prompt-template.md) | Inspect a bundle, challenge claims, and produce the next execution prompt. | PLAN MODE | NEXT_PROMPT_READY: yes |
| [memory-sprint-prompt-template.md](memory-sprint-prompt-template.md) | Capture decisions, architecture, preferences into durable local repo artifacts. | EXECUTION MODE | EVIDENCE_BUNDLE: <absolute Windows path to zip> |
| [closure-hygiene-prompt-template.md](closure-hygiene-prompt-template.md) | Normalize an emergency contract to clean PASS mode. | EXECUTION MODE | EVIDENCE_BUNDLE: <absolute Windows path to zip> |
| [unblocking-patch-prompt-template.md](unblocking-patch-prompt-template.md) | Minimal targeted fix for a single specific blocker. | EXECUTION MODE | EVIDENCE_BUNDLE: <absolute Windows path to zip> or BLOCKER_EVIDENCE_BUNDLE: <absolute Windows path to zip> |
| [fresh-chat-bootstrap-prompt.md](fresh-chat-bootstrap-prompt.md) | Orientation prompt for a new session with no prior context. | PLAN MODE | NEXT_PROMPT_READY: yes |

---

## Which Template to Use

| Situation | Template |
|-----------|----------|
| Human gives goal or plan draft | plan-hardening-prompt-template.md |
| Plan passes hardening (18/22+) | execution-handoff-prompt-template.md |
| Prior sprint needs independent check (DEC-034) | independent-verification-prompt-template.md |
| Prior bundle needs review before next sprint | evidence-bundle-review-prompt-template.md |
| Strategy or architecture decision to persist | memory-sprint-prompt-template.md |
| Emergency contract to normalize after clean sprint | closure-hygiene-prompt-template.md |
| Specific blocker must be removed | unblocking-patch-prompt-template.md |
| Fresh chat window, no prior history | fresh-chat-bootstrap-prompt.md |

---

## Required Final Lines

Every execution prompt must include exactly one of these as the final line of the response:

```
EVIDENCE_BUNDLE: <absolute Windows path to zip>
```

For PLAN MODE prompts (hardening, bundle review, fresh-chat bootstrap):

```
NEXT_PROMPT_READY: yes
```

For blocked sprints where a partial bundle was produced:

```
BLOCKER_EVIDENCE_BUNDLE: <absolute Windows path to zip>
```

Nothing may follow the final line.

---

## Reminder

Evidence, taskcards, gates, and status repair are necessary infrastructure, not waste.
They are the quality foundation that makes trustworthy format knowledge possible.

Skipping plan hardening, independent verification, or evidence bundle validation is a
governance violation -- not a time-saving shortcut.

---

## ChatGPT Evidence-Review Sprint Prompts (added 2026-05-09)

Sprint prompts generated from ChatGPT evidence review should follow these additional rules:

1. **Classify active streams.** Every ChatGPT review prompt must identify which active stream
   the sprint belongs to (MAIN_SPRINT, SECONDARY_SPRINT, or MEMORY_SPRINT) and which authority
   files it may or may not touch.

2. **Include memory update requirements.** When a ChatGPT sprint review produces architectural
   direction changes or sprint supervision rule changes, the sprint prompt must require the agent
   to run a memory sprint to capture those changes before the next execution sprint.

3. **Include stream classification table.** If multiple streams are active, the prompt must
   include a table classifying each untracked or dirty file by stream before any staging is done.

4. **Include current state reconstruction.** Before prescribing fixes, the prompt must require
   the agent to reconstruct actual state from files, not from prior summaries.

5. **Require bundle validation against contract.** Every execution sprint prompt must name the
   exact evidence contract file and run `validate_evidence_bundle.py --check-no-pending`.

These rules complement the existing template rules. Do not change templates for templates that
are already being used in active sprints -- adapt them only when starting a new sprint generation.

---

## See Also

- [docs/agent-methodology-index.md](../agent-methodology-index.md) -- full methodology entry point
- [docs/planning-methodology.md](../planning-methodology.md) -- planning principles and prompt anatomy
- [docs/agent-execution-handoff-standard.md](../agent-execution-handoff-standard.md) -- handoff standard
- [docs/plan-hardening-checklist.md](../plan-hardening-checklist.md) -- 22-item checklist
- [AGENTS.md](../../AGENTS.md) Section AD -- enforcement rules
- [GOVERNANCE.md](../../GOVERNANCE.md) Sections 23, 24 -- governance rules
