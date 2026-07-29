---
artifact_id: FF6-CLAUDE-EXECUTION-START-EVENT-28
artifact_type: execution_runbook
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
---

# Claude execution start — FF6 Event 28

Mode: execution. Do not ask for continuation. Do not infer completion from
file presence, test count, or previous status prose.

## 1. Read before mutation

Read completely:

1. `AGENTS.md`
2. `CLAUDE.md`
3. `plans/master-plan.md`
4. `plans/codex/handover/START-HERE.md`
5. `plans/codex/handover/event-28/RUNBOOK.md`
6. `plans/codex/handover/PROVIDER-SHIFT-CONTRACT.md`
7. `plans/strategic/ff6/product-goal.yaml`
8. `plans/strategic/autonomous-six-python-production-execution-plan.md`
9. `plans/strategic/ff6/controller-state.yaml`
10. `plans/strategic/ff6/events.jsonl`
11. `taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md`
12. `taskcards/TC-FF6-UBL-TYPING-001.md`

Claude uses its ambient hooks but must still explicitly claim broad/logical
scopes. It must not inherit any Codex runtime credential.

## 2. Recompute state

Run:

```powershell
git fetch origin
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor f98d220a0a3903b1107de90b2e39bf480ec4b19d origin/main
git merge-base --is-ancestor cde3b417 origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_handover.py --self-test
python -m tools.supervisor.coordination --json status
```

Fail closed on a broken event chain, non-ancestor checkpoint, packet validation
failure, or unexplained path drift. Continue safe disjoint work when only one
format lane is unavailable.

## 3. Register and select

Register a new Claude identity. Apply this order:

```text
newer event exists
  -> validate/reproject newer state
else XLIFF stale and bytes preserved
  -> governed takeover, XLF-04-BATCH-005
else XLIFF active
  -> disjoint UBL-03-PARTIAL-002
else XLIFF clean/released
  -> claim and resume XLF-04-BATCH-005
```

Never release another identity. A stale lease is acquired only through
`takeover --reason`.

## 4. Exact XLIFF scope

Expected working paths:

```text
reports/ff6/xliff-core-authority-candidate-census.yaml
tests/tools/test_extract_sal_facts.py
tools/spec/extract_sal_facts.py
tests/tools/test_extract_sal_facts_candidate_binding.py
tools/spec/xliff_core_candidate_binding.py
```

Claim the logical Batch 005 scope and every intended report/receipt path.
Create an execution manifest covering the actual write set and use the
registered TDD, SAL ingestion/healing, and plan-control skills.

Before changing a byte:

- hash and diff all five paths;
- prove the combined focused baseline;
- inspect existing candidate classes, occurrence digests, validators, report
  schema, and incomplete conditions;
- distinguish implemented behavior from still-missing acceptance criteria.

Do not assume `62 passed` proves Batch 005 complete.

## 5. Exact UBL fallback scope

Read the UBL taskcard and commit `f98d220a`. Claim:

```text
logical:FF6-UBL-UBL03
tests/tools/test_ubl_schema_graph.py
tools/spec/ubl_schema_graph.py
tools/spec/compile_ubl_schema_graph.py
reports/ff6/ubl-reachable-schema-graph.json
required skill receipts and local transcript
```

Start with one RED test for offline import/include closure and exact reference
resolution. Continue in small cycles. Do not fold all remaining graph behavior
into one unreviewable change.

## 6. Validation

Use the exact matrices in [Event 28 runbook](event-28/RUNBOOK.md). In all
cases:

- validate primary authority digests;
- run focused, affected, static, and deterministic-replay checks;
- preserve baseline-known unrelated failures as named evidence, never as
  blanket exclusions;
- never exercise a source-tree import when installed-wheel proof is required;
- never treat synthetic fixtures as the only interoperability proof.

## 7. Commit and journal

Use three explicit commits when the work merits a checkpoint:

1. bounded implementation/evidence commit;
2. native event and projection commit;
3. provider-neutral handover refresh commit.

Before each:

- fetch GitLab;
- prove `origin/main` is an ancestor of `HEAD`;
- stage an explicit reviewed path list;
- run coordination `precommit-check`;
- never stage the five XLIFF paths while working only on UBL.

Push only `origin main`.

## 8. Stop boundary

A provider shift is `RESUMABLE` only when:

- successful work is immutable on GitLab main;
- journal and projections agree;
- this packet validates with negative controls;
- all remaining dirty paths are content-addressed and attributed;
- no product readiness or gate claim exceeds evidence;
- the outgoing provider releases only its own leases.

Otherwise leave the last valid committed checkpoint unchanged and record the
in-flight state as recovery input, not completion.
