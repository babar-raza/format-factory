# Feature Compilation Layer

```yaml
layer_metadata:
  layer_id: L14
  canonical_name: Feature Compilation Layer
  canonical_slug: feature-compilation-layer
  permanent_plan_path: plans/layers/feature-compilation-layer.md
  schema_version: '1.0'
  plan_revision: '3'
  repository_revision: a7744cf6
  status: HARDENING_REQUIRED
  health: DEGRADED
  maturity_current: 1
  maturity_target: 5
  current_stage: SKILL_REGISTERED_WIRING_PROVEN
  current_owner: null
  session_id: 923e237958c1
  active_taskcards:
  - TC-FEAT-001
  ready_taskcards: []
  blocked_taskcards: []
  completed_taskcards: []
  dependencies:
  - L03
  upstream_layers:
  - L03
  downstream_layers:
  - L06
  skill_ids:
  - capability-compiler
  command_ids:
  - /capability-compiler
  evidence_paths:
  - plans/strategic/spec-to-feature-radical-correction-plan.md
  - .claude/commands/capability-compiler.md
  - plans/layers/decision-register.yaml
  - tools/supervisor/proof_capability_taskcard_wiring.py
  last_updated_at: '2026-07-14'
  last_verified_at: '2026-07-14'
  next_task_id: TC-FEAT-001
  next_action: 'TC-EXT-009 (2026-07-14) resolved SKILL-GAP-003: capability_compiler.py
    is registered as skill_id capability-compiler, routed, and its output is wired
    into autonomous_task_generator.py''s actual candidate selection (proof script
    PASS). Maturity moved 0 -> 1 on that basis only. FEAT-GAP-001 (deep Lane-3
    batch/concept-graph compilation, format-family-plugin generalization, hundreds-of-formats
    scalability) remains OPEN and unattempted — explicitly out of TC-EXT-009 scope.
    Do NOT claim this layer or TC-FEAT-001 is complete.'
```

## 1. Layer Metadata

This plan is the canonical working plan for **Feature Compilation Layer** (`L14`). It replaces placeholder/stub prose with a governed layer contract, current known state, gaps, and executable next actions based on the Format Factory project memory and the existing layer-plan pattern.

## 2. Authority and Purpose

This layer owns the missing compiler from SAL/obligation/capability records into executable product feature tasks and code-generation/refactor plans. Its authority is limited to its owned scope and must be exercised through registered skills, taskcards, evidence declarations, and validation gates.

## 3. Scope

- feature graph compiler
- capability-to-taskcard generation
- format feature decomposition
- hundreds-of-formats scalability rules

## 4. Explicit Non-Scope

- manual one-off feature selection
- claim writing without implementation

## 5. Owned Decisions

- Defines the contracts, registries, evidence, and acceptance criteria for capability-to-feature compiler.
- Decides whether layer work is ready, blocked, rework-required, or release/certification-ready.
- Maintains gap records instead of hiding missing implementation behind stubs or vague prose.

## 6. Upstream Inputs

- Upstream layers: `['L03']`.
- Dependencies: `['L03']`.
- Repository governance, AGENTS/CLAUDE instructions, active master/challenger plans, taskcards, and evidence bundles.
- Project memory: SAL/RCAL findings, QName hierarchy requirement, supervisor dual-pipeline model, dogfood export target, package/release constraints, and no-stub policy.

## 7. Downstream Consumers

- Downstream layers: `['L06']`.
- Autonomous supervisor lanes, product implementation lanes, audit/certification lanes, and future agents that need a discoverable layer summary.

## 8. Ideal Production Design

1. Every layer input has a declared source, artifact ID, provenance chain, and freshness status.
2. Every layer output is machine-readable where practical and accompanied by human-readable summary.
3. Every claim is tied to proof: tests, oracle checks, source facts, evidence packets, or true external approvals.
4. Every missing capability is represented as a gap/taskcard, not a stub or fake completion.
5. Layer work is repeatable, idempotent, and safe for multi-lane autonomous execution.

## 9. Verified Current Implementation

Current repository snapshot referenced by this plan family uses revision `a7744cf6` and layer plan date `2026-06-29`, updated `2026-07-14` by TC-EXT-009. The layer already has metadata, dependencies, and at least a minimal next action. Some original files were shallow; this revision fills the operational sections so future agents can execute without guessing.

Known current state for this layer:

- Status: `HARDENING_REQUIRED`.
- Health: `DEGRADED` (was `ABSENT`; upgraded 2026-07-14 — the compiler is now registered,
  routed, and its output is proven to reach real candidate selection, but deep
  Lane-3 batch-compilation work remains unimplemented).
- Stage: `SKILL_REGISTERED_WIRING_PROVEN` (was `DESIGN_REQUIRED`).
- Maturity: `1/5` (was `0/5`).
- Existing evidence paths: `['plans/strategic/spec-to-feature-radical-correction-plan.md', '.claude/commands/capability-compiler.md', 'plans/layers/decision-register.yaml', 'tools/supervisor/proof_capability_taskcard_wiring.py']`.

## 10. Current Execution Stage

`SKILL_REGISTERED_WIRING_PROVEN`. The formal skill-coverage gap for the existing
compiler is closed (TC-EXT-009, 2026-07-14). Deep Lane-3 batch-compilation, concept-graph,
and format-family-plugin work still has no skill coverage and no design — that work
must go through its own skill-coverage check before it proceeds.

## 11. Current Maturity Assessment

Maturity is currently **1** (raised from 0 by TC-EXT-009, 2026-07-14). This reflects
that the compiler is now a registered, routed skill whose output is proven (by a
passing focused proof script and a live dry run against real repository data) to
reach `autonomous_task_generator.py`'s actual candidate selection — not merely
annotate pre-existing goals. It does NOT reflect deep batch-compilation, Phase 4
concept-graph work, or hundreds-of-formats scalability, all of which remain
unimplemented (FEAT-GAP-001, still open). The layer still needs stronger proof,
backfill, automation, and registry enforcement before it can be treated as fully
production-grade (target: 5).

## 12. Target Maturity

Target maturity is **5**. The target state is a governed, evidence-backed, discoverable, repeatable layer that can run inside autonomous supervisor trains without relying on chat memory alone.

## 13. Current Strengths

- The project has strong governance expectations: skill-first execution, taskcards, evidence declarations, negative controls, and review gates.
- Several mature layers already prove the 39-section pattern used here.
- The user has clarified key architecture principles: spec-first SAL, RCAL proof graph, QName hierarchy, no stubs, dogfood exports, and stage-aware reporting.

## 14. Gap Register

- User explicitly identified no capability-to-feature compiler as a major project gap.
- Autonomous trains currently need hardcoded goals; compiler must derive work from proof gaps.
- Feature tasks must include object-model, parser, writer, tests, oracle, and documentation work.

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

Current skill IDs: `[capability-compiler]` (registered TC-EXT-009-01, 2026-07-14; resolves SKILL-GAP-003).

Current command IDs: `[/capability-compiler]` — a pipeline-tool wrapper, not an interactive user workflow; see `.claude/commands/capability-compiler.md` for invocation-mode notes.

This closes the "skill coverage audit" gap for the compiler itself. Deep Lane-3 batch-compilation work (Phase 4 concept-graph, format-family-plugin generalization) has no registered skill yet and remains a future gap if/when that work is scoped.

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

Effort depends on upstream availability: `['L03']`. When the layer has no listed dependencies, it still depends on repository governance, skill coverage, and clean working-tree preflight.

## 29. Active Taskcards

Active taskcards from metadata: `['TC-FEAT-001']`.

TC-FEAT-001 is IN_PROGRESS, not CLOSED. Its SKILL-GAP-003 portion (skill registration
+ routing + candidate-selection wiring) is done as of TC-EXT-009 (2026-07-14); its
FEAT-GAP-001 portion (deep Lane-3 batch/concept-graph compilation, format-family-plugin
generalization, hundreds-of-formats scalability rules) remains open and unattempted.
See `plans/layers/task-register.yaml`'s `partial_closure_note` for the exact boundary.

## 30. Ready Taskcards

Ready taskcards from metadata: `[]`. TC-FEAT-001 moved from blocked to active (see above)
rather than ready, since its remaining FEAT-GAP-001 scope still needs design work
before it can be picked up as a bounded, executable taskcard.

## 31. Completed Taskcards

Completed taskcards from metadata: `[]`.

Completed work must remain linked to evidence and should not be trusted from summary text alone.
No taskcard under this layer is fully CLOSED yet — TC-EXT-009 closed the skill-gap
portion of TC-FEAT-001 only, not the whole taskcard.

## 32. Blocked and Waiting Work

Blocked taskcards from metadata: `[]`. TC-FEAT-001 is no longer blocked on missing
skill coverage (SKILL-GAP-003 resolved) — it is now IN_PROGRESS with an open,
narrower remaining scope (FEAT-GAP-001).

A blocker is valid only when it is a true external gate, missing authority, missing skill coverage, or failed validation that requires rework.

## 33. Decision Log

- 2026-06-29: Filled this layer plan from placeholder/shallow state into the standard 39-section governed plan pattern.
- 2026-06-29: Preserved existing metadata shape and updated status, maturity, gaps, and next action according to known Format Factory project context.
- 2026-07-14 (TC-EXT-009): Decided to register the ALREADY-EXISTING `tools/supervisor/capability_compiler.py`
  (521 lines, phases 0/1/2/3/3.5/6/7/8 implemented) as a formal skill rather than
  writing a new compiler, since the prior SKILL-GAP-003 closure attempt
  (`.supervisor/skill-gap-003-closure-proof.yaml`, 2026-07-12) had declared the gap
  `DEFERRED_BY_DESIGN` without ever removing it from the 3 gating registries. See
  `plans/layers/decision-register.yaml` DEC-030..DEC-036 for the full disposition of
  this compiler and 6 related/duplicate files, including a flagged (not fixed)
  sys.path shadowing finding in DEC-036.

## 34. Work Log

- Normalized layer purpose, scope, gaps, contracts, evidence, rollback, and completion gate.
- Added no-stub and proof-backed execution requirements.
- Connected this layer to SAL/RCAL, QName, supervisor, taskcard, evidence, and certification expectations where applicable.
- 2026-07-14 (TC-EXT-009): Registered `capability-compiler` skill
  (`.claude/commands/capability-compiler.md`); added its route to
  `capability-routing-registry.yaml`; closed SKILL-GAP-003 consistently in
  `work-type-skill-map.yaml`, `skill-system-baseline.yaml`, and
  `skill-registry.yaml`; added `_load_compiled_taskcards()` to
  `autonomous_task_generator.py` and wired it into `generate_task_candidates()`'s
  actual candidate pool (verified live: 2 real pre-existing compiled taskcards with
  `advisory_only: false` surfaced as candidates in a dry run, plus a synthetic proof
  in `tools/supervisor/proof_capability_taskcard_wiring.py`, PASS). Deep Lane-3
  batch-compilation work is explicitly NOT part of this work log entry.

## 35. Verification Log

Verification required after repository application:

- Parse every layer YAML metadata block.
- Check taskcard/register consistency.
- Confirm referenced evidence paths or create follow-up gaps.
- Run relevant governance validators and tests.

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  layer_id: L14
  handoff_date: "2026-07-14"
  status: "HARDENING_REQUIRED"
  health: "DEGRADED"
  next_task_id: "TC-FEAT-001"
  next_action: "SKILL-GAP-003 portion CLOSED (TC-EXT-009): capability-compiler skill
    registered, routed, and wired into autonomous_task_generator.py candidate
    selection. FEAT-GAP-001 portion remains OPEN: design and pilot deep Lane-3
    batch/concept-graph compilation and format-family-plugin generalization for
    hundreds-of-formats scalability. Do not re-attempt the skill-registration part."
```

## 37. Exact Next Actions

1. Run skill coverage check for this layer.
2. Open/create the next taskcard `TC-FEAT-001`.
3. Bind the taskcard to source paths, evidence outputs, validators, and rollback plan.
4. Execute the smallest useful pilot.
5. Audit results, update gap ledger, and expand only after proof.

Layer-specific next action: **Design and pilot the 9-phase feature compiler on FODS/FODT/ZST, then generalize to Python reduced/FOSS products.**

## 38. Layer Completion Gate

This layer can be marked complete only when:

- All ready taskcards are accepted or intentionally superseded with reasons.
- All gaps have owners, taskcards, or explicit external blockers.
- Evidence declarations, tests/validators, and reviewer verdicts are present.
- No stub implementation, fake fact, unsupported claim, or untraceable artifact remains.

## 39. Change History

- 2026-06-29 — Rebuilt as a complete governed layer plan using the existing 39-section project pattern and available Format Factory project context.
- 2026-07-14 (TC-EXT-009, plan yes-my-earlier-answer-humming-waffle) — Resolved SKILL-GAP-003
  only: registered `capability-compiler` skill, added routing, closed the gap in all
  3 gating registries, and wired compiled-taskcard output into
  `autonomous_task_generator.py`'s real candidate selection (proof script PASS).
  Maturity 0 -> 1, health ABSENT -> DEGRADED. FEAT-GAP-001 (deep Lane-3 batch
  compilation, hundreds-of-formats scalability) is explicitly NOT closed by this
  entry — see task-register.yaml TC-FEAT-001 `partial_closure_note`. `index.yaml`'s
  L14 row was intentionally NOT touched here; that update is deferred to TC-EXT-006,
  which owns a broader index.yaml pass in the same plan.
