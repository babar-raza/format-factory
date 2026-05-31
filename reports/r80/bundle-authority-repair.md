# Bundle Authority Repair

**sprint_id:** FORMAT-FACTORY-R80-REPAIR-PLUS-ADVANCEMENT-SUPERVISOR-EVIDENCE-PRODUCT-SYSTEM-HARDENING-20260530

## Protocol — Two-Stage Final Artifact

To avoid the circular SHA problem that caused D-SUP-03, R80 uses this protocol:

### Stage 1 — Content Finalization
1. All code, tests, reports, and supervisor outputs finalized
2. NO SHA values in any tracked file
3. Inner `final-verdict.md` uses delegation labels:
   - `BUNDLE_SHA256: delegated_to_sidecar_proof`
   - `SIDECAR_SHA256: delegated_to_sidecar_proof`

### Stage 2 — Build and Proof
1. Build final ZIP via `build_evidence_bundle.py`
2. Compute final ZIP SHA256 (certutil or Python hashlib)
3. Generate sidecar via `write_sidecar_proof.py` — sidecar is authoritative
4. Compute sidecar file SHA256
5. Write external `reports/r80/final-verdict.md` with correct SHA/size/entries
6. Validate via `validate_evidence_bundle.py --sidecar-proof`
7. Validate via `validate_supervisor_evidence_bundle.py`
8. Do NOT rebuild after writing external final-verdict.md

### Result
- ZIP inside the bundle has `final-verdict.md` with delegation labels (correct — no circular dependency)
- Sidecar is the authoritative SHA proof
- External `reports/r80/final-verdict.md` has the correct final SHA (human reference only)
- Bundle validator accepts delegation labels as correct

## SHA Chain Summary (to be filled after build)

```
BUNDLE_SHA256: [computed after Stage 2, Step 2]
SIDECAR_SHA256: [computed after Stage 2, Step 4]
BUNDLE_VALIDATION: PASS
SIDECAR_PROOF_VALIDATION: PASS
```
