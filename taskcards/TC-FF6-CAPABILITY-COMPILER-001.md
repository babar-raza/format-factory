---
artifact_id: TC-FF6-CAPABILITY-COMPILER-001
artifact_type: taskcard
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-PROGRAM-CAPABILITIES-001
status: PASS
skill_ids:
  - validate-missing-skill-workflow
  - preflight-skill-entry
  - compile-production-capability-universe
  - validate-skill-contracts
  - sync-capabilities
  - plan-control
---

# Build the Deterministic Production Capability-Universe Compiler

## State

- Status: `PASS`
- Parent task: `TC-FF6-PROGRAM-CAPABILITIES-001` (`NEEDS_REPAIR`)
- Source defect: `FF6-GAP-012` through `FF6-GAP-015`
- Skill gap: `SKILL-GAP-FF6-CAPABILITY-UNIVERSE-001`
- Product source mutation: prohibited
- Product promotion effect: none

## Objective

Create and register one deterministic compiler that transforms canonical format
contracts, SAL fact stores, locked release-scope policy, and explicit capability
enrichment records into the complete FF6 capability and normative-obligation
universe. The compiler replaces manual YAML editing and parallel identity
families with a reproducible, fail-closed projection.

## Root cause addressed

The prior checkpoint manually copied one record per SAL fact, producing 128
parallel `OBL-*` identities while the canonical strict contract runtime produced
636 `SAL-<FORMAT>-OBL-*` obligations. It had no writer, replay command, manifest
closure, or three-run proof. Review-time checks could therefore validate internal
consistency while missing most of the actual obligation universe.

## Allowed tracked outputs

- `tools/format_contract/capability_universe.py`
- `tools/format_contract/capability_universe_command.py`
- `tools/format_contract/capability_universe_runtime.py`
- `tools/format_contract/capability_universe_validation.py`
- `tests/production_program/test_capability_universe.py`
- `schemas/ff6/capability-universe.schema.json`
- `.claude/commands/compile-production-capability-universe.md`
- `.supervisor/skill-registry.yaml`
- `.claude/commands/command-registry.yaml`
- `.supervisor/capability-routing-registry.yaml`
- capability-sync generated outputs
- `plans/strategic/ff6/capability-policy.yaml`
- `plans/strategic/ff6/capability-enrichments/*.yaml`
- `plans/strategic/ff6/capabilities/*.yaml`
- `plans/strategic/ff6/obligations/*.yaml`
- `plans/strategic/ff6/capability-taxonomy.yaml`
- `plans/strategic/ff6/capability-coverage.yaml`
- `plans/strategic/ff6/capability-manifest.json`
- `plans/strategic/ff6/current-gaps.yaml`
- `plans/strategic/ff6/controller-state.yaml`
- `plans/strategic/ff6/events.jsonl`
- this taskcard, the parent taskcard, and `taskcards/index.yaml`
- governed transcripts and local evidence

All `src/**`, product tests, package/release metadata, gate approvals, and
authority bytes are forbidden.

## Compiler contract

1. Load only repository-relative allowlisted inputs.
2. Compile obligations through `tools.format_contract.product_contract`.
3. Preserve the canonical stable obligation IDs and exact provenance edges.
4. Require one enrichment record for every authored contract capability.
5. Use only:
   `STABLE_REQUIRED`, `OPTIONAL_ADAPTER_REQUIRED`, `PREVIEW_ISOLATED`,
   `EXCLUDED_WITH_AUTHORITY`.
6. Reject missing fields, empty future references not explicitly `PLANNED`,
   duplicate IDs, foreign format/fact/profile edges, unknown obligations,
   unowned obligations, multiple owners, and exclusions without authority plus
   user disposition.
7. Reject locked-scope conflicts, including IPYNB code execution.
8. Include every contract, SAL, policy, enrichment, compiler, and schema digest
   in `capability-manifest.json`.
9. Exclude timestamps, absolute paths, random IDs, and ordering noise from
   canonical outputs.
10. Support `--check`, `--output-dir`, and `--verify-idempotency`; check mode
    performs no writes.

## Acceptance criteria

- [x] New skill and route pass preflight, registry parity, and command validation.
- [x] Unit tests reproduce and prevent the 128/636 false close.
- [x] All six contract capability identities reconcile exactly.
- [x] All 636 current canonical obligations are emitted and owned exactly once.
- [x] OpenRaster's missing SAL/profile/surface limitations remain explicit gaps;
      they are not hidden by the 32 currently compiled obligations.
- [x] IPYNB execution is excluded with the locked no-execution disposition.
- [x] SafeTensors framework adapters are optional-adapter classified.
- [x] Every output passes schema and referential-integrity validation.
- [x] Three clean output directories are byte-identical file-for-file.
- [x] Changing each input category changes the aggregate manifest digest.
- [x] `--check` detects drift and writes nothing.
- [x] Existing production-program tests remain green; 76 unaffected
      format-contract tests pass. One CSV idempotency test fails identically at
      the pre-change commit and is not hidden or attributed to this compiler.
- [x] Parent task/controller remain unpromoted until all parent acceptance
      criteria, including authority closure, are independently satisfied.

## Verified result

- Manifest aggregate:
  `26cbe9d21cedafe70653bfaa8134ffa4e481080278e954546cf9710c97a5b00a`
- Three-run digest:
  `018c26be67ea91fe86aeb65374365b5e917eb8c0058235f999d59909bfd08943`
- Focused compiler tests: 14 passed.
- Production-program regression: 43 passed.
- Format-contract regression: 76 passed, 1 baseline-known test deselected.
- Baseline reproduction at `bebafab65e92cd8cb33892fd407d67538c2a5ce5`:
  the deselected CSV test fails with the same added-gap-id defect.
- Skill registry: 197 skills, 0 fail, 0 warning.
- Capability parity: 197 full parity, 0 missing commands, 0 orphans.
- Product promotion effect: none.

## Required validation

```text
focused compiler unit tests
production_program regression suite
format_contract regression suite
skill registry and command parity
three-run byte comparison
negative controls for missing/foreign/duplicate/unowned references
event chain and output digest verification
coordination precommit check
validated execution transcript
```

## Exit states

- `PASS`: compiler machinery is registered and proven; parent repair resumes.
- `NEEDS_REPAIR`: a compiler defect or registry inconsistency remains.
- `TECHNICALLY_BLOCKED`: only after three materially different failed repairs.

No exit state from this task certifies a format or unlocks product promotion.
