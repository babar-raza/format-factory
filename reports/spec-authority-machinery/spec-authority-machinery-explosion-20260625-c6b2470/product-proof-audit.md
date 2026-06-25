# Product Proof Audit — Spec Authority Chain Traceability
## Run ID: spec-authority-machinery-explosion-20260625-c6b2470

---

## Method

For each format, trace the chain: **spec PDF → FACT-* → requirement → code citation → test citation → evidence declaration → proof graph**

Actual authority level determined by the weakest link in the chain, not the claimed level.

---

## Format: FODS

**Claimed level**: P6
**Actual level**: P6 for FACT-FODS-001 / P5 for FACT-FODS-004 and FACT-FODS-006 / P4 for remaining 4985 facts

| Chain Link | Status | Evidence |
|------------|--------|----------|
| Spec PDF cached | YES | `.local/spec-cache/fods/1.3/raw/OpenDocument-v1.3-os-part3-schema.pdf` |
| Normalized text | YES | `normalized/text.txt`, `sections.jsonl`, `chunks.jsonl` |
| Verified facts | YES | `workbench/verified-facts.yaml` — 4348 verified, 4988 total |
| Requirement packs | PARTIAL | `workbench/requirement-packs/` — FACT-FODS-001 through ~010 |
| Code citation | PARTIAL | `Compat/fods_document.py` → FACT-FODS-001; `fods_sheet.py` → FACT-FODS-004; `fods_cell.py` → FACT-FODS-006. No citations in non-Compat code. |
| Test citation | PARTIAL | `tests/python/fods/test_r125_fact_traceability.py` — behavioral assertions for FACT-FODS-001 |
| Proof graph | PARTIAL | `fods-p6-proof-graph.yaml` — FACT-FODS-001 ONLY. Explicit scope statement. |
| Evidence declaration | PARTIAL | sprint evidence cites FACT-FODS-001, FACT-FODS-004, FACT-FODS-006 |

**Assessment**: FODS is genuinely P6 for FACT-FODS-001 (complete chain with behavioral tests and proof graph). FACT-FODS-004 and FACT-FODS-006 are P5 (code citations exist, tests exist, no proof graph). 4985 remaining facts are P4 (verified but not cited in code or tests). Product code outside Compat/ has no FACT-* citations.

---

## Format: FODT

**Claimed level**: P6
**Actual level**: P5 at best (stale spec cache; no proof graph)

| Chain Link | Status | Evidence |
|------------|--------|----------|
| Spec PDF cached | STALE/MISSING | `fodt/` directory exists but spec file is missing/stale per refresh_check |
| Normalized text | COMPLETE_FROM_SHARED_ODF | Uses shared ODF 1.3 artifacts |
| Verified facts | 4298 verified | `workbench/verified-facts.yaml` — from shared ODF facts |
| Requirement packs | UNKNOWN | Not confirmed present |
| Code citation | PARTIAL | `Compat/fodt_*.py` files have spec authority comments |
| Test citation | PARTIAL | Some FODT tests reference spec sections |
| Proof graph | NONE | No proof graph YAML for any FODT fact |
| Evidence declaration | PARTIAL | Recent sprints cite spec sections but not specific FACT-FODT-* IDs |

**Assessment**: FODT is at P5 (facts cited in code and tests) but cannot claim P6 without a proof graph. The stale spec file should be re-acquired. Shared ODF facts provide coverage but are not FODT-specific.

---

## Format: ODS / ODT / FODG / FODP

**Claimed level**: P5
**Actual level**: P5 (correctly classified)

| Chain Link | Status | Evidence |
|------------|--------|----------|
| Spec PDF cached | PARTIAL (shared ODF) | Uses shared ODF 1.3 PDF |
| Verified facts | YES | ODS=1069, ODT=1066, FODG=1066, FODP=1066 |
| Code citation | PARTIAL | Some Compat/ files have spec citations |
| Test citation | PARTIAL | tests/python/{format}/test_tc_sp_*.py cite spec qnames |
| Proof graph | NONE | No proof graph for any fact in these formats |

**Assessment**: P5 classification is correct. Path to P6 requires creating proof graphs for at least FACT-{FORMAT}-001 in each format, and extending code+test citations.

---

## Format: ZST

**Claimed level**: P6
**Actual level**: P6 for FACT-ZST-001 / P4 for remaining 92 facts

| Chain Link | Status | Evidence |
|------------|--------|----------|
| Spec (RFC8878) cached | PARTIAL | RFC text cached; 94 facts extracted |
| Verified facts | YES | 94 verified from RFC8878 |
| Code citation | MINIMAL | FACT-ZST-001 (magic bytes: 0xFD2FB528) cited in `zst_codec.py`; FACT-ZST-002 cited |
| Test citation | MINIMAL | Tests reference magic number verification |
| Proof graph | PARTIAL | `zst-p6-proof-graph.yaml` — FACT-ZST-001 only |
| Evidence declaration | PARTIAL | Recent ZST sprints cite gap_ledger_ref not spec_fact_refs |

**Assessment**: ZST is P6 for FACT-ZST-001 (magic number). 92 remaining RFC8878 facts are at P4 (verified but not cited in code). Overclaim risk: product readiness claims for ZST imply full RFC8878 compliance but only 2 facts are cited.

---

## Format: PBM / PGM / PPM

**Claimed level**: P5
**Actual level**: P5 (barely — 2 facts, magic numbers only)

| Chain Link | Status | Evidence |
|------------|--------|----------|
| Spec (Netpbm doc) | PARTIAL | Community documentation cached |
| Verified facts | 2 per format | Magic number + format descriptor only |
| Code citation | PARTIAL | Magic number check in parsers |
| Test citation | YES | `test_pbm_malformed_and_security.py` etc. — 3 test files each |
| Proof graph | NONE | No proof graphs |

**Assessment**: P5 classification barely holds. Only 2 facts (magic numbers) covered. Full Netpbm spec has encoding rules, whitespace rules, maxval constraints, binary vs. ASCII format differences — all uncovered. Overclaim risk: MODERATE (presenting P5 without disclosing 2-fact coverage).

---

## Format: Gnumeric

**Claimed level**: P1 (correctly designed)
**Actual level**: P1

| Chain Link | Status | Evidence |
|------------|--------|----------|
| Formal spec | NONE | No published Gnumeric XML narrative spec |
| XSD schema | YES | gnumeric-stf-2.0.xsd available |
| Structural facts | 3 | FACT-GNUMERIC-001..003 from XSD inspection |
| Code citation | NO | gnumeric_codec.py has no FACT-GNUMERIC-* citations in code comments |
| Test citation | IDENTIFIER ONLY | `test_spec_compat_layer.py` checks `GnumericWorkbook.spec_fact_ref == "FACT-GNUMERIC-001"` |
| Proof graph | NONE | Correct — P1 formats do not need proof graphs |

**Assessment**: P1 classification is architecturally correct. `schema_authority_available` exception is appropriate. The test checks an identifier, not a behavioral spec-derived assertion. Product ledger should explicitly record P1 as the ceiling.

---

## Format: ABW

**Claimed level**: P1 (correctly designed)
**Actual level**: P1

| Chain Link | Status | Evidence |
|------------|--------|----------|
| Formal spec | NONE | AWM/AWML not a formally published standard |
| Structural facts | 5 | Basic AbiWord XML structure elements |
| Code citation | NO | No FACT-ABW-* citations in abw_parser.py |
| Test citation | IDENTIFIER ONLY | Similar to Gnumeric pattern |

**Assessment**: P1 classification correct. `no_public_spec_available` exception is appropriate.

---

## Format: CSV / NDJSON / TOML / XCF / QOI

**Claimed level**: P2 (legacy_backfill)
**Actual level**: P2

| Chain Link | Status | Evidence |
|------------|--------|----------|
| Formal spec | ACCESSIBLE but not acquired | RFC4180, spec-toml.io, ndjson.org, qoi.phoboslab.org |
| Normalized text | NONE | spec_normalizer.py not run for these |
| Verified facts | 2 per format | Magic number / basic structural fact only |
| Code citation | NO | No FACT-CSV-* etc. in source files |
| Test citation | IDENTIFIER ONLY | spec_qname attribute tests only |

**Assessment**: P2 classification is correct but `legacy_backfill` exception should not be permanent. These formats have accessible specs and should advance to P3-P4 after T3 authorization and normalization.

---

## Summary — Actual vs. Claimed Authority Levels

| Format | Claimed | Actual | Gap | Overclaim Risk |
|--------|---------|--------|-----|----------------|
| FODS | P6 | P6 (1 fact) / P5 (2 facts) / P4 (4985 facts) | Coverage scope | LOW (scoped) |
| FODT | P6 | P5 | Missing proof graph, stale spec | LOW |
| ODS/ODT/FODG/FODP | P5 | P5 | Correct | LOW |
| ZST | P6 | P6 (1 fact) / P4 (92 facts) | Coverage scope | MODERATE |
| PBM/PGM/PPM | P5 | P5 (2 facts each) | Minimal coverage | MODERATE |
| Gnumeric | P1 | P1 | Correct (designed) | LOW |
| ABW | P1 | P1 | Correct (designed) | LOW |
| SYLK/DIF/TSV | P1 | P1 | Correct (designed) | LOW |
| CSV/NDJSON/TOML/XCF/QOI | P2 | P2 | legacy_backfill not permanent | MODERATE |
