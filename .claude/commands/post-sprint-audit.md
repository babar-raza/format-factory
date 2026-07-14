---
version: "1.1"
last-updated: "2026-06-15"
phase-available: "all"
gate-required: null
created-by: post-sprint-autonomy-loop sprint
---

# /post-sprint-audit

Run Stage 1 (Post-Sprint Strict Evidence Audit) of the Post-Sprint Autonomy Loop.

## Steps

1. Read `.supervisor/prompts/prompt1-post-sprint-audit.md` for full audit instructions.
2. Read `reports/supervisor/session-resume.md` for last sprint state.
3. Read `reports/supervisor/work-item-grades.yaml` for item grades.
4. Read `.local/supervisor/continuation-signal.json` for continuation state.
5. Locate and read the latest evidence declaration from `.local/evidences/`.
6. Execute the audit per prompt1 instructions:
   - Section A: What we achieved
   - Section B: What this proves
   - Section C: Effect on final outcome
   - L1 execution issues
   - L2 integration issues
   - L3 system weakness issues
   - Claim classification matrix
   - Evidence quality verdict
   - Next-stage recommendation
7. Write structured output conforming to `.supervisor/schemas/stage1-issue-model.schema.json`.
8. Write outputs to the current evidence root under `stage1-*` filenames.

## Pre-Closure Verification Checklist

Before recording any audit finding as verified (Claim classification matrix, Evidence
quality verdict), apply the Gate Function — adapted from obra/superpowers
`verification-before-completion` (MIT license):

1. **Identify** — name the exact command that proves the claim under audit (e.g. the
   focused test command cited in the evidence declaration, or the governance validator
   invocation for a validator-pass claim). A claim with no identifiable proof command
   cannot be marked verified.
2. **Run** — execute that command fresh, in full, in this session. A prior sprint's or
   agent's report of having run it does not satisfy this step.
3. **Read** — read the complete output: exit code, pass/fail/error counts, and any
   stack trace or failure text. Do not sample or truncate.
4. **Verify** — confirm the output actually substantiates the specific claim being
   audited, not merely that the command exited without crashing.
5. **Claim** — only after Steps 1-4 succeed may the audit record the item as
   `completed_verified` (or the equivalent stage1 classification).

### Red Flags — STOP and re-run Step 2

Treat any of the following, found while drafting the audit, as a signal to stop and
re-verify before writing output:
- Hedging language in the draft: "should pass", "probably works", "seems to be fixed"
- Expressing satisfaction with a result before the fresh verification command has run
- Trusting an evidence declaration's or prior agent's self-report without independently
  re-running the cited proof command
- Citing an evidence path without having opened and read its contents this session

## Output Format

1. `stage1-issue-model.json` (machine-readable, schema-conformant)
2. `stage1-sprint-audit-summary.md` (human-readable)
3. `stage1-next-stage-recommendation.yaml`

## Allowed Paths

- `.local/evidences/` (write audit outputs)
- `reports/supervisor/` (read)
- `.supervisor/` (read prompts and schemas)

## Forbidden Paths

- `src/**` (no source edits)
- `registry/format-registry.yaml`
- `AGENTS.md`, `GOVERNANCE.md`

## Constraints

- Do not execute implementation work
- Do not modify source files
- Do not commit or push
- Output must conform to stage1-issue-model.schema.json

## Usage

```
/post-sprint-audit
```
