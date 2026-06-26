# ZST SAL Fact-Depth Pilot
## Taskcard: TC-LA-PILOT-005
## Date: 2026-06-26
## Analyst: autonomous sprint (FORMAT-FACTORY-LAYER-AUDIT-20260626)
## Mode: READ-ONLY (no SAL runner execution; no zst.yaml edits)

---

## Pre-Check Results

### ZST SAL Facts (`.local/spec-cache/sal-facts-zst.json`)

| Field | Value |
|---|---|
| format_id | zst |
| generated_at | 2026-06-21T14:44:45.277602+00:00 |
| spec_facts count | **94** |
| Source | `.local/spec-cache/zst/` (normalized spec text) |

### ZST QName Registry (`shared/qname-registry/zst.yaml`)

| QName | spec_fact_ref | Status |
|---|---|---|
| `zst:frame` | FACT-ZST-001 | **LINKED** |
| `zst:block` | FACT-ZST-002 | **LINKED** |
| `zst:magic-number` | FACT-ZST-003 | **LINKED** |

**All 3 ZST QName entries already have spec_fact_ref populated.** The linkage was completed prior to this sprint. Zero entries require updating.

### SAL Facts Consolidated (`sal-facts-latest.json`)

| Field | Value |
|---|---|
| formats_processed | 25 |
| spec_facts_total | 14,441 |
| ZST entry in results | 1 (ZST appears in results metadata) |

Note: `sal-facts-latest.json` stores format-level results metadata, not individual facts. The 94 ZST facts live in `sal-facts-zst.json`. This is the correct architecture.

---

## Execution

**SAL runner executed: NO**

Reason: The write condition in the plan was not met — zst.yaml already has all 3 spec_fact_ref values populated (FACT-ZST-001, FACT-ZST-002, FACT-ZST-003). Per TC-LA-PILOT-005 plan: "The conditional write in step 5 is ALREADY DONE — skip it. This taskcard is now READ-ONLY documentation of the completed linkage state."

Additionally, the SAL facts file (`sal-facts-zst.json`) contains 94 spec facts confirming extraction was completed on 2026-06-21.

---

## QName Linkage

| Metric | Value |
|---|---|
| QName entries with spec_fact_ref populated | 3 / 3 (100%) |
| QName entries still missing spec_fact_ref | **0** |
| SAL facts available for ZST format | 94 |
| Fact IDs used in qname linkage | FACT-ZST-001, FACT-ZST-002, FACT-ZST-003 |

---

## Effort Estimate for Next 3 Formats (SAL Fact Extraction)

| Format | SAL Facts Available | Blocker | Estimate |
|---|---|---|---|
| **CSV** | Unknown (spec-cache/csv/ exists) | CSV has no single authoritative spec (RFC 4180 is informational); normalized text may be sparse | 2-4h: normalize RFC 4180 text, run sal_master_runner.py, link to csv.yaml |
| **NDJSON** | Unknown | No IETF RFC for NDJSON; informal spec only (ndjsonl.org) | 3-5h: manual normalization required; may yield 10-30 facts only |
| **TSV** | Unknown | No formal spec; TSV is ad-hoc convention; no IANA registration | 4-6h: compose normative text from TSV conventions; minimal fact yield expected |

**Key constraint for all 3:** The SAL extraction pipeline (`sal_master_runner.py`) requires a normalized text file in `.local/spec-cache/{format}/`. Without a formal spec source, normalization must be done manually — the main cost for these formats.

---

## Verdict

**PILOT_PASS**

The ZST SAL linkage is complete: 94 spec facts extracted, all 3 QName entries linked to FACT-ZST-001/002/003. This taskcard documents the existing complete state. No action was needed in this sprint.

The next priority for SAL expansion is the ODF-family formats (ODS/ODT already chain-intact per `chain-verification-multiformat.json`) or CSV if RFC 4180 normalization can be automated.
