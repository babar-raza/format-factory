---
version: "1.0"
last-updated: "2026-06-24"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Same registry produces same results; read-only"
loc_budget: "<80 lines"
test_path: "tests/supervisor/test_validate_skill_contracts.py"
---

# /validate-skill-contracts

For each registered active skill in `skill-registry.yaml`, verify:
(a) command_file exists on disk, (b) required fields present, (c) status is a valid enum value.

## Purpose

Audit skill contract completeness. FAIL entries indicate broken skills (missing file or fields).
WARN entries indicate advisory issues. Deprecated skills are excluded.

## Steps

1. Read `.supervisor/skill-registry.yaml`
2. Skip skills with `status: deprecated`
3. For each remaining skill, check: `skill_id`, `purpose`, `command`, `status` fields present
4. Validate `status` is one of: active, deprecated, experimental, retired
5. Verify `command_file` path exists on disk (if specified)
6. Write results to `.supervisor/skill-contract-validation-results.yaml`

```bash
python tools/supervisor/validate_skill_contracts.py
```

## Output

`.supervisor/skill-contract-validation-results.yaml` with:
- `overall_verdict`: PASS | WARN | FAIL
- `fail_count`, `warn_count`
- `results[]`: per-skill verdict with `findings[]`

## Pass Criteria

Zero `FAIL` entries. WARN entries are allowed and noted.

## Allowed Paths

- `.supervisor/skill-contract-validation-results.yaml` (write)
- `.supervisor/skill-registry.yaml` (read)
- `.claude/commands/` (read — to verify command_file paths)

## Forbidden Paths

- `src/**`
- Writing to `skill-registry.yaml`

## Constraints

- Read-only except for output file
- Deprecated skills excluded from contract requirements

## Idempotency Contract

Same registry input produces same validation results. File is overwritten, not appended.

## Error Handling

On registry parse failure: exit non-zero and log error to stderr.

## Usage

```
/validate-skill-contracts
```
