# SAL (Specification Authority Layer) Audit

**Sprint:** forensics-archaeology-20260621

---

## SAL Infrastructure

### Tool Files (tools/specification-authority-layer/)

```
context_pack_builder.py
extractor_to_workbench_adapter.py
fact_coverage_report.py
migrate_sources_jsonl.py
qname_src_compliance_reporter.py
requirement_extractor.py
requirement_graph.py
run_extraction_pipeline.py
run_fact_verification.py
sal_master_runner.py
spec_census.py
spec_digestor.py
spec_governance_runtime.py
spec_indexer.py
spec_normalizer.py
spec_parser.py
spec_source_registry.py
spec_vault_ingest.py
spec_verifier.py
```

**Total:** 19 tool files (NOT 17 dormant as stated in older plan — some have been activated)

---

## SAL Fact Counts Per Format

| Format | Spec Facts | Source | Verified? |
|--------|-----------|--------|----------|
| fods | 4,987 | `.local/spec-cache/sal-facts-fods.json` | workbench_verified |
| fodt | 4,933 | `.local/spec-cache/sal-facts-fodt.json` | workbench_verified |
| ods | 1,066 | `.local/spec-cache/sal-facts-ods.json` | workbench_verified |
| odt | 1,066 | `.local/spec-cache/sal-facts-odt.json` | workbench_verified |
| gnumeric | (check) | `.local/spec-cache/sal-facts-gnumeric.json` | unknown |
| zst | 94 | `.local/spec-cache/sal-facts-zst.json` | workbench_verified |
| abw | (check) | `.local/spec-cache/sal-facts-abw.json` | unknown |
| csv | 0 | `.local/spec-cache/sal-facts-csv.json` | NO FACTS |
| xcf | 0 | `.local/spec-cache/sal-facts-xcf.json` | NO FACTS |
| toml | (missing) | No file found | NO FILE |
| sylk | (check) | `.local/spec-cache/sal-facts-sylk.json` | unknown |
| pbm | (check) | `.local/spec-cache/sal-facts-pbm.json` | unknown |
| pgm | (check) | `.local/spec-cache/sal-facts-pgm.json` | unknown |
| ppm | (check) | `.local/spec-cache/sal-facts-ppm.json` | unknown |

**Master summary (sal-facts-20260621.json):**
- formats_processed: 22
- spec_facts_total: 14,284
- workbench_verified_fact_total: 14,284

**Critical finding:** `workbench_verified_fact_total = spec_facts_total = 14,284` suggests
ALL facts are marked `workbench_verified`. But FODS file contains 4,987 facts and CSV/XCF
have 0. The "workbench_verified" flag appears to be auto-set during ingestion rather than
through actual human verification. This is a **verification theater** risk.

---

## FODS SAL Fact Quality (Sample)

```
FACT-FODS-001: FODS root element is <office:document> with office:mimetype attribute
  section: 3.1.2 | authority: verified-facts-review.yaml | status: verified
FACT-FODS-003: Spreadsheet content is in <office:body>/<office:spreadsheet>
  section: 3.7 | status: verified
FACT-FODS-004: Sheets are <table:table> children of <office:spreadsheet>
  section: 9.4 | status: verified
FACT-FODS-005: Rows are <table:table-row> children of <table:table>
  section: 9.4 | status: verified
```

**Quality assessment:** Facts are structural/schema-level, referencing ODF 1.3 spec sections.
They are specific, actionable, and properly typed. The qname (FACT-FODS-NNN) format is correct
and stable. However, 4,987 facts for a single format suggests either very granular extraction
or inflation. The `fods` SAL file is 3MB — this implies most facts are attribute-level details.

---

## SAL Pipeline Status

| Pipeline Step | Tool | Status |
|--------------|------|--------|
| Spec ingestion | `spec_vault_ingest.py` | PARTIAL — only run for ODF formats |
| Fact extraction | `requirement_extractor.py` | PARTIAL |
| Fact normalization | `spec_normalizer.py` | PARTIAL |
| Fact verification | `run_fact_verification.py` | SUSPECT — auto-verified |
| Workbench adaptation | `extractor_to_workbench_adapter.py` | ACTIVE |
| SAL master runner | `sal_master_runner.py` | ACTIVE (recent sprint) |
| Compliance reporter | `qname_src_compliance_reporter.py` | PARTIAL |
| Coverage report | `fact_coverage_report.py` | PARTIAL |

---

## Key Problems

### Problem 1: Verification Theater
`workbench_verified_fact_total = spec_facts_total` for all 22 formats. This means the
verification step either auto-passes everything or the verification status is set to
`verified` during ingestion without actual checking. The SAL governance runtime may be
marking facts as verified without adversarial testing.

**Evidence against this conclusion:** The FODS facts DO reference `verified-facts-review.yaml`
as their authority source. This is a human-reviewed YAML file. If this exists and was
actually reviewed by a human, the verification is real. Need to check this file exists.

### Problem 2: Empty Facts for CSV, XCF
CSV has 0 SAL facts despite being a well-specified format (RFC 4180 + IANA conventions).
XCF has 0 SAL facts. These formats cannot participate in spec-to-feature pipeline without
facts. Capability compiler for these formats returns empty results.

### Problem 3: Facts Not Linked to Code
The SAL facts reference spec sections and claim/description text. But there is no systematic
check that every `spec_qname` class attribute in source code has a corresponding `FACT-FORMAT-NNN`
entry. The linkage is manual and ad-hoc.

### Problem 4: SAL Not Regenerated Deterministically
Per the correction plan: "Facts extracted once (run030), never regenerated." The master
runner was recently run (hence 2026-06-21 timestamp on sal-facts-20260621.json), but whether
the pipeline is truly deterministic and repeatable is unverified.

---

## SAL Readiness Assessment

| Format Group | SAL Status | Ready for Spec-to-Feature? |
|-------------|-----------|---------------------------|
| FODS, FODT | 4,987 / 4,933 facts — large, verified | PARTIAL (facts exist, integration partial) |
| ODS, ODT | 1,066 facts each | PARTIAL |
| ZST | 94 facts | MINIMAL |
| Others (CSV, XCF, etc.) | 0 facts | NOT READY |

**Overall SAL Readiness:** PARTIAL — works for ODF family, broken for non-ODF formats.
