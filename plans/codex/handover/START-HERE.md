---
artifact_id: FF6-PROVIDER-NEUTRAL-HANDOVER-START
artifact_type: handover_entrypoint
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
---

# FF6 Provider-Neutral Handover: Start Here

This is the only current human entrypoint for the six-library production
mission. It is written for Claude, Codex, or another governed executor. The
canonical repository state always wins over this derived packet.

Absolute path:

```text
C:\Users\prora\OneDrive\Documents\GitHub\format-factory\plans\codex\handover\START-HERE.md
```

## Current committed checkpoint

| Field | Verified value |
|---|---|
| Forge / branch | GitLab `origin/main` only |
| Handover source checkpoint | `18bb295f94e43338611ef88caff073eed17411c9` |
| Controller Event 26 commit | `15ab7d0455e109bd88289e16d73c0835324a21ab` |
| Controller state | `CONTRACT` |
| Native event | `FF6-EVENT-000026` |
| Event hash | `34b36bf5dc4344713ac1c0f026b30e6b15fb6a63b86f4876ee98230952fabcd0` |
| Active task | `TC-FF6-XLIFF-PROFILE-SURFACE-001` |
| Task state | `WORK_IN_PROGRESS` |
| Completed task steps | `XLF-01`, `XLF-02`, `XLF-03` |
| Completed XLF-04 batches | `001`, `002`, `003`, `004` |
| First unmet step | `XLF-04` |
| Exact next microstep | `XLF-04-BATCH-005` |
| Production certifications | `0/6` |
| Promotion state | all six products `UNASSESSED` |

The packet commit that contains this file must descend from the source
checkpoint. It cannot truthfully embed its own final commit hash.

At the final refresh, the committed handover scope was clean and remote
verified, while a separately leased Batch 005 worker owned two untracked
implementation paths in the shared worktree. Those classified paths are
preserved and are not part of this handover commit.

## Mission

Produce six independently publishable, production-grade Python libraries:

- Jupyter Notebook (`format-factory-ipynb`)
- OpenRaster (`format-factory-openraster`)
- NRRD (`format-factory-nrrd`)
- XLIFF (`format-factory-xliff`)
- SafeTensors (`format-factory-safetensors`)
- OASIS UBL (`format-factory-ubl`)

The libraries and every developer-facing capability must be secure, typed,
documented, maintainable, interoperable, professionally structured, tested
against installed wheels, and supported by current digest-bound evidence.
Planning, source presence, test counts, package smoke tests, candidate routing,
or old readiness labels do not satisfy this goal.

Read the canonical [product goal](../../strategic/ff6/product-goal.yaml) and
[execution plan](../../strategic/autonomous-six-python-production-execution-plan.md)
before changing mission state.

## True current product state

The program has a deterministic 110-capability / 672-obligation planning
universe. That is a contract denominator, not implementation proof.
For the active XLIFF Core work, 25 of 105 expected IDs have source-bound
obligation rows and 80 remain missing.

| Format | Contract-stage state | Source state | Production state |
|---|---|---|---|
| IPYNB | profile surface repaired; 25 capabilities / 68 obligations | existing partial package | not certified |
| OpenRaster | profile surface repaired; 20 / 134 | no Python product package | not certified |
| NRRD | profile surface repaired; 21 / 65 | existing partial package | not certified |
| XLIFF | profile compilation in progress; 15 / 125 | existing partial package | not certified |
| SafeTensors | compiled planning surface; 11 / 86 | existing partial package | not certified |
| UBL | typing/profile repair still required; 18 / 194 | existing partial package | not certified |

All six ProductContracts remain lifecycle `DRAFT`. Five existing oracle
summaries are shallow `D0` partial evidence, the existing install proofs have
stale input closures, clean-checkout collection is not yet proven, corpus
adequacy is not proven, and OpenRaster source is absent. See
[current gaps](../../strategic/ff6/current-gaps.yaml).

## Exact next work

Resume `TC-FF6-XLIFF-PROFILE-SURFACE-001` at `XLF-04-BATCH-005`.

1. Add RED controls for the independent post-commit finding that the
   standalone census validator accepts forged normalized requirement text,
   member/source digests, and occurrence locations.
2. Bind every candidate occurrence with an explicit candidate class and a
   content-sensitive digest while preserving stable candidate identity.
3. Classify every non-modal Core prose paragraph excluded by Batch 004.
4. Replace all 78 coarse structural dispositions with an exact semantic
   mapping or an explicit, source-located, reasoned non-obligation.
5. Expand the 105-ID expected-obligation denominator when the newly classified
   authority surface exposes missing normative behavior.
6. Compile source-bound obligations for remaining expected IDs without
   changing the meaning or identity of the 25 stable rows already present.
7. Keep `complete: false` until the full Core authority surface is exhaustive,
   every expected ID has a source-bound obligation, and canonical SAL
   verification succeeds.

Do not start product source, architecture, packaging, certification,
promotion, release, or gate work. Do not skip to XLF-05 or UBL while this
mandatory XLF-04 work is safely executable.

Read [Claude/Codex execution instructions](CLAUDE-START.md), the
[active checkpoint](ACTIVE-WORK-CHECKPOINT.md), and the
[machine state](CURRENT-MACHINE-STATE.yaml) before acting. The immutable
Event 26 packet is [here](event-26/START-HERE.md).

## Resume preflight

Run from the repository root:

```powershell
git fetch origin
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor 18bb295f94e43338611ef88caff073eed17411c9 origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_handover.py --self-test
python -m tools.supervisor.coordination status
```

Proceed only when:

- the handover source checkpoint is an ancestor of fetched `origin/main`;
- the handover validator returns `valid: true`;
- the native controller and journal still select the same task/microstep;
- any local changes are classified and preserved;
- the incoming provider has registered its own coordination identity and
  claimed exact paths;
- the registered skill route and execution manifest cover every intended
  mutation.

If `origin/main` has advanced, do not blindly follow this projection. Recompute
the latest native event, controller, taskcard, gaps, proofs, and exact next
task, then refresh this packet through `/refresh-provider-neutral-handover`.

## Authority and reading order

Read these in order:

1. [AGENTS.md](../../../AGENTS.md)
2. [Codex adapter](../../../docs/governance/codex-adapter.md) when using Codex
3. [Product goal](../../strategic/ff6/product-goal.yaml)
4. [Execution plan](../../strategic/autonomous-six-python-production-execution-plan.md)
5. [Controller](../../strategic/ff6/controller-state.yaml)
6. [Complete event journal](../../strategic/ff6/events.jsonl)
7. [Current gaps](../../strategic/ff6/current-gaps.yaml)
8. [Active XLIFF taskcard](../../../taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md)
9. [Machine state](CURRENT-MACHINE-STATE.yaml)
10. [Event 26 runbook](event-26/RUNBOOK.md)

The root [manifest](manifest.yaml) binds the current packet and canonical
inputs. [Checkpoint](checkpoint.yaml) is the compact machine projection.
[Recovery](INFLIGHT-RECOVERY.yaml) describes dirty-worktree and crash cases.
[Validation](validate_handover.py) proves hashes, links, journal agreement,
task registration, GitLab ancestry, and negative controls.

## Historical documents

The following files retain deeper design background but are historical
projections. Their embedded Event 24/25 exact-next instructions are superseded
by this file and Event 26:

- [root-cause analysis](CURRENT-STATE-AND-ROOT-CAUSES.md)
- [older execution runbook](EXECUTION-RUNBOOK.md)
- [shift protocol](SHIFT-AND-RESUME-PROTOCOL.md)
- [state-machine protocol](STATE-MACHINE-AND-TASKCARD-PROTOCOL.md)
- [validation and release notes](VALIDATION-AND-RELEASE.md)
- [Event 25 packet](event-25/START-HERE.md)

Use them for rationale only. Never select work from a historical packet.

## Shift invariants

- One writer owns the active task at a time.
- Provider identities, tokens, leases, local manifests, and uncommitted state
  are never transferred as authority.
- Every shift ends only at a `RESUMABLE` boundary: successful work committed,
  pushed to GitLab `main`, native event appended, controller/task projections
  updated, and the handover refreshed and validated.
- RED-only, unjournaled, local-only, or unexplained dirty states are recovery
  states, not clean checkpoints.
- Existing user or agent work is preserved. Never reset, clean, stash, restore,
  or overwrite unexplained paths.
- Explicit file staging only. Never use `git add .` or `git add -A`.
- The next executor recomputes state from GitLab, the journal, controller,
  taskcard, proofs, and coordination plane; it does not trust conversation
  memory.
