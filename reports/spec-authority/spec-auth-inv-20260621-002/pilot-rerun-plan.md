# Specs Authority Layer — Pilot Run/Rerun Plan
**Run ID:** spec-auth-inv-20260621-002
**Date:** 2026-06-21

---

## Pilot Selection Rationale

**Selected: ZST (Zstandard compression — RFC 8878)**

Reasons:
1. **Spec already fetched and cached**: `.local/spec-cache/zst/rfc8878/` exists with sha256 = `8ee6be0353...` in sources.jsonl
2. **Small fact set**: 94 facts (15 hand-curated FACT-ZST-001 to FACT-ZST-015 + 79 verified_with_note)
3. **Workbench exists**: `.local/spec-cache/zst/rfc8878/workbench/` has verified-facts-review.yaml
4. **Product code has fact refs**: `src/python/zst/zst_codec.py` cites `FACT-ZST-*` in comments
5. **Source is an RFC**: publicly available, free of legal restrictions, deterministic text
6. **SAL test coverage**: `test_spec_authority_mwp.py::test_pilot_zst` exists

The ZST pilot is the smallest format that has all four required elements: cached spec, verified workbench, product code with fact refs, and existing tests.

**Secondary pilot: FODS (selective — behavioral facts only)**

FODS has a 5.2MB workbench and 4,991 facts. The secondary pilot focuses on the 78 hand-curated FACT-FODS-001 to FACT-FODS-078 only — the strongest provenance class. This proves the behavioral authority chain end-to-end without the noise of 4,913 auto-extracted facts.

---

## Pilot Plan: ZST

### Step 1: Acquire/Verify Spec Source

**Command:**
```bash
python tools/spec-cache/refresh_check.py --verbose
```

**Expected output:**
```
ZST RFC8878: not_stale (sha256: 8ee6be03...)
ZST RFC9659: not_stale (sha256: a43584f2...)
```

**Gate:** Both entries return `not_stale`. If stale: `python tools/spec-cache/acquire_spec.py --format zst --allow-network` (requires T3 authorization).

**Evidence file:** `reports/spec-authority/<run_id>/evidence/pilot-zst-01-refresh-check.txt`

---

### Step 2: Normalize/Index the Spec

**Verify normalization artifacts exist:**
```bash
ls .local/spec-cache/zst/rfc8878/
# Expected: text.txt, sections.jsonl, chunks.jsonl, citations.yaml
```

**If missing:** `python tools/spec-normalize/build_spec_workbench.py --format zst --version rfc8878`

**Evidence file:** `reports/spec-authority/<run_id>/evidence/pilot-zst-02-normalization.txt`

---

### Step 3: Extract and Verify Facts

**Run fact verification:**
```bash
python tools/specification-authority-layer/run_fact_verification.py --format zst
```

**Expected output:**
```
ZST facts: 15 verified, 0 not_found, verification pass rate: 100%
```

**Evidence file:** `.local/sal-output/fact-verification-report.json` (ZST section)

**Verify each of the 15 FACT-ZST-* facts has:**
- `source_id`: non-null
- `section_id`: valid RFC 8878 section
- `verification_evidence`: exact RFC text fragment

---

### Step 4: Generate SAL Output with Source IDs

**Command:**
```bash
python tools/specification-authority-layer/sal_master_runner.py --format zst --from-cache-only
```

**Expected:**
```json
{
  "format_id": "zst",
  "spec_facts": [
    {"qname": "FACT-ZST-001", "source_id": "SPEC-ZST-RFC8878", "section": "3.1", ...},
    ...
  ]
}
```

**Assertions:**
- All 15 FACT-ZST-* facts have non-null `source_id`
- `source_id` matches a registered entry in `sources.jsonl`
- `sal-facts-latest.json` still has 22 formats (not overwritten by single-format run — proves MVR-1)

**Evidence file:** `.local/sal-output/sal-facts-zst.json`

---

### Step 5: Feed Facts into Acquisition Task Packet

**Command:**
```bash
python tools/spec-normalize/export_task_packet.py --format zst --task-type parser
```

**Expected:** Task packet YAML with `fact_refs: [FACT-ZST-001, FACT-ZST-003, ...]`

**Verify:** Each fact_ref in the packet resolves to a fact with spec text evidence.

**Evidence file:** `.local/spec-cache/zst/rfc8878/workbench/task-packets/parser-packet.yaml`

---

### Step 6: Produce Implementation Test Case

**Create a governance-integrated test declaration:**
```yaml
planned_work_items:
  - item_id: TC-ZST-PILOT-001
    item_type: PRODUCT_SOURCE
    format_id: zst
    spec_fact_refs:
      - FACT-ZST-001
      - FACT-ZST-003
    description: "Verify ZST header magic byte detection per RFC 8878 §3.1"
```

**Run governance validators against it:**
```bash
python tools/supervisor/governance_validators.py  # or through autonomous_cycle
```

**Expected:** V13 PASS (spec_fact_refs present), V47 PASS (FACT-ZST-001 in SAL output)

**Evidence file:** `reports/spec-authority/<run_id>/evidence/pilot-zst-06-governance.json`

---

### Step 7: Deterministic Rerun

**Run SAL output twice:**
```bash
python tools/specification-authority-layer/sal_master_runner.py --format zst --from-cache-only
cp .local/sal-output/sal-facts-zst.json /tmp/zst-run1.json

python tools/specification-authority-layer/sal_master_runner.py --format zst --from-cache-only
cp .local/sal-output/sal-facts-zst.json /tmp/zst-run2.json

python -c "
import json
r1 = json.loads(open('/tmp/zst-run1.json').read())
r2 = json.loads(open('/tmp/zst-run2.json').read())
# Compare facts (excluding generated_at timestamp)
f1 = sorted([f['qname'] for f in r1.get('spec_facts',[])])
f2 = sorted([f['qname'] for f in r2.get('spec_facts',[])])
assert f1 == f2, f'Non-deterministic: {set(f1).symmetric_difference(f2)}'
print('PASS: output is deterministic')
"
```

**Evidence file:** `reports/spec-authority/<run_id>/evidence/pilot-zst-07-deterministic.txt`

---

### Step 8: Stale/Missing/Unsupported Fact Detection

**Test missing spec:**
- Rename `.local/spec-cache/zst/rfc8878/text.txt` to `text.txt.bak`
- Run `python tools/specification-authority-layer/run_fact_verification.py --format zst`
- Expected: warning "spec text not found; facts cannot be verified"
- Restore: rename back

**Test unsupported fact (hallucinated):**
- Add `FACT-ZST-FAKE-999: "ZST uses LZ4 compression"` to test fixture
- Run verification
- Expected: `verification_status: not_found_in_normalized_text`

**Evidence file:** `reports/spec-authority/<run_id>/evidence/pilot-zst-08-negative.txt`

---

### Step 9: Prevent AI-Only Facts

**Test spec_verifier anti-bypass:**
```python
from tools.specification_authority_layer.spec_verifier import verify_requirements
result = verify_requirements([{
    "req_id": "FAKE-AI-001",
    "source_id": None,  # no source
    "text_fragment": "ZST is a compression algorithm",
    "context": "ai_summary"
}])
assert result[0].status == "ANTI_BYPASS_REJECTED"
print("PASS: AI-only fact rejected")
```

**Evidence file:** `reports/spec-authority/<run_id>/evidence/pilot-zst-09-anti-bypass.txt`

---

### Step 10: Traceability Evidence Package

Final evidence for ZST pilot:
1. `spec-index.yaml` showing sha256 and download_date
2. `fact-verification-report.json` showing 15/15 verified
3. `sal-facts-zst.json` with all facts having `source_id`
4. Test declaration passing V13 and V47
5. Deterministic rerun proof
6. Negative test outputs (missing spec, hallucinated fact)

---

## FODS Secondary Pilot (behavioral facts only)

**Scope:** FACT-FODS-001 to FACT-FODS-078 only (78 hand-curated facts)

**Goal:** Prove behavioral facts have spec line citations and drive test generation

**Steps:**
1. Run `run_fact_verification.py --format fods --filter-ids "FACT-FODS-001..078"`
2. Verify all 78 have `verification_evidence` with exact spec text
3. Show FACT-FODS-001 appears in: `src/python/fods/constants.py`, `src/python/fods/neutral_model.py`
4. Show at least one test in `tests/python/fods/` covers FACT-FODS-001 behavior

**Why bounded:** 4,913 EX facts are structural enumeration; behavioral pilot only needs the 78 core facts.

---

## Pilot Success Criteria

| Criterion | ZST Target | FODS Target |
|-----------|-----------|-------------|
| Spec source has sha256 | YES | YES (92cfe64…) |
| Facts have source_id | 15/15 | 78/78 |
| Facts have verification_evidence | 15/15 | 78/78 |
| Verification pass rate | ≥90% | ≥90% |
| SAL output deterministic | YES | YES |
| V47 passes for pilot task | YES | YES |
| Anti-bypass test passes | YES | YES |
| Missing spec → warning | YES | YES |
| AI-only fact → rejected | YES | YES |
