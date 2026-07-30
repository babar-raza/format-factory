---
artifact_id: FF6-CLAUDE-EXECUTION-START-EVENT-29-RED-OVERLAY
artifact_type: execution_handoff
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
---

# Claude execution handoff — Event 29 plus bounded RED overlay

## 1. MODE

`EXECUTION MODE`.

Execute autonomously. Do not ask for continuation or confirmation. A real
external publication or business gate may block publication, but it does not
block technical work, evidence preparation, or another safe format lane.

## 2. Sprint type

`MAIN SPRINT — CONTRACT EVIDENCE / XLIFF XLF-04`.

This is not a product-source sprint. Product source and product tests remain
locked until contract/profile closure is journaled.

## 3. Sprint name

`FF6 XLIFF Batch 005 Partial 002-A — Adopt RED Overlay, Gate Obligation Compilation, and Checkpoint`.

## 4. Project and repository

```text
Project: format-factory
Repository: C:\Users\prora\OneDrive\Documents\GitHub\format-factory
Canonical forge: GitLab
Canonical remote: origin
Canonical branch: main
```

Do not use GitHub as an integration authority. Do not create or use another
branch or worktree for this transfer unless a higher repository authority
explicitly supersedes the GitLab-main-only mission rule.

## 5. Primary evidence input

The immutable evidence baseline is
[Event 29](event-29/START-HERE.md), implementation
`315efa5f5f4420202b5254c86ccd8863a91c385f`, projection
`c1f4be66b97acb9a23faa02764e3d41ec1e4a3b0`, and journal hash
`de12acdefd04c37a918e3fd27dcb8dd076f53e576ee7049cf1efc732d02028bb`.

The repository/remote head at outbound freeze is
`edcc121152e4a238b62c33180f9e733badfde4b7`. The lossless local continuation
input is [INFLIGHT-RECOVERY.yaml](INFLIGHT-RECOVERY.yaml). These are distinct:
Event 29 is current committed authority; the seven-file overlay is
content-addressed recovery input and has no controller effect.

## 6. Goal

Adopt the exact seven-file XLIFF overlay without loss, replay its
`13 passed / 1 expected RED failure` boundary, and make the obligation
compiler accept Batch 005 only when a separately validated adjudication
authorizes the obligation ID. Preserve every Event 29 candidate and every
existing obligation row. End only at a bounded GREEN, regression-tested,
committed, replayed, journaled, projected, GitLab-verified checkpoint—or
leave an equally exact `RECOVERY_REQUIRED` record if a new safe boundary
cannot be reached.

The mission-level goal remains six independently publishable,
production-grade libraries for IPYNB, OpenRaster, NRRD, XLIFF, SafeTensors,
and UBL. This sprint advances contract evidence only; it does not certify any
library.

## 7. Authorization

By running this handoff, the user authorizes Claude to:

1. Fetch and verify GitLab `origin/main`.
2. Register a fresh Claude coordination identity.
3. Adopt the seven exact recovery paths after matching their raw-byte hashes
   and Git statuses.
4. Execute the registered TDD, `ingest-spec-sal`, and `sal-pipeline-heal`
   skills for the bounded candidate.
5. Modify only exact paths claimed and authorized by fresh manifests.
6. Add the one independently adjudicated target-language obligation to the
   Batch 005 compiler path and wire the adjudication artifact into the CLI.
7. Regenerate only invalidated XLIFF evidence artifacts.
8. Run focused, affected, static, authority, determinism, transcript, and
   handover validation.
9. Commit and push the bounded implementation to GitLab `main`.
10. Replay from that immutable commit, append one native FF6 event, rebuild
    derived projections, refresh this packet, commit, and push those exact
    control files.

## 8. Not authorized

This handoff does not authorize:

1. Product implementation under `src/python/**`.
2. Product tests under `tests/python/**`.
3. Any gate, certification, approval, promotion, or release state change.
4. Reducing the 105-ID denominator to make coverage appear complete.
5. Converting generated candidate proposals into verified dispositions.
6. Editing old events or immutable `event-29/**` files.
7. Creating a GitHub PR, pushing GitHub, or using a non-main branch.
8. Releasing another provider's lease or reusing the outgoing identity.
9. Publishing packages or bypassing human-only Gate 10.

## 9. Hard prohibitions

- Never run `git reset --hard`, `git clean`, `git restore`, `git checkout --`,
  or broad `git stash`.
- Never run `git add .` or `git add -A`.
- Never overwrite a recovery path before its status and SHA-256 match
  [INFLIGHT-RECOVERY.yaml](INFLIGHT-RECOVERY.yaml).
- Never treat the local count `1/1130` as Event 29 or controller state.
- Never edit `plans/strategic/ff6/events.jsonl` before a source/evidence
  implementation commit exists and has been independently replayed.
- Never append Event 30 twice.
- Never call XLF-04, XLIFF, or any library complete from this bounded slice.
- Never allow `tools/spec/extract_sal_facts.py` to trust a bare caller-provided
  ID set without validating the adjudication artifact and its dependency
  closure at the CLI boundary.

## 10. Read first

Read completely, in this order:

1. `AGENTS.md`
2. `CLAUDE.md`
3. `plans/master-plan.md`
4. `docs/governance/skill-only-policy.yaml`
5. `plans/codex/handover/START-HERE.md`
6. `plans/codex/handover/PROVIDER-SHIFT-CONTRACT.md`
7. `plans/codex/handover/INFLIGHT-RECOVERY.yaml`
8. `plans/codex/handover/NEXT-MICROSTEP.yaml`
9. `plans/codex/handover/event-29/START-HERE.md`
10. `plans/codex/handover/event-29/RUNBOOK.md`
11. `plans/strategic/ff6/product-goal.yaml`
12. `plans/strategic/autonomous-six-python-production-execution-plan.md`
13. `plans/strategic/ff6/controller-state.yaml`
14. the complete `plans/strategic/ff6/events.jsonl`
15. `taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md`
16. `.claude/commands/test-driven-development.md`
17. `.claude/commands/ingest-spec-sal.md`
18. `.claude/commands/sal-pipeline-heal.md`

Before product architecture or source work in a future phase, also read the
spec-to-feature correction plan and verified knowledge contracts required by
AGENTS.md B2a/B2b. They are not a license to enter product work now.

## 11. Current-state verification and inbound adoption

Run:

```powershell
git fetch origin main --prune
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git rev-list --left-right --count HEAD...origin/main
git merge-base --is-ancestor 315efa5f5f4420202b5254c86ccd8863a91c385f origin/main
git merge-base --is-ancestor c1f4be66b97acb9a23faa02764e3d41ec1e4a3b0 origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_handover.py --self-test
python -m tools.supervisor.coordination --json status
```

Expected Git result before any newer event: `HEAD == origin/main`, divergence
`0 0`, `edcc121152e4a238b62c33180f9e733badfde4b7` is an ancestor of that
head, and both named implementation/event ancestry checks return zero. The
packet cannot embed the hash of the commit containing its own final bytes.

Register a fresh Claude identity. Do not reuse any identity, lease, token,
manifest, or mutation authorization named by the outgoing record. Query
coordination again. Historical OPEN conflicts may make global `status`
nonzero; classify whether any exact recovery or next-write path has a live
owner.

For all seven recovery paths, independently recompute raw-byte SHA-256 and
compare Git status and digest to `INFLIGHT-RECOVERY.yaml`. If every value
matches, claim each path plus `tools/spec/extract_sal_facts.py`. If one differs,
freeze that path, record a conflict, preserve both observations, and continue
only safe disjoint work.

Then create fresh execution manifests, call the mutation guard, and run
`preflight --file` before every write. The old Codex manifests and
authorizations are evidence of prior execution only.

## 12. Execution sections

### A. Replay the inherited RED boundary

Run:

```powershell
.venv\Scripts\python.exe -m pytest `
  tests/tools/test_xliff_core_candidate_adjudication.py `
  tests/tools/test_extract_sal_facts.py::test_batch_five_compiles_only_the_independently_adjudicated_obligation `
  -q
```

Expected: `13 passed, 1 failed`. The only failure must be
`test_batch_five_compiles_only_the_independently_adjudicated_obligation` with
`DID NOT RAISE ExtractionError`.

If the failure identity differs, do not patch toward the new symptom. Compare
all seven hashes, authority inputs, and current HEAD first.

### B. Make seed compilation fail closed

In `tools/spec/extract_sal_facts.py`:

1. Extend `_default_core_obligation_seeds` with
   `verified_obligation_ids: set[str] | None = None`.
2. Preserve default behavior through `XLF-04-BATCH-003`.
3. For `through_batch="XLF-04-BATCH-005"`, raise `ExtractionError` containing
   `independently adjudicated` unless
   `SAL-XLIFF-CORE-DOCUMENT-TARGET-LANGUAGE-001` is verified.
4. Add exactly one Batch 005 seed:
   - ID: `SAL-XLIFF-CORE-DOCUMENT-TARGET-LANGUAGE-001`
   - profiles: `xliff_2.0`, `xliff_2.1`
   - owner: `core:document`
   - category: `document_structure`
   - class: `SEMANTIC_CONSTRAINT`
   - normative level: `MUST`
   - rule: root `trgLang` is required iff target children occur under segment
     or ignorable
   - source anchor: exact Core `xliff` paragraph
   - interpretation: binds decision
     `XLF-ADJ-CORE-SCHEMATRON-0001` and SAL fact `SAL-XLIFF-00009`.
5. Do not add the four rejected proposal IDs.

The test fixture currently spells `required` lowercase while pinned authority
uses `REQUIRED`. Make the fixture and source anchor agree with the exact
authority casing, or use a narrow anchor that is stable across both profiles.
Do not weaken source-location matching globally.

Run the focused test. Expected: PASS and 26 cumulative source-bound rows in
the synthetic compilation while `complete` remains false.

### C. Bind the real CLI to adjudication proof

Write a new RED CLI control before changing CLI behavior. It must prove:

1. Batch 005 without `--adjudications` fails closed.
2. The CLI accepts `--batch-id XLF-04-BATCH-005` and an adjudication artifact.
3. Candidate, occurrence, authority member, denominator, decision, SAL store,
   SAL manifest, SAL receipt, or adjudicator drift invalidates compilation.
4. The accepted obligation set comes from validated decisions, not a raw
   untrusted list.
5. Existing Batch 003 CLI behavior remains byte-identical.

Implement `--batch-id` and `--adjudications` in
`tools/spec/extract_sal_facts.py`. Reuse the adjudication validator; do not
duplicate a weaker parser. Export a narrow validated accessor from
`tools/spec/xliff_core_candidate_adjudication.py` if needed.

### D. Regenerate only affected proof

Regenerate/check:

```powershell
.venv\Scripts\python.exe tools\spec\xliff_core_candidate_adjudication.py `
  --candidate-census reports\ff6\xliff-core-authority-candidate-census.yaml `
  --denominator reports\ff6\xliff-core-obligation-denominator.yaml `
  --sal-store shared\sal-facts\xliff.yaml `
  --sal-manifest shared\sal-facts\evidence\xliff.yaml `
  --sal-receipt reports\sal-verification\xliff.json `
  --decisions shared\sal-facts\evidence\xliff-core-candidate-decisions.yaml `
  --output reports\sal-verification\xliff-core-candidate-adjudications.yaml `
  --check
```

Then invoke the Core-obligation CLI with the new Batch 005/adjudication
arguments and update only
`reports/ff6/xliff-core-obligation-inventory.yaml`.

Required result: 26 source-bound rows, 79 missing expected rows, one locally
verified disposition, 1,129 unverified dispositions, and `complete: false`.
The 105-ID denominator does not shrink. All prior 25 IDs and their semantics
remain stable.

### E. Verification

Run the exact focused suites, all existing XLIFF extraction/candidate-binding
tests, Ruff, strict Mypy, Pyright, bytecode compilation, SAL verification,
five-source XLIFF authority audit, affected format-contract regression,
69-test production-program regression, and three clean-process deterministic
generations.

Do not count a test file or generated artifact as evidence. Capture command,
exit code, pass/fail count, source/test/artifact hashes, environment, and
installed tool versions in skill transcripts.

### F. Immutable checkpoint

Only after all declared checks pass:

1. Run coordination `precommit-check`.
2. Stage only the explicit reviewed implementation/evidence/transcript files.
3. Commit the bounded implementation with a precise Conventional Commit.
4. Push only to GitLab `origin main`.
5. Recreate/replay proof from the immutable commit.
6. Append exactly one native Event 30 describing what is verified and what
   remains open.
7. Rebuild controller/task/gap projections from the event.
8. Refresh this provider-neutral packet.
9. Validate packet hashes, links, YAML/JSON, journal, projections, GitLab
   ancestry, recovery closure, and semantic negative controls.
10. Commit and push the exact plan-control/handover files.
11. Verify `origin/main` contains both commits.
12. Release only the outgoing Claude identity's leases and complete it.

If implementation does not reach GREEN, do not append Event 30. Refresh
`INFLIGHT-RECOVERY.yaml` with new exact hashes and the first failing command.

## 13. Validation acceptance

The bounded slice passes only when:

- all seven inherited hashes were adopted exactly;
- the inherited RED failed for the same reason before mutation;
- no Batch 005 obligation compiles without validated adjudication proof;
- the single accepted target-language mapping and four explicit rejections
  survive tamper controls;
- source-bound inventory is 26/105 and remains incomplete;
- committed Event 29 baseline stays 0/1130 until Event 30 is validly appended;
- the changed proof closure is deterministic across three clean processes;
- focused, affected, static, authority, transcript, and handover checks pass;
- no product, certification, gate, promotion, or release state changes.

## 14. Taskcard updates

Keep `TC-FF6-XLIFF-PROFILE-SURFACE-001` as `WORK_IN_PROGRESS`. Keep first
unmet step `XLF-04`. Add the bounded partial result only after immutable replay
and Event 30. Do not mark Batch 005 or XLF-04 complete. Do not alter the parent
from `NEEDS_REPAIR` unless its own full acceptance criteria pass.

## 15. Evidence contract

Evidence must bind:

- Git commit/tree and GitLab ancestry;
- authority package/member/occurrence hashes;
- denominator, SAL store, SAL manifest, SAL receipt, decision-set, adjudicator,
  source, test, and generated-output hashes;
- exact commands, exit codes, selectors, Python/tool versions, OS and
  architecture;
- the built artifact only when a product package is in scope (not this slice);
- coordination identity, exact leases, clean/dirty classification, manifests,
  mutation authorization, and write receipts.

Use the three registered skill transcripts plus plan-control and handover
transcripts. A self-authored claim without executed proof is non-promoting.

## 16. Search audit

Before commit, search the changed set for:

```text
VERIFIED
complete: true
RELEASED
CERTIFIED
NOT_YET_EXECUTED
1130
1129
80
79
SOURCE_BOUND_UNVERIFIED
GitHub
codex/
```

Classify every hit. Fail if the changed packet promotes local proof, retains
stale counts in a current overlay, changes canonical forge/branch, or calls
the bounded slice complete. Historical Event 29 text may retain its original
0/1130 and 80-missing values.

## 17. Commit rules

Stage explicit reviewed paths only. Never stage `.local/**`, authority caches,
unrelated dirt, or evidence bundles. Never use broad staging. Preserve user
and foreign changes.

Suggested implementation commit:

```text
fix(xliff): gate core obligations on adjudication proof
```

Suggested checkpoint commit:

```text
docs(ff6): checkpoint XLIFF adjudication slice
```

Push only after the relevant commit is complete and replayable.

## 18. Evidence-bundle and handback rules

If repository policy requires a local evidence bundle, build it only after
the immutable checkpoint and exclude `.local` credentials/tokens. Validate
the bundle with its contract. The tracked handover remains a derived index,
not a substitute for the native event chain.

At any provider/token boundary, record:

- last clean GitLab commit;
- event ID/hash;
- exact dirty paths/statuses/hashes;
- last passing and first failing command;
- completed and first unmet microstate;
- live/stale lease classification;
- exact next file, test, and expected result;
- nonclaims and promotion effect.

## 19. Self-challenge

Answer YES or NO before handback:

1. Did I read all required authority and governance files?
2. Did I fetch and verify GitLab `origin/main`?
3. Did I register a fresh identity?
4. Did I verify all seven recovery hashes before writing?
5. Did I preserve every unexplained or foreign path?
6. Did I observe the inherited RED for the recorded reason?
7. Did I use registered skills and fresh manifests?
8. Did I preflight and record every write?
9. Did I keep generated proposals separate from independent adjudication?
10. Did I bind obligation compilation to validated proof?
11. Did I preserve all 25 existing obligation rows and the 105-ID denominator?
12. Did I keep XLF-04 and Batch 005 incomplete?
13. Did all focused and affected regression checks pass?
14. Did three clean generations match?
15. Did I avoid product source and product tests?
16. Did I avoid gate, certification, promotion, and release changes?
17. Did I avoid stash/reset/restore/checkout cleanup/clean?
18. Did I avoid broad staging?
19. Did I append at most one event and only after immutable replay?
20. Did controller, taskcard, index, gaps, proof, and packet agree?
21. Did I push only to GitLab main?
22. Is every completion claim no stronger than current evidence?

Any `NO` that violates acceptance means `NEEDS_REPAIR` or
`RECOVERY_REQUIRED`, never completion.

## 20. Final response format

Report:

1. Sprint outcome and immutable commit(s).
2. Exact files changed.
3. RED observation and GREEN result.
4. Focused, regression, static, authority, determinism, transcript, and
   handover validation results.
5. Controller event/state and task microstate.
6. Certified product count and promotion effect.
7. Git status and coordination completion.
8. Exact next microstep.
9. Evidence bundle path if one was required and validated.

End with the absolute path to the refreshed `START-HERE.md`.

Handoff quality score: `22/22` — all 20 prompt-anatomy components plus
provider-neutral identity separation and content-addressed RED recovery are
present.
