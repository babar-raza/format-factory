# Current State and Evidence Authority

**Document type:** Policy
**Phase:** 3 (applies to all phases)
**Version:** 1.0 (run041)
**Created:** 2026-05-07

---

## 1. Problem: The Self-Referential Commit-Hash Loop

Previous sprints (run036–run040) attempted to record the exact final Git HEAD commit hash inside committed
repository files (`plans/master-plan.md` and `memory/09-current-state-before-phase1.md`). This created an
infinite loop:

1. Commit X records "Latest commit: Y" (the previous commit hash).
2. X becomes the new HEAD.
3. The consistency checker reports FAIL because the file says Y but HEAD is X.
4. A new commit X' is made to record X.
5. X' becomes HEAD; the file still says X. FAIL again.
6. Repeat indefinitely.

This loop caused every sprint to end with 5–10 housekeeping commits, multiple PENDING markers, and a
consistency checker that always reported FAIL for the final committed state.

---

## 2. New Model: Stable Run-State Authority

### 2.1 Principle

**Committed repo files record run state and gate state, not exact final Git HEAD.**

The exact final Git HEAD is authoritative only in the evidence bundle metadata:
- `bundle-metadata/git-log.txt`
- `bundle-metadata/git-status-final.txt`

Reviewers who need the exact final commit for a run must inspect the evidence bundle metadata, not committed
markdown files.

### 2.2 What Committed Files Record

| Field | Format in committed files |
|---|---|
| Last completed run | `last_completed_run: runNNN` |
| Last verified run | `last_verified_run: runMMM` |
| Run commit set | Historical list (e.g. `b3cfdd7 + 2ca4b78 + ...`) — informational only |
| Final commit authority | Note: "Exact final HEAD in bundle-metadata/" |
| Gate states | Current gate status per format |
| WIP limits | Current WIP limit usage |

### 2.3 What Committed Files Must NOT Contain

| Prohibited pattern | Reason |
|---|---|
| `Latest commit: PENDING` | Implies sprint is still in progress after final commit |
| `changes pending commit` | Implies uncommitted work after sprint end |
| `run041 changes pending commit` | Same — sprint-in-progress language in final state |
| Exact final Git HEAD as a required match | Creates self-referential loop |

---

## 3. Current-State Consistency Rules

The `tools/evidence/check_current_state_consistency.py` script enforces the following invariants:

### Invariant 1: No current-looking PENDING markers in master-plan

The `**Current status:**` header section of `plans/master-plan.md` must not contain:
- `Latest commit: PENDING`
- `changes pending commit`
- `working tree dirty` (alongside any PENDING claim)

These patterns indicate the current state docs were written during an active sprint and not cleaned up.

### Invariant 2: No current-looking PENDING markers in memory/09

`memory/09-current-state-before-phase1.md` must not contain "changes pending commit" or equivalent
run-in-progress language.

### Invariant 3: FODS Gate 6 not approved

`registry/format-registry.yaml` FODS entry:
- `gate_6.approved_by` must be `null`
- `gate_6.approved_date` must be `null`
- `gate_6.status` must not be `passed`

Gate 6 is only approved by a human after oracle comparison completes.

### Invariant 4: FODT state internally consistent

If `registry/format-registry.yaml` contains a `format_id: fodt` entry:
- `gate_1.status` must be `passed`
- `registry/candidates/fodt-gate1-scoring-package.yaml` must have `gate_1_approved: true`
- `acquisition-packs/fodt/` must exist

If no `format_id: fodt` entry exists in the registry:
- `fodt-gate1-scoring-package.yaml` must have `gate_1_approved: false`
- `acquisition-packs/fodt/` must not exist

### Invariant 5: FODS pack.yaml gate_6 not approved

`acquisition-packs/fods/pack.yaml` gate_6 section must not contain `approved: true` or `status: passed`.

### Invariant 6: Final commit authority noted

The `## Section 33 — Run Commit Ledger and Evidence Authority` section must exist and must not use
language requiring repo files to contain exact HEAD hash.

---

## 4. Evidence Bundle Final-State Authority

### 4.1 Bundle metadata is the authoritative record of final Git state

Every evidence bundle produced by `tools/evidence/build_evidence_bundle.py` includes:
- `bundle-metadata/git-log.txt` — full git log at bundle build time
- `bundle-metadata/git-status-final.txt` — `git status` at bundle build time

These files record the exact Git HEAD at the time the bundle was built. No post-bundle housekeeping
commits are required.

### 4.2 Post-bundle housekeeping commits are expected and normal

After an evidence bundle is built, it is normal for additional Section 33 housekeeping commits to be
made (recording the run's commit set in the ledger). These commits do not invalidate the bundle.

The next run's independent verification step confirms the full set of commits for the prior run by
examining the git log, not by matching a hash in a markdown file.

### 4.3 Bundle validator for current-state PENDING markers

`tools/evidence/validate_evidence_bundle.py` with `--check-no-pending` scans both bundle metadata files
and the bundled repo's current-state files for prohibited PENDING patterns:
- `Latest commit: PENDING`
- `changes pending commit`
- `run\d+ changes pending commit`

Any match causes `BUNDLE_VALIDATION: FAIL`.

---

## 5. Negative Tests

The following behaviors are enforced by tests in `tests/evidence/test_current_state_consistency.py`:

| # | Scenario | Expected result |
|---|---|---|
| 1 | master-plan Current Status contains "Latest commit: PENDING" | FAIL |
| 2 | memory/09 contains "changes pending commit" | FAIL |
| 3 | FODS Gate 6 approved_by is not null | FAIL |
| 4 | FODT registry entry exists but scoring package says gate_1_approved: false | FAIL |
| 5 | Final bundle has no git-log.txt | FAIL (build-time check) |
| 6 | Clean state with no PENDING markers and consistent gate/FODT state | PASS |

---

## 6. Adoption in Evidence Contracts

All run contracts from run041 forward must include:
```yaml
# Current-state authority policy (run041+)
# Exact final Git HEAD is recorded in bundle-metadata/git-log.txt and git-status-final.txt.
# Repo files record last_completed_run, last_verified_run, run_commit_set (informational).
# Repo files must not contain "Latest commit: PENDING" in final committed state.
current_state_authority: bundle-metadata
```

---

## 7. Governance

- This document is authoritative over any conflicting guidance in earlier sprint summaries.
- This policy was introduced in run041 to fix the recursive commit-hash self-reference problem.
- Any agent that encounters a self-referential "Latest commit must equal HEAD" requirement must
  report it as a gap and apply this policy instead.
- Human approval is not required to apply this policy (it is a bug fix, not a gate).

---

## Note on Playbook Replay Reports (Proposed — Requires S-F2F-01 Human Approval)

A future playbook layer is proposed in the Full2Foss-inspired secondary sprint roadmap
(plans/secondary/full2foss-inspired-system-strengthening-plan-v2.md, S-F2F-03). If and
when the dry-run replay engine is implemented, playbook replay reports will be produced as
derived artifacts. These replay reports will carry the same authority as other evidence
bundle metadata — informational inputs only, not authoritative for gate state. Gate state
authority remains exclusively in plans/master-plan.md and the evidence bundle metadata
(bundle-metadata/git-log.txt, bundle-metadata/git-status-final.txt). A replay report
showing "PASS" does NOT constitute gate approval and does NOT supersede the DEC-034
independent verification requirement or human gate approval.
