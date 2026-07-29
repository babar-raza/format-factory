---
artifact_id: FF6-PROVIDER-EXECUTOR-INSTRUCTIONS
artifact_type: execution_handover
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
---

# Claude/Codex Shift Instructions

Resume the FF6 production mission from the clean Event 26 checkpoint. Do not
infer state from chat history, provider-local branches, local tokens, or old
handover prose.

## Locked inputs

```text
mission_id: FF6-PRODUCTION-LIBRARIES-001
canonical_forge: GitLab
canonical_remote: origin
canonical_branch: main
packet_input_checkpoint: 7fc49c290bdbfcb8c27bb8ca5c39f6f5576f242c
controller_handover_source: 18bb295f94e43338611ef88caff073eed17411c9
latest_bounded_implementation_ancestor: 7fc49c290bdbfcb8c27bb8ca5c39f6f5576f242c
controller_event_commit: 15ab7d0455e109bd88289e16d73c0835324a21ab
controller: plans/strategic/ff6/controller-state.yaml
journal: plans/strategic/ff6/events.jsonl
current_taskcard: taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md
controller_event: FF6-EVENT-000026
controller_event_hash: 34b36bf5dc4344713ac1c0f026b30e6b15fb6a63b86f4876ee98230952fabcd0
exact_next_microstep: XLF-04-BATCH-005
```

## Start procedure

1. Read `AGENTS.md` completely. If using Codex, also read
   `docs/governance/codex-adapter.md` and the canonical skill-only policy.
2. Fetch `origin`; confirm the source checkpoint is an ancestor of
   `origin/main`. GitHub is not a mission remote.
3. Inspect status and coordination. Preserve every unexplained change.
4. Run:

   ```powershell
   .venv\Scripts\python.exe plans\codex\handover\validate_handover.py --self-test
   ```

5. Re-read the product goal, execution plan, full native journal, controller,
   current gaps, active taskcard, Batch 004 artifacts, Batch 004 receipts, and
   `plans/codex/handover/CURRENT-SHIFT-HANDOVER.md` and
   `plans/codex/handover/PARALLEL-UBL-CHECKPOINT.yaml`.
6. Register a new provider-specific coordination identity. Never reuse the
   outgoing provider's token or release another agent's lease.
7. Select the registered skills required by the active task. Expected
   composition for Batch 005 is:

   - `test-driven-development`
   - `ingest-spec-sal`
   - `sal-pipeline-heal`
   - `plan-control` only after implementation evidence is committed
   - `refresh-provider-neutral-handover` only after the new native checkpoint

8. Claim exact files, create a skill execution manifest, call the mutation
   guard, preflight before each write, and record every write.

If any canonical input has advanced, recompute state and refresh the handover
before implementation. Do not ask for continuation; keep doing safe unblocked
work.

## Transfer-state discriminator

The committed Event 26 checkpoint is `RESUMABLE`, but the shared workspace was
`IN_FLIGHT_RED_NOT_TRANSFERABLE` when this packet was refreshed. Do not treat
those as contradictory or merge them into one optimistic state.

First fetch GitLab and query coordination, Git status, the controller journal,
and the two captured Batch 005 paths. Then choose exactly one case:

| Recomputed condition | Required action |
|---|---|
| Captured owner is still live and owns Batch 005 | Do not claim or mutate its scope. Do not repeat the UBL SAL repair committed at `7fc49c29`. Use a safe serialized window to record UBL-01/UBL-02, or execute another controller-authorized path-disjoint task that does not skip task state. |
| `origin/main` contains a Batch 005 implementation commit and event 27 or later | Ignore the captured test counts, validate the newer journal head, rebuild projections, and resume its computed next task. |
| `origin/main` contains a Batch 005 implementation commit but the journal remains at event 26 | Independently validate the immutable implementation commit, then use `plan-control` to append exactly one event. Do not duplicate implementation. |
| Owner is stale/dead, no commit exists, and attributable local files remain | Preserve bytes, invoke governed `takeover --reason`, recapture baselines, and continue the same RED/GREEN batch. Never release or reuse the old identity manually. |
| Prior owner completed and released its leases, no commit exists, and both optional files exactly match their recorded identities | Register a new identity, claim the logical scope and exact files, preflight/rebaseline, and adopt the preserved RED/GREEN work. No takeover is needed because no foreign lease remains. |
| No owner, no local files, no newer remote commit | Register a new identity and start Batch 005 from the clean Event 26 checkpoint. |
| Files or ownership are unexplained | Fail closed for those paths, log/reconcile the conflict, and continue non-overlapping safe work. |

At capture, the active owner was
`agent-codex-20260729T181022-74dc4a`. Its two untracked paths were
`tools/spec/xliff_core_candidate_binding.py` and
`tests/tools/test_extract_sal_facts_candidate_binding.py`. A read-only replay
returned `17 passed, 10 failed`, so the local batch was RED, not transferable.
These are observations only; the incoming provider must not inherit the agent
ID, token, or leases.

At the later packet refresh, coordination showed
`agent-codex-20260729T190440-e2dd38` actively owning the broader Batch 005
working set, including the primary extractor, primary tests, three XLIFF
reports, and Batch 005 receipts. Several tracked paths differed from HEAD.
Treat this as `ACTIVE_XLIFF_BATCH005_FOREIGN_WORKING_SET`; the packet does not
freeze those mutable bytes. Requery rather than assuming that this later
identity is still live.

The last pre-handover observation was taken at
`2026-07-29T19:27:45Z`. Local `HEAD` and `origin/main` were both
`7fc49c290bdbfcb8c27bb8ca5c39f6f5576f242c`. The recorded XLIFF process
(`PID 31488`) no longer existed, but the coordination lease remained
`ACTIVE` because its last heartbeat was only ten minutes old and its TTL was
7,200 seconds. Do not infer ownership expiry from the missing process. Only a
fresh coordination result of stale/dead plus a governed takeover permits
Claude to write those paths.

This is the expected immediate branch:

```text
newer GitLab event?
  yes -> validate new event, rebuild projections, select its next task
  no  -> XLIFF lease still live?
           yes -> preserve XLIFF bytes; do not repeat UBL closure;
                  serialize its completed evidence when safe
           no  -> lease stale with bytes?
                    yes -> governed takeover, rebaseline, resume Batch 005
                    no  -> claim exact XLIFF paths, rerun, resume Batch 005
```

Before adopting the files, verify their LF-normalized identities:

```text
tools/spec/xliff_core_candidate_binding.py
SHA-256 042c670acefff8d0a6932ea3df7f1582f887f756148dd0bdfc356f69ca56f8b7
14,443 bytes; 387 lines

tests/tools/test_extract_sal_facts_candidate_binding.py
SHA-256 fcb25b8f9400fc72a485eea23e8daf7d29e579f45a27353e3bf9a15d4c89dcb3
13,375 bytes; 427 lines
```

The handover validator checks these values when the optional files are
present and not classified as a newer active foreign working set. It does not
freeze bytes that a live owner is changing. A clean checkout may legitimately
lack them and restart Batch 005 from Event 26. A digest or Git-state mismatch
without active ownership is a preserved conflict.

The prior UBL writers are no longer active foreign owners. The package/root
census is committed at `7b5cce4f`, and the authority-closure replay is
committed at `7fc49c29`. Use those immutable commits and
[PARALLEL-UBL-CHECKPOINT.yaml](PARALLEL-UBL-CHECKPOINT.yaml), not their old
coordination identities.

## Current truth boundary

Batch 004 proves a deterministic census only for its declared selector:
direct/leaf modal Core prose, Core XSD nodes, and Core Schematron assertions.
It selected 542 candidates:

- 182 normative-prose candidates
- 264 Core XSD candidates
- 96 Core Schematron candidates
- 411 common-identical profile relations
- 19 common-changed relations
- 4 removed in XLIFF 2.1
- 108 added in XLIFF 2.1
- 0 unmapped and 0 multiply dispositioned within the declared selector
- 464 lexical/context dispositions
- 78 coarse structural fallback dispositions

This does not prove the Core obligation inventory complete. Non-modal prose is
unclassified. Candidate dispositions mention 45 of 105 expected IDs, but only
25 IDs have source-bound obligation rows and 80 remain missing. Every existing
row is `SOURCE_BOUND_UNVERIFIED`. XLF-04 is open; product certification is
0/6.

The six committed Batch 004 files are source, tests, census, and three skill
transcripts. Their existence is evidence input, not self-certification.

The UBL package/root census and authority replay are bounded evidence only.
They prove 890 package files, 91 unique document roots, three current
authority artifacts, and 34 promoted SAL facts with deterministic output.
They do not prove UBL-03 schema graph completion, a recorded task-state
transition, or any product behavior.

## Disjoint UBL resume when XLIFF is live-leased

Use this route only when coordination prevents safe XLIFF mutation. It is not
permission to skip runnable XLIFF work.

The stale-SAL repair is complete at immutable commit `7fc49c29`; do not
repeat it. Claude starts this lane by independently validating that commit,
then acquiring a safe serialized `plan-control` window to record UBL-01 and
UBL-02 without changing the canonical XLIFF task. Never take over or stage the
live XLIFF paths.

1. Register a new identity and claim only the plan-control projection paths
   after proving no live owner holds them.
2. Independently replay the current verifier:

   ```powershell
   .venv\Scripts\python.exe tools\spec\verify_sal_facts.py --format-id ubl
   ```

   Expected result:

   ```text
   PASS, 34 facts, canonical receipt SHA-256
   2cc0f2cac163b7f42ab18bbe5220837d1f49a808904ac964c536085ca6d111a0
   ```

3. Validate the three UBL closure skill receipts and the capability compiler
   with `--check --verify-idempotency`.
4. Under serialized `plan-control` ownership, append exactly one event binding
   commits `7b5cce4f` and `7fc49c29`.
5. Advance the UBL task projection through `AUTHORITY_REVALIDATED` and
   `PACKAGE_CENSUS_COMPLETE`, while retaining XLIFF as the canonical active
   controller task.
6. Commit and push that projection checkpoint independently.
7. Start UBL-03 only after event, controller, taskcard, current-state, and
   handover projections validate.

Do not rerun `--apply` merely to refresh evidence, weaken member-digest
checking, edit a status label without an event, or infer UBL-03 completion
from the package census.

## Execute XLF-04-BATCH-005

### RED: define failure before implementation

Add focused tests that initially fail for the intended missing behavior:

1. Forged normalized requirement text, authority-member digest,
   authority-source digest, and occurrence location are rejected even when
   other fields are unchanged.
2. Every candidate publishes an explicit semantic class and a
   content-sensitive occurrence digest. Digest validation binds the normalized
   content, source member, source package, profile, and occurrence location.
3. Candidate classes distinguish prose, XSD declaration/type/facet/
   cardinality/order/wildcard semantics, and Schematron assert/report
   semantics.
4. Every non-modal paragraph in the unique Core section of both pinned
   standards is classified exactly once as:
   - normative and mapped to an expected obligation;
   - normative and requiring a newly added expected obligation; or
   - non-obligation with a deterministic reason code and source location.
5. No selected or classified paragraph can disappear, duplicate, or acquire
   multiple dispositions.
6. Every one of the 78 Batch 004 coarse structural fallbacks is replaced by:
   - an exact semantic obligation mapping; or
   - an explicit reasoned non-obligation.
7. The new artifact rejects coarse fallback, unmapped candidates, duplicate
   disposition, foreign/preview profiles, invalid source digests, and
   denominator drift.
8. Denominator expansion is deterministic and preserves every existing ID.
9. All 25 current source-bound obligation rows preserve ID, authority class,
   profiles, source location, and semantic meaning.
10. Newly resolved expected IDs compile to source-bound obligation rows with
   positive and rejection evidence requirements.
11. `complete` remains false unless the full authority census, expected-ID
   closure, and canonical SAL verification conditions are all true.

Capture the RED failure and its intended reason in the TDD receipt. Do not add
tests that merely assert filenames or counts.

### GREEN and refactor

Implement the smallest coherent production pipeline in
`tools/spec/extract_sal_facts.py` and its generated FF6 reports. Keep parsing,
classification, disposition, denominator compilation, obligation compilation,
validation, and serialization separate enough to test independently.

Requirements:

- deterministic IDs and ordering;
- exact digest binding to both pinned OASIS packages and policy inputs;
- bounded ZIP/XML processing and fail-closed validation;
- semantic-token matching with boundary controls;
- no short-name substring inference;
- stable profiles only (`xliff_2.0`, `xliff_2.1`);
- no XLIFF 2.2 leakage;
- source locations sufficient for independent replay;
- canonical LF YAML and atomic replacement;
- explicit limitations and current verification status.

Do not rewrite the existing 25 rows simply to simplify generation. If an
authority contradiction is found, add a discriminating test and record it;
never choose the interpretation that merely makes tests pass.

### Verify the bounded batch

At minimum run, using the repository virtual environment:

```powershell
.venv\Scripts\python.exe -m pytest -q tests\tools\test_extract_sal_facts.py
.venv\Scripts\python.exe -m pytest -q tests\tools\test_extract_sal_facts_candidate_binding.py
.venv\Scripts\python.exe -m pytest -q tests\format_contract --deselect tests/format_contract/test_consumption_chain.py::test_full_slice_second_run_is_idempotent
.venv\Scripts\python.exe -m pytest -q tests\production_program
.venv\Scripts\python.exe -m ruff check tools\spec\extract_sal_facts.py tools\spec\xliff_core_candidate_binding.py tests\tools\test_extract_sal_facts.py tests\tools\test_extract_sal_facts_candidate_binding.py
.venv\Scripts\python.exe -m mypy --strict tools\spec\extract_sal_facts.py tools\spec\xliff_core_candidate_binding.py
.venv\Scripts\python.exe -m pyright tools\spec\extract_sal_facts.py tools\spec\xliff_core_candidate_binding.py tests\tools\test_extract_sal_facts.py tests\tools\test_extract_sal_facts_candidate_binding.py
.venv\Scripts\python.exe -m py_compile tools\spec\extract_sal_facts.py tools\spec\xliff_core_candidate_binding.py tests\tools\test_extract_sal_facts.py tests\tools\test_extract_sal_facts_candidate_binding.py
```

The exact stateful CSV test observed during the current Batch 005 audit is
`test_consumption_chain.py::test_full_slice_second_run_is_idempotent`. A full
run wrote `reports/capability-layer/gap-ledger.json` and two
`reports/format-contract-layer/csv-*.json` projections before failing. The
bytes were restored under governed rollback and verified against HEAD. Run
that test only in an isolated generated-output environment; in the shared
worktree use only the exact deselection above and never broaden it.

Before integration, the captured optional test file must reproduce exactly
`17 passed, 10 failed`. After GREEN, both focused files must pass completely.
Any other pre-integration result indicates input drift and requires
reclassification rather than editing expectations to fit it.

Run `tools/spec/extract_sal_facts.py --help` and invoke `--check` for:

- `matrix`
- `core-denominator`
- `core-obligations`
- `core-census`
- every new Batch 005 artifact

Use the pinned packages:

```text
.local/format-contracts/acquired/xliff/src-xlf-001.bin
SHA-256 aaefef5797c2387cfaaa2ca69bfeabe59fa5248535d45d3056b7fad024916055
.local/format-contracts/acquired/xliff/src-xlf-002.bin
SHA-256 73efc952aed29a31e8a6af1f985224d49c7bb67e6691fec8c2c994aa3d3d1751
```

Generate the new canonical outputs three times in clean temporary locations and
prove byte identity. Run the XLIFF authority audit and validate every skill
transcript with zero warnings.

### Checkpoint protocol

Use two commits so implementation proof cannot be confused with controller
projection:

1. Commit only the bounded Batch 005 source/tests/reports/receipts. Push to
   GitLab `main` and verify remote ancestry.
2. Recompute the native FF6 event from that immutable implementation commit.
   Append exactly one event, update controller/taskcard/current projection
   through the registered `plan-control` skill, validate the full chain, commit
   explicit files, push, and verify.
3. Refresh this provider-neutral handover through
   `refresh-provider-neutral-handover`, commit explicit packet files, push, and
   verify.

Never manually promote a product. If Batch 005 does not close XLF-04, keep the
task `WORK_IN_PROGRESS`, append the verified partial microstep, and select the
next deterministic XLF-04 batch.

## State machine

Program:

```text
DISCOVER -> SNAPSHOT -> CONTRACT -> IMPLEMENT -> VERIFY
         -> REPAIR -> CERTIFY -> EXTRACT -> RELEASE_PREP -> COMPLETE
```

Current program state is `CONTRACT`.

Batch:

```text
REVALIDATE -> RED -> GREEN -> REFACTOR -> VERIFY
           -> COMMIT_IMPLEMENTATION -> APPEND_EVENT
           -> UPDATE_PROJECTIONS -> PUSH -> REFRESH_HANDOVER -> RESUMABLE
```

Only `RESUMABLE` is a planned provider-shift boundary.

## What must be preserved

- Event journal history and hashes.
- The 17 authority records and exact bytes.
- The 110-capability / 672-obligation canonical planning universe.
- The 25 current source-bound XLIFF Core/policy rows.
- Working existing product behavior until characterized and deliberately
  migrated.
- Existing user and concurrent-agent work.
- GitLab `origin/main` as the sole execution line.

## What remains redesigned by the mission

- one authoritative ProductContract and content-addressed proof graph;
- complete dependency-closure invalidation;
- immutable fixtures and isolated certification;
- current-state gap projection rather than historical-ledger scheduling;
- independently publishable namespace packages;
- installed-wheel and external-oracle evidence;
- complete format-specific obligations and professional internal layering;
- reproducible builds, SBOM, provenance, signatures, and extraction proof.

No local prompt tweak, file-presence check, self-reported status, or synthetic
fixture alone can close these structural requirements.
