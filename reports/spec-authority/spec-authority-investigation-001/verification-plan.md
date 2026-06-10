# Specs Authority Layer — Verification Plan
# Sprint: SPEC-AUTHORITY-LAYER-PRODUCTION-INVESTIGATION-001
# Generated: 2026-06-06

---

## Verification Gates

### VG-01: Baseline Tests Pass Before Any Changes

**Command:**
```bash
.local/venv/Scripts/python -m pytest tests/spec_authority/ tests/specification-authority-layer/ tests/requirements/ -v --tb=short
```

**Expected Result:** 223 passed, 0 failed

**Failure Interpretation:** Pre-existing regression; do not proceed with healing until baseline is green

**Evidence File:** `reports/spec-authority/spec-authority-investigation-001/vg01-baseline-test-results.txt`

**Blocking:** YES

---

### VG-02: FODS Spec PDF Is Present

**Command:**
```bash
ls -la .local/spec-cache/fods/1.3/*.pdf
sha256sum .local/spec-cache/fods/1.3/*.pdf
```

**Expected Result:** File exists; SHA-256 = `92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066`

**Failure Interpretation:** PDF missing or corrupted; re-download required with T3 authorization before normalization can run

**Evidence File:** `reports/spec-authority/spec-authority-investigation-001/vg02-pdf-sha-verify.txt`

**Blocking:** YES (for normalization gate)

---

### VG-03: Normalization Pipeline Runs Successfully (FODS)

**Command:**
```bash
python tools/spec-normalize/normalize_pdf.py \
  --input .local/spec-cache/fods/1.3/OpenDocument-v1.3-os-part3-schema.pdf \
  --output .local/spec-normalize/fods/ \
  --format-id fods --version 1.3

python tools/spec-normalize/validate_normalized_spec.py --path .local/spec-normalize/fods/
```

**Expected Result:** Exit 0; `.local/spec-normalize/fods/text.txt` exists; validation passes

**Failure Interpretation:** Normalizer bug or PDF layout issue; investigate normalize_pdf.py; may need format-specific adapter

**Evidence File:** `reports/spec-authority/spec-authority-investigation-001/vg03-normalization-output.txt`

**Blocking:** YES (blocks VG-04 through VG-07)

---

### VG-04: Lexical Retrieval Works on FODS Spec

**Command:**
```bash
python tools/spec-normalize/query_normalized_spec.py \
  --format-id fods \
  --path .local/spec-normalize/fods/ \
  --section "3.1.2"

python tools/spec-normalize/query_normalized_spec.py \
  --format-id fods \
  --path .local/spec-normalize/fods/ \
  --keyword "office:document"
```

**Expected Result:** Section 3.1.2 returns text about office:document root element; keyword search returns relevant pages with citations

**Failure Interpretation:** Section index or chunk index building failed; re-run build_section_index.py and build_chunk_index.py

**Evidence File:** `reports/spec-authority/spec-authority-investigation-001/vg04-retrieval-output.txt`

**Blocking:** YES

---

### VG-05: Real Requirement Extraction from FODS Spec

**Command:**
```bash
python tools/specification-authority-layer/requirement_extractor.py \
  --source-id FODS-SPEC-001 \
  --input .local/spec-normalize/fods/text.txt \
  --sections .local/spec-normalize/fods/sections.yaml \
  --format-id fods \
  --output .local/spec-artifacts/FODS-SPEC-001-requirements-real.json
```

**Expected Result:** Requirements file with N>10 candidate requirements; each has section_id, heading, text_fragment, keyword from real spec text; status="candidate"

**Failure Interpretation:** Extraction yielded 0 requirements → normalizer output format incompatible with extractor; fix schema mismatch

**Evidence File:** `.local/spec-artifacts/FODS-SPEC-001-requirements-real.json`

**Blocking:** YES

---

### VG-06: Golden Spec-Fact Test — FODS Root Element

**Test:** Write a test that reads a minimal FODS file and asserts root element is `office:document` per FACT-FODS-001

**Command:**
```bash
.local/venv/Scripts/python -m pytest tests/net/fods/test_fods_spec_facts.py -v --tb=short
```

**Expected Result:** `test_fods_root_element_office_document` PASSED

**Failure Interpretation:** Parser does not correctly handle the root element as per spec; implementation gap found

**Evidence File:** `reports/spec-authority/spec-authority-investigation-001/vg06-golden-test-results.txt`

**Blocking:** YES (for pilot proof)

---

### VG-07: Human Review Workflow Promotes Candidate to Verified

**Command:**
```bash
# Run review CLI on one candidate requirement
python tools/specification-authority-layer/spec_verifier.py \
  --review \
  --requirements .local/spec-artifacts/FODS-SPEC-001-requirements-real.json \
  --spec-text .local/spec-normalize/fods/text.txt \
  --output .local/spec-cache/fods/1.3/workbench/verified-facts-real.yaml
```

**Expected Result:** At least 1 requirement promoted to verified; YAML file updated with `verification_status: "verified"` and `validated_by: "human"`

**Failure Interpretation:** Review CLI not built yet; this is the missing tool to implement

**Evidence File:** `.local/spec-cache/fods/1.3/workbench/verified-facts-real.yaml`

**Blocking:** YES (for full pilot proof)

---

### VG-08: Evidence Declaration Validation (Schema Check)

**Command:**
```bash
# Create a test declaration without spec_fact_refs
# Expect validation to warn (Phase 1) or fail (Phase 2)
.local/venv/Scripts/python tools/supervisor/validate_declaration.py \
  --declaration tests/fixtures/test-declaration-no-spec-facts.yaml \
  --mode warn
```

**Expected Result:** Warning issued for PRODUCT_SOURCE item missing spec_fact_refs

**Failure Interpretation:** Schema not yet updated; update supervisor-worker-contract.md first

**Evidence File:** `reports/spec-authority/spec-authority-investigation-001/vg08-schema-check.txt`

**Blocking:** NO (advisory for Phase 1)

---

### VG-09: Full Pilot Regression — Existing Tests Still Pass

**Command:**
```bash
.local/venv/Scripts/python -m pytest tests/spec_authority/ tests/specification-authority-layer/ tests/requirements/ tests/requirement_capability_authority/ -v --tb=short
```

**Expected Result:** All tests that passed before still pass; no regressions from healing changes

**Failure Interpretation:** Healing changes broke existing functionality; rollback the specific change and investigate

**Evidence File:** `reports/spec-authority/spec-authority-investigation-001/vg09-regression-results.txt`

**Blocking:** YES

---

### VG-10: Source Registry Persistence Check

**Command:**
```bash
# After any acquisition task runs:
ls -la .local/spec-source-registry/sources.jsonl
tail -5 .local/spec-source-registry/sources.jsonl
```

**Expected Result:** File exists; contains JSON entries with source_id, format_id, registered_at

**Failure Interpretation:** Registry persistence not wired into acquisition entry point; wire spec_source_registry.register_source() into task startup

**Evidence File:** `reports/spec-authority/spec-authority-investigation-001/vg10-registry-persistence.txt`

**Blocking:** NO (Phase 2)

---

## Negative Tests Required

| Negative Test | What It Verifies | Expected Outcome |
|---------------|-----------------|-----------------|
| Query with wrong format-id | Format isolation | Returns empty result or error, not results from another format |
| Ingest spec with wrong SHA-256 | Tamper detection | spec_vault_ingest.verify_snapshot_integrity() raises error |
| Cite unregistered source | Anti-bypass | spec_governance_runtime.check_citation_allowed() returns REJECTED |
| Set requirement status=verified via tool (not human review) | Lifecycle enforcement | Tool raises error or returns REJECTED |
| Declare PRODUCT_SOURCE without spec_fact_refs | Schema enforcement | Validation warns/fails |

---

## Pilot Rerun Test

After all verification gates pass, the pilot rerun must demonstrate:

1. Start with empty `.local/spec-normalize/fods/` (clean state)
2. Run normalization pipeline — deterministic output
3. Run requirement extractor — same requirements as previous run (determinism check)
4. Human review one fact — update verified-facts-real.yaml
5. Run golden spec-fact test — PASS
6. Run full test suite — no regressions
7. SHA-256 of normalized text matches spec PDF hash

**This proves the spec authority chain is deterministic and repeatable.**
