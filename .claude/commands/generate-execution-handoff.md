# /generate-execution-handoff

Generate a formal execution handoff document for a src/* change that cannot be
performed via an existing governed skill directly (e.g., multi-file refactor,
complex algorithmic change, format-specific knowledge required).

## Usage

```
/generate-execution-handoff
```

## What This Skill Does

1. **Describe the change**: Documents what src change is needed, why, and acceptance criteria
2. **Pre-flight check**: Verifies the change is not covered by an existing governed skill
3. **Write handoff**: Creates `reports/r<n>/execution-handoffs/handoff-<id>.md` with:
   - Target file(s) and expected change
   - Pre-change SHA-256 for each file
   - Acceptance test command
   - Expected test count after change
4. **Register**: Adds pre-change SHA to ledger as PENDING_EXECUTION_HANDOFF entry
5. **Execute**: Makes the declared change
6. **Complete**: Updates ledger with post-change SHA and GOVERNED_PRODUCT_CHANGE classification

## Constraints

- Only used when no existing governed skill covers the change
- Must document the change BEFORE making it (pre-change SHA required)
- Must update the product-code ledger after the change
- Cannot be used to bypass governance — the handoff IS the governance

## Handoff Document Format

```markdown
# Execution Handoff: <ID>

**Target:** src/<format>/<file>
**Skill used:** /generate-execution-handoff
**Pre-change SHA-256:** <sha>
**Expected change:** <description>
**Acceptance test:** pytest tests/<format>/test_r<n>_<feature>.py -v
**Expected tests:** <N> passed, 0 failed
```
