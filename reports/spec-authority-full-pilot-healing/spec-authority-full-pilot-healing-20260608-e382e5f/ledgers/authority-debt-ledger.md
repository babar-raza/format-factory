# Authority Debt Ledger
**Sprint:** SPEC-AUTHORITY-LAYER-FULL-PILOT-VERIFICATION-HEALING-AND-CLOSURE-001
**Run ID:** spec-authority-full-pilot-healing-20260608-e382e5f
**Date:** 2026-06-08

---

## Format Authority Status

| Format | Authority Type | Status | Verified Facts | Proof Level | Notes |
|--------|---------------|--------|---------------|-------------|-------|
| FODS | ODF 1.3 Part 3 PDF (OASIS RF) | CACHED | 1/10 verified | **P4** | FACT-FODS-001 verified; 9 need review |
| FODT | ODF 1.3 Part 2 | PRESUMED_CACHED | 0 verified | **P2** | Spec available but fact verification not run this sprint |
| Netpbm | Netpbm manual | PRESUMED_CACHED | 0 verified | **P2** | Tests exist; fact verification not run |
| Gnumeric | gnumeric.xsd (de-facto) | SCHEMA_METADATA_ONLY | 0 verified | **P1** | Full XSD not cached; no verified facts |
| ABW | No public spec (abisource.com DOWN) | BLOCKED_SERVER_DOWN | 0 verified | **P0** | All code is pre-existing backfill |
| SYLK | Deprecated Microsoft format | UNKNOWN | 0 verified | **P0** | No spec acquisition attempted |
| DIF | Deprecated Apple/Lotus format | UNKNOWN | 0 verified | **P0** | No spec acquisition attempted |
| CSV | RFC 4180 | UNKNOWN | 0 verified | **P0** | RFC exists; not acquired this sprint |
| TSV | Ad-hoc standard | UNKNOWN | 0 verified | **P0** | No formal spec |
| ZST | Zstandard RFC 8878 | UNKNOWN | 0 verified | **P0** | RFC exists; not acquired this sprint |

---

## Known Authority Debt Items

### DEBT-001: FODS — 9 unverified facts
- FACT-FODS-002 through FACT-FODS-010: needs_review
- Verification requires reading normalized/text.txt against each claim
- Grace: legacy_backfill for existing code; must be addressed before P5 claim

### DEBT-002: Gnumeric — schema authority without verified facts
- schema_authority_available allows PRODUCT_SOURCE and READINESS (per READINESS_ALLOWED_EXCEPTIONS)
- Risk: readiness can be claimed with schema authority alone, without verified facts
- Mitigation: governance oversight required before RELEASE_GATE

### DEBT-003: ABW — no public spec available
- All ABW code is pre-existing backfill (legacy_backfill exception)
- Cannot claim readiness or release gate without spec authority
- Stable state: no regression risk, just debt

### DEBT-004: Fact ID existence check missing
- Validator checks FACT-xxx format but NOT existence in fact registry
- FACT-DOES-NOT-EXIST passes format check (syntactically valid)
- A fact registry lookup would require scanning workbench/*.yaml files
- Recorded as known gap — medium severity

### DEBT-005: schema_authority_available readiness scope
- schema_authority_available is in READINESS_ALLOWED_EXCEPTIONS
- This means Gnumeric could claim readiness with schema authority alone
- Should require at minimum 1 schema-verified fact before readiness
- Governance decision needed — not auto-fixed (would break schema_authority pattern)

---

## Machinery Bypass Ledger

| Bypass ID | Classification | Format | Exception | Notes |
|-----------|---------------|--------|-----------|-------|
| BYP-GNUMERIC-001 | schema_authority_available | Gnumeric | Schema (XSD) is primary authority | Correct — upgraded from no_public_spec_available in repair sprint |
| BYP-ABW-001 | no_public_spec_available | ABW | No accessible spec | Confirmed correct — server down |

---

## Continuation Safety Status

- `advisory_prompt_executable: false` ✓
- Next sprint must NOT advance Gate 11 before fact verification is complete
- Product expansion (product deepening) can resume after this sprint closeout
- No authority pilots remain blocked — all complete or documented as external-gate items
