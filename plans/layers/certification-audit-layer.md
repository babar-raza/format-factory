# Certification Audit Layer

```yaml
layer_metadata:
  layer_id: L28
  canonical_name: Certification Audit Layer
  canonical_slug: certification-audit-layer
  permanent_plan_path: plans/layers/certification-audit-layer.md
  schema_version: '1.0'
  plan_revision: '2'
  repository_revision: 16b454ca
  status: GOVERNED_OPERATIONAL
  health: HEALTHY
  maturity_current: 4
  maturity_target: 5
  current_stage: CERTIFICATION_HARDENING
  current_owner: null
  agent_type: null
  session_id: null
  active_sprint: null
  active_taskcards: []
  ready_taskcards:
  - TC-CERT-L-003
  blocked_taskcards: []
  completed_taskcards:
  - TC-CERT-L-001
  - TC-CERT-L-002
  dependencies:
  - L05
  - L06
  - L07
  upstream_layers:
  - L05
  - L06
  - L07
  downstream_layers:
  - L18
  skill_ids:
  - certification-assertion-scorer
  - certification-ci-gate
  - certification-cross-language-parity
  - certification-dashboard
  - certification-dotnet-assertion-scorer
  - certification-exception-checker
  - certification-fix-weak-assertions
  - certification-generate-exception-tests
  - certification-generate-security-tests
  - certification-inventory-extractor
  - certification-mutation-tester
  - certification-performance-benchmark
  - certification-stub-detector
  command_ids:
  - certification-assertion-scorer
  - certification-ci-gate
  - certification-cross-language-parity
  - certification-dashboard
  - certification-dotnet-assertion-scorer
  - certification-exception-checker
  - certification-fix-weak-assertions
  - certification-generate-exception-tests
  - certification-generate-security-tests
  - certification-inventory-extractor
  - certification-mutation-tester
  - certification-performance-benchmark
  - certification-stub-detector
  evidence_paths:
  - reports/certification/portfolio-certification-matrix.json
  - reports/certification-integration/report-integrity-audit.yaml
  - reports/certification-integration/product-verdict-review.yaml
  - reports/certification-integration/gap-reconciliation-map.yaml
  last_started_at: '2026-06-28'
  last_progress_at: '2026-07-13'
  last_updated_at: '2026-07-13'
  last_verified_at: '2026-07-13'
  last_verified_revision: 3fdaf841
  next_task_id: null
  next_action: null
  handoff_id: HO-008
```

## 1. Layer Metadata

This plan is the canonical working plan for **Certification Audit Layer** (`L28`). It replaces placeholder/stub prose with a governed layer contract, current known state, gaps, and executable next actions based on the Format Factory project memory and the existing layer-plan pattern.

## 2. Authority and Purpose

This layer owns final certification matrices, audit trails, product verdicts, gap reconciliation, and release readiness closure. Its authority is limited to its owned scope and must be exercised through registered skills, taskcards, evidence declarations, and validation gates.

## 3. Scope

- portfolio certification matrix
- product verdict review
- gap reconciliation maps
- audit reports and closure evidence

## 4. Explicit Non-Scope

- creating features
- waiving missing proof

## 5. Owned Decisions

- Defines the contracts, registries, evidence, and acceptance criteria for portfolio certification and audit closure.
- Decides whether layer work is ready, blocked, rework-required, or release/certification-ready.
- Maintains gap records instead of hiding missing implementation behind stubs or vague prose.

## 6. Upstream Inputs

- Upstream layers: `['L05', 'L06', 'L07']`.
- Dependencies: `['L05', 'L06', 'L07']`.
- Repository governance, AGENTS/CLAUDE instructions, active master/challenger plans, taskcards, and evidence bundles.
- Project memory: SAL/RCAL findings, QName hierarchy requirement, supervisor dual-pipeline model, dogfood export target, package/release constraints, and no-stub policy.

## 7. Downstream Consumers

- Downstream layers: `['L18']`.
- Autonomous supervisor lanes, product implementation lanes, audit/certification lanes, and future agents that need a discoverable layer summary.

## 8. Ideal Production Design

1. Every layer input has a declared source, artifact ID, provenance chain, and freshness status.
2. Every layer output is machine-readable where practical and accompanied by human-readable summary.
3. Every claim is tied to proof: tests, oracle checks, source facts, evidence packets, or true external approvals.
4. Every missing capability is represented as a gap/taskcard, not a stub or fake completion.
5. Layer work is repeatable, idempotent, and safe for multi-lane autonomous execution.

## 9. Verified Current Implementation

Current repository snapshot referenced by this plan family uses revision `16b454ca` and layer plan date `2026-06-29`. The layer already has metadata, dependencies, and at least a minimal next action. Some original files were shallow; this revision fills the operational sections so future agents can execute without guessing.

Known current state for this layer:

- Status: `GOVERNED_OPERATIONAL`.
- Health: `HEALTHY`.
- Stage: `CERTIFICATION_HARDENING`.
- Maturity: `3/5`.
- Existing evidence paths: `['reports/certification/portfolio-certification-matrix.json', 'reports/certification-integration/report-integrity-audit.yaml', 'reports/certification-integration/product-verdict-review.yaml', 'reports/certification-integration/gap-reconciliation-map.yaml']`.

## 10. Current Execution Stage

`CERTIFICATION_HARDENING`. Work may proceed only after skill coverage is checked. If no skill covers a required action, the agent must write a skill-gap report and stop the uncovered portion while continuing any covered work.

## 11. Current Maturity Assessment

Maturity is currently **3**. This means the layer has enough structure to guide work, but it still needs stronger proof, backfill, automation, or registry enforcement before it can be treated as fully production-grade.

## 12. Target Maturity

Target maturity is **5**. The target state is a governed, evidence-backed, discoverable, repeatable layer that can run inside autonomous supervisor trains without relying on chat memory alone.

## 13. Current Strengths

- The project has strong governance expectations: skill-first execution, taskcards, evidence declarations, negative controls, and review gates.
- Several mature layers already prove the 39-section pattern used here.
- The user has clarified key architecture principles: spec-first SAL, RCAL proof graph, QName hierarchy, no stubs, dogfood exports, and stage-aware reporting.

## 14. Gap Register

- Certification exists but must consume proof graphs and evidence bundles directly.
- Product statuses must be stage-aware and avoid overclaiming.
- Human review gates must be represented as external blockers, not failures.
- CERT-LAYER-GAP-001: Layer tasks invisible to supervisor (TC-SUP-002 TODO, confirmed 2026-07-13).
  TC-CERT-L-003 was in TODO state since 2026-06-29 and was never surfaced by the autonomous loop.
  It required manual identification and scheduling via glittery-splashing-manatee plan.
  Root cause: `generate_next_worker_prompt.py` reads next-sprint.md, not plans/layers/task-register.yaml.
  Fix requires adding G9 train group (TC-SUP-002 — deferred separate sprint).

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

Current skill IDs: `certification-assertion-scorer, certification-dashboard, certification-dotnet-assertion-scorer, certification-exception-checker, certification-fix-weak-assertions, certification-generate-exception-tests, certification-generate-security-tests, certification-inventory-extractor, certification-stub-detector` (9 skills registered via layer_promotion.py update, TC-LHEAL-004, 2026-07-13).

Current command IDs: `[]`.

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

Effort depends on upstream availability: `['L05', 'L06', 'L07']`. When the layer has no listed dependencies, it still depends on repository governance, skill coverage, and clean working-tree preflight.

## 29. Active Taskcards

Active taskcards from metadata: `[]`.

No new active taskcard should be started until ownership, evidence, and validation are declared.

## 30. Ready Taskcards

Ready taskcards from metadata: `[]`.

Primary next task: `null` (TC-CERT-L-003 CLOSED 2026-07-13 via TC-LHEAL-004).

## 31. Completed Taskcards

Completed taskcards from metadata: `['TC-CERT-L-001', 'TC-CERT-L-002', 'TC-CERT-L-003']`.

Completed work must remain linked to evidence and should not be trusted from summary text alone.

## 32. Blocked and Waiting Work

Blocked taskcards from metadata: `[]`.

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
  layer_id: L28
  handoff_date: "2026-06-29"
  status: "GOVERNED_OPERATIONAL"
  health: "HEALTHY"
  next_task_id: "TC-CERT-L-003"
  next_action: "Link certification verdicts to capability proof sufficiency and stage-aware product matrix."
```

## 37. Exact Next Actions

1. Run skill coverage check for this layer.
2. Open/create the next taskcard `TC-CERT-L-003`.
3. Bind the taskcard to source paths, evidence outputs, validators, and rollback plan.
4. Execute the smallest useful pilot.
5. Audit results, update gap ledger, and expand only after proof.

Layer-specific next action: **Link certification verdicts to capability proof sufficiency and stage-aware product matrix.**

## 38. Layer Completion Gate

This layer can be marked complete only when:

- All ready taskcards are accepted or intentionally superseded with reasons.
- All gaps have owners, taskcards, or explicit external blockers.
- Evidence declarations, tests/validators, and reviewer verdicts are present.
- No stub implementation, fake fact, unsupported claim, or untraceable artifact remains.

## 39. Maturity Criteria

### Maturity 4 (ACHIEVED — 2026-07-13)
All 13 certification tools registered as skills in skill-registry.yaml and index.yaml.
run_manager.py active — atomic run concept preventing hybrid verdicts.
MISSING_EVIDENCE semantics enforced in certification_dashboard.py.
Behavioral inject-and-verify tests present (test_tool_detection.py, test_dashboard_integrity.py).
gap_reconciler.py implemented with machine-verifiable finding → gap mappings.

Criteria are testable:
- `grep -c "skill_id: certification-" .supervisor/skill-registry.yaml` must return ≥ 13
- `python tools/certification/run_manager.py --help` exits 0
- `python -m pytest tests/certification/ -q` passes ≥ 589 tests
- `python tools/certification/gap_reconciler.py --findings reports/certification-integration/normalized-findings.yaml` exits 0

### Maturity 5 (TARGET)
5 governance validators active in governance_validators_certification.py.
gap_reconciler.py integrated with supervisor routing proof (autonomous task dispatch).
V_CERT_01–V_CERT_05 all produce correct verdicts verified by manual injection.
Idempotency confirmed: running the full certification pipeline twice produces zero delta.
Sustained autonomous routing: at least one recertification task dispatched and completed through the supervisor loop without human intervention.

## 40. Change History

- 2026-06-29 — Rebuilt as a complete governed layer plan using the existing 39-section project pattern and available Format Factory project context.
- 2026-07-13 — TC-006 (precious-wandering-lighthouse): 4 new skills registered (certification-ci-gate, certification-cross-language-parity, certification-mutation-tester, certification-performance-benchmark). maturity_current updated 3→4. Maturity 4/5 criteria defined.
