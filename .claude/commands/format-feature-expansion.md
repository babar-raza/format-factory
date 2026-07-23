---
version: "2.0"
last-updated: "2026-07-23"
phase-available: "3+"
gate-required: "Explicit product implementation authorization"
skill_type: "ATOMIC_SKILL"
idempotency: "The same obligation, bounded change, and input closure produce the same source, tests, and proof projection."
loc_budget: "One coherent obligation slice; split work when more than one independently testable behavior changes."
test_path: "tests/production_program/test_production_skills.py"
risk_level: "MEDIUM"
created-by: "TC-FF6-MACH-001"
product_track: "foss_python"
generated_by: codex
visibility: generated
---

# /format-feature-expansion

Implement one unmet ProductContract obligation in an existing production
format library. This skill is obligation-driven; adding an arbitrary export or
meeting a test-count target is not a completion criterion.

## Required Inputs

- `format_id`
- `profile_id`
- `obligation_id`
- `contract_digest`
- `authority_digests`
- `affected_layer`
- `planned_paths`
- `proof_inputs`
- `task_id`

## Execution

1. Run `/check-skill-coverage`, load `KC-PYTHON-003`, acquire exact leases, and
   pass the pre-mutation guard.
2. Confirm the obligation is current, belongs to the format/profile, and is
   mandatory or deliberately selected by deterministic queue priority.
3. Characterize affected working behavior and enumerate every public caller.
4. Add a failing positive test. For rejection/security obligations, also add
   the required failing negative test. Use licensed independent fixtures where
   interoperability is claimed.
5. Implement the smallest coherent change in the correct package layer.
6. Run focused tests, then format regression, architecture, typing, lint,
   installed-wheel, and the risk-appropriate security tier.
7. Record exact executed evidence and input closure. Recompute invalidation and
   promotion; never edit readiness directly.
8. If another obligation is exposed, materialize it in the current-gap
   projection and allow deterministic scheduling.

## Mandatory Validations

- obligation and SAL fact resolve to the selected format
- tests were observed failing for the intended reason before implementation
- executed positive proof; executed negative proof where applicable
- no source/test/fixture/environment digest is omitted
- public API snapshot and caller blast radius remain compatible or have an
  explicit pre-1.0 migration record
- installed wheel, not source tree, passes import and behavior checks
- format and machinery regression tiers pass

## Allowed Paths

- the selected format’s source, tests, fixtures, examples, docs, and manifests
- canonical proof/run outputs

## Forbidden Paths

- unrelated formats
- manual coverage or promotion labels
- test-count substitutions for behavior
- implementation-derived fixtures as the only oracle
- `src/net/**`, `src/dotnet/**`, `plans/strategic/**`

## Stop Conditions

- Quarantine a corrupt fixture without erasing its digest/history.
- On oracle disagreement, add a discriminating test and consult primary
  authority; do not choose the convenient outcome.
- On repeated root cause, apply the controller’s three-attempt technical-block
  rule and continue other work.

## Output

Return obligation ID, changed paths, before/after test evidence, regression
results, input/output digests, new proof nodes, computed readiness, and next
queued obligation.
