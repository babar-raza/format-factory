---
version: "1.0"
last-updated: "2026-06-25"
phase-available: "all"
gate-required: null
skill-id: rollback-and-recovery
---

# /rollback-and-recovery

Govern rollback, backup-restore, and partial-state recovery operations.
Ensures every destructive or reversible operation is declared, verified, and
evidence-captured before execution.

## When to Use

- Rolling back a failed sprint mutation to a known-good state
- Restoring from a backup path after a partial-state corruption
- Recovering from a broken plan lock or stale continuation signal
- Using `git stash pop` or `git restore` after verifying current state

## Required Handoff Fields

- `rollback_target` — the file, branch, or state to restore
- `backup_path_or_stash_ref` — source for the restore operation
- `before_state_description` — documented state before rollback begins
- `after_state_expected` — expected state after rollback completes

## Mandatory Validations (GH-001)

1. `backup_path_exists_before_restore` — verify backup/stash exists before touching target
2. `git_stash_list_checked_before_pop` — verify stash ref is valid before pop
3. `no_destructive_operation_without_confirm` — all destructive actions must be declared in evidence

## Governance Note

This skill is gated by SKILL-GAP-011. The capability-routing-registry.yaml
`rollback_and_recovery` route currently has `current_status: MISSING_SKILL_CAPABILITY`.
This command file enables the skill to pass `validate_skill_contracts`. Full capability
route activation requires resolving SKILL-GAP-011.

All rollback actions must be captured in evidence with before/after state comparison.

## Required Inputs

- `rollback_target` — value for `rollback_target`
- `backup_path_or_stash_ref` — value for `backup_path_or_stash_ref`
- `before_state_description` — value for `before_state_description`
- `after_state_expected` — value for `after_state_expected`

## Allowed Paths

- `.local/ — local state files (read/write)`
- `tools/ — repair scripts (read-only)`
- `reports/ — repair reports (write)`

## Forbidden Paths

- `src/net/**` — .NET product source is out of scope for machinery repair
- `src/python/**` — Python product source is out of scope for machinery repair
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if the skill's mandatory validations cannot be completed
- Stop if any required input field is missing or invalid

## Output Format

- Structured result written to `reports/` in YAML or JSON format
- Human-readable summary printed to stdout
- Verdict: PASS / FAIL with per-item evidence
