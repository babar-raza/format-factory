---
version: "1.0"
last-updated: "2026-06-24"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Same synthetic declaration produces same validator output"
loc_budget: "<60 lines"
test_path: "tests/supervisor/test_mutation_guard_validation.py"
---

# /validate-mutation-guard

Prove that governance validators in `autonomous_cycle.py` Step 2d correctly block
evidence declarations that contain undeclared `src/` path edits or architecture_only
stub citations in RELEASE_GATE items.

## Purpose

Validate the declaration-based enforcement layer. This proves governance validators
(V48, etc.) fire on synthetic test declarations as expected.

**LIMITATION (explicit, SKILL-GAP-012):** This validates the DECLARATION enforcement
layer only. Agents that edit files without submitting a declaration bypass this entirely.
That structural gap is tracked as SKILL-GAP-012.

## Steps

1. Read `.local/supervisor/skill-first-run-id.json` for `run_id`
2. Construct a synthetic evidence declaration at `.local/evidences/{run_id}/test-synthetic-declaration.yaml`
   containing a RELEASE_GATE item citing an `architecture_only` stub file
3. Run governance validators against it:
   ```bash
   python tools/supervisor/governance_validator_runner.py \
     --declaration .local/evidences/{run_id}/test-synthetic-declaration.yaml \
     --dry-run
   ```
4. Confirm V48 fires (output contains "V48" or "architecture_only")
5. Write results to `.supervisor/mutation-guard-results.yaml`

## Output

`.supervisor/mutation-guard-results.yaml` with:
- `v48_fired`: true/false
- `validator_output_path`
- `verdict`: MUTATION_GUARD_PROVEN | MUTATION_GUARD_FAILED

## Allowed Paths

- `.local/evidences/{run_id}/test-synthetic-declaration.yaml` (write synthetic only)
- `.supervisor/mutation-guard-results.yaml` (write)
- `tools/supervisor/governance_validator_runner.py` (execute)

## Forbidden Paths

- `src/**`
- Any production evidence paths

## Constraints

- Synthetic declaration written ONLY to `.local/evidences/{run_id}/` (isolated)
- Cannot affect production evidence
- `--dry-run` flag must be used to prevent state mutation

## Idempotency Contract

Same synthetic declaration produces same validator output. Deterministic.

## Error Handling

If `governance_validator_runner.py` not found: write `verdict: TOOL_UNAVAILABLE` and exit 0.
If V48 does not fire: write `v48_fired: false`, `verdict: MUTATION_GUARD_FAILED`.

## Usage

```
/validate-mutation-guard
```

## Output Format

- Structured result written to `reports/` in YAML or JSON format
- Human-readable summary printed to stdout
- Verdict: PASS / FAIL with per-item evidence
