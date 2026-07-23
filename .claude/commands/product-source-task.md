---
version: "2.0"
last-updated: "2026-07-23"
phase-available: "3+"
gate-required: "Explicit product implementation authorization"
skill_type: "ATOMIC_SKILL"
idempotency: "A replay with the same bounded task and complete input digests is a no-op or produces byte-identical generated/source artifacts."
loc_budget: "One bounded responsibility; broad work is decomposed by obligation and package layer."
test_path: "tests/production_program/test_production_skills.py"
risk_level: "MEDIUM"
created-by: "TC-FF6-MACH-001"
product_track: "foss_python"
generated_by: codex
visibility: generated
---

# /product-source-task

Execute one bounded source repair or implementation task in a production Python
format library. Use `/format-feature-expansion` when the task originates from
an unmet ProductContract obligation; use this skill for an already-proven
defect, migration slice, or internal refactor with unchanged behavior.

## Required Inputs

- `format_id`
- `task_id`
- `task_kind` (`defect`, `migration`, `refactor`, or `generated_source`)
- `root_cause`
- `planned_paths`
- `input_digests`
- `acceptance_evidence`
- `regression_tier`

## Execution

1. Load `KC-PYTHON-003`, resolve product paths, acquire leases, and pass the
   pre-mutation guard.
2. Reproduce the defect or capture characterization proof for migration and
   refactor work.
3. Enumerate callers and proof descendants invalidated by the change.
4. Apply one coherent change in the owning layer; do not mix model I/O,
   reader/writer logic, analytics, or optional adapters.
5. Run the smallest relevant verification followed by the declared regression
   tier and installed-wheel import proof.
6. Record exact commands, results, package/source/test/fixture/tool/lock/
   environment digests, and proof nodes.
7. Commit successful work to the owned integration branch. Failed work remains
   unpromoted and generates a current-state remediation task.

## Mandatory Validations

- reproduced failure or preserved characterization baseline
- complete input closure and transitive invalidation
- focused and declared regression tiers pass
- package architecture and public API checks pass
- built-wheel import location is outside the source tree
- generated output is reproducible when `task_kind=generated_source`
- no critical/high open defect is hidden by a waiver or status edit

## Allowed Paths

- exact format-owned source, tests, fixtures, examples, docs, and manifests
- canonical run/proof outputs

## Forbidden Paths

- unrelated formats or shared mutable fixtures
- source-tree-only import proof
- hand-edited generated source without generator repair
- manual promotion/readiness changes
- `src/net/**`, `src/dotnet/**`, `plans/strategic/**`

## Stop Conditions

- Preserve unexpected user changes and move work to an isolated worktree.
- Split the task if multiple independent responsibilities are discovered.
- Do not weaken current successful behavior; characterize it before migration.
- Apply the controller’s retry/technical-block policy without pausing the
  broader program.

## Output

Return task identity, root cause, changed paths, invalidated/rebuilt proof
nodes, exact verification results, installed-package proof, current gaps,
computed promotion, and next deterministic task.
