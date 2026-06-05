# Plan Review and Single-Go Execution Template

**Added:** 2026-06-04
**Use:** When reviewing a plan document and deciding whether it's ready for execution.

## Plan Review Decision

Every plan review must produce exactly one of:
- `PLAN_NEEDS_REPAIR` → provide repair prompt
- `READY_FOR_SINGLE_GO_EXECUTION` → provide single-go execution handoff

Do not produce vague COMPLETE/PARTIAL/BLOCKED verdicts.

## Plan Review Checklist

### Structure
- [ ] Taskcards initialized as `READY` (not `IN_PROGRESS`)
- [ ] Lifecycle: `READY → IN_PROGRESS → CLOSED_VERIFIED`
- [ ] No pre-filled `worker_self_verdict: PASS`
- [ ] No hardcoded counts as authority (taskcard count, file count)
- [ ] Evidence_paths declared but not pre-filled

### Evidence and Closeout
- [ ] Declaration-driven closeout: `python tools/supervisor/autonomous_cycle.py --declaration <path>`
- [ ] Review package builder: `python tools/supervisor/build_declaration_review_package.py --declaration <path>`
- [ ] Allowed paths include `.local/supervisor/reviews/<run_id>/**`
- [ ] Python portability: `.local/venv/Scripts/python` preferred, `python` fallback
- [ ] No machine-specific absolute paths in plan text

### Validation Requirements
- [ ] Declared output existence check
- [ ] Markdown H1 validation
- [ ] JSON/YAML parse validation
- [ ] No unresolved taskcards at closeout
- [ ] No forbidden changes check (git diff)
- [ ] Autonomous-cycle run captured
- [ ] Package exists check
- [ ] SHA-256 computed

### Path and Scope
- [ ] Allowed paths list is complete and tight
- [ ] Forbidden paths include src/net/*, src/python/* (if not a product sprint)
- [ ] Lane ownership declared
- [ ] File ownership map included
- [ ] Overlap check included

### External Tools
- [ ] Ruflo fallback mode declared
- [ ] Superpowers normalization required before use
- [ ] GhidraMCP DISABLED_BY_DEFAULT

## If PLAN_NEEDS_REPAIR

Produce a repair prompt with:
- Sprint ID: `FORMAT-FACTORY-<PLAN>-PLAN-REPAIR-001`
- Mission: Repair the plan only — do NOT execute the plan
- Allowed paths: the plan file itself + reports/
- Forbidden paths: all product source paths
- Repair checklist: exact items from this review
- Target repair verdicts:
  - `<PLAN>_PLAN_REPAIRED_READY_FOR_SINGLE_GO_EXECUTION`
  - `<PLAN>_PLAN_REPAIRED_WITH_LIMITATIONS`
  - `<PLAN>_PLAN_STILL_NEEDS_REPAIR`

## If READY_FOR_SINGLE_GO_EXECUTION

Produce a single-go execution handoff with:
- All required fields from format-factory-stream-prompt-requirements.md
- Taskcards pre-populated as READY
- Specific product targets
- Evidence closeout command (declaration-driven)
- Final response contract including absolute path and SHA-256
