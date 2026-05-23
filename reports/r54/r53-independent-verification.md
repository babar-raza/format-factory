# R53 Independent Verification

**Sprint:** FORMAT-FACTORY-R54-SIDECAR-ENFORCEMENT-FODT-PRESERVATION-PHASE5-MEGA-TRAIN-001
**Date:** 2026-05-23
**IV sprint:** FORMAT-FACTORY-R53-SELF-VERIFYING-BASELINE-001
**IV classification:** `R53_STATE_VALIDATOR_CLEAN_PRODUCT_PARTIAL_ACCEPTED_WITH_R54_REPAIR_REQUIRED`

## Verification Findings

### Finding 1: TC-0054 Taskcard Status Not Updated (DEFECT)

**Claim:** R53 Phase Audit 4 says TC-0054 is CLOSED.
**Evidence:** `reports/r53/phase-audit-4-continuation.md` line: "TC-0054: FODS Formula Preservation — CLOSED"

**Finding:** `taskcards/TC-0054-formula-preservation-fods.md` still has `Status: OPEN`.
**Root cause:** R53 implemented and tested TC-0054 but did not update the taskcard file status field.
**Severity:** MEDIUM — inconsistency between report and taskcard.
**R54 action:** Lane 5 updates TC-0054 taskcard to CLOSED_VERIFIED.

### Finding 2: Phase Audit 4 TC Mislabeling (DEFECT)

**Claim:** R53 Phase Audit 4 report lists:
```
| FODT | Heading preservation (TC-0057) | OPEN |
| FODT | List preservation (TC-0058) | OPEN |
| FODT | Table preservation (TC-0059) | OPEN |
```

**Finding:** The actual taskcards say:
- `TC-0057`: **Inline Span Preservation** (not heading)
- `TC-0058`: **Table Preservation** (not list)
- `TC-0059`: **List Preservation** (not table)

TC-0058 and TC-0059 are **swapped** in the audit table and gap ledger.
TC-0057 is **completely wrong** (heading vs inline spans).

**Root cause:** R53 generated the phase audit without verifying against actual taskcards.
**Severity:** HIGH — the mislabeling propagates to gap-ledger (GAP-004/005/006) and requirements matrix.
**R54 action:** Lane 4 corrects the phase audit table, gap ledger, and requirements matrix. Lane 5 verifies TC-0057 title is correct in the taskcard.

### Finding 3: FODT Heading Preservation Already Implemented (FALSE CLAIM IN R53)

**Claim:** R53 Phase Audit 4 says "FODT Heading Preservation — OPEN — FODT writer does not emit heading attributes."

**Finding (VERIFIED):** FODT heading preservation is ALREADY implemented in `src/python/fodt/writer.py` since R49:
```python
if block_type == "heading":
    el = ET.SubElement(parent, _qn("text", "h"))
    level = block.get("heading_level") or 1
    el.set(_qn("text", "outline-level"), str(level))
    el.text = text
```

**Proof:** Round-trip test output:
```
HEADING_PRESERVATION: PASS -- text:h with outline-level emitted in writer
```
XML contains `<text:h text:outline-level="1">Section One</text:h>` as expected.

**Root cause:** R53 audit generated a false finding. The R49 writer fix is documented in `writer.py` docstring:
> "Heading blocks (type='heading') serialized as `text:h` with `text:outline-level`."

**Severity:** HIGH — false NOT_MET claim delays headings from being correctly classified as PASS.
**R54 action:** Lane 4 corrects heading preservation status to PASS. No heading taskcard is needed; headings are proven working. Open FODT gaps are: inline spans (TC-0057), tables (TC-0058), lists (TC-0059).

### Finding 4: Gap Ledger Inherits Mislabeling (DEFECT)

`reports/r53/gap-ledger.md`:
- GAP-004: "FODT Heading Preservation Not Implemented" → references TC-0057 (WRONG: TC-0057 is inline spans)
- GAP-005: "FODT List Preservation Not Implemented" → references TC-0058 (WRONG: TC-0058 is table)
- GAP-006: "FODT Table Preservation Not Implemented" → references TC-0059 (WRONG: TC-0059 is list)

**R54 action:** Lane 4 creates corrected `reports/r54/gap-ledger.md/json`.

### Finding 5: memory/00-index.md Lacks R53 and Later Rows (DEFECT)

**Finding:** `memory/00-index.md` stream history stops at R32. R53 (and R49-R52) memory files were created but the 00-index.md table was not updated.

**Severity:** LOW — agent continuity gap, not product defect.
**R54 action:** Lane 13 adds R53 and R54 rows to `memory/00-index.md`.

### Finding 6: Sidecar Enforcement Is Optional (IMPROVEMENT REQUIRED)

**Finding:** `validate_evidence_bundle.py --sidecar-proof` is an optional flag. No contract mechanism makes it fail-closed. A sprint claiming `SELF_VERIFYING` or `BASELINE_CLEAN` can pass without providing a sidecar.

**Severity:** MEDIUM — design gap, not an error in R53 output.
**R54 action:** Lane 2 adds `sidecar_required` contract field and fail-closed enforcement.

### Finding 7: write_sidecar_proof.py Trusts --validation-result PASS (IMPROVEMENT REQUIRED)

**Finding:** `write_sidecar_proof.py` accepts `--validation-result PASS` without running actual validation. The sidecar could lie about the validation result.

**Severity:** MEDIUM — the sidecar only adds value if it cannot be faked without running actual validation.
**R54 action:** Lane 2 adds `--verify` mode that runs actual validation before writing sidecar.

## Sidecar Verification (R53 Proof)

Run command:
```
python tools/evidence/validate_evidence_bundle.py \
  --bundle .local/evidence-bundles/r53-self-verifying-baseline.zip \
  --contract tools/evidence/contracts/r53-self-verifying-baseline.yaml \
  --check-no-pending \
  --sidecar-proof .local/evidence-bundles/r53-self-verifying-baseline.sha256-proof.json
```

Result: `BUNDLE_VALIDATION: PASS` + `SIDECAR_PROOF_VALIDATION: PASS`

Sidecar SHA-256: `8e99b1ec0191de911a1d6b2ee4c0c4aa63a7d4740b8afe8ad77f65fda263be88`
Git HEAD at sidecar creation: `7b36c4633aff6864557ca91abe21a3f1c63587db`

### No-pending Check

- 0 metadata PENDING markers
- 0 repo current-state PENDING markers
- 0 repo/reports final-verdict PENDING markers

## R53 IV Summary

| Finding | Severity | R53 Status | R54 Action |
|---------|---------|-----------|-----------|
| TC-0054 taskcard not updated | MEDIUM | DEFECT | Lane 5: close taskcard |
| Phase Audit 4 TC mislabeling | HIGH | DEFECT | Lane 4: correct audit |
| FODT heading preservation false claim | HIGH | FALSE_CLAIM | Lane 4: mark as PASS |
| Gap ledger inherits mislabeling | HIGH | DEFECT | Lane 4: correct ledger |
| 00-index.md missing rows | LOW | DEFECT | Lane 13: add rows |
| Sidecar enforcement optional | MEDIUM | GAP | Lane 2: fail-closed |
| write_sidecar trusts --validation-result | MEDIUM | GAP | Lane 2: --verify mode |

## IV Classification

**R53 final classification:**
`R53_STATE_VALIDATOR_CLEAN_PRODUCT_PARTIAL_ACCEPTED_WITH_R54_REPAIR_REQUIRED`

Real progress: preserved (sidecar protocol, TC-0054 formula fix, requirements matrix, gap ledger).
Defects: truth/label defects requiring R54 correction. No product code defects.
R53 bundle and sidecar: VALID. History preserved without rewrite.
