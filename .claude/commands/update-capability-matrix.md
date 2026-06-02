---
version: "1.0"
last-updated: "2026-06-02"
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

## Changelog

- 1.0 (2026-06-02): Initial R90 governed minimum viable command.

