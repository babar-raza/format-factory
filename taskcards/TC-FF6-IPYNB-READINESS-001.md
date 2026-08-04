---
artifact_id: TC-FF6-IPYNB-READINESS-001
artifact_type: taskcard
path: taskcards/TC-FF6-IPYNB-READINESS-001.md
format_id: ipynb
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
  trigger: ipynb-source-test-contract-package-or-oracle-change
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-COMPACT-READINESS-001
status: DEFERRED_AFTER_REFERENCE_SLICES
lane: IPYNB
skill_ids:
  - build-product-context
  - inventory-format-dom
  - package-install-proof
  - run-oracle
  - validate-product-code-ledger
release_blockers: []
notes: Deferred until the NRRD and SafeTensors reference slices prove the batch contract; full source classification is not a prerequisite to the first IPYNB vertical slice.
---

# TC-FF6-IPYNB-READINESS-001: Establish IPYNB production readiness truth

## Recovery-route disposition

**Status:** `DEFERRED_AFTER_REFERENCE_SLICES`.

When IPYNB becomes active, select one 3-8 obligation vertical slice from the
highest security/data-loss/mandatory interoperability gap. Inventory only the
symbols, schemas, fixtures, and official `nbformat` behavior in that slice's
dependency closure. Complete 68-obligation and whole-tree classification is a
certification milestone, not a source-mutation prerequisite.

## Objective and boundary

Characterize the current IPYNB package against the compiled nbformat 4.0-4.5
contract and official `nbformat` implementation. Produce a complete KEEP,
REPAIR, REPLACE, or REMOVE decision for every public/source unit and an ordered
residual implementation queue. This card is read-only for product source and
cannot promote the package.

## Inputs and outputs

Read exact GitLab-main digests for `src/python/ipynb/**`,
`tests/python/ipynb/**`, its format contract, 25-capability/68-obligation
manifest, package metadata/locks, docs/examples, corpora, prior proof, and the
pinned official schema/`nbformat` oracle. Write only content-addressed readiness,
mapping, contradiction, installed-wheel, and residual-task reports under
`reports/ff6/` plus governed transcripts and untracked run proof.

## Ordered work

1. Bind commit/tree and the authority/contract/source/test/fixture/lock/tool/
   environment closure for the selected vertical slice; reject stale proof.
2. Inventory exports, signatures, typed notebook/cell/output/attachment/MIME
   models, metadata preservation, parser/writer, validation, version conversion,
   cell-ID handling, output clearing/filtering/normalization, CLI/docs/adapters,
   tests and fixtures.
3. Build sdist/wheel in isolation; install outside the worktree; assert all
   imports resolve from the wheel and examples run without source leakage.
4. Replay strict, preservation, rejection, semantic-roundtrip, deterministic
   serialization, resource-limit, malformed JSON/schema, duplicate cell-ID,
   unknown metadata, attachment, output, and conversion behavior.
5. Differentially test with a pinned official `nbformat` version and official
   schemas. Record disagreements; never execute notebook code.
6. Move only the selected obligations from their previous evidence-backed
   state. Leave every other obligation unchanged in the current gap projection.
7. Emit the next vertical card ordered by data loss/security, mandatory
   read/write/schema/version behavior, interoperability, packaging, public API,
   docs, and optional utilities.

## Acceptance and verification

- [ ] Every public/source unit and all 68 obligations are accounted for.
- [ ] Fresh wheel build/install/import isolation and documentation examples pass or fail explicitly.
- [ ] Official schema and `nbformat` oracle versions/digests are recorded.
- [ ] Unknown safe metadata preservation and deterministic output are tested.
- [ ] No code execution path exists or is claimed.
- [ ] Three same-input report runs are byte-identical.
- [ ] Every mandatory gap has one exact successor; no product/controller source changed.

Run focused/full installed-wheel suites, Ruff/Mypy/Pyright inventory checks,
contract/referential validation, differential tests, three-run report replay,
and detached-checkout T3 replay. Fuzz, mutation, performance, platform and
dependency matrices become mandatory residual tasks before promotion.
