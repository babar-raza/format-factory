---
artifact_id: TC-FF6-XLIFF-STATE-001
artifact_type: taskcard
path: taskcards/TC-FF6-XLIFF-STATE-001.md
format_id: xliff
product_family: six_python_production_program
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-26
---

# TC-FF6-XLIFF-STATE-001: Enforce XLIFF Advanced Translation-State Target Requirement

**Status:** completed
**Skill:** `format-feature-expansion`
**Contract capability:** `XLIFF-STATE-001`
**Obligation:** `SAL-XLIFF-00018`
**Scope:** `format_factory.xliff` semantic validation only.

## Objective

Reject a segment marked `translated`, `reviewed`, or `final` when it has no
`target`. These states require a target under the XLIFF core Schematron rule.
The task also preserves existing handling of the default/initial state and
does not invent a workflow ordering policy.

## Root Cause

The model preserves `state` and the validator accepts only known state values,
but it did not enforce the state-to-target implication. Consequently invalid
documents could pass the package's public `validate()` API.

## In Scope

- A focused positive/negative semantic-validation test.
- One validator-layer diagnostic with a stable error code.
- XLIFF focused and regression verification, then installed-wheel proof.

## Out of Scope

- Proprietary `subState` semantics.
- Workflow transition ordering policies.
- XLIFF optional-module validation and parser/writer changes.

## Acceptance Criteria

- [x] `translated`, `reviewed`, and `final` without target produce a diagnostic.
- [x] Those states with target remain valid.
- [x] Empty/default/`initial` state remains valid without target.
- [x] Existing public behavior remains covered by XLIFF regression tests.
- [x] Built-wheel proof executes outside the source tree.

## Evidence Required

- Failing pre-implementation test run bound to this obligation.
- Focused and full XLIFF test results.
- Installed-wheel package proof with input and wheel digests.
- Skill execution transcript and source/test input digests.

## Completion Evidence

- Red test: all three advanced states failed because `validate()` returned no
  diagnostics; the initial/target-present control passed.
- Green test: 4 focused assertions passed.
- Regression: `190 passed` for `tests/python/xliff`.
- Physical wheel proof: `PACKAGE-PROOF-4E859712536392E1B2ACFEC5A46717F2DB348F08192F98AB670A9728984A24EE`,
  source digest `6ff81a232622a3598e74329d806533b467377dbb5ae1314c7a6d8b945fe4193c`,
  wheel digest `58d3fd3ab7ed809192a7d6adab464c19224a80eab6dc6152de361b93bbb795d9`.

This closes only the state-to-target validation slice. XLIFF remains in
implementation because its other mandatory obligations remain open.

## Self-Challenge Record

1. Yes — the contract-backed state-to-target rule, focused regression, suite,
   and installed-wheel proof were completed.
2. Yes — all evidence required for this bounded slice is present; the
   repository-wide ledger migration remains separately open.
3. Yes — red/green tests and physical-wheel proof are sufficient for this
   semantic validation rule.
4. No — the primary OASIS source is pinned through `SRC-XLF-002` and its SAL
   assertion, not replaced by a secondary authority.
5. No — only XLIFF source/tests plus task/proof records were changed.
6. No — no gate or release status was self-approved.
7. No — the work remained within XLIFF implementation/verification.
8. No — commits were authorized by the user's explicit autonomous execution
   instruction and were guarded by the coordination pre-commit check.
9. Yes — the persisted transcript and canonical package-proof manifest were
   inspected before this taskcard was closed.
10. No — the transient misplaced ledger entry was corrected before commit and
    recorded by this self-challenge; the pre-existing ledger migration gap
    remains explicitly documented in `TC-FI-033-LEDGER-VALIDATOR-001`.
11. Yes — the applicable knowledge registry and production-package contract
    were read before source work.
12. Yes — those contracts were used as context while the ProductContract and
    pinned OASIS fact remained semantic authority.
13. Yes — no contradiction affecting this narrow rule was found.
14. Not applicable — no memory-update trigger occurred.
15. Not applicable — no human review or approval was requested.
