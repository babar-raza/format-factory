---
version: "1.1"
last-updated: "2026-06-03"
phase-available: "3+"
gate-required: null
generated_by: claude
visibility: generated
---

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

## When to Use This vs. Other Skills

Use `/generate-execution-handoff` only when:
- The change does not fit any existing skill (multi-file refactor, algorithmic change, etc.)
- You need to document the change before making it for traceability

Use a governed skill instead when the change fits:
- Single API addition → `/add-dotnet-api` or `/add-python-api`
- Object model feature → `/add-dotnet-object-model-feature` or `/add-python-object-model-feature`
- Save/write → `/add-same-format-writer-feature`
- Export → `/add-dogfood-export`

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

## Allowed Paths

- `reports/r<n>/execution-handoffs/` (handoff document)
- `src/python/<format>/` or `src/net/<format>/` (governed change)
- `tests/python/<format>/` or `tests/net/<format>/` (tests)
- `reports/r90/product-code-change-ledger.json` (ledger update)

## Forbidden Paths

- `registry/format-registry.yaml` (gate authority)
- `plans/master-plan.md` (operational authority)

## Rollback

1. Revert source changes
2. Remove test file
3. Remove the ledger entry
4. Remove the handoff document from `reports/r<n>/execution-handoffs/`
5. Re-run `python tools/supervisor/validate_product_code_ledger.py` to confirm PASS

## Evidence Required

- Handoff document path
- Source file(s) changed with pre/post SHA-256
- Test file(s) and pass result
- Ledger entry ID

## Validation

Complete when: handoff document exists, source changes match declared scope, ledger updated, and tests pass.

## Transcript Requirement

After execution, emit a skill invocation transcript JSON to `reports/skills-r<N>/skill-transcripts/`
with: skill_id, handoff_id, target_files, changed_files, test_results, ledger_entry_id, verdict.

## Changelog

- 1.0 (2026-06-02): Initial version
- 1.1 (2026-06-03): Added frontmatter, "when to use" decision tree, allowed/forbidden paths, rollback, changelog (Skills R99)
- 1.2 (2026-06-03): Added evidence, validation, transcript requirement (Skills R101).
