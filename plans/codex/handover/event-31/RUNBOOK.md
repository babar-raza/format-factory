---
artifact_id: FF6-EVENT-31-RUNBOOK
artifact_type: immutable_checkpoint_runbook
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
---

# Event 31 exact resume runbook

## Establish authority

```powershell
git fetch origin main --prune
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor 240474babf868fa141850d4ed4792d3a8269ef28 origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_committed_checkpoint.py --ref origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_handover.py
```

The detached validation proves the committed packet. The shared-worktree
validation is an ownership/drift probe. Preserve any leased or unexplained
overlay.

## Select the lane

Register a fresh provider identity and query coordination. Never reuse the
outgoing identity or its manifests.

- If the XLIFF repair scope is unowned, claim only the exact RED-derived
  paths and execute `XLF-04-BATCH-005-PARTIAL-002-B-REPAIR-001`.
- If XLIFF remains live-owned, do not wait and do not overlap. Execute only
  UBL `UBL-03-PARTIAL-002`.

## Reproduce the contradiction

Before mutation, prove all of these from committed bytes:

- Event 31 is the journal head and controller sequence is 31.
- `d99fc6bf` is present on GitLab and its mechanical artifacts reproduce.
- Only one of the two reciprocal Schematron candidates has a decision.
- The decision accepts `SAL-XLIFF-CORE-INLINE-PC-001`.
- The generated row claims both XLIFF 2.0 and 2.1.
- The adjudicator rejects a valid accepted denominator ID omitted by the
  generated proposal set.
- Event 31 retains production acceptance at 26/105 and 1/1,130.

If any observation differs, create a named discrepancy and recompute the next
task from the newer committed event. Do not edit status labels.

## Repair with TDD

1. Bind the execution manifest to Event 31, commit `240474ba`, attempted
   implementation `d99fc6bf`, and the exact `NEXT-MICROSTEP.yaml` digest.
2. Write RED controls for unproposed denominator acceptance, reciprocal
   decision completeness, one-sided compilation rejection, and profile
   authority.
3. Repair the adjudicator without weakening generated-proposal disposition
   completeness.
4. Repair canonical SAL through registered `ingest-spec-sal` and
   `sal-pipeline-heal` skills.
5. Write one independent decision for each reciprocal candidate.
6. Accept only `SAL-XLIFF-CORE-INLINE-PAIRING-001`.
7. Compile at most one `xliff_2.1` pairing row unless separate pinned 2.0
   authority is proven.
8. Preserve all 26 accepted rows and all 1,130 candidate IDs.
9. Run focused, tamper, deterministic, static, authority, SAL,
   format-contract, production-program, and transcript validation.
10. Commit the bounded repair to GitLab main, replay from the immutable
    commit, append one native event, then refresh the root handover.

Mechanical count growth is not an exit criterion.
