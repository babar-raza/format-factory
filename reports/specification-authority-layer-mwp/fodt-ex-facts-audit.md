# FACT-FODT-EX-* Quality Audit
# TC-FODT-AUDIT-001
# Date: 2026-06-21
# Scope: Sample of 20 FACT-FODT-EX-* facts from verified-facts-review.yaml

---

## Summary

| Metric | Value |
|--------|-------|
| Total facts in workbench | 4936 |
| Named (FACT-FODT-001..027) | 27 |
| EX facts (FACT-FODT-EX-*) | 4909 |
| EX facts sampled | 20 (FACT-FODT-EX-0001..0021, skipping 0004) |
| Template-generated? | NO — all from `xml_element_scan` of real ODF spec |
| Independently verified? | NO — `deterministic_spec_text_search` (automated heuristic) |

---

## EX Facts Are NOT Template-Generated

The `authority_note` says "27 verified facts" but the EX facts are NOT synthetic.
They were extracted from the ODF 1.3 spec text using `xml_element_scan` method —
a real scan of the normalized spec text at `.local/spec-cache/fods/1.3/normalized/text.txt`.

**Key distinction from template facts:**
- Template facts: Hardcoded Python dicts in `sal_master_runner.py` with no spec provenance
- EX facts: Real spec text sentences extracted by automated XML element scan

---

## Verification Status Distribution (All 4909 EX Facts)

| verification_status | Count | TC-GUARD-001 Citeability |
|--------------------|-------|--------------------------|
| `verified` | 4271 | CITEABLE_WITH_CAUTION (automated scan, not human-reviewed) |
| `verified_with_note` | 635 | NEEDS_REVIEW (caveats present) |
| `` (empty) | 3 | NOT_CITEABLE |

---

## Extraction Method Distribution (All 4909 EX Facts)

| extraction_method | Count |
|------------------|-------|
| `xml_element_scan` | 4909 |

All 4909 EX facts use `xml_element_scan` — real spec text extraction.

---

## Validation Method Distribution (All 4909 EX Facts)

| validated_by | Count |
|-------------|-------|
| `deterministic_spec_text_search` | 4906 |
| `` (empty) | 3 |

**Critical distinction:** The 27 named facts (FACT-FODT-001..027) use `validated_by: independent_agent_verifier`.
The EX facts use `validated_by: deterministic_spec_text_search` — a machine heuristic, NOT independent human review.

---

## Classification Table (20 Sampled Facts)

| Fact ID | Claim (truncated) | extraction | validated_by | status | Classification |
|---------|-------------------|-----------|-------------|--------|----------------|
| FACT-FODT-EX-0001 | text:formula attribute namespace prefix | xml_element_scan | deterministic_spec_text_search | verified_with_note | NEEDS_REVIEW |
| FACT-FODT-EX-0002 | table:formula no namespace prefix | xml_element_scan | deterministic_spec_text_search | verified_with_note | NEEDS_REVIEW |
| FACT-FODT-EX-0003 | `<office:body>` shall have `<office:text>` child | xml_element_scan | deterministic_spec_text_search | verified | CITEABLE_WITH_CAUTION |
| FACT-FODT-EX-0005 | table:formula namespace prefixes bound | xml_element_scan | deterministic_spec_text_search | verified_with_note | NEEDS_REVIEW |
| FACT-FODT-EX-0006 | table:formula conforming OpenDocument formula | xml_element_scan | deterministic_spec_text_search | verified_with_note | NEEDS_REVIEW |
| FACT-FODT-EX-0007 | `<office:body>` shall have `<office:drawing>` | xml_element_scan | deterministic_spec_text_search | verified | CITEABLE_WITH_CAUTION |
| FACT-FODT-EX-0008 | `<office:body>` shall have `<office:chart>` | xml_element_scan | deterministic_spec_text_search | verified | CITEABLE_WITH_CAUTION |
| FACT-FODT-EX-0009 | `<office:body>` shall have `<office:image>` | xml_element_scan | deterministic_spec_text_search | verified | CITEABLE_WITH_CAUTION |
| FACT-FODT-EX-0010 | `<office:body>` shall have `<office:database>` | xml_element_scan | deterministic_spec_text_search | verified | CITEABLE_WITH_CAUTION |
| FACT-FODT-EX-0011 | IRI specified via xlink:href | xml_element_scan | deterministic_spec_text_search | verified | CITEABLE_WITH_CAUTION |
| FACT-FODT-EX-0012 | meta:value-type content types | xml_element_scan | deterministic_spec_text_search | verified_with_note | NEEDS_REVIEW |
| FACT-FODT-EX-0013 | text:page element master-page-name | xml_element_scan | deterministic_spec_text_search | verified | CITEABLE_WITH_CAUTION |
| FACT-FODT-EX-0014 | list without style:name — default style | xml_element_scan | deterministic_spec_text_search | verified | CITEABLE_WITH_CAUTION |
| FACT-FODT-EX-0015 | text:id attribute parent element binding | xml_element_scan | deterministic_spec_text_search | verified | CITEABLE_WITH_CAUTION |
| FACT-FODT-EX-0016 | text:change-id links to `<text:changed-region>` | xml_element_scan | deterministic_spec_text_search | verified | CITEABLE_WITH_CAUTION |
| FACT-FODT-EX-0017 | text:name attribute uniqueness (reference 1) | xml_element_scan | deterministic_spec_text_search | verified | CITEABLE_WITH_CAUTION |
| FACT-FODT-EX-0018 | text:name attribute uniqueness (reference 2) | xml_element_scan | deterministic_spec_text_search | verified | CITEABLE_WITH_CAUTION |
| FACT-FODT-EX-0019 | text:span paragraph content with text:style-name | xml_element_scan | deterministic_spec_text_search | verified | CITEABLE_WITH_CAUTION |
| FACT-FODT-EX-0020 | text:style-name references text style | xml_element_scan | deterministic_spec_text_search | verified | CITEABLE_WITH_CAUTION |
| FACT-FODT-EX-0021 | text:name attribute identical value | xml_element_scan | deterministic_spec_text_search | verified | CITEABLE_WITH_CAUTION |

### Classification Summary (20 sampled)

| Classification | Count |
|----------------|-------|
| CITEABLE_WITH_CAUTION | 14 |
| NEEDS_REVIEW | 6 |
| NOT_CITEABLE | 0 |

---

## TC-GUARD-001 Compliance Guidance

### Safe to cite in sprint declarations:
- **FACT-FODT-001..027** — `independent_agent_verifier` + `tier1_section` — ALWAYS SAFE
- **FACT-FODT-EX-* with status=`verified`** — SAFE for sprint sprint declarations with note
  that validation was `deterministic_spec_text_search`, not `independent_agent_verifier`

### Cite with caution:
- **FACT-FODT-EX-* with status=`verified_with_note`** — Include the note; do not claim full verification

### Do NOT cite:
- **FACT-FODT-EX-* with empty status** (3 facts) — Cannot cite; no validation record

---

## §17 Correction Requirement (TC-FODT-AUDIT-002)

The `authority_note` states "27 verified facts" which is misleading. Correct interpretation:

| Category | Count | Quality |
|----------|-------|---------|
| FACT-FODT-001..027 | 27 | Independently verified (independent_agent_verifier) |
| FACT-FODT-EX-* | 4909 | Spec-extracted (xml_element_scan, deterministic validation) |
| Total | 4936 | — |

Gate D3 (Extraction Recall Proven) status for FODT should be:
- `PARTIAL` — not `COMPLETE`
- Reason: The 4909 EX facts are spec-extracted but NOT independently verified per SAL §2.1 contract
- The 27 named facts ARE fully verified and D3-eligible

---

## Conclusion

FACT-FODT-EX-* facts are **NOT template-generated**. They are extracted from real ODF spec text
via automated scanning. However, per the SAL contract (§2.1), they require `independent_agent_verifier`
validation before achieving full `verified` status for governance claims.

For current sprint work, they are acceptable as supporting references with explicit caveats.
For Gate 11 gate criteria claims, only FACT-FODT-001..027 should be cited.

**TC-FODT-AUDIT-001: CLOSED.** 20 facts sampled and classified.
