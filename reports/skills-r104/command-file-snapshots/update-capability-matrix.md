---
version: "1.2"
last-updated: "2026-06-03"
phase-available: "3+"
gate-required: null
generated_by: codex
visibility: generated
---

# /update-capability-matrix

Reconcile proven product behavior into `product-capability-matrix/poc-targets.yaml`. The matrix
is a reference snapshot. It must not be used to grant gate approval or release authorization.

## Required Inputs

- exact matrix entry to update
- claimed field transitions
- evidence paths and focused validation commands
- sprint ID that produced the proof

## Steps

1. Read `AGENTS.md`, `plans/master-plan.md`, `.supervisor/skill-registry.yaml`, and
   `product-capability-matrix/poc-targets.yaml`.
2. Confirm the active handoff explicitly authorizes the matrix file and names the exact entry.
3. Read the implementation evidence and rerun or inspect the named focused validations.
4. Update only evidence-backed capability, test-count, dogfood-status, blocker, example, or
   next-action fields. Preserve unrelated entries.
5. Keep `commercial_product_ready: false`, `gate_11_approved: false`, and publication authorization
   unchanged unless a separate human-authorized gate execution prompt explicitly permits otherwise.
6. Preserve documented gaps. Do not convert `GAP_DOGFOOD_EXTERNAL` to `IMPLEMENTED` unless
   `/add-dogfood-export` reload proof exists.
7. Validate YAML parsing and inspect the diff for unrelated changes.
8. Report each old value, new value, and evidence path. Do not commit or push.

## Allowed Paths

- `product-capability-matrix/poc-targets.yaml` (matrix update)

## Forbidden Paths

- `registry/format-registry.yaml` (gate authority)
- `plans/master-plan.md` (operational authority)
- `src/**` (no source edits — use governed skill)

## Stop Conditions

- Evidence is missing, stale, or contradicts the requested status.
- The update would alter gate authority, release authority, or commercial readiness.
- The handoff does not name the exact matrix entry.
- YAML validation fails.

## Output Format

Report matrix entry, field transitions, evidence paths, validation command results, and unchanged
authority flags.

## Validation

The edited YAML must parse, the diff must be entry-scoped, and every status transition must cite
local proof.

## Rollback

1. Revert `product-capability-matrix/poc-targets.yaml` to prior state (git checkout)
2. Verify YAML still parses

## Transcript Requirement

After execution, emit a skill invocation transcript JSON to `reports/skills-r<N>/skill-transcripts/`
with: skill_id, matrix_entry, field_transitions, evidence_paths, verdict.

## Sample Invocation

```
/update-capability-matrix
# Inputs:
#   matrix_entry: commercial-net-fods
#   claimed_status_changes: [dotnet_tests: 215->273, added: get_column_headers]
#   evidence_paths: [tests/net/fods/FodsR93GetColumnHeadersTests.cs]
#   focused_validation_commands: [dotnet test tests/net/fods/ --filter "FodsR93"]
```

## Changelog

- 1.0 (2026-06-02): Initial R90 governed minimum viable command.
- 1.2 (2026-06-03): Added allowed/forbidden paths, rollback, transcript requirement, sample invocation (Skills R101).
