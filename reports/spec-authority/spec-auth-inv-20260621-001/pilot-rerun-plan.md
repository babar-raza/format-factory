# Specs Authority Layer — Pilot Run/Rerun Plan
**Run ID:** spec-auth-inv-20260621-001
**Date:** 2026-06-21

---

## Chosen Pilot: ZST (Zstandard Frame Format) Vertical Slice

### Why ZST?

ZST is the optimal pilot for proving the authority chain because:

1. **Smallest bounded spec**: RFC 8878 is ~25 pages. Complete and normative. No ambiguity.
2. **Public domain spec**: No legal barriers. T3 authorization is straightforward.
3. **Already partially done**: 15 facts registered in workbench with 100% verified status.
4. **Real product code**: `src/python/zst/zst_codec.py` has `# spec_fact_refs: FACT-ZST-001` comments.
5. **Existing tests**: ZST has tests. Can verify spec_fact→product_code→test chain.
6. **No complex XML**: Binary frame format is simpler to text-search than ODF XML namespaces.
7. **Minimal risk**: ZST does not affect Gate 11 commercial targets (FODS/FODT). Safe pilot.

**Not chosen:**
- FODS: too large (278 facts, complex XML, 27.3% coverage backlog)
- FODT: lacks spec cache sha256 (GAP-SA-002)
- Netpbm (PBM/PGM/PPM): only 2 facts each — too trivial for full pilot
- ABW: spec unavailable (status: unavailable in registry)

---

## Pilot Scope

The pilot must prove that a healed specs authority layer can:

1. Acquire or confirm the relevant spec source (RFC 8878)
2. Normalize and index spec text
3. Extract/verify spec facts with source_id and sha256
4. Generate a task-specific requirement from a verified fact
5. Feed that requirement into product implementation traceability
6. Produce tests or validation cases tied to spec facts
7. Rerun deterministically
8. Detect stale/missing spec facts
9. Prevent AI-only facts from becoming authority
10. Package evidence showing source-to-requirement-to-test-to-code traceability

---

## Pilot Task Sequence

### Phase P1 — Spec Acquisition (if not already available)

**Pre-condition check:**
```
python tools/spec-cache/refresh_check.py --format zst
```
Expected: `stale: false` OR `needs_refresh: true` if not yet cached.

**If spec not yet cached (T3 authorization required):**
1. Verify T3-1: ZST passed Gate 1 → YES (`acquisition-packs/zst/pack.yaml`)
2. Verify T3-2: Legal category 2 (public domain RFC) → YES
3. Verify T3-3: redistribution_permitted → YES (public domain)
4. Verify T3-4: canonical_url = `https://www.rfc-editor.org/rfc/rfc8878` → VERIFY
5. Verify T3-5: Spec version rfc8878 confirmed → YES
6. T3-6: Record authorization in `acquisition-packs/zst/spec-evidence.md`

**Acquisition command (requires explicit human authorization per T3-6):**
```
python tools/spec-cache/acquire_spec.py \
  --format zst \
  --version rfc8878 \
  --url https://www.rfc-editor.org/rfc/rfc8878.txt \
  --title "RFC 8878 — Zstandard Compression" \
  --legal-category 2 \
  --redistribution-permitted true \
  --allow-network
```

**Verification:**
- `cat .local/spec-cache/zst/rfc8878/spec-index.yaml` — sha256 populated, stale=false
- `python tools/spec-cache/spec_index.py --verify --format zst` — exit 0

---

### Phase P2 — Normalization and Indexing

```bash
python tools/spec-normalize/build_spec_workbench.py --format zst --version rfc8878
```

This runs: normalize_pdf.py → build_section_index.py → build_chunk_index.py → build_citation_map.py

**Verification:**
- `ls .local/spec-cache/zst/rfc8878/` — text.txt, section-index.yaml, chunk-index.jsonl, citation-map.yaml present
- `python tools/spec-normalize/validate_normalized_spec.py --format zst` — exit 0
- `wc -l .local/spec-cache/zst/rfc8878/text.txt` — line count > 100

**Determinism test:** Run normalization twice. Compare sha256 of text.txt between runs → identical.

---

### Phase P3 — Fact Verification

**Run verification against the 15 registered ZST facts:**
```bash
python tools/specification-authority-layer/run_fact_verification.py --format zst --calibrate
```
Expected: ≥12/15 found (≥80% precision before batch run is safe per calibration threshold).

```bash
python tools/specification-authority-layer/run_fact_verification.py --format zst
```
Expected: All 15 facts promoted to `verified` or `verified_with_note`.

**Verification:**
- `cat .local/spec-cache/zst/rfc8878/workbench/verified-facts-review.yaml` — all facts have `verification_status: verified`
- Each verified fact has `text_fragment` showing the matched text

---

### Phase P4 — SAL Output with Source Provenance

After MVR-1 and MVR-4 repairs from healing-design.md:

```bash
python tools/specification-authority-layer/sal_master_runner.py --format zst
```

**Verification:**
- `cat .local/sal-output/sal-facts-zst.json` — exists, non-empty
- All 15 facts have `source_id: "SPEC-ZST-RFC8878"` (not MISSING)
- All 15 facts have `sha256` field populated
- All 15 facts have `fact_status: "verified"` (not "bootstrap_only")

---

### Phase P5 — Task-Specific Requirement Generation

Generate a requirement pack for the ZST magic number check:

```bash
python tools/spec-normalize/build_requirement_pack.py \
  --format zst \
  --task parser-frame-identification \
  --fact-ids FACT-ZST-001
```

Expected output: `requirement-pack-zst-parser.json` containing:
```json
{
  "req_id": "REQ-ZST-FRAME-MAGIC",
  "source_fact_id": "FACT-ZST-001",
  "requirement_text": "Parser MUST verify the first 4 bytes equal 0xFD2FB528",
  "spec_citation": {"section_id": "3.1", "sha256": "<hash>", ...}
}
```

---

### Phase P6 — Product Code Traceability

Build and run traceability report for ZST:

```bash
python tools/traceability/fact_product_linker.py --format zst
```

Expected:
```json
{
  "FACT-ZST-001": {
    "verified": true,
    "product_files": ["src/python/zst/zst_codec.py:716"],
    "test_files": ["tests/python/zst/test_*.py"],
    "traceability": "FULL"
  }
}
```

---

### Phase P7 — Rerun Determinism Test

Run the full pilot (P1–P6) a second time without changing any inputs.

**Verification:**
- Compare `sal-facts-zst.json` between run 1 and run 2 — identical content
- Compare `verified-facts-review.yaml` — identical
- Compare `requirement-pack-zst-parser.json` — identical

---

### Phase P8 — Stale Detection Test

```bash
# Temporarily corrupt the sha256 in spec-index.yaml
python -c "
import yaml
p = '.local/spec-cache/zst/rfc8878/spec-index.yaml'
d = yaml.safe_load(open(p))
d['spec_cache_entry']['file_sha256'] = 'fakehash123'
open(p, 'w').write(yaml.dump(d))
"

# Run autonomous_cycle.py step 0a
python tools/supervisor/autonomous_cycle.py --check-sal-only  # or trigger full cycle
```

Expected: Log message `STALE: spec hash mismatch for zst/rfc8878`, derived_artifacts_stale=true, workbench NOT used until refreshed.

Restore spec-index.yaml after test.

---

### Phase P9 — AI Authority Contamination Prevention

**Test that hardcoded/AI-only fact is rejected as authority:**
```bash
python -c "
from tools.specification_authority_layer.spec_verifier import verify_requirements
fake_req = [{'req_id': 'REQ-TEST', 'source_id': '', 'text_fragment': 'AI-generated claim'}]
results = verify_requirements(fake_req, registered_source_ids=['SPEC-ZST-RFC8878'])
print(results[0].status)  # Expected: ANTI_BYPASS_REJECTED
"
```

**Test that bootstrap_only fact is not confused with verified:**
```bash
python -c "
import json
d = json.load(open('.local/sal-output/sal-facts-zst.json'))
bootstrap = [f for f in d['spec_facts'] if f.get('fact_status') == 'bootstrap_only']
verified = [f for f in d['spec_facts'] if f.get('fact_status') == 'verified']
print(f'bootstrap: {len(bootstrap)}, verified: {len(verified)}')
# After pilot: bootstrap=0 or minimal, verified=15
"
```

---

### Phase P10 — Evidence Packaging

Bundle evidence for the pilot:
```bash
python tools/evidence/build_evidence_bundle.py \
  --run-id spec-auth-pilot-zst-20260621 \
  --include .local/sal-output/sal-facts-zst.json \
  --include .local/spec-cache/zst/rfc8878/spec-index.yaml \
  --include .local/spec-cache/zst/rfc8878/workbench/verified-facts-review.yaml \
  --include reports/spec-authority/spec-auth-inv-20260621-001/
```

---

## Success Criteria

The pilot is a SUCCESS if:
1. ≥12/15 ZST facts verified against spec text (P3)
2. All verified facts have source_id and sha256 (P4)
3. Requirement REQ-ZST-FRAME-MAGIC generated with spec citation (P5)
4. Traceability report shows FACT-ZST-001 → product file → test (P6)
5. Two runs produce identical output (P7)
6. Stale hash detected and workbench blocked (P8)
7. ANTI_BYPASS_REJECTED for AI-only claim (P9)

**The pilot is NOT a success if:**
- "verified" facts have source_id=null (bootstrap_only in disguise)
- Spec citation is present but points to wrong section
- Second run produces different output (non-deterministic)
- Stale hash not detected automatically

---

## Why This Pilot Is Representative

ZST is representative because:
- It tests the FULL authority chain (acquisition → normalization → extraction → verification → SAL → traceability)
- It uses a real, publicly available spec (RFC 8878) — not synthetic
- It has existing product code and tests to verify traceability
- It is small enough (15 facts) to fully verify every fact manually if needed
- It demonstrates the three-tier retrieval strategy (section lookup is feasible with RFC structure)
- If the authority chain cannot be proven for ZST (the simplest case), it cannot be proven for FODS/FODT either

Completing this pilot provides the model that can be repeated for FODT, then FODS, then all other formats.
