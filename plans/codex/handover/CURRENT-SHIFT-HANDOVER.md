---
artifact_id: FF6-CURRENT-SHIFT-HANDOVER-EVENT-29
artifact_type: provider_shift_handover
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
---

# Codex to Claude shift handover — Event 29 plus RED recovery overlay

## Outbound freeze at 2026-07-30

The immutable controller boundary has not advanced:

```text
packet source HEAD == origin/main: edcc121152e4a238b62c33180f9e733badfde4b7
controller: CONTRACT / Event 29
certified products: 0/6
promotions: UNASSESSED for all six
```

The eventual handover commit must descend from that source HEAD. There is a
bounded seven-file local overlay above the clean Event 29 checkpoint. It is
not a clean handoff, not Event 30, and not current proof. It is
`RECOVERY_REQUIRED_RED_OBSERVED` and is intentionally preserved so Claude can
continue the same TDD cycle without repeating work or losing evidence.

What the overlay has achieved:

- independent adjudication machinery exists outside the proposal generator;
- the fixed Schematron candidate is bound to exact candidate, occurrence,
  member, package, denominator, SAL, decision, and tool hashes;
- 13 adjudication controls pass;
- only the document target-language obligation is accepted;
- four incidental/downstream proposal IDs have explicit rejection reasons;
- canonical SAL proof closure was refreshed with no claim change;
- a new compiler control is RED for the intended reason.

Exact remaining defect:

```text
test_batch_five_compiles_only_the_independently_adjudicated_obligation
FAILED: DID NOT RAISE ExtractionError
```

`tools/spec/extract_sal_facts.py::_default_core_obligation_seeds` still ignores
independent adjudication and returns only the prior 25 seeds. Claude starts
there after verifying and claiming the exact recovery bytes. Full commands and
acceptance are in [CLAUDE-START.md](CLAUDE-START.md); exact hashes are in
[INFLIGHT-RECOVERY.yaml](INFLIGHT-RECOVERY.yaml).

## Portfolio truth at transfer

| Format | Existing implementation foothold | Current production truth |
|---|---|---|
| IPYNB | typed notebook/cell/output models, codec, validation, conversion, editing | contract is DRAFT; shallow oracle and stale input closure; not certified |
| OpenRaster | authority/SAL and profile contract work | no product package, product tests, corpus, oracle, or install proof |
| NRRD | header/payload codec, attached/detached paths, encodings, limits | typed spatial depth and external oracle/package proof incomplete |
| XLIFF | Core foothold plus mature authority/candidate machinery | profile/Core/module obligation contract still incomplete; local RED overlay only |
| SafeTensors | descriptors, layout checks, mmap, writer, adapters | edge/dtype/differential/co-installation matrices incomplete |
| UBL | generic XML model, 91 root subclasses, first schema root/type graph | full reachable typed schema graph and all-root typed APIs incomplete |

The 110 capabilities and 672 obligations are planning/compiler records. They
are not executed product behavior. The durable defect is not merely missing
functions: previous machinery allowed stale status, partial proof closure,
generated/self-derived oracles, and source/test presence to appear stronger
than executed installed-package and independent interoperability evidence.
Preserve the useful source footholds, authority lock, native journal,
taskcards, content digests, and negative controls. Continue redesigning the
proof boundary, package architecture, external-oracle depth, and
installed-wheel matrices; do not paper over them with prompt wording or
locally passing smoke tests.

## Mission and invariant

Build six independently publishable, production-grade Python libraries for
IPYNB, OpenRaster, NRRD, XLIFF 2.0/2.1, SafeTensors, and UBL 2.3. Provider
changes never change the goal, state machine, task priority, evidence rules,
or exit criteria.

The current program is still in `CONTRACT`, not product implementation or
certification. All six promotions are `UNASSESSED`; certified products are
`0/6`.

## Immutable boundary

```text
implementation: 315efa5f5f4420202b5254c86ccd8863a91c385f
event/projection: c1f4be66b97acb9a23faa02764e3d41ec1e4a3b0
event: FF6-EVENT-000029
event hash: de12acdefd04c37a918e3fd27dcb8dd076f53e576ee7049cf1efc732d02028bb
controller: CONTRACT
task: TC-FF6-XLIFF-PROFILE-SURFACE-001 / WORK_IN_PROGRESS
first unmet: XLF-04
next: XLF-04-BATCH-005-PARTIAL-002_DISPOSITION_VERIFICATION_AND_OBLIGATION_COMPILATION
```

Both commits are on GitLab `origin/main`. The Event 29 baseline is clean and
replayable; the current working tree is intentionally not clean because the
seven-file RED overlay is the lossless recovery input.

## What was achieved

The prior stale five-path XLIFF working set was not blindly adopted. Codex:

1. took over stale leases through the audited coordination verb;
2. recaptured baselines and confirmed the preserved LF digests;
3. replayed 62 recovered tests;
4. identified four structural weaknesses:
   - precision labels overstated generated mapping certainty;
   - the validator trusted generated disposition fields;
   - internally consistent rehashed content was not replayed against authority;
   - ad hoc `sys.path` import mutation broke professional structure/Mypy;
5. added RED tests for honest unverified state, forged mapping metadata, and
   rehashed authority-forged content;
6. implemented deterministic disposition recomputation and full pinned-source
   replay;
7. replaced false exactness with explicit `_UNVERIFIED` precision classes;
8. moved candidate classification to a typed sibling module with
   package-first import;
9. regenerated the canonical census;
10. ran focused, regression, static, authority, transcript, and deterministic
    replay checks;
11. committed/pushed implementation, independently replayed it, then
    committed/pushed Event 29 and projections.

## Capability depth reached in this slice

The XLIFF contract compiler can now enumerate and authenticate:

- 182 modal normative prose candidates;
- 588 non-modal prose candidates;
- 264 Core XSD structural/constraint candidates;
- 96 Core Schematron assertions/reports;
- 929 common-identical, 32 common-changed, 26 removed-in-2.1, and 143
  added-in-2.1 candidate relations;
- content and occurrence hashes bound to exact authority package/member bytes;
- deterministic semantic-token/structural-class mapping proposals;
- fail-closed report validation and authority replay.

This is mature evidence machinery, not a production XLIFF library capability.
No product source changed in this shift.

## What remains and why it is hard

All 1,130 dispositions are generated proposals. They are deterministic and
source-authentic but have zero independent semantic verification. The next
work is intentionally not a bulk relabel:

- independently verify 1,130 dispositions against exact authority occurrences;
- create discriminating tests for contradictions;
- expand the expected-ID denominator when authority reveals missing behavior;
- resolve 60 expected IDs with no candidate mapping;
- compile 80 missing source-bound obligation rows while preserving the 25
  existing stable rows;
- reconcile every resulting obligation through canonical SAL;
- then continue XLF-05 through XLF-08 for all eight modules, profile ownership,
  ProductContract compilation, and deterministic verification.

Product implementation follows only after contract/profile closure. Later
waves still require production-grade source, corpora, interoperability,
fuzz/property/mutation/security/performance proof, installed wheels on Python
3.11–3.14 and three OSes, reproducible packages, SBOM/provenance/signatures,
and independent repository extraction for all six formats.

## Exact next execution

Follow [CLAUDE-START.md](CLAUDE-START.md), then the
[Event 29 runbook](event-29/RUNBOOK.md). Begin with revalidation from the
immutable commits and exact recovery hashes. Register a fresh Claude identity.
Claim the seven recovery paths, `tools/spec/extract_sal_facts.py`, and the
logical Batch 005 scope. Use registered TDD, SAL ingestion, and SAL healing
skills.

Process bounded candidate batches with stable IDs:

```text
authority occurrence
  -> independent semantic reading
  -> discriminating RED evidence
  -> mapping/denominator/obligation repair
  -> SAL verification
  -> focused and affected regression
  -> recomputed open counts
```

The exact first batch is
`XLF-04-BATCH-005-PARTIAL-002-A`, defined in
[NEXT-MICROSTEP.yaml](NEXT-MICROSTEP.yaml). It starts with candidate
`XLF-CAND-CORE-SCHEMATRON-B109E9507A685F90` and four RED controls separating
source-authentic generated proposals from independently verified semantic
adjudications. The separate adjudication machinery and those controls now
exist in the local overlay and pass. Do not restart them. Replay the 13 passing
controls, observe the one compiler RED, then gate obligation compilation and
wire the CLI to validated adjudication proof.

Do not use the candidate generator as its own oracle. Do not reduce open
counts by deleting expected IDs or calling preservation semantic support.

## UBL fallback

If another live provider owns the exact XLIFF scope, continue only disjoint UBL
work from `f98d220a`:

```text
UBL-03-PARTIAL-002
offline import/include closure
unique reference resolution
remote/path-escape/namespace/ambiguity negative controls
```

Keep `reachable_schema_graph_complete: false` and do not mutate XLIFF files.

## Required handback

The next provider ends its shift with:

- bounded implementation commit on GitLab main;
- proof replayed from the immutable commit;
- one new native event appended before projections;
- controller/taskcard agreement;
- valid production-skill and plan-control receipts;
- refreshed provider-neutral packet and negative controls;
- explicit dirty-path classification;
- only its own leases released and session completed.

If no new verified boundary exists, Event 29 remains authoritative. Partial
work becomes content-addressed recovery input, never completion.
