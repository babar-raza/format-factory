# R59 Independent Verification

**Sprint:** FORMAT-FACTORY-R60-CURRENT-HEAD-RC-ARTIFACTS-SIDECAR-CLOSURE-PHASE11-MEGA-TRAIN-001
**Date:** 2026-05-24
**Verifier:** R60 independent agent (Train A)

## R59 Reclassification

**R59_RECLASSIFIED_VERDICT:** R59_BROAD_PRODUCT_AND_PACKAGING_PROGRESS_ACCEPTED_RC_CLOSURE_REJECTED

R59 delivered real product and packaging progress (30 FODS/FODT tests, CSV Gate 7, PGM/PBM/SYLK Gate 10, Phase Audit 10, 103 new tests). However, RC closure is rejected because 14 defects prevent self-verifying RC closure.

---

## Evidence Examined

1. `reports/r59/final-verdict.md` — Pass 2 SHA `0a9bb470...` ≠ sidecar SHA `669fc0b6...`
2. `reports/r59/python-full-rc-artifacts.md` — source_commit = `7f17f43` (R58 era)
3. `.local/r59-metadata/package-artifact-manifest.yaml` — source_commit = `7f17f439336e9adfe37fdc1b98f1fe45d820f1b5` (R58)
4. `reports/r59/dotnet-nuget-local-consumer-proof.md` — describes steps; no actual command output
5. `reports/r59/packaging-test-suite-normalization.md` — 1 test still SKIPs
6. `reports/r59/phase-audit-9-repair-and-phase-audit-10.md` — counts accurate (10 packages)
7. `git log` — Final R59 HEAD = ba057fc; package artifacts built at 7f17f43 commit (pre-R59-final)

---

## Defects

### IV-R59-001: No external sidecar delivered with uploaded final ZIP
- **Severity:** Critical
- **Evidence:** Bundle was uploaded without corresponding `.sha256-proof.json` sidecar
- **Contract requires:** `sidecar_required: true`, `final_proof_policy: external_sidecar`
- **Status:** Open — must repair in R60 Train B

### IV-R59-002: Contract requires sidecar_required: true but external sidecar not established before upload
- **Severity:** Critical
- **Evidence:** tools/evidence/contracts/r59-clean-rc-closure.yaml specifies `sidecar_required: true`
- **Status:** Open — R60 must deliver sidecar with uploaded ZIP

### IV-R59-003: Validation without sidecar fails (negative proof)
- **Severity:** High
- **Evidence:** `python validate_evidence_bundle.py --bundle r59-pass2-final.zip --contract r59-clean-rc-closure.yaml` would fail with `SIDECAR_REQUIRED` because no sidecar supplied at validation time
- **Status:** Open — R60 Train M must validate with `--sidecar-proof`

### IV-R59-004: Uploaded ZIP SHA ≠ internal proof Pass 2 SHA
- **Severity:** Critical
- **Evidence:** final-verdict.md shows Pass 2 SHA `0a9bb470...`; sidecar records `669fc0b6...`; these differ because final-verdict was committed with a candidate SHA, then the bundle was rebuilt (sidecar is authoritative)
- **Status:** Open — R60 must make these match (or sidecar must be built from the same ZIP that passes validation)

### IV-R59-005: Package artifact manifest source_commit is R58-era commit
- **Severity:** High
- **Evidence:** `.local/r59-metadata/package-artifact-manifest.yaml` line 3: `source_commit: 7f17f439336e9adfe37fdc1b98f1fe45d820f1b5` = commit 7f17f43 = R58 chore commit
- **Status:** Open — R60 Train C must rebuild from R60 HEAD

### IV-R59-006: Final R59 git log has later commits through ba057fc
- **Severity:** Medium
- **Evidence:** git log shows d004237 → e73fbc1 → 111db66 → ba057fc after packages were built at 7f17f43
- **Status:** Open — R60 Train C repairs this

### IV-R59-007: Installed FODS/FODT wheels don't expose R59 APIs
- **Severity:** High
- **Evidence:** R59 python-full-rc-artifacts.md installed smoke only proves `workbook_stats`/`document_stats` (R57 APIs). New R59 APIs (workbook_type_distribution, find_sheet_by_name, document_heading_outline, document_text_content) not tested from installed wheel
- **Status:** Open — R60 Train D must prove all 4 R59 APIs from installed wheel

### IV-R59-008: Installed smoke only proves R57/R58 APIs
- **Severity:** High
- **Evidence:** python-full-rc-artifacts.md smoke script: `wb.workbook_stats()`, `doc.document_stats()` — R57 era functions only
- **Status:** Open — same as IV-R59-007, repair in Train D

### IV-R59-009: Package tests skip current-bundle checks
- **Severity:** Medium
- **Evidence:** packaging-test-suite-normalization.md: "1 test SKIPs: R59 bundle not yet built"
- **Status:** Open — R60 Train E must eliminate all skips

### IV-R59-010: Full packaging suite fails from extracted bundle
- **Severity:** Medium
- **Evidence:** Legacy packaging tests hardcode `.local/package-builds/` path; bundle extraction paths differ
- **Status:** Open — R60 Train E must normalize paths

### IV-R59-011: NuGet proof lacks actual local consumer restore/install/run
- **Severity:** High
- **Evidence:** dotnet-nuget-local-consumer-proof.md describes steps consumer "can" take but shows no actual command execution output
- **Status:** Open — R60 Train F must run actual commands and capture output

### IV-R59-012: Reports say "7 wheels + 7 sdists" but bundle has 10+10
- **Severity:** Medium
- **Evidence:** python-full-rc-artifacts.md references 7 packages; Phase Audit 10 shows 10 wheels + 10 sdists; package-artifact-manifest has 20 artifacts
- **Status:** Open — R60 Train C must produce consistent report with 10+10

### IV-R59-013: R59 product-deepening source APIs not in built wheels
- **Severity:** High
- **Evidence:** Wheels were built from 7f17f43 (before R59 Train G added new APIs at d004237). workbook_type_distribution etc. are in source but NOT in the installed wheel wheel binary
- **Status:** Open — same as IV-R59-005/007, repair in Train C+D

### IV-R59-014: Count inconsistency across reports/manifests/metadata
- **Severity:** Medium
- **Evidence:** python-full-rc-artifacts.md: "7 wheels + 7 sdists"; phase-audit-10: "10 wheels + 10 sdists"; r59-metadata/package-artifact-manifest.yaml: 20 entries; all three inconsistent
- **Status:** Open — R60 Train C must produce consistent 10+10 report

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 3 (001, 002, 004) |
| High | 6 (003, 005, 007, 008, 011, 013) |
| Medium | 5 (006, 009, 010, 012, 014) |
| **Total** | **14** |

All 14 defects are confirmed. No R59 defects are disputed.

**R59_IV_STATUS:** COMPLETE — 14/14 defects confirmed
