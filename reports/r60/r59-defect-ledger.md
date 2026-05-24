# R59 Defect Ledger

**Sprint:** FORMAT-FACTORY-R60-CURRENT-HEAD-RC-ARTIFACTS-SIDECAR-CLOSURE-PHASE11-MEGA-TRAIN-001
**Date:** 2026-05-24

## Defect Ledger

| ID | Severity | Category | Description | R60 Train | Status |
|----|----------|----------|-------------|-----------|--------|
| IV-R59-001 | Critical | Sidecar | No external sidecar with uploaded ZIP | B | OPEN |
| IV-R59-002 | Critical | Sidecar | sidecar_required: true not satisfied | B | OPEN |
| IV-R59-003 | High | Validation | Validation fails without sidecar | B+M | OPEN |
| IV-R59-004 | Critical | SHA | Uploaded ZIP SHA ≠ final-verdict Pass 2 SHA | B+M | OPEN |
| IV-R59-005 | High | Packaging | source_commit = R58-era commit 7f17f43 | C | OPEN |
| IV-R59-006 | Medium | Packaging | Later commits exist after package build | C | OPEN |
| IV-R59-007 | High | Smoke | R59 APIs not proven from installed wheel | D | OPEN |
| IV-R59-008 | High | Smoke | Smoke only proves R57 APIs | D | OPEN |
| IV-R59-009 | Medium | Testing | Package tests skip current-bundle checks | E | OPEN |
| IV-R59-010 | Medium | Testing | Full packaging suite fails from extracted bundle | E | OPEN |
| IV-R59-011 | High | .NET | NuGet proof is description, not actual output | F | OPEN |
| IV-R59-012 | Medium | Reports | Reports say 7+7 but manifest has 10+10 | C | OPEN |
| IV-R59-013 | High | Packaging | R59 APIs not in built wheels (pre-R59-final) | C+D | OPEN |
| IV-R59-014 | Medium | Reports | Count inconsistency across reports/manifests | C | OPEN |
