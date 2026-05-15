# Memory Note 31: ZST R14 Gate 2 Spec Retrieval
Sprint: FORMAT-FACTORY-R14-ZST-SPEC-RETRIEVAL-AND-GATE2-SWARM-001
Date: 2026-05-15

## Gate 2 Status

ZST Gate 2 PASSED (R14, 2026-05-15, delegated under Babar Raza R14 execution prompt).

## Spec Cache

| Item | Value |
|------|-------|
| RFC 8878 path | .local/spec-cache/zst/rfc8878/rfc8878.txt |
| RFC 8878 SHA-256 | sha256:8ee6be03534113f5689cda75b9539a02e0704a2506d420814223e506420aeea4 |
| RFC 8878 size | 112,425 bytes |
| RFC 9659 path | .local/spec-cache/zst/rfc9659/rfc9659.txt |
| RFC 9659 SHA-256 | sha256:a43584f250506db54df8bc9ff90652888135369fbc331453f67a71829b0827a2 |
| RFC 9659 size | 6,599 bytes |
| Source | rfc-editor.org (NOT tools.ietf.org) |
| Cached date | 2026-05-15 |

## RFC Relationship

- RFC 8878: IETF Informational (2021-02-01). Core Zstandard spec. Obsoletes RFC 8478.
- RFC 9659: IETF Informational (2024-09-01). Updates RFC 8878 — window size in HTTP contexts only.
- RFC 9659 does NOT affect core frame format. Primary spec for acquisition: RFC 8878.

## Errata

- RFC 8878: 7 errata (3 verified, 4 reported) — all implementation-level (FSE/Huffman tables)
- RFC 9659: 0 errata

## Legal Classification

- GATE2_PASS_WITH_LEGAL_NOTES
- legal_category: 2 (BSD + patent grant)
- No IETF IPR disclosures found
- Meta ADDITIONAL_GRANT patent license documented in R13B

## Tests

- tests/skills/test_zst_spec_cache_gate2.py: 20 tests created, 20/20 PASS

## Files Updated

- registry/format-registry.yaml: gate_2 status=passed, spec hashes, spec_cache_path
- acquisition-packs/zst/pack.yaml: Gate 2 fields, duplicate keys removed, spec hashes
- acquisition-packs/zst/legal-notes.md: Gate 2 cache-backed classification
- acquisition-packs/zst/spec-evidence.md: CREATED (Gate 2 spec evidence)
- plans/master-plan.md: v2.58 → v2.59, R14 added to sprint chain
- README.md: ZST Gate 2 PASSED line added
- taskcards/ZST-R14-SPEC-RETRIEVAL.md: completed
- taskcards/ZST-R15-GATE3-SAMPLE-SOURCES.md: CREATED (pending R15)
- taskcards/ZST-GATE2-IV.md: CREATED (DEC-034 IV pending)

## Governance Invariants (unchanged)

- commercial_product_ready: false
- FODS Gate 11: NOT APPROVED
- FODT Gate 11: NOT APPROVED
- ZST Gate 3: NOT AUTHORIZED (requires R15)
- ZST implementation_authorized: false
- ZST generated_requirements_authorized: false
- src/ mutations: NONE

## R14C Closure Repair and IV (2026-05-15)

Sprint: FORMAT-FACTORY-R14C-ZST-GATE2-CLOSURE-REPAIR-AND-IV-SWARM-001

Contradiction resolved: R14 evidence bundle was built before commit 2e24110 (BUNDLE_BUILT_BEFORE_COMMIT).
Commit 2e24110 exists and is HEAD. All R14 work correctly committed. Repo clean.

IV result: ZST_GATE2_IV_STATUS: PASS_15_OF_15 (20/20 tests, all hashes verified independently)
IV report: reports/verification/r14c-zst-gate2-independent-verification-20260515.md

ZST-GATE2-IV.md taskcard: updated to completed.
spec-cache-manifest-record.md: created in acquisition-packs/zst/ as committed evidence proxy.

Gate 2 evidence status: evidence_verified_by_independent_sprint

## Next Sprint

R15: FORMAT-FACTORY-R15-ZST-GATE3-SAMPLE-SOURCE-ACQUISITION-SWARM-001 (pending R15 authorization prompt)
DEC-034 IV: COMPLETE (R14C served as the required IV sprint)
