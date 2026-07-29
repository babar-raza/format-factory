---
artifact_id: FF6-EXECUTION-RUNBOOK-001
artifact_type: autonomous_execution_runbook
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
authoritative_state: false
---

# FF6 Execution Runbook

## Mission state machine

```text
DISCOVER -> SNAPSHOT -> CONTRACT -> IMPLEMENT -> VERIFY
         -> REPAIR -> CERTIFY -> EXTRACT -> RELEASE_PREP -> COMPLETE
```

Current state is `CONTRACT`. The canonical capability compiler subtask passed,
but the parent contract task remains `NEEDS_REPAIR`. Product implementation is
still locked. Authority closure is `WORK_IN_PROGRESS` at controller event 14.

## Provider-neutral task lifecycle

Every bounded taskcard uses the same lifecycle regardless of executor:

```text
UNREGISTERED
  -> READY
  -> CLAIMED
  -> WORK_IN_PROGRESS
  -> VERIFYING
  -> PASS | NEEDS_REPAIR | TECHNICALLY_BLOCKED
  -> CLOSE_INTENT
  -> COMPLETE
```

Rules:

- `READY` means dependencies and an exact skill/allowlist exist; it does not
  mean implementation exists.
- `CLAIMED` is off-repo coordination state and cannot be inferred from Git.
- `WORK_IN_PROGRESS` must name completed substeps, exact changed files,
  digests, failing/absent gates, and next substep.
- `PASS` means the taskcard acceptance criteria pass; it does not imply product
  certification.
- `NEEDS_REPAIR` names a reproducible technical failure and schedules repair.
- `TECHNICALLY_BLOCKED` requires three materially different failed repairs for
  the same root cause; other unblocked work continues.
- `CLOSE_INTENT` is write-ahead state. Only independently replayed proof may
  produce `COMPLETE`.
- Only the hash-chained journal may change the controller projection.
- Provider/token/session changes never change lifecycle state or acceptance.

## Program task DAG

```text
TC-FF6-PROGRAM-TRUTH-001 [COMPLETE]
  -> TC-FF6-PROGRAM-CAPABILITIES-001 [NEEDS_REPAIR]
       -> TC-FF6-CAPABILITY-COMPILER-001 [PASS]
       -> TC-FF6-AUTHORITY-CLOSURE-001 [WORK_IN_PROGRESS, EVENT 14]
       -> OpenRaster profile/surface repair [NOT YET REGISTERED]
  -> TC-FF6-PROGRAM-ARCHITECTURE-001
  -> TC-FF6-PROGRAM-TASKCARDS-001
  -> TC-FF6-PROGRAM-QUALITY-GATES-001
  -> TC-FF6-PROGRAM-REPLAY-001
  -> per-format contract/implement/verify/certify/extract tasks
```

No broad product wave may bypass these program tasks.

## Exact next task

Execute
[`TC-FF6-AUTHORITY-CLOSURE-001.md`](../../../taskcards/TC-FF6-AUTHORITY-CLOSURE-001.md).

### Inputs

- `plans/strategic/ff6/capability-manifest.json`;
- all six format contracts, SAL facts, and SAL evidence stores;
- all 15 authority source declarations and expected digests;
- existing acquisition tools, spec cache, receipts, and artifact index;
- primary official endpoints, immutable versions, and license/terms evidence;
- controller event 14, `ACTIVE-WORK-CHECKPOINT.md`, and parent gaps 13/14.

### Outputs

Produce one shared authority lock/materialization contract, legal and
redistribution classifications, tracked internal product-requirement
artifacts, safe acquisition/cache machinery, focused tests, strict six-format
contract compilation, regenerated FF6 universe/manifest, proof, and atomic
controller/task/gap updates. Exact paths must be selected through the governed
authority skills and coordination preflight.

### Atomic steps

1. `[DONE]` Recompute the 15-source authority inventory; do not trust
   `ACQUIRED`.
2. `[DONE]` Reuse the existing source-research owner and select one shared
   lock/materializer design.
3. `[IN PROGRESS]` Verify official immutable endpoints, versions, expected
   digests, license, terms, and redistribution source by source. IPYNB,
   OpenRaster candidates, XLIFF, SafeTensors, and UBL candidates are recorded;
   finish NRRD and reverify all before lock creation.
4. `[PARTIAL]` Implement one shared content-addressed lock/cache/materializer,
   not six one-off download scripts. The schema/runtime/CLI exist and focused
   tests pass; redirect and concurrency hardening remain.
5. `[PARTIAL]` Make fetching temporary, size/redirect/timeout bounded,
   digest-before-place, atomic, and concurrency-safe. Size, timeout, digest,
   and basic atomicity are implemented; explicit redirect count and
   same-process concurrency proof remain.
6. `[DONE]` Convert four internal product-requirement identities into tracked
   canonical non-spec artifacts with paths and digests.
7. `[PENDING]` Create the canonical 15-source authority lock and reconcile
   contract declarations.
8. `[PENDING]` Never commit external spec bytes without affirmative redistribution
   evidence; use deterministic external cache materialization otherwise.
9. `[ONGOING INVARIANT]` Treat digest mismatch as a contradiction; never edit the expected value
   merely to accept downloaded bytes.
10. `[PENDING]` Integrate the registered source-research skill, ProductContract
    verifier, store input closure, and capability compiler.
11. `[PENDING]` Prove clean online materialization and offline matching-cache replay.
12. `[PENDING]` Compile all six ProductContracts without authority override.
13. `[PENDING]` Recompile the universe three times without
    `--allow-blocked-authority`; require all authority artifacts `MATCH`.
14. `[PENDING]` Update event/controller/task/gap projections atomically, leaving the parent
    open for OpenRaster gap 13.

### Format breadth floors

- IPYNB: nbformat 4.0 through 4.5, typed cells/outputs/attachments/MIME/metadata,
  IDs, schemas, conversion, deterministic writing, preservation, safe cleanup,
  trust inspection without execution, limits, official differential behavior.
- OpenRaster: named 0.0.3, 0.0.4 and 0.0.5 interoperability profiles, secure
  deterministic ZIP, typed stack/layer/group/mask, rendering, PNG assets,
  extensions, bomb/path/duplicate defenses, two independent applications.
- NRRD: NRRD0001 through NRRD0005, all types/endian/encodings, attached and
  detached forms, spatial metadata, raw preservation, streaming/mmap, NumPy,
  Teem and pynrrd, overflow/path/decompression/truncation defenses.
- XLIFF: 2.0/2.1 Core and every official 2.1 module, inline code, segmentation,
  state, skeleton, original data, modules, ITS, extension preservation, schema
  and processing validation, canonical XML.
- SafeTensors: every defined dtype and descriptor edge, strict layout,
  lazy mmap/random access/slicing, deterministic write, NumPy/PyTorch, sharded
  indexes, upstream differential and co-installation proof.
- UBL: all 91 UBL 2.3 roots, all common components/types/attributes/order/
  cardinality, typed parse/build/edit/write, XSD, extensions, code lists,
  streaming, signatures, curated core workflows, schema-engine validation.

## Following program tasks

### Architecture

Characterize working APIs, define split-ready package boundaries and import
direction, separate generated/handwritten source, produce migration maps, and
create decomposition cards for oversized or monolithic modules.

### Task compilation

Generate deterministic bounded implementation, verification, certification,
and extraction taskcards. Each card owns one coherent capability or 5 to 15
related obligations and an exact file allowlist.

### Quality gates

Make typing, lint, architecture, API, coverage, mutation, fuzz, security,
performance, documentation, packaging, SBOM, provenance, license, and
vulnerability gates executable and fail-closed.

### Replay

Prove three-run determinism, dependency invalidation, deleted-test revocation,
fixture mutation detection, authority staleness, foreign-fact rejection,
deferral rejection, concurrency isolation, installed-wheel import identity,
manual-promotion rejection, legacy-evidence quarantine, and extraction digest
preservation.

## Product execution order

1. SafeTensors and IPYNB.
2. NRRD and OpenRaster.
3. XLIFF.
4. UBL generator and all roots.
5. Independent repository extraction and release preparation.

Formats promote independently. A blocked format does not pause safe work on
others. The mission ends only when all six are at least release candidates or
every remaining path is a true external block after all technical work.
