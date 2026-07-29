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

Current state is `SNAPSHOT`. The next transition is not product implementation.
It is `SNAPSHOT -> CONTRACT` through capability and obligation compilation.

## Program task DAG

```text
TC-FF6-PROGRAM-TRUTH-001 [COMPLETE]
  -> TC-FF6-PROGRAM-CAPABILITIES-001 [READY]
  -> TC-FF6-PROGRAM-ARCHITECTURE-001
  -> TC-FF6-PROGRAM-TASKCARDS-001
  -> TC-FF6-PROGRAM-QUALITY-GATES-001
  -> TC-FF6-PROGRAM-REPLAY-001
  -> per-format contract/implement/verify/certify/extract tasks
```

No broad product wave may bypass these program tasks.

## Exact next task

Execute
[`TC-FF6-PROGRAM-CAPABILITIES-001.md`](../../../taskcards/TC-FF6-PROGRAM-CAPABILITIES-001.md).

### Inputs

- all six format contracts and SAL facts;
- pinned primary authority artifacts;
- target stable profiles from the execution plan;
- existing source/public API and test inventory;
- current corpus, oracle, packaging, and proof state;
- current product snapshot and goal.

### Outputs

Use the already-adopted canonical root:

```text
plans/strategic/ff6/capability-taxonomy.yaml
plans/strategic/ff6/capabilities/ipynb.yaml
plans/strategic/ff6/capabilities/ora.yaml
plans/strategic/ff6/capabilities/nrrd.yaml
plans/strategic/ff6/capabilities/xliff.yaml
plans/strategic/ff6/capabilities/safetensors.yaml
plans/strategic/ff6/capabilities/ubl.yaml
plans/strategic/ff6/obligations/ipynb.yaml
plans/strategic/ff6/obligations/ora.yaml
plans/strategic/ff6/obligations/nrrd.yaml
plans/strategic/ff6/obligations/xliff.yaml
plans/strategic/ff6/obligations/safetensors.yaml
plans/strategic/ff6/obligations/ubl.yaml
plans/strategic/ff6/capability-coverage.yaml
plans/strategic/ff6/current-gaps.yaml
```

Do not create a competing `plans/programs/ff6` root.

### Atomic steps

1. Pin and hash every authority used by each stable profile.
2. Compile every normative MUST, MUST NOT, REQUIRED, conditional requirement,
   optional stable module, and rejection rule into a stable obligation ID.
3. Compile developer-use capabilities across read, write, validate, edit,
   inspect, transform, preserve, security, resource, streaming, lazy/random
   access, deterministic output, adapters, and format-native workflows.
4. Classify every capability exactly once as `STABLE_REQUIRED`,
   `OPTIONAL_ADAPTER_REQUIRED`, `PREVIEW_ISOLATED`, or
   `EXCLUDED_WITH_AUTHORITY`.
5. Map each capability to authority facts and normative obligations.
6. Map observed public/source symbols as current candidates, never as proof.
7. Define model invariants, preservation and error contracts, security limits,
   performance budgets, optional dependencies, tests, fixtures, oracles,
   documentation, proof nodes, invalidation inputs, and task ownership.
8. Mark unsupported and preview behavior explicitly.
9. Reject duplicates, missing fields, foreign-format facts, unresolved aliases,
   dangling edges, and mandatory obligations with no future task owner.
10. Reconcile counts from authority to obligations to capabilities with zero
    omitted and zero unclassified.
11. Run compilation three times from clean inputs and compare canonical bytes.
12. Append verified controller events and select the architecture task.

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
