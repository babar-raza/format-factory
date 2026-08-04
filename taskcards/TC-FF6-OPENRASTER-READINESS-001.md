---
artifact_id: TC-FF6-OPENRASTER-READINESS-001
artifact_type: taskcard
path: taskcards/TC-FF6-OPENRASTER-READINESS-001.md
format_id: ora
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
  trigger: openraster-authority-contract-corpus-policy-or-package-change
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-ORA-PROFILE-SURFACE-001
status: DEFERRED_WITH_CAPPED_PREPARATION
lane: OPENRASTER
skill_ids:
  - build-product-context
  - research-format-contract-sources
  - ingest-spec-sal
  - run-oracle
  - product-source-task
release_blockers:
  - product_source_gate_revalidation
notes: Product source is absent; preparation is capped to the first secure archive/model slice and cannot be represented as implementation progress.
---

# TC-FF6-OPENRASTER-READINESS-001: Prepare OpenRaster production implementation

## Recovery-route disposition

**Status:** `DEFERRED_WITH_CAPPED_PREPARATION`.

OpenRaster follows IPYNB, XLIFF, and UBL in the default recovery order because
its source is absent and its draft authority needs application interoperability
evidence. Read-only preparation is capped at the authority, legal corpus, ZIP
threat model, and RED inputs required for the first secure archive/model slice.
Do not build the complete application matrix or package architecture before the
exact source gate and first vertical card are ready.

## Objective and boundary

Close the evidence and architecture prerequisites for a new OpenRaster package
covering named 0.0.3, 0.0.4, and 0.0.5 interoperability profiles. OpenRaster
currently has no product source; contract/profile work is not implementation.
This card may prepare authority, corpus, oracle, architecture, RED tests, and
source taskcards but may not create `src/python/openraster/` until the repository
source-creation gate is revalidated for the exact task.

## Inputs and outputs

Bind the complete pinned OpenRaster draft/profile authority set, current
contract/capability/obligation manifests, licensing records, ZIP/PNG/XML
security policies, Pillow-compatible rendering adapter decision, package
namespace chassis, and independently produced ORA samples. Outputs are hashed
authority/corpus manifests, interoperability matrices, architecture decisions,
RED-test fixtures, and exact vertical implementation taskcards.

## Ordered work

1. Revalidate every profile authority digest and distinguish normative draft,
   application convention, and optional extension. Record uncertainty.
2. Acquire licensed immutable corpora from at least two ORA-producing
   applications. Record producer/version, license, source URL, digest, expected
   feature surface, and independent provenance. Synthetic archives cannot be
   the only evidence.
3. Enumerate required ZIP behavior: first uncompressed `mimetype`, duplicates,
   path traversal, absolute paths, case collisions, symlinks, bombs, member and
   total limits, XML entity/DTD controls, PNG validation, truncation, and
   deterministic ordering/timestamps/metadata.
4. Define only the model and security boundary needed for the first secure
   probe/load plus stack XML vertical slice. Record other model/rendering work
   in the current gap projection.
5. Acquire at least one independently produced discriminating sample for the
   first slice; the two-application read/write matrix remains required before
   interoperability certification.
6. Write the first RED tests and one exact vertical implementation taskcard.
7. Re-run the explicit source-creation policy gate only when that exact card is
   next. A failed gate records a
   current blocker but does not discard prepared evidence or stop other formats.

## Acceptance and verification

- [ ] Authority/profile claims are pinned, licensed, and uncertainty-labelled.
- [ ] Two independently produced application corpora are hashed and redistributable or test-access controlled.
- [ ] Complete ZIP/XML/PNG threat matrix and resource policies exist.
- [ ] Architecture and public API boundaries meet the common package contract.
- [ ] Interoperability matrices cover read and write, not only ZIP presence.
- [ ] RED tests and residual cards own every mandatory obligation.
- [ ] Source absence remains explicit and no certification/progress is fabricated.
- [ ] Source creation occurs only after a current governed gate passes.

Verify authority closure, corpus licenses/digests, archive negative controls,
cross-application sample inspection, deterministic generated reports, taskcard
referential integrity, and independent review of the rendering/compositing
semantics. Universal conformance must not be claimed from an early draft.
