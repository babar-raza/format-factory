# R60 Work-Ahead Policy

**Sprint:** FORMAT-FACTORY-R60-CURRENT-HEAD-RC-ARTIFACTS-SIDECAR-CLOSURE-PHASE11-MEGA-TRAIN-001
**Date:** 2026-05-24

## Policy

1. **Auto-expansion:** Lanes that finish early must look for the next safe adjacent work
2. **Critical path:** Train G (source changes) → Train C (rebuild packages) → Train D (smoke) → Train M (bundle)
3. **Independent lanes** (can run in any order): A, B, E, F, H, I, J, K, L
4. **No PENDING at close:** Every metadata file must have real values. No placeholder SHAs.
5. **Internal adversarial review required before Train M:** Must self-challenge all claims
6. **No stop after first contradiction:** Governance mandate — continue all other lanes

## R60 Mandatory Deliverables

- [ ] External sidecar file alongside final ZIP
- [ ] All 10 packages rebuilt from R60 HEAD (source_commit = R60 HEAD SHA)
- [ ] Installed smoke proving: workbook_type_distribution, find_sheet_by_name, document_heading_outline, document_text_content
- [ ] .NET consumer restore/install/run (actual commands, not description)
- [ ] No packaging tests skipping
- [ ] Phase Audit 11 PASS
- [ ] BUNDLE_VALIDATION: PASS with sidecar proof

## Escalation

If any lane cannot deliver a mandatory deliverable, the issue must be documented in `risk-register.md` and Train M must reflect the actual status (partial closure allowed as a verdict).
