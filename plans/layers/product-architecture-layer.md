# Product Architecture Layer

```yaml
layer_metadata:
  layer_id: L06
  canonical_name: Product Architecture Layer
  canonical_slug: product-architecture-layer
  permanent_plan_path: plans/layers/product-architecture-layer.md
  schema_version: '1.0'
  plan_revision: '2'
  repository_revision: a7744cf6
  status: HARDENING_REQUIRED
  health: DEGRADED
  maturity_current: 2
  maturity_target: 5
  current_stage: ARCHITECTURE_REPAIR
  current_owner: null
  session_id: 923e237958c1
  active_taskcards: []
  ready_taskcards: []
  blocked_taskcards:
  - TC-PROD-001
  completed_taskcards: []
  dependencies:
  - L01
  - L02
  - L03
  - L14
  upstream_layers:
  - L01
  - L02
  - L03
  - L14
  downstream_layers:
  - L05
  - L07
  - L08
  - L16
  - L19
  skill_ids:
  - add-python-api
  - add-dotnet-api
  - add-dotnet-object-model-feature
  - add-python-object-model-feature
  - add-same-format-writer-feature
  - decompose-monolithic-codec
  command_ids:
  - add-python-api
  - add-dotnet-api
  - add-dotnet-object-model-feature
  - add-python-object-model-feature
  evidence_paths:
  - registry/source-structure-baseline.json
  - docs/code-quality/production-library-standard-v2.md
  - reports/r90/product-code-change-ledger.json
  last_updated_at: '2026-06-29'
  last_verified_at: '2026-06-26'
  last_verified_revision: a7744cf6
  next_task_id: TC-PROD-001
  next_action: Continue .NET deepening S141+; Gate 11 execution requires Babar Raza
```

## 1. Layer Metadata

This plan is the canonical working plan for **Product Architecture Layer** (`L06`). It replaces placeholder/stub prose with a governed layer contract, current known state, gaps, and executable next actions based on the Format Factory project memory and the existing layer-plan pattern.

## 2. Authority and Purpose

This layer owns the actual product architecture: object model decomposition, namespaces, class boundaries, parser/writer organization, and cross-language alignment. Its authority is limited to its owned scope and must be exercised through registered skills, taskcards, evidence declarations, and validation gates.

## 3. Scope

- src/net and src/python product source layout
- class/namespace hierarchy
- parser, model, writer, exporter separation
- commercial .NET and reduced/FOSS architecture targets

## 4. Explicit Non-Scope

- spec authority
- package publication

## 5. Owned Decisions

- Defines the contracts, registries, evidence, and acceptance criteria for source architecture, object model, and QName hierarchy.
- Decides whether layer work is ready, blocked, rework-required, or release/certification-ready.
- Maintains gap records instead of hiding missing implementation behind stubs or vague prose.

## 6. Upstream Inputs

- Upstream layers: `['L01', 'L02', 'L03', 'L14']`.
- Dependencies: `['L01', 'L02', 'L03', 'L14']`.
- Repository governance, AGENTS/CLAUDE instructions, active master/challenger plans, taskcards, and evidence bundles.
- Project memory: SAL/RCAL findings, QName hierarchy requirement, supervisor dual-pipeline model, dogfood export target, package/release constraints, and no-stub policy.

## 7. Downstream Consumers

- Downstream layers: `['L05', 'L07', 'L08', 'L16', 'L19']`.
- Autonomous supervisor lanes, product implementation lanes, audit/certification lanes, and future agents that need a discoverable layer summary.

## 8. Ideal Production Design

1. Every layer input has a declared source, artifact ID, provenance chain, and freshness status.
2. Every layer output is machine-readable where practical and accompanied by human-readable summary.
3. Every claim is tied to proof: tests, oracle checks, source facts, evidence packets, or true external approvals.
4. Every missing capability is represented as a gap/taskcard, not a stub or fake completion.
5. Layer work is repeatable, idempotent, and safe for multi-lane autonomous execution.

## 9. Verified Current Implementation

Current repository snapshot referenced by this plan family uses revision `a7744cf6` and layer plan date `2026-06-29`. The layer already has metadata, dependencies, and at least a minimal next action. Some original files were shallow; this revision fills the operational sections so future agents can execute without guessing.

Known current state for this layer:

- Status: `HARDENING_REQUIRED`.
- Health: `DEGRADED`.
- Stage: `ARCHITECTURE_REPAIR`.
- Maturity: `2/5`.
- Existing evidence paths: `['registry/source-structure-baseline.json', 'docs/code-quality/production-library-standard-v2.md', 'reports/r90/product-code-change-ledger.json']`.

## 10. Current Execution Stage

`ARCHITECTURE_REPAIR`. Work may proceed only after skill coverage is checked. If no skill covers a required action, the agent must write a skill-gap report and stop the uncovered portion while continuing any covered work.

## 11. Current Maturity Assessment

Maturity is currently **2**. This means the layer has enough structure to guide work, but it still needs stronger proof, backfill, automation, or registry enforcement before it can be treated as fully production-grade.

## 12. Target Maturity

Target maturity is **5**. The target state is a governed, evidence-backed, discoverable, repeatable layer that can run inside autonomous supervisor trains without relying on chat memory alone.

## 13. Current Strengths

- The project has strong governance expectations: skill-first execution, taskcards, evidence declarations, negative controls, and review gates.
- Several mature layers already prove the 39-section pattern used here.
- The user has clarified key architecture principles: spec-first SAL, RCAL proof graph, QName hierarchy, no stubs, dogfood exports, and stage-aware reporting.

## 14. Gap Register

- User flagged .NET products as monolithic single-class parse/export implementations.
- Python products are also monolithic and disconnected from the .NET object model.
- Class names and namespaces must follow spec QName hierarchy, e.g. table:table-cell becomes Table/TableCell, not arbitrary names.
- No stubs are allowed; incomplete features must be explicit gaps, not fake methods.

## 15. Root-Cause Register

- Earlier sprint plans sometimes converted governance into prose without executable registries or validators.
- Some product work was driven by manually chosen goals instead of deterministic spec/capability gaps.
- Parallel autonomous execution requires stronger ownership, evidence, and continuation contracts than a single-agent prompt.

## 16. Repair Architecture

- Convert layer prose into taskcards and registry entries.
- Bind each taskcard to upstream facts, owned paths, required skills, validators, and evidence outputs.
- Run pilot formats first, then backfill across the portfolio only after proof and rollback are ready.
- Feed audit findings back into the plan/harden/execute/audit/expand loop.

## 17. Schemas and Contracts

Required contracts:

- Layer metadata block remains valid YAML.
- Taskcard IDs use the existing `TC-*` convention.
- Evidence declarations must include provenance, produced artifacts, validation commands, and verdict.
- Gaps must be explicit and machine-trackable where possible.

## 18. Producers

- Planning/hardening agents.
- Supervisor coordinator lane.
- Product/healing lanes.
- Audit/reviewer lanes.
- Registered skills and command wrappers listed in this layer metadata.

## 19. Consumers

- Product implementation agents.
- Certification/audit layer.
- Evidence/review layer.
- Future continuation sessions.
- Human reviewer only where a true external gate applies.

## 20. Skills and Commands

Current skill IDs: `['add-python-api', 'add-dotnet-api', 'add-dotnet-object-model-feature', 'add-python-object-model-feature', 'add-same-format-writer-feature', 'decompose-monolithic-codec']`.

Current command IDs: `['add-python-api', 'add-dotnet-api', 'add-dotnet-object-model-feature', 'add-python-object-model-feature']`.

If these are empty or incomplete, the first covered action is a skill coverage audit. Missing skills must be registered before implementation work proceeds.

## 21. Validators and Enforcement

- Validate YAML metadata and taskcard references.
- Validate that evidence paths exist or are created by the sprint.
- Validate no stub code, fake capability, or unsupported release claim is introduced.
- Validate layer-specific acceptance gates before marking work complete.

## 22. Tests and Negative Controls

- Positive controls must prove the intended layer behavior on at least one pilot format or representative fixture.
- Negative controls must prove the system rejects missing authority, missing provenance, fake facts, unsupported capabilities, and AI-only evidence.
- Regression tests must be added before broad backfill or refactor work.

## 23. Evidence and Observability

Expected evidence outputs:

- Evidence declaration for the run.
- Changed files list and source ownership record.
- Validator/test logs.
- Gap reconciliation notes.
- Final reviewer verdict: ACCEPTED, ACCEPTED_WITH_REWORK, REWORK_REQUIRED, BLOCKED_EXTERNAL, or FAILED.

## 24. Recovery and Rollback

- Before mutating source or registry files, capture current branch, revision, and changed-file status.
- Use reversible patches and isolated taskcard lanes.
- If validation fails, rollback or quarantine the lane output and create a rework taskcard.
- Do not delete or replace production artifacts without migration and verification proof.

## 25. Security and Compliance

- Respect legal/spec provenance and package publication boundaries.
- Do not expose credentials, tokens, or private evidence.
- Treat external publication, commercial sign-off, and credential-dependent actions as true external gates.

## 26. Cross-Layer Handoffs

Handoffs must include:

- Producing layer and consuming layer.
- Artifact IDs and paths.
- Evidence path.
- Known gaps and blocked external decisions.
- Exact next action.

## 27. Migration and Backfill

Backfill should run in this order:

1. Pilot proof on most mature/important target formats.
2. Audit and repair validators.
3. Expand to adjacent formats with similar structure.
4. Record every deferred item as a gap, not a stub.

## 28. Effort and Dependencies

Effort depends on upstream availability: `['L01', 'L02', 'L03', 'L14']`. When the layer has no listed dependencies, it still depends on repository governance, skill coverage, and clean working-tree preflight.

## 29. Active Taskcards

Active taskcards from metadata: `[]`.

No new active taskcard should be started until ownership, evidence, and validation are declared.

## 30. Ready Taskcards

Ready taskcards from metadata: `[]`.

Primary next task: `TC-PROD-001`.

## 31. Completed Taskcards

Completed taskcards from metadata: `[]`.

Completed work must remain linked to evidence and should not be trusted from summary text alone.

## 32. Blocked and Waiting Work

Blocked taskcards from metadata: `['TC-PROD-001']`.

A blocker is valid only when it is a true external gate, missing authority, missing skill coverage, or failed validation that requires rework.

## 33. Decision Log

- 2026-06-29: Filled this layer plan from placeholder/shallow state into the standard 39-section governed plan pattern.
- 2026-06-29: Preserved existing metadata shape and updated status, maturity, gaps, and next action according to known Format Factory project context.

## 34. Work Log

- Normalized layer purpose, scope, gaps, contracts, evidence, rollback, and completion gate.
- Added no-stub and proof-backed execution requirements.
- Connected this layer to SAL/RCAL, QName, supervisor, taskcard, evidence, and certification expectations where applicable.

## 35. Verification Log

Verification required after repository application:

- Parse every layer YAML metadata block.
- Check taskcard/register consistency.
- Confirm referenced evidence paths or create follow-up gaps.
- Run relevant governance validators and tests.

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  layer_id: L06
  handoff_date: "2026-06-29"
  status: "HARDENING_REQUIRED"
  health: "DEGRADED"
  next_task_id: "TC-PROD-001"
  next_action: "Backfill architecture maps and refactor pilot formats toward spec-derived object model decomposition with no stub classes."
```

## 37. Exact Next Actions

1. Run skill coverage check for this layer.
2. Open/create the next taskcard `TC-PROD-001`.
3. Bind the taskcard to source paths, evidence outputs, validators, and rollback plan.
4. Execute the smallest useful pilot.
5. Audit results, update gap ledger, and expand only after proof.

Layer-specific next action: **Backfill architecture maps and refactor pilot formats toward spec-derived object model decomposition with no stub classes.**

## 38. Layer Completion Gate

This layer can be marked complete only when:

- All ready taskcards are accepted or intentionally superseded with reasons.
- All gaps have owners, taskcards, or explicit external blockers.
- Evidence declarations, tests/validators, and reviewer verdicts are present.
- No stub implementation, fake fact, unsupported claim, or untraceable artifact remains.

## 39. Change History

- 2026-06-29 — Rebuilt as a complete governed layer plan using the existing 39-section project pattern and available Format Factory project context.
