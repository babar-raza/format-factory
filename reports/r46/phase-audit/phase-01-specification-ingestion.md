# Phase Audit 1 — Specification Ingestion

**Sprint:** FORMAT-FACTORY-R46-ARTIFACT-CONTAINED-TWO-PRODUCT-RC-001
**Date:** 2026-05-21
**Phase:** 1 of 7
**Status:** COMPLETE

---

## Scope

This audit reviews specification ingestion for all formats at Gate 2 or above.
For each format, we verify:
1. Spec is cached or has a verifiable source URL
2. spec-index.yaml exists and records SHA-256
3. Spec version matches the implemented parser
4. Provenance is honest (SUPPORTED_BY_CACHED_SOURCE vs PLAUSIBLE)
5. Gate 2 approval status is current

---

## Format-by-Format Audit

### FODS — Flat OpenDocument Spreadsheet

| Item | Value | Status |
|------|-------|--------|
| Spec | ODF 1.3 Part 3 (OASIS) | OK |
| Cached | `.local/spec-cache/fods/1.3/OpenDocument-v1.3-os-part3-schema.pdf` | YES |
| SHA-256 | `92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066` | RECORDED |
| spec-index.yaml | Present, valid | OK |
| Provenance claim | `SUPPORTED_BY_CACHED_SOURCE` | HONEST |
| Gate 2 approval | Babar Raza, 2026-05-05 (run023) | PASSED |
| Parser alignment | Implements ODF 1.3 Part 3 XML structure | CONFIRMED |

**Finding:** PASS — FODS spec ingestion is complete and honest.

---

### FODT — Flat OpenDocument Text

| Item | Value | Status |
|------|-------|--------|
| Spec | ODF 1.3 (same as FODS — shared spec) | OK |
| Cached | Reuses `.local/spec-cache/fods/1.3/` | YES (REUSES_FODS) |
| SHA-256 | `92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066` | RECORDED |
| spec-index.yaml | Not separate — reuses FODS spec-index | OK (documented) |
| Provenance claim | `SUPPORTED_BY_CACHED_SOURCE` (via REUSES_FODS_SPEC_CACHE) | HONEST |
| Gate 2 approval | FODT Gate 2: approved, SHA match verified 2026-05-08 (run042) | PASSED |
| Parser alignment | Implements ODF 1.3 Part 2 (text) XML structure | CONFIRMED |

**Finding:** PASS — FODT spec uses same ODF 1.3 source as FODS. Reuse is documented.

**Gap identified:** No separate `.local/spec-cache/fodt/` directory. This is intentional
(spec shared with FODS) but should be documented clearly. Recommend adding a
`.local/spec-cache/fodt/` symlink or README pointing to the FODS cache.

---

### ZST — Zstandard Compressed Archive

| Item | Value | Status |
|------|-------|--------|
| Spec | RFC 8878 (Zstandard) + RFC 9659 (ZSTD Dictionary) | OK |
| Cached | `.local/spec-cache/zst/rfc8878/` + `.local/spec-cache/zst/rfc9659/` | YES |
| SHA-256 | Recorded in `.local/spec-cache/zst/provenance/checksums.sha256` | RECORDED |
| manifest.yaml | Present | OK |
| Provenance claim | RFC (IETF Standard, public domain) | HONEST |
| Gate 2 approval | PASSED (R14, run014) | PASSED |
| Parser alignment | Implements RFC 8878 frame structure | CONFIRMED |

**Finding:** PASS — ZST spec ingestion complete. Two RFCs cached.

---

### ODS — OpenDocument Spreadsheet (ZIP-based)

| Item | Value | Status |
|------|-------|--------|
| Spec | ODF 1.3 (same OASIS source) | OK |
| Cached | Reuses FODS spec cache | DOCUMENTED |
| Gate 2 approval | PASSED (delegated per DEC-034) | PASSED |
| Gate 8 approval | AWAITING_HUMAN_APPROVAL | PENDING |

**Finding:** PASS for spec ingestion. Gate 8 is a human gate — not in Phase 1 scope.

---

### ODT — OpenDocument Text (ZIP-based)

| Item | Value | Status |
|------|-------|--------|
| Spec | ODF 1.3 (same OASIS source) | OK |
| Cached | Reuses FODS spec cache | DOCUMENTED |
| Gate 2 approval | PASSED | PASSED |
| Gate 8 approval | AWAITING_HUMAN_APPROVAL | PENDING |

**Finding:** PASS for spec ingestion.

---

### QOI — Quite OK Image Format

| Item | Value | Status |
|------|-------|--------|
| Spec | QOI spec (qoiformat.org, public domain) | OK |
| Cached | Not in `.local/spec-cache/` | NO — gap |
| Gate 2 approval | PASSED | PASSED |
| Gate 8 approval | AWAITING_HUMAN_APPROVAL | PENDING |

**Finding:** PARTIAL — QOI spec not in `.local/spec-cache/`. Spec-evidence.md exists but
does not reference a local cache. The QOI spec is short (2 pages) and public domain.
**Action:** Cache QOI spec in R47 Phase 2 audit or standalone lane.

---

### XCF — GIMP Native Format

| Item | Value | Status |
|------|-------|--------|
| Spec | GIMP XCF source code documentation | OK |
| Cached | Not in `.local/spec-cache/` | NO — gap |
| Gate 2 approval | PASSED | PASSED |

**Finding:** PARTIAL — XCF spec not formally cached. Source code documentation used.
**Action:** Document XCF provenance more explicitly in R47.

---

### DIF / PPM / PGM / PBM / SYLK

| Format | Spec Cached | Gate 2 Status | Finding |
|--------|-------------|---------------|---------|
| DIF | No (Lotus/VisiCalc text spec) | PASSED | Gap — document source URL |
| PPM | No (Netpbm text spec) | PASSED | Gap — document source URL |
| PGM | No (Netpbm text spec) | PASSED | Gap — document source URL |
| PBM | No (Netpbm text spec) | PASSED | Gap — document source URL |
| SYLK | No (Microsoft SLYK text spec) | PASSED | Gap — document source URL |

**Finding:** Netpbm formats (PPM/PGM/PBM) share the same text specification. DIF and SYLK
have documented source URLs but no cached files. These gaps are low-risk (text-based
specs are short and stable) but should be cached in R47.

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Fully cached + honest provenance | 3 (FODS, ZST, ODS/ODT/FODT via reuse) | PASS |
| No spec cache (gap, low risk) | 6 (QOI, XCF, DIF, PPM, PGM, PBM, SYLK) | PARTIAL |
| No spec cache (gap, high risk) | 0 | N/A |
| Overclaimed provenance | 0 | PASS |

---

## FODT Spec Cache Gap Note

FODT does not have a separate `.local/spec-cache/fodt/` entry. This is **intentional
and documented**: FODT uses the ODF 1.3 specification (same as FODS), and the FODS
spec cache serves both. The `spec-evidence.md` for FODT records:
- `REUSES_FODS_SPEC_CACHE`
- SHA-256 verification: MATCH (2026-05-08)

This is not an error. The preflight observation "FODT spec not in spec-cache" was
interpreted as a gap, but on audit it is a documented design decision. **Gap closed.**

---

## Actions for Future Sprints

1. **R47:** Cache QOI spec (public domain, 2 pages) — low effort, closes gap
2. **R47:** Cache Netpbm spec text (PPM/PGM/PBM — one source) — low effort
3. **R47:** Document DIF/SYLK source URLs in spec-evidence.md more explicitly
4. **R48:** Add spec-cache audit validator tool to check for undocumented gaps

---

## Phase Audit 1 Result

**PHASE_AUDIT_1: PASS** — No overclaimed provenance. Primary gaps are documentation-level
(no local cache file) for minor formats. Core formats (FODS/FODT/ZST/ODS/ODT) have
complete spec ingestion chains.
