# Next Healing Sprint Prompt
# Sprint: SPEC-AUTHORITY-LAYER-PRODUCTION-INVESTIGATION-HEALING-001
# Generated from: SPEC-AUTHORITY-LAYER-PRODUCTION-INVESTIGATION-001
# Based on: Actual repo evidence — f76d845bd3b1d61d53619fadd0f5a34a1832c8d1

---

## Mission

Execute Phase 1 of the specs authority layer healing plan.

This is NOT a cosmetic sprint. This is NOT a test-count sprint.
This sprint must prove the spec authority chain works end-to-end for ONE fact about ONE format.
If the chain does not work, the sprint is not complete.

Do not declare complete unless the pilot rerun plan's 10 pass/fail criteria are all met.

---

## Background (Read Before Starting)

The investigation sprint `SPEC-AUTHORITY-LAYER-PRODUCTION-INVESTIGATION-001` found that:

1. The spec authority layer has real implemented tools (`tools/specification-authority-layer/`, `tools/spec-normalize/`)
2. 223 authority tests pass — but they test the tools against **synthetic fixture data**, not real spec PDFs
3. Only FODS has a real cached spec PDF (`.local/spec-cache/fods/1.3/`, SHA-256 verified)
4. `.local/spec-normalize/` does NOT exist — normalization has never been run for any format
5. All `.local/spec-artifacts/` requirements are candidate status from synthetic text
6. No implementation code cites any spec fact ID (FACT-xxx)
7. Evidence declarations do not require spec_fact_refs for product work

The healing plan is in:
`reports/spec-authority/spec-authority-investigation-001/healing-design.md`

The pilot plan is in:
`reports/spec-authority/spec-authority-investigation-001/pilot-rerun-plan.md`

The verification gates are in:
`reports/spec-authority/spec-authority-investigation-001/verification-plan.md`

---

## Sprint Identity

Sprint ID: `SPEC-AUTHORITY-LAYER-PRODUCTION-INVESTIGATION-HEALING-001`

Run directory: `reports/spec-authority/spec-authority-investigation-healing-001/`

Evidence directory: `.local/evidences/spec-authority-healing-001/`

---

## Mandatory Preflight

Before any code changes:

1. Verify FODS spec PDF exists:
```bash
ls -la .local/spec-cache/fods/1.3/*.pdf
sha256sum .local/spec-cache/fods/1.3/*.pdf
```
Expected SHA-256: `92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066`

If PDF is missing: STOP. Record as BLOCKED. Do not proceed with normalization. The PDF is required.

2. Run baseline tests:
```bash
.local/venv/Scripts/python -m pytest tests/spec_authority/ tests/specification-authority-layer/ tests/requirements/ -v --tb=short
```
Expected: 223 passed. If any fail, fix before proceeding.

---

## Work Items

### WI-1: Run Normalization Pipeline for FODS (P1 — Blocks all others)

**Root cause addressed:** GAP-001 (normalization pipeline not run)

**Steps:**
1. Create `.local/spec-normalize/fods/1.3/`
2. Run `tools/spec-normalize/normalize_pdf.py` against the FODS PDF
3. Build section index with `build_section_index.py`
4. Build chunk index with `build_chunk_index.py`
5. Validate with `validate_normalized_spec.py`
6. Run determinism check (run twice; compare SHA-256 of text.txt)

**Success criteria:**
- `.local/spec-normalize/fods/1.3/text.txt` exists with >50 pages
- `sections.yaml` contains section "3.1.2" or equivalent
- `pages.jsonl` has >100 chunks
- `validate_normalized_spec.py` passes
- Two runs of normalize_pdf.py produce the same text.txt SHA-256

**If normalize_pdf.py fails or does not support the FODS PDF format:**
- Investigate what format the tool expects
- Check if FODS PDF requires a specific pdfminer/pypdf adapter
- If tool needs a small fix to handle the PDF layout, make the minimal fix
- If tool requires significant rework (>50 lines), record as BLOCKED with root cause and stop WI-1

**Evidence required:**
- `reports/spec-authority/spec-authority-investigation-healing-001/vg02-pdf-sha-verify.txt`
- `reports/spec-authority/spec-authority-investigation-healing-001/vg03-normalization-output.txt`
- `reports/spec-authority/spec-authority-investigation-healing-001/vg04-retrieval-output.txt`
- Screenshot/output of determinism check

---

### WI-2: Real Requirement Extraction from Normalized FODS Text (P1)

**Root cause addressed:** GAP-002 (synthetic seed data)
**Prerequisite:** WI-1 complete

**Steps:**
1. Run `requirement_extractor.py` against `.local/spec-normalize/fods/1.3/text.txt`
2. Compare output against existing synthetic `FODS-SPEC-001-requirements.json`
3. Verify at least one extracted requirement mentions "office:document"
4. Save as `.local/spec-artifacts/FODS-SPEC-001-requirements-real.json` (keep old file as backup)

**Success criteria:**
- New requirements file has ≥10 candidates
- At least 1 candidate has section_id pointing to section containing "3.1.2" or "Root Element"
- Status of all requirements is "candidate" (never "verified")
- Requirements have text_fragment from real spec text (not fixture strings like "Document root SHALL be office:document element.")

**Evidence required:**
- `.local/spec-artifacts/FODS-SPEC-001-requirements-real.json`
- `reports/spec-authority/spec-authority-investigation-healing-001/vg05-requirements.txt` (head -50 of the file)

---

### WI-3: Human Review Workflow — Verify One Fact (P1)

**Root cause addressed:** GAP-006 (no promotion workflow)
**Prerequisite:** WI-2 complete

**Steps:**
1. Read candidate requirements from `FODS-SPEC-001-requirements-real.json`
2. Find the requirement related to the root element being `office:document`
3. Read the actual spec text at the cited location (from normalized text or section index)
4. Verify: does the spec actually say the root element is `office:document`? (YES — ODF 1.3 §3.1.2)
5. Write to `verified-facts-real.yaml`:

```yaml
claim_id: FACT-FODS-011
claim: "FODS document root element is office:document"
confidence: high
verification_status: verified
validated_by: human
validated_at: "2026-06-06"
provenance:
  source_id: FODS-SPEC-001
  source_sha256: "sha256:92cfe64ee30a..."
  page_start: <actual page from normalized text>
  section_id: "<actual section ID from index>"
  extraction_method: tier2_lexical
```

**Do not use `spec_verifier.py` as a CLI unless it already has this functionality.
If the tool needs to be built, write the minimal human-review output directly as YAML
and document that the tool build is deferred to a subsequent sprint.**

**Success criteria:**
- `verified-facts-real.yaml` exists with at least 1 fact with `verification_status: "verified"` and `validated_by: "human"`
- The verified fact has a page_start that can be manually confirmed in the spec

**Evidence required:**
- `.local/spec-cache/fods/1.3/workbench/verified-facts-real.yaml`
- Prose explanation of which spec section was read and why the fact is confirmed

---

### WI-4: Golden Spec-Fact Test (P2)

**Root cause addressed:** GAP-007 (tests empirical, not spec-driven)
**Prerequisite:** WI-3 complete

**Steps:**
1. Write `tests/net/fods/test_fods_spec_facts.py` (or Python equivalent)
2. Add one test: parses a minimal FODS document and asserts root element handling per FACT-FODS-011
3. The test must have a comment citing the verified fact ID
4. Run the test; it must PASS

**Success criteria:**
- `test_fods_root_element_is_office_document` PASSES
- Test file has comment `# SPEC-FACT: FACT-FODS-011`

**Evidence required:**
- `tests/net/fods/test_fods_spec_facts.py` (or Python equivalent)
- `reports/spec-authority/spec-authority-investigation-healing-001/vg06-golden-test.txt`

---

### WI-5: Evidence Declaration Schema — Add spec_fact_refs (P1, warn only)

**Root cause addressed:** GAP-004 (evidence schema missing spec_fact_refs)
**Prerequisite:** None (can be done in parallel)

**Steps:**
1. Read `docs/automation/supervisor-worker-contract.md`
2. Add `spec_fact_refs: []` as an optional field to the PRODUCT_SOURCE work item schema
3. Add a validation warning (not error) in supervisor validation logic when a PRODUCT_SOURCE item has empty spec_fact_refs
4. Write a test: declaration with spec_fact_refs passes; without it, warning is logged

**Success criteria:**
- Schema updated in supervisor-worker-contract.md
- Validation produces warning (not failure) for empty spec_fact_refs
- Test passes

**Evidence required:**
- Diff of supervisor-worker-contract.md change
- Test result

---

## Required Tests

All of the following tests must pass by sprint end:

1. `tests/spec_authority/` — 163 tests (regression: must not drop)
2. `tests/specification-authority-layer/` — 28 tests (regression)
3. `tests/requirements/` — 32 tests (regression)
4. `tests/net/fods/test_fods_spec_facts.py::test_fods_root_element_is_office_document` (NEW)
5. Schema test for spec_fact_refs warning (NEW)

**Total expected: ≥226 passing (223 existing + ≥3 new)**

---

## Forbidden Paths

1. Do NOT declare WI-1 complete if `.local/spec-normalize/fods/1.3/text.txt` is empty or contains only fixture text
2. Do NOT make up requirement text — all requirements must come from the actual normalized spec
3. Do NOT set `verification_status: "verified"` via an automated tool alone — the human must read the spec
4. Do NOT submit a PRODUCT_SOURCE declaration without spec_fact_refs as part of this sprint's evidence
5. Do NOT delete or overwrite `.local/spec-cache/fods/1.3/` — it contains the only real spec PDF
6. Do NOT commit the FODS PDF to git — it is gitignored; keep it local-only
7. Do NOT push, commit, or approve gates

---

## Stop Gates

**STOP and report BLOCKED if:**
- FODS spec PDF is missing from `.local/spec-cache/fods/1.3/`
- `normalize_pdf.py` fails with an unrecoverable error (not a minor config fix)
- Requirement extraction produces 0 results from real normalized text
- Existing 223 spec_authority tests drop below 223 after any change

**STOP and report PARTIAL_COMPLETE if:**
- WI-1 and WI-2 succeed but the human review workflow (WI-3) cannot be completed due to missing tool
  → Record what was done; write the verified-facts-real.yaml manually for pilot continuity
- WI-4 (golden test) fails because the parser behavior contradicts the spec fact
  → This is a product finding, NOT an authority layer failure; record the contradiction and stop

---

## Required Evidence Bundle

At sprint end, build the declaration review package:

```bash
python tools/supervisor/build_declaration_review_package.py \
  --declaration .local/evidences/spec-authority-healing-001/evidence-declaration.yaml
```

Report the absolute path and SHA-256 of the output ZIP.

---

## Final Verdict Format

Report one of:

- `SPEC_AUTHORITY_HEALING_PHASE1_COMPLETE` — all 10 pilot pass/fail criteria met; 226+ tests passing; evidence bundle ready
- `SPEC_AUTHORITY_HEALING_PHASE1_PARTIAL_NORMALIZATION_BLOCKED` — PDF missing or normalizer failed; other WIs attempted; document findings
- `SPEC_AUTHORITY_HEALING_PHASE1_PARTIAL_EXTRACTION_FAILED` — normalization worked but requirement extraction from real text produced unexpected results; document root cause
- `SPEC_AUTHORITY_HEALING_PHASE1_PRODUCT_CONTRADICTION_FOUND` — golden test revealed parser behavior contradicts spec; escalate to product sprint

Do NOT use a generic ACCEPTED verdict for this sprint. The verdict must reflect what was actually achieved.
