# FACT-FODT-EX-* Quality Audit
**Date:** 2026-06-22
**Source:** `.local/spec-cache/fodt/odf-1.3/workbench/verified-facts-review.yaml`
**Audit scope:** All 4,909 FACT-FODT-EX-* entries; 20 sampled in detail
**Related plan section:** snoopy-juggling-seal.md §17 (Gate D3 status)
**Taskcard:** TC-FODT-AUDIT-001

---

## Summary

| Category | Count | % | Usability for TC-GUARD-001 |
|----------|-------|---|---------------------------|
| FACT-FODT-001..027 (manually verified) | 27 | 0.5% | SAFE — `independent_agent_verifier` + `tier1_section` |
| FACT-FODT-EX-* (automated extraction) | 4,909 | 99.5% | LIMITED — `deterministic_spec_text_search` only |
| — EX status: `verified` | 4,271 | 86.8% of EX | Means: spec text was found matching keyword pattern |
| — EX status: `verified_with_note` | 635 | 12.9% of EX | Means: extracted but has caveats |
| — EX status: `pending_verification` | 3 | 0.1% of EX | Not usable; explicitly pending |
| **Total facts** | **4,936** | | |

---

## Extraction Method Classification

All 4,909 EX facts share identical provenance characteristics:

| Field | Value | Meaning |
|-------|-------|---------|
| `extraction_method` | `automated_extraction` | Automated keyword/pattern scan of spec text |
| `validated_by` | `deterministic_spec_text_search` | Text-search match, NOT independent review |
| `created_by` | (missing) | No agent attribution |
| `validated_at` | (missing) | No manual validation timestamp |

Compare with the 27 manually verified facts:

| Field | Value (FACT-FODT-001..027) |
|-------|---------------------------|
| `extraction_method` | `tier1_section` |
| `validated_by` | `independent_agent_verifier` |
| `created_by` | `spec_authority_proof_closure_sprint` or `plan-hardening-sprint-20260616` |
| `spec_page_confirmed` | `true` |

---

## 20-Fact Sample Classification

| Fact ID | Claim (truncated) | vstat | Method | Classification |
|---------|-------------------|-------|--------|---------------|
| FACT-FODT-EX-0001 | `text:formula` attribute namespace rule | `verified_with_note` | automated | `NEEDS_REVIEW` — caveated |
| FACT-FODT-EX-0002 | namespace prefix binding rule | `verified_with_note` | automated | `NEEDS_REVIEW` — caveated |
| FACT-FODT-EX-0003 | spec text fragment about text:formula syntax | `verified` | automated | `AUTO_ONLY` |
| FACT-FODT-EX-0005 | additional attribute syntax rule | `verified_with_note` | automated | `NEEDS_REVIEW` — caveated |
| FACT-FODT-EX-0006 | namespace binding requirement | `verified_with_note` | automated | `NEEDS_REVIEW` — caveated |
| FACT-FODT-EX-0007 | spec text containing keyword | `verified` | automated | `AUTO_ONLY` |
| FACT-FODT-EX-0008 | spec text containing keyword | `verified` | automated | `AUTO_ONLY` |
| FACT-FODT-EX-0009 | spec text containing keyword | `verified` | automated | `AUTO_ONLY` |
| FACT-FODT-EX-0010 | spec text containing keyword | `verified` | automated | `AUTO_ONLY` |
| FACT-FODT-EX-0011 | spec text containing keyword | `verified` | automated | `AUTO_ONLY` |
| FACT-FODT-EX-0012 | spec text with caveated match | `verified_with_note` | automated | `NEEDS_REVIEW` — caveated |
| FACT-FODT-EX-0013 | spec text containing keyword | `verified` | automated | `AUTO_ONLY` |
| FACT-FODT-EX-0014 | spec text containing keyword | `verified` | automated | `AUTO_ONLY` |
| FACT-FODT-EX-0015 | spec text containing keyword | `verified` | automated | `AUTO_ONLY` |
| FACT-FODT-EX-0016 | spec text containing keyword | `verified` | automated | `AUTO_ONLY` |
| FACT-FODT-EX-0017 | spec text containing keyword | `verified` | automated | `AUTO_ONLY` |
| FACT-FODT-EX-0018 | spec text containing keyword | `verified` | automated | `AUTO_ONLY` |
| FACT-FODT-EX-0019 | spec text containing keyword | `verified` | automated | `AUTO_ONLY` |
| FACT-FODT-EX-0020 | spec text containing keyword | `verified` | automated | `AUTO_ONLY` |
| FACT-FODT-EX-0021 | spec text containing keyword | `verified` | automated | `AUTO_ONLY` |

**Classification totals (sample):**
- `AUTO_ONLY` — 15/20 (75%): Automated text-search match, spec text confirmed to contain the keyword. Fact is traceably grounded but NOT independently verified.
- `NEEDS_REVIEW` — 5/20 (25%): `verified_with_note` status indicates the extractor found a match but flagged a caveat. Requires human review before citing in a declaration.
- `template_generated` — 0/20: No purely synthetic facts found in the sample.

---

## TC-GUARD-001 Implications

**Are EX facts safe to cite in declarations?**

- `FACT-FODT-001` through `FACT-FODT-027`: **SAFE**. These are tier1_section extractions verified by `independent_agent_verifier`. Any declaration citing these passes TC-GUARD-001 validation.

- `FACT-FODT-EX-*` with `verified` status: **CONDITIONALLY SAFE**. The spec text was found and matched. The `qname` field in sal-facts-latest.json contains the EX fact ID, so V47 (`validate_spec_fact_refs_in_sal_output`) will accept it. However, the fact is NOT independently verified — it is an automated keyword extraction from the ODF 1.3 spec text. Appropriate for feature-level product claims but NOT appropriate for spec-authority gate claims.

- `FACT-FODT-EX-*` with `verified_with_note` or `pending_verification`: **NOT RECOMMENDED**. Caveated or pending. Do not cite in gate-blocking declarations.

**Recommendation:** For declarations where spec authority matters (Gate 11, RELEASE_GATE items), cite only FACT-FODT-001..027. For product deepening sprint declarations (PRODUCT_SOURCE items), EX facts with `verified` status are acceptable.

---

## Impact on §17 Gate D3

The plan §17 states: "Gate D3 — Extraction Recall Proven: COMPLETE (FODT: 4,940 facts)"

**Correction required:**
- The 4,940 count is confirmed (4,936 in current file, minor discrepancy from file version)
- But "D3 COMPLETE" implies full extraction recall. The 27 tier1_section facts are fully recall-proven. The 4,909 EX facts represent automated keyword extraction — they exist and are spec-grounded, but do NOT represent the same extraction recall quality as tier1_section.
- D3 status should read: **PARTIAL** — 27 facts tier1_section verified; 4,909 facts automated extraction (spec-grounded, not independently verified)

---

## Audit Verdict

```
FODT FACT AUDIT VERDICT: AUTOMATED_EXTRACTION_DOMINANT
- 27 facts: MANUALLY_VERIFIED (tier1_section + independent_agent_verifier)
- 4,271 EX facts: AUTO_ONLY (deterministic_spec_text_search, no caveats)
- 635 EX facts: NEEDS_REVIEW (verified_with_note)
- 3 EX facts: PENDING_VERIFICATION

Risk level: LOW for product deepening; MEDIUM for gate declarations.
Action: Update §17 to show verified_count: 27, auto_extracted: 4,909.
```
