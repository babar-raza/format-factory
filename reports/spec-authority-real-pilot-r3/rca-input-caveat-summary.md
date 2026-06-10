# RCA Input Caveat Summary
Sprint: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R3-CLOSURE-HARDENING-AND-ODF-DEPTH-001
Lane: F — RCA Input Snapshot Caveats
Generated: 2026-06-05

## Purpose

This document summarizes the authority caveats, limitations, and downstream usage rules
for all 5 sources captured in the RCA input snapshot manifest
(`rca-input-snapshot-manifest.json`). These caveats MUST be propagated to any consumer of
the SAL context packs — including the Requirement-Capability Authority Layer (RCAL),
product obligation derivation, and coverage validation.

---

## Source-by-Source Caveat Summary

### 1. ZST — RFC 8878

| Field | Value |
|-------|-------|
| source_id | src-r2-zst-rfc8878 |
| authority_status | ACCEPTED_SPEC |
| caveat | None |
| fetch | REAL_FETCH (112,425 bytes, SHA-256 verified) |
| downstream_usage | Requirements MAY be used as authoritative product obligations |

**Caveat:** NONE. RFC 8878 is an IETF Proposed Standard. Requirements extracted from this
source are fully authoritative and binding for ZST format compliance.

**Downstream rule:** ZST requirements from CP-ZST-9707e015c308 may be used directly as
product obligations without further qualification.

---

### 2. Netpbm — Public Domain Spec (PBM/PGM/PPM)

| Field | Value |
|-------|-------|
| source_id | src-r2-netpbm-spec |
| authority_status | ACCEPTED_WITH_CAVEAT |
| caveat | De facto public domain standard; no formal IETF/ISO standards body |
| fetch | REAL_FETCH (3 HTML pages, SHA-256 verified) |
| downstream_usage | Advisory; no formal standards body |

**Caveat:** Netpbm specifications are published at netpbm.sourceforge.net and are treated
as de facto public domain standards. There is no formal standards body (IETF, ISO, ANSI)
that governs Netpbm formats. Specifications may evolve without notice.

**Downstream rule:** Netpbm requirements from CP-NETPBM-9dee4b8f8608 are advisory. They
reflect the documented format intent but MUST NOT be presented as binding RFC/ISO obligations.
Requirements should be labeled "de facto standard" in product documentation.

---

### 3. DIF — Data Interchange Format (Empirical)

| Field | Value |
|-------|-------|
| source_id | src-r2-dif-empirical |
| authority_status | EMPIRICAL_ONLY |
| caveat | No authoritative public spec. Requirements are observational only. MUST NOT be promoted. |
| fetch | LOCAL_FIXTURE (no URL, no SHA-256) |
| downstream_usage | Observational only; not binding; MUST NOT be promoted |

**Caveat:** No authoritative public specification exists for DIF format. Requirements
extracted from the DIF fixture are based on empirical observation of known-valid DIF files
and reverse-engineered structural rules. These are NOT derived from any authoritative source.

**Critical rule — ANTI-BYPASS:** DIF requirements MUST NOT be promoted to ACCEPTED_SPEC or
ACCEPTED_WITH_CAVEAT status under any circumstances without locating an authoritative
public specification. Doing so constitutes a governance bypass.

**Downstream rule:** DIF requirements from CP-DIF-9ccc23683556 are observational only.
They may be used as implementation guidance but MUST NOT be cited as specifications.
Any product documentation referencing DIF behavior MUST note the empirical-only status.

---

### 4. FODS — ODF 1.3 (Scoped Introduction)

| Field | Value |
|-------|-------|
| source_id | src-r2-fods-odf13 |
| authority_status | ACCEPTED_WITH_CAVEAT |
| caveat | Scoped ODF 1.3 intro only (6000 chars). Full 1000+ page spec deferred to R4+. License review pending. |
| fetch | REAL_FETCH_SCOPED (OASIS HTML, scoped first 6000 chars) |
| downstream_usage | Scoped intro only; full spec pending |

**Caveat:** The FODS context pack CP-FODS-418cb43b3ad8 is derived from only the
introductory portion (~6000 chars) of the ODF 1.3 specification. The full ODF 1.3
specification spans 1000+ pages and covers the complete spreadsheet element model,
formula language, style system, and metadata schema. Only 3 high-level requirements
were extractable from the scoped introduction.

**License caveat:** OASIS ODF 1.3 specification license review is pending. The spec is
publicly available from OASIS but the license terms for derivative works have not been
confirmed. FODS stays at ACCEPTED_WITH_CAVEAT until license is confirmed.

**Downstream rule:** FODS requirements from CP-FODS-418cb43b3ad8 may be used as
structural guidance for FODS format support but MUST be qualified as "from ODF 1.3
introduction only." Full ODF 1.3 spec ingestion is targeted for R4+.

---

### 5. FODT — ODF 1.3 (Scoped Introduction)

| Field | Value |
|-------|-------|
| source_id | src-r3-fodt-odf13 |
| authority_status | ACCEPTED_WITH_CAVEAT |
| caveat | Scoped ODF 1.3 intro only (5000 chars). Full spec deferred to R4+. License review pending. |
| fetch | REAL_FETCH_SCOPED (reused R2 ODF abstract, scoped first 5000 chars) |
| downstream_usage | Scoped intro only; full spec pending |

**Caveat:** The FODT context pack CP-FODT-ce25cfe79029 is derived from the same ODF 1.3
abstract used for FODS in R2, scoped to the first 5000 chars with FODT-specific prefixing.
FODT is the flat (non-ZIP) variant of ODF Text Document format. Only 3 high-level
requirements were extractable from the scoped introduction. The full ODF text document
model (text:p, text:h, text:body, style system) is not represented in the scoped extract.

**License caveat:** Same as FODS — OASIS ODF 1.3 license pending.

**Downstream rule:** FODT requirements from CP-FODT-ce25cfe79029 may be used as structural
guidance only. Full ODF 1.3 text document spec ingestion is targeted for R4+.

---

## Cross-Source Caveat Matrix

| Source | Status | Binding? | Cite as Spec? | Promote? |
|--------|--------|----------|---------------|----------|
| ZST (RFC 8878) | ACCEPTED_SPEC | YES | YES | N/A (already spec) |
| Netpbm | ACCEPTED_WITH_CAVEAT | Advisory | No (de facto only) | Only with caveat |
| DIF | EMPIRICAL_ONLY | NO | NO | HARD BLOCKED |
| FODS | ACCEPTED_WITH_CAVEAT | Partial | Intro only | Pending R4 full spec |
| FODT | ACCEPTED_WITH_CAVEAT | Partial | Intro only | Pending R4 full spec |

---

## RCA Input Readiness

The `rca-input-snapshot-manifest.json` is FROZEN and RCA-ready with these constraints:
- `capability_claims_present: false` — the SAL layer makes no product capability claims
- `rca_ready: true` — caveats documented; downstream rules established
- All 5 sources have deterministic context packs with verified SHA-256
- DIF anti-bypass rule enforced in the manifest and this document

**Next steps for RCAL (R4+):**
1. Ingest full ODF 1.3 spec (FODS + FODT) for complete requirement coverage
2. Resolve OASIS ODF 1.3 license question before promoting FODS/FODT to ACCEPTED_SPEC
3. Locate authoritative DIF specification or formally retire DIF from spec-authority scope

---

## Verdict

`RCA_INPUT_CAVEAT_SUMMARY_COMPLETE`

All caveats documented. Downstream usage rules established. No capability claims.
DIF anti-bypass enforced. FODS/FODT scoped-only limitations noted.
