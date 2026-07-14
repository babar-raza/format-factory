---
version: "1.0"
last-updated: "2026-07-14"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Same target file/diff + same 5 checks produce the same findings; read-only end to end"
loc_budget: "0 lines of executable code (prompt-driven checklist only; no bundled script)"
test_path: "N/A (prompt-spec skill, no executable code) — verification is the manual scan proof recorded under TC-EXT-017-03"
external_skill_origin: true
external_skill_source: anthropics/claude-code
external_skill_commit: 988b3e56432775c09bba903ba22522b97cd0f2fb
external_skill_license: Apache-2.0
risk_level: LOW
created-by: TC-EXT-017-03
product_track: governance
---

# /comment-analyzer

Read-only reviewer that checks comments (and docstrings) for factual
accuracy, completeness, and long-term value. Analyzes and provides feedback
only — never modifies code or comments directly.

## Attribution

This skill adapts the 5 checks from the `comment-analyzer` skill in
Anthropic's `claude-code` PR Review Toolkit (`anthropics/claude-code`,
Apache-2.0), commit `988b3e56432775c09bba903ba22522b97cd0f2fb`. The 5 checks
and the explicit "analyze and provide feedback only" constraint are carried
over near-verbatim from the upstream skill; the FF-specific finding-routing
rule (Critical Issues hand off to `/found-issue-ownership`) is original to
this repository. License: Apache-2.0 — attribution preserved per license
terms; no upstream code is executed, only its documented methodology is
adapted into prose. Cleared by `/skill-scanner` per TC-EXT-012's mandatory
gating rule.

## Purpose

A comment that is stale, misleading, or merely restates the code it sits
beside does not just fail to help — a misleading comment actively misdirects
the next person (or agent) who trusts it over the code. This skill applies a
structured, repeatable check to distinguish comments that carry real
long-term value from comments that should be corrected or removed.

## When to Use

- Reviewing any diff or file that adds, modifies, or removes comments or
  docstrings.
- Before closing a taskcard whose scope touched public API documentation
  (docstrings on functions/classes exposed via `add-python-api` or
  `add-dotnet-api`).
- On request, against any existing file's comments, as an ad hoc audit.

## Important Constraint

**You analyze and provide feedback only. Do not modify code or comments
directly.** This skill's entire output is a report; any correction it
recommends is applied, if at all, by a separate governed mutation skill
(e.g. `/product-source-task`), never by this skill itself.

## Steps (the real 5 checks, adapted)

1. **Verify Factual Accuracy.** Confirm the comment's claims about function
   signatures match the actual documented parameters and return values, and
   that the described behavior actually aligns with the code's logic below
   it. A docstring claiming a function "returns None on failure" when the
   code actually raises an exception is a factual-accuracy failure.
2. **Assess Completeness.** Check whether the comment covers what a reader
   actually needs to know — parameters, return value, side effects, raised
   exceptions, non-obvious preconditions — or omits load-bearing information
   a caller would need.
3. **Evaluate Long-term Value.** Distinguish comments that explain *why*
   (a design decision, a non-obvious constraint, a historical reason for an
   otherwise-strange approach) from comments that merely restate *what* the
   code already says in plain sight. Restating-the-obvious comments are
   flagged for removal — "why" comments carry long-term value; "what"
   comments that just narrate the next line generally do not.
4. **Identify Misleading Elements.** Look specifically for comments that
   actively contradict the code, reference removed parameters/behavior,
   or describe an earlier version of the logic that no longer applies —
   these are worse than no comment at all because they actively mislead.
5. **Suggest Improvements.** For every issue found in checks 1-4, propose a
   specific, concrete replacement — not merely "improve this comment."

## Output Format

```
## Comment Analysis: [Target]

### Summary
- <one-paragraph overview of comment quality in this target>

### Critical Issues
1. Location: <file:line>
   Issue: <factual inaccuracy or actively misleading content>
   Suggestion: <concrete corrected text>

(repeat per critical issue)

### Improvement Opportunities
- Location: <file:line> — <what is incomplete and what to add>

### Recommended Removals
- Location: <file:line> — <why this comment adds no long-term value>

### Positive Findings
- <comments that are accurate, complete, and carry real "why" value>
```

## Finding Routing

- **Critical Issues** (factually inaccurate or actively misleading
  comments/docstrings) — hand off to `/found-issue-ownership`
  (Step 1 — Capture). A misleading comment on a public API is a correctness
  risk to every caller who trusts it, not a cosmetic nit.
- **Improvement Opportunities and Recommended Removals** — logged inline in
  the review output only; no mandatory hand-off.

## Allowed Paths

- The file(s)/diff under review — read only
- `.claude/commands/comment-analyzer.md` (this file, its own reference
  checklist)
- No report file is written by default — findings are recorded inline in the
  invoking taskcard's evidence

## Forbidden Paths

- **This skill never writes to the reviewed target, or to any other file** —
  not even to correct a comment it just flagged as factually inaccurate.
  It is read-only end to end: no edits to source, tests, configuration, or
  documentation under review.
- `src/**`, `tests/**` — read only, for the purpose of locating and checking
  comments/docstrings; never mutated by this skill
- `.supervisor/skill-registry.yaml`, `registry/found-issue-register.yaml` —
  never written directly; Critical Issue hand-off goes through
  `/found-issue-ownership`, not a direct write from this skill

## Constraints

- Read-only in all 5 checks. No writes, no external network calls, no hooks
  executed.
- A recommended replacement text (check 5) is always a suggestion in the
  report — never applied directly by this skill.

## Idempotency Contract

Given the same target file/diff content and the same 5 checks (this file),
the review produces the same findings. No randomness; no time-dependent
output.

## Governance Note

Per TC-EXT-012 (external-skill-import plan) and TC-EXT-017 (5 read-only
reviewer imports), this skill was cleared by `/skill-scanner` before
registration. It is a pure prompt/methodology spec: no bundled script, no
automated file operations, no hooks, and no external network calls of its
own.
