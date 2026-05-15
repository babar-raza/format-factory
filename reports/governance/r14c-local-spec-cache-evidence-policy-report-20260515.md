# R14C Local Spec Cache Evidence Policy Report
Sprint: FORMAT-FACTORY-R14C-ZST-GATE2-CLOSURE-REPAIR-AND-IV-SWARM-001
Gate: 4 (Lane E)
Date: 2026-05-15

---

## Policy Context

Per `docs/specification-cache.md`: spec cache is stored under `.local/spec-cache/` which is
gitignored. IETF RFC text is copyrighted and redistribution is not permitted. Full RFC text
must NOT be committed to git.

The R14 evidence bundle correctly excluded `.local/` per the `base-run.yaml` `forbidden_patterns`
(`.local/**` is explicitly forbidden from bundles). This is correct behavior.

---

## Gap Identified

The R14 bundle contained only metadata summaries of the spec cache (via bundle-metadata/ files),
but no committed file in the repo served as a durable, auditable record of:
- Exact cache paths
- SHA-256 hashes (per RFC)
- Errata detail
- Refresh policy
- IV verification date

---

## Repair Action

Created: `acquisition-packs/zst/spec-cache-manifest-record.md`

This committed file provides:
1. Local cache root path: `.local/spec-cache/zst/`
2. RFC 8878 source URL, local path, SHA-256, size, status
3. RFC 9659 source URL, local path, SHA-256, size, status
4. RFC update relationship (HTTP-only scope)
5. Errata table (7 RFC 8878 errata with IDs, status, sections)
6. IPR check record (403 noted, no disclosures)
7. Refresh policy
8. IV verification date and test command
9. Explicit statement: full spec text is local-only, not committed

---

## Bundle Policy Compliance

The R14C evidence contract explicitly lists `acquisition-packs/zst/spec-cache-manifest-record.md`
as a required repo file. The bundle will include this committed record while the full RFC text
remains local-only under `.local/spec-cache/zst/`.

The R14C evidence bundle will NOT include full RFC text (`.local/**` remains forbidden in bundle).
The committed manifest record provides sufficient audit trail without redistribution violation.

---

SPEC_CACHE_EVIDENCE_POLICY: COMPLIANT
COMMITTED_MANIFEST_RECORD: acquisition-packs/zst/spec-cache-manifest-record.md
FULL_RFC_LOCAL_ONLY: true
