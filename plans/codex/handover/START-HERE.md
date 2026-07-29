---
artifact_id: FF6-PROVIDER-NEUTRAL-HANDOVER-START
artifact_type: handover_entrypoint
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
---

# FF6 production mission — start here

Absolute start path:

```text
C:\Users\prora\OneDrive\Documents\GitHub\format-factory\plans\codex\handover\START-HERE.md
```

This is the only current human entrypoint for Claude, Codex, or another
governed executor. The native journal, controller, taskcards, immutable Git
commits, and evidence always outrank this derived packet.

## Current clean checkpoint

| Field | Verified value |
|---|---|
| Forge and branch | GitLab `origin/main` only |
| Latest implementation commit | `f98d220a0a3903b1107de90b2e39bf480ec4b19d` |
| Native checkpoint commit | `cde3b417` or a descendant containing Event 28 |
| Controller state | `CONTRACT` |
| Journal head | `FF6-EVENT-000028` |
| Event hash | `131631d21906c86ade3775d12504f97d8b55defb8987040a97d3f29af621713e` |
| Canonical active task | `TC-FF6-XLIFF-PROFILE-SURFACE-001` |
| Canonical microstep | `XLF-04-BATCH-005` |
| Parallel UBL task | `TC-FF6-UBL-TYPING-001` |
| UBL substate | `SCHEMA_GRAPH_ROOT_TYPE_BINDING_PARTIAL` |
| Certified libraries | `0/6` |
| Promotions | all six `UNASSESSED` |

The handover packet commit cannot embed its own final hash. A valid packet
must instead prove that its cited checkpoint commits are ancestors of fetched
GitLab `origin/main`.

## What Codex actually completed in the last shift

Codex implemented and pushed the first bounded UBL-03 graph increment:

- a digest-bound entrypoint in `tools/spec/compile_ubl_schema_graph.py`;
- a decomposed graph primitive in `tools/spec/ubl_schema_graph.py`;
- focused tests in `tests/tools/test_ubl_schema_graph.py`;
- exact parsing of all 106 XSD documents from the pinned official UBL 2.3
  package;
- unique binding of all 91 maindoc roots to declared content types;
- 182 content-addressed root/type nodes and 91 type-reference edges;
- active DOCTYPE/entity rejection without false rejection of declaration text
  inside XML comments;
- three identical official-package graph identities:
  `7b754187690ce1bb04db62657cfb552653cb381a1bdd745a56856e58215af029`;
- 14 focused and existing census tests passing;
- Ruff, Mypy, Pyright 1.1.411, and `py_compile` passing.

Implementation commit:
`f98d220a0a3903b1107de90b2e39bf480ec4b19d`.

Event 28 records this as a partial, non-promoting microstep. It does not claim
that UBL-03 is complete.

## What is not complete

The UBL graph still lacks:

- import/include closure edges;
- all reachable global and local element/attribute references;
- anonymous-type stable identities;
- sequences, choices, all-groups, model groups, and attribute groups;
- extension, restriction, substitution, and abstract semantics;
- order, occurrence, nil, default, fixed, and form rules;
- simple/complex content and all required facets;
- union/list semantics;
- wildcards and `processContents`;
- schema documentation annotations;
- complete reference/security negative controls;
- the checked-in canonical complete graph artifact;
- three clean-process, byte-identical canonical graph generations.

No format library is production-certified. OpenRaster still has no production
Python product package. Existing packages for the other five formats remain
partial. The 110-capability / 672-obligation projection is a planning
denominator, not product proof.

## Preserved XLIFF working set

Five XLIFF Batch 005 paths remain dirty and were not staged, reset, cleaned,
stashed, restored, or overwritten:

- `reports/ff6/xliff-core-authority-candidate-census.yaml`
- `tests/tools/test_extract_sal_facts.py`
- `tools/spec/extract_sal_facts.py`
- `tests/tools/test_extract_sal_facts_candidate_binding.py`
- `tools/spec/xliff_core_candidate_binding.py`

The prior owner is now `STALE_SUSPECT`. A fresh combined focused run produced
`62 passed`. That is useful recovery evidence, but it is not an immutable
implementation checkpoint, complete Batch 005 proof, or authority to commit
the bytes. The incoming executor must use governed `takeover --reason`,
recapture every baseline, rerun all required validations, create missing
receipts, and only then decide whether the working set is commit-ready.

Exact LF-normalized identities and recovery rules are in
[INFLIGHT-RECOVERY.yaml](INFLIGHT-RECOVERY.yaml).

## Deterministic next-action rule

After fetch and live coordination requery:

1. If Event 29 or later exists, validate the newer journal and rebuild this
   projection. Do not execute stale instructions.
2. If the five XLIFF paths are still live-owned, preserve them and continue
   UBL-03 at `UBL-03-PARTIAL-002` under disjoint exact-path leases.
3. If their leases are stale and the five bytes match the recovery record,
   take over the XLIFF leases with a recorded reason, recapture baselines, and
   resume Batch 005 from the preserved working set.
4. If the bytes differ, preserve both the observed filesystem state and the
   committed Event 28 boundary; investigate before any write.
5. If Batch 005 has since been committed, independently replay its immutable
   evidence before appending a new event. Never reimplement or duplicate an
   integrated commit.

At the captured state, rule 3 is expected to select XLIFF. Live state, not this
sentence, decides.

## Required reading order

1. [AGENTS.md](../../../AGENTS.md)
2. [Current Event 28 packet](event-28/START-HERE.md)
3. [Current shift handover](CURRENT-SHIFT-HANDOVER.md)
4. [Claude execution instructions](CLAUDE-START.md)
5. [Provider-shift contract](PROVIDER-SHIFT-CONTRACT.md)
6. [Current machine state](CURRENT-MACHINE-STATE.yaml)
7. [Recovery state](INFLIGHT-RECOVERY.yaml)
8. [Parallel UBL checkpoint](PARALLEL-UBL-CHECKPOINT.yaml)
9. [Product goal](../../strategic/ff6/product-goal.yaml)
10. [Autonomous execution plan](../../strategic/autonomous-six-python-production-execution-plan.md)
11. [Native controller](../../strategic/ff6/controller-state.yaml)
12. [Complete native event journal](../../strategic/ff6/events.jsonl)
13. [Active XLIFF taskcard](../../../taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md)
14. [Parallel UBL taskcard](../../../taskcards/TC-FF6-UBL-TYPING-001.md)

Historical Event 26 and Event 27 packets remain immutable rationale and
recovery inputs; they do not select current work.

## Complete supporting-document index

The following documents explain the durable design and remain required
background. They are not allowed to override a newer native event:

- [Production truth and root-cause analysis](CURRENT-STATE-AND-ROOT-CAUSES.md)
- [Program execution runbook](EXECUTION-RUNBOOK.md)
- [Provider-shift and resume protocol](SHIFT-AND-RESUME-PROTOCOL.md)
- [State-machine and taskcard protocol](STATE-MACHINE-AND-TASKCARD-PROTOCOL.md)
- [Validation, certification, and release controls](VALIDATION-AND-RELEASE.md)
- [Provider-neutral shift contract](PROVIDER-SHIFT-CONTRACT.md)
- [Event 26 historical packet](event-26/START-HERE.md)
- [Event 27 historical packet](event-27/START-HERE.md)

The repository-wide goal, task ordering, product profiles, architecture,
quality bars, exact validation commands, and known limits are deliberately
split across these documents. This entrypoint links them rather than
duplicating and silently drifting their contents.

## Resume preflight

Run from the repository root:

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

Then:

- register a new provider identity;
- never inherit the Codex identity, token, leases, local manifest, or
  mutation authorizations;
- classify all dirty paths;
- select work through the Event 28 decision rule;
- claim the exact logical scope and paths;
- create a new execution manifest;
- call the mutation guard;
- preflight before every write and record every write;
- use one RED-GREEN-REFACTOR cycle per behavior increment;
- stage explicit files only;
- push only GitLab `main`;
- finish with implementation commit, native event/projections, refreshed
  handover, validation, and released leases.

The full command-level procedure is in [event-28/RUNBOOK.md](event-28/RUNBOOK.md).

## Shift invariants

- Provider-local identity and runtime state are never authority.
- Uncommitted bytes are recovery input, never completion evidence.
- A task shift is clean only when successful work is committed and pushed,
  the native event and projections agree, and this packet validates.
- Product status is computed from proof; it is never edited into readiness.
- One blocked format does not stop disjoint safe work.
- No agent may discard unexplained or foreign changes.
- `git add .`, `git add -A`, reset, clean, broad stash, checkout, and restore
  of unexplained state are forbidden.
- Gate 10 and other human-only business authorization remain external; all
  technically possible release preparation proceeds without prompting.
