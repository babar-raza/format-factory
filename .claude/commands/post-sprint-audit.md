---
version: "1.0"
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
