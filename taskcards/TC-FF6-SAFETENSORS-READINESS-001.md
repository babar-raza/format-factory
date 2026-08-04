---
artifact_id: TC-FF6-SAFETENSORS-READINESS-001
artifact_type: taskcard
path: taskcards/TC-FF6-SAFETENSORS-READINESS-001.md
format_id: safetensors
product_family: python-format-library
visibility: internal
publish_allowed: false
license: null
provenance_required: true
provenance_status: pending-execution
source_hash: null
generated_by: codex
generated_at: 2026-08-02
reusable: false
refresh_policy:
  trigger: safetensors-source-test-contract-package-or-oracle-change
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-COMPACT-READINESS-001
status: SUPERSEDED_BY_REFERENCE_SLICE_PENDING_REVIEW
lane: SAFETENSORS
skill_ids:
  - build-product-context
  - inventory-format-dom
  - package-install-proof
  - run-oracle
  - validate-product-code-ledger
release_blockers: []
notes: Full classification-first route is superseded by a bounded SafeTensors reference slice after NRRD acceptance; prior evidence remains non-promoting input.
---

# TC-FF6-SAFETENSORS-READINESS-001: Establish SafeTensors production readiness truth

## Recovery-route disposition

**Status:** `SUPERSEDED_BY_REFERENCE_SLICE_PENDING_REVIEW`.

This card is retained as certification backlog and historical scope. It must
not run a complete 86-obligation or KEEP/REPAIR/REPLACE/REMOVE inventory before
product work. `TC-FF6-SAFETENSORS-REFERENCE-SLICE-001` owns the first bounded
source slice after NRRD acceptance. Existing source/oracle/wheel findings may
be reused only when their full input closure still matches.

## Objective and boundary

Characterize the current SafeTensors package against the exact pinned upstream
format revision and official implementation. Preserve useful work while
detecting binary safety, mmap/lazy-access, dtype, namespace, wheel, and
co-installation defects. This card is read-only for product source and cannot
promote the package.

## Inputs and outputs

Bind `src/python/safetensors/**`, `tests/python/safetensors/**`, the
11-capability/86-obligation contract, pinned official authority/implementation,
locks, docs, corpora, package metadata, prior source-only oracle result, and the
known stale-wheel collection failure. Output only content-addressed readiness,
mapping, contradiction, install/co-install, and residual-task reports.

## Ordered work

1. Capture exact closure digests and invalidate every result bound to the stale
   installed wheel or accidental source import.
2. Inventory public descriptors, dtype/shape/offset math, header parser/writer,
   lazy mmap access, metadata, sharded index support, NumPy/PyTorch adapters,
   resource limits, errors, docs, tests, fuzz seeds, and package namespaces.
3. Rebuild/install a fresh wheel; co-install official `safetensors`; prove
   `format_factory.safetensors` does not shadow the official top-level package.
4. Test every defined dtype including scalar, empty, and sub-byte/alignment
   cases; duplicate keys, UTF-8, shape/size overflow, offsets, overlap, holes,
   truncation, enormous headers, and resource-limit rejection.
5. Prove deterministic writing, lazy payload access, safe mmap lifetime, and
   adapter isolation without forcing optional dependencies.
6. Run read/write differential matrices against the pinned official release;
   retain contradictions and add discriminating residual tests.
7. Defer complete 86-obligation and source-unit classification to later
   certification milestones. After the reference slice, generate only the next
   highest-risk coherent vertical card from the current gap projection.

## Acceptance and verification

- [ ] All 86 obligations and every public/source unit have evidence or a gap.
- [ ] Fresh installed-wheel and official-package co-installation proof passes or records exact failure.
- [ ] Stale wheel/source-only results cannot satisfy readiness.
- [ ] All dtype/offset/shape/overlap/hole/truncation/resource-limit cases are classified.
- [ ] Lazy mmap ownership and deterministic writer behavior are exercised.
- [ ] Three report reruns are byte-identical.
- [ ] Every mandatory gap has an exact successor; no product/controller source changed.

Run installed-wheel tests, official differentials, contract integrity,
Ruff/Mypy/Pyright inventory, binary property/metamorphic tests available without
source mutation, three-run report replay, and detached T3 replay. Fuzz,
mutation, performance, cross-platform and dependency matrices remain mandatory
before promotion.
