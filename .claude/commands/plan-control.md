---
version: "1.1"
last-updated: "2026-07-23"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Event append is idempotent by event_id; replay and projection are deterministic for identical inputs."
loc_budget: "Bounded by taskcard; new modules remain below repository structure limits."
test_path: "tests/plan_control/"
risk_level: HIGH
created-by: TC-FFPC-SKILL-001
product_track: infrastructure
generated_by: codex
---

# /plan-control

Implement and operate the repository-wide plan lifecycle control plane without
replacing the master plan, the coordination database, or domain-specific
evidence authorities.

## When to Use

- Build or repair `tools/plan_control/` and its deterministic projections.
- Discover, reconcile, schedule, migrate, or explain repository plans and tasks.
- Adapt existing plan-lifecycle supervisor entry points to the canonical control plane.
- Integrate read-only worktree and domain-producer observations.
- Not for product source, format contracts, packaging, release, or gate approval.
- Not for creating an unrelated planning document; use `/create-taskcard`,
  `/plan-hardening`, or `/create-permanent-layer-plan` as appropriate.

## Required Handoff

- `task_id`
- `mission_id`
- `operation`: `implement | discover | reconcile | migrate | project | integrate`
- `target_paths`
- `coordination_scope`
- `acceptance_evidence`

## Steps

1. Read `AGENTS.md`, the Codex adapter, the skill-only policy, and the current
   master-plan phase. Query skill and capability routing before mutation.
2. Register with the shared coordination CLI and claim the exact worktree,
   logical mission, and target paths. If the coordination package is absent
   from an isolated worktree but is running from the canonical shared root,
   invoke it from that root; this is not an emergency-recovery exception.
3. Inspect all active worktrees and leases read-only. Never write into, release,
   resolve, or take over another active mission's worktree or lease.
4. Classify each input as canonical integrated state or a read-only external
   occurrence. External dirty content may inform status but cannot close a task.
5. Preflight every file immediately before writing. Append the idempotent,
   hash-chained event before updating any registry, queue, or Markdown
   projection. Record every successful write.
6. Rebuild projections from the journal and compare digests. Ambiguous parsing,
   missing evidence, and partial replay remain nonterminal and create explicit
   gaps.
7. Run focused tests, deterministic replay, current-state consistency, skill
   transcript validation, and governance checks. Write the evidence declaration
   and bundle before reporting completion.
8. Release only this mission's leases and complete its coordination session.

## Output Format

```yaml
plan_control_result:
  task_id: <task>
  operation: <operation>
  changed_paths: []
  journal_head: <sha256-or-null>
  projection_digest: <sha256-or-null>
  runnable_count: 0
  blocked_count: 0
  validations: []
  evidence_bundle: <absolute-path-or-null>
```

## Allowed Paths

- `tools/plan_control/**` — implementation.
- `tests/plan_control/**` — focused tests and fixtures.
- `plans/.control/**` — committed schemas, journal, and projections.
- `tools/evidence/contracts/ff-plan-control-*.yaml` — this mission's evidence contract.
- `.local/plan-control/**`, `.local/evidences/**`, `.local/evidence-bundles/**`,
  `.local/transcripts/**` — runtime state and evidence.
- `taskcards/TC-FFPC-*.md` and `taskcards/index.yaml` — this mission's task state.
- Existing plan-lifecycle supervisor modules and their focused tests only when
  named in `target_paths` for `operation: integrate`.
- Skill, capability, command, layer, and CI registries only during the serialized
  integration lane with exact-path leases and canonical generators.

## Forbidden Paths

- `src/**`, format-specific tests, format contracts, package metadata, release
  manifests, and gate approval records.
- Any path inside another active worktree.
- Direct reads or writes to the coordination SQLite database; use its CLI.
- Cross-plan Markdown rewriting outside a declared canary or mutable canonical
  occurrence.
- Emergency bypasses justified only by urgency, a dirty tree, or an isolated
  worktree lacking uncommitted shared-root machinery.

## Mandatory Validations

- `coordination_preflight_and_write_journal_pass`
- `event_chain_and_replay_deterministic`
- `no_duplicate_plan_or_task_identity`
- `external_worktrees_read_only`
- `source_item_accounting_no_loss`
- `focused_and_governance_tests_pass`
- `skill_transcript_valid`
- `evidence_declaration_valid`

## Stop Conditions

- Stop the affected write if its lease is owned by another active mission or
  preflight reports drift; continue unrelated ready work.
- Stop projection promotion on a broken journal chain, unknown schema,
  ambiguous task structure, missing verification, or uncommitted external input.
- Defer shared-authority integration while another mission has uncommitted
  overlapping files; do not stop branch-local implementation or testing.
- Quarantine true external publication and business-approval gates without
  asking for continuation.

## Idempotency Contract

An identical command with identical canonical inputs emits no duplicate event,
task, alias, or occurrence. Replaying the same journal produces byte-identical
machine projections and stable queue ordering. A crash after event append but
before projection replacement is recovered by replay without repeating the
domain action.

## Skill-Creation Hardening Record

- RED baseline: under deadline pressure, an agent proposed an emergency
  exception and direct creation of `tools/plan_control/__init__.py` and
  `__main__.py` before skill registration.
- Counter: Step 2 and Forbidden Paths require using the already-running shared
  coordination CLI and reject isolated-worktree absence as an exception.
- REFACTOR result: the original shortcut is explicitly prohibited while
  legitimate fail-closed recovery remains possible through governed policy.
