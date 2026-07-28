---
version: "1.0"
last-updated: "2026-07-24"
phase-available: "all"
gate-required: null
skill_type: "ATOMIC_SKILL"
idempotency: "Equivalent contracts, source trees, test inputs, fixtures, environments, and commands produce the same current proof and gap projection."
risk_level: HIGH
created-by: SKILL-GAP-FF6-PRODUCTION-PROOF
product_track: governance
generated_by: codex
visibility: generated
---

# /materialize-production-proof

Materialize current implementation obligations and executed proof in the
six-format production controller. Use this skill when contract readiness can
outlive implementation evidence, when deleted or changed test inputs retain
credit, or when a controller reports no gaps without source-bound execution.

Do not use this skill to implement format behavior, edit a contract, approve a
gate, or turn historical/path-only evidence into current proof.

## Required Inputs

- `defect_id`
- `failing_regression`
- `invalidation_input`
- `target_product`

## Execution

1. Reproduce the false-ready or stale-proof condition with a minimal controller
   state and compiled mandatory obligation.
2. Compile every mandatory obligation into the canonical production proof
   graph; do not infer satisfaction from source, test, or fixture presence.
3. Execute proof commands through the controller and bind successful results to
   the exact contract, full product source tree, selected tests, fixtures,
   dependency inputs, environment, command, exit code, and output digest.
4. Accept one obligation and one required polarity per executed result. Reject
   unknown obligations, missing inputs, non-zero commands, and inputs modified
   during execution.
5. Rebuild the graph and current-gap projection from live inputs. Resolve a gap
   only when an executed result remains digest-valid and has the obligation's
   required positive or negative polarity.
6. Persist canonical nodes, edges, proof records, promotion decision, and
   controller state atomically. Treat legacy proof as historical until replayed.
7. Prove same-input determinism and mutation/deletion invalidation before
   recording a PASS receipt.

## Mandatory Validations

- `mandatory_obligations_materialized`
- `presence_is_not_proof`
- `one_obligation_per_executed_result`
- `complete_execution_input_closure`
- `changed_test_or_fixture_invalidates`
- `deleted_input_revokes_proof`
- `nonzero_execution_rejected`
- `three_run_determinism`
- `manual_promotion_cannot_override`

## Allowed Paths

- `tools/supervisor/production_program.py`
- `tests/production_program/test_production_program.py`
- `reports/skills-rff6/skill-transcripts/materialize-production-proof-*.json`
- `.local/production-program/**`

## Forbidden Paths

- `src/**`
- `shared/format-contracts/**`
- `shared/sal-facts/**`
- human-only gate, approval, or release records
- status-only promotion edits
- importing legacy/path-only evidence as current proof

## Stop Conditions

- Fail closed if any proof input is outside the repository, missing, or changes
  during execution.
- Fail closed if an obligation is unknown, non-mandatory, or receives the wrong
  polarity.
- Do not record a failed command as proof.
- If canonical same-input outputs differ, retain the implementation gaps and
  isolate the nondeterministic field before continuing.

## Output Format

Return a structured result containing the product, obligation, proof digest,
live input digests, command exit code, graph digest, promotion state, and
current gap IDs. The output is evidence, not a gate approval.
