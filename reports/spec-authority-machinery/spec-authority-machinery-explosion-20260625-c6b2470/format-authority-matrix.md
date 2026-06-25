# Format Authority Matrix
## Run ID: spec-authority-machinery-explosion-20260625-c6b2470

---

| Format | Spec Source | Cache State | SAL Facts | Verified | Auth Level | Product Exp? | Readiness? | Bypass Risk | Overclaim Risk | Next Work |
|--------|------------|-------------|-----------|----------|------------|-------------|------------|-------------|----------------|-----------|
| **FODS** | ODF1.3/PDF (official) | FULL | 4988 | 4988 | **P6** | YES | YES | LOW | LOW | Extend proof graph to FACT-FODS-002..010; advance all 4988 facts |
| **FODT** | ODF1.3/PDF (stale) | STALE_MISSING | 4936 | 4298 | **P6** | YES | YES | LOW | LOW | Re-acquire FODT spec PDF; create proof graph for FACT-FODT-001 |
| **ODS** | ODF1.3/PDF (shared) | PARTIAL | 1069 | 1069 | **P5** | YES | YES | LOW | LOW | Create proof graph; verify code+test citations exist |
| **ODT** | ODF1.3/PDF (shared) | PARTIAL | 1066 | 1066 | **P5** | YES | YES | LOW | LOW | Create proof graph for ODT key facts |
| **FODG** | ODF1.3/PDF (shared) | PARTIAL | 1066 | 1066 | **P5** | YES | YES | LOW | LOW | Create proof graph for FODG key facts |
| **FODP** | ODF1.3/PDF (shared) | PARTIAL | 1066 | 1066 | **P5** | YES | YES | LOW | LOW | Create proof graph for FODP key facts |
| **ZST** | RFC8878 (rfc_text) | PARTIAL | 94 | 94 | **P6** | YES | YES | LOW | **MODERATE** | 94 RFC8878 facts; only 2 cited in code. Advance remaining 92. |
| **PBM** | Netpbm spec (community) | PARTIAL | 2 | 2 | **P5** | YES | YES | **MODERATE** | **MODERATE** | Only 2 facts (magic numbers). Expand Netpbm spec coverage. |
| **PGM** | Netpbm spec (community) | PARTIAL | 2 | 2 | **P5** | YES | YES | **MODERATE** | **MODERATE** | Only 2 facts. Expand Netpbm spec coverage. |
| **PPM** | Netpbm spec (community) | PARTIAL | 2 | 2 | **P5** | YES | YES | **MODERATE** | **MODERATE** | Only 2 facts. Expand Netpbm spec coverage. |
| **Gnumeric** | XSD schema only | METADATA_ONLY | 3 | 3 | **P1** | **NO** | **NO** | **HIGH** | **HIGH** | P1 ceiling correct. No formal spec. schema_authority_available exception correct. |
| **ABW** | No public spec | METADATA_ONLY | 5 | 0 | **P1** | **NO** | **NO** | **HIGH** | **HIGH** | P1 ceiling correct. no_public_spec_available exception correct. |
| **SYLK** | No public spec | METADATA_ONLY | 3 | 3 | **P1** | **NO** | **NO** | **HIGH** | **HIGH** | P1 ceiling correct. No accessible formal spec. |
| **DIF** | No public spec | METADATA_ONLY | 3 | 3 | **P1** | **NO** | **NO** | **HIGH** | **HIGH** | P1 ceiling correct. No formal published standard. |
| **TSV** | No formal spec | METADATA_ONLY | 2 | 2 | **P1** | **NO** | **NO** | **HIGH** | **HIGH** | P1 ceiling correct. No formal TSV RFC. |
| **CSV** | RFC4180 (rfc) | UNKNOWN | 2 | 2 | **P2** | **NO** | **NO** | **HIGH** | **HIGH** | RFC4180 available. Run spec acquisition + normalization. Advance from P2 to P3-P4. |
| **NDJSON** | ndjson.org (informal) | METADATA_ONLY | 2 | 2 | **P2** | **NO** | **NO** | **HIGH** | **HIGH** | ndjson.org spec accessible. Run spec acquisition. |
| **TOML** | spec-toml.io (community) | UNKNOWN | 2 | 2 | **P2** | **NO** | **NO** | **HIGH** | **HIGH** | spec-toml.io accessible. Run spec acquisition. |
| **XCF** | GIMP internal (community) | METADATA_ONLY | 2 | 2 | **P2** | **NO** | **NO** | **HIGH** | **HIGH** | GIMP community docs available. Check T3 eligibility. |
| **QOI** | qoi.phoboslab.org (community) | UNKNOWN | 2 | 2 | **P2** | **NO** | **NO** | **HIGH** | **HIGH** | qoi.phoboslab.org spec available. Check T3 eligibility. |

---

## Summary Statistics

| Category | Count | Formats |
|----------|-------|---------|
| P6 (complete proof graph) | 2 | FODS, ZST (1 fact each) |
| P5 (cited in code+tests) | 7 | FODT, ODS, ODT, FODG, FODP, PBM, PGM, PPM |
| P2 (spec cached, no facts extracted) | 5 | CSV, NDJSON, TOML, XCF, QOI |
| P1 (schema/metadata only / no public spec) | 6 | Gnumeric, ABW, SYLK, DIF, TSV, PPM |
| **Product expansion allowed** | **10** | FODS, FODT, ODS, ODT, FODG, FODP, ZST, PBM, PGM, PPM |
| **Product expansion blocked** | **10** | Gnumeric, ABW, SYLK, DIF, TSV, CSV, NDJSON, TOML, XCF, QOI |

---

## Exception Classification Summary

| Exception | Formats | Rationale | Risk |
|-----------|---------|-----------|------|
| `no_public_spec_available` | ABW, SYLK, DIF, TSV | No publicly accessible formal specification | Correct — P1 is the ceiling |
| `schema_authority_available` | Gnumeric | XSD schema exists but no narrative spec | Correct — structural facts only |
| `legacy_backfill` | CSV, NDJSON, TOML, XCF, QOI | Spec accessible but not yet acquired | Incorrect long-term — should acquire and advance |

---

## Authority Level Definitions

| Level | Name | Criteria |
|-------|------|----------|
| P0 | No evidence | No spec, no facts, no code |
| P1 | Schema/metadata only | XSD or metadata only; no narrative spec text |
| P2 | Spec cached, no facts | Spec available or cached; no fact extraction done |
| P3 | Candidate facts | Fact extraction run; not yet verified |
| P4 | Verified facts | Facts verified against spec text; not yet cited in code |
| P5 | Facts cited in code+tests | Verified facts referenced in source code AND tests |
| P6 | Complete proof graph | Full chain: spec→fact→requirement→code→test→evidence |
