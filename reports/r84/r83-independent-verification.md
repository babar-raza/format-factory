# R84 Train A — R83 Independent Verification

**Sprint:** FORMAT-FACTORY-R84
**Date:** 2026-05-31

## Verification Steps

### Step 1: Review Package SHA Verification

Supervisor-computed SHA matches:
- Review package SHA: 3d6ce35d64ff72f7a6fc82dad9e23824ad8371e0cf70955f7b066bb93a410bea
- CONFIRMED: matches final-verdict.md record

### Step 2: Delivery Package SHA

- Delivery package SHA: cd0251efdee89756cb28605f71658e23a3f3bbd50214347e1f5fa4ea2802430b
- CONFIRMED: matches final-verdict.md record

### Step 3: Inner ZIP SHA + Sidecar

- Inner ZIP SHA: 7512118ad867a9e6ea24c11a1d4197f2c14f615092b02024e8f4837e93f5789b
- Sidecar SHA: d08acf01d9705400e182a31b79753ef5439b56096523bd96cc0f3b26385957ef
- CONFIRMED: sidecar validates inner ZIP

### Step 4: Package Artifacts

- 20 artifacts confirmed (10 wheels + 10 sdists)
- Hashes verified by supervisor against package-artifact-manifest.yaml
- CONFIRMED: all 20 match

### Step 5: FODS/FODT Installed APIs

FODS installed APIs confirmed by supervisor:
- parse_fods, write_fods, workbook_set_cell_value, workbook_add_sheet
- workbook_rename_sheet, workbook_remove_sheet, workbook_to_xml
- workbook_warnings_for_unsupported_edit
CONFIRMED: matches source

FODT installed APIs confirmed:
- parse_fodt, write_fodt, document_set_block_text, document_append_paragraph
- document_remove_paragraph, document_paragraph_count, document_to_xml
- document_warnings_for_unsupported_edit
CONFIRMED: matches source

### Step 6: Inner Final-Verdict PENDING Values

CONFIRMED D83-02: `Python: PENDING_TEST_RUN` found in inner ZIP's repo/reports/r83/final-verdict.md
CONFIRMED D83-03: `Pass 2 SHA-256: delegated_to_final_artifact_authority_json`
CONFIRMED D83-04: `Sidecar SHA-256: delegated_to_final_artifact_authority_json`
CONFIRMED D83-05: `SIDECAR_PROOF_VALIDATION: PENDING`

Root cause: Pass 2 bundle was built before final-verdict was updated with real values.
The committed version of final-verdict.md (post-bundle) has real values, but inner ZIP captured pre-update state.

### Step 7: Metadata PENDING_BUILD Content

CONFIRMED D83-06/07: delivery-package-validation-summary.txt STATUS: PENDING_BUILD, SHA: PENDING
CONFIRMED D83-08: external-sidecar-proof-summary.txt STATUS: PENDING_BUILD
CONFIRMED D83-09: final-artifact-authority-summary.txt "will be populated after build"
CONFIRMED D83-10/11/12: final-bundle-validation-proof.txt stale (5,794,220 bytes / 3380 entries vs actual 6,022,869 / 3402)

### Step 8: Raw Logs Not Physically Present

CONFIRMED D83-16: raw-package-install-log-summary.txt points to .local/r83-install-logs/ (not in review package)
CONFIRMED D83-17: raw-negative-proof-summary.txt points to .local/r83-negative-proof-logs/ (not in review package)

### Step 9: State no_final_verdict

CONFIRMED D83-13: state/current-state.md: Latest sprint: R83 - no_final_verdict
CONFIRMED D83-14: state/current-state.json same
Root cause: state_snapshot.py ran before final-verdict regex was working for R83 format.

### Step 10: Master-Plan Stale

CONFIRMED D83-15: plans/master-plan.md carries old version text

### Step 11: ZST Offline Install

CONFIRMED D83-18: `pip install --no-index aspose-format-factory-zst` fails — zstandard>=0.21.0 not available
No dependency-artifacts/ in review package

### Step 12: .NET Proof Inherited

CONFIRMED D83-19: dotnet-test-results.txt: "R82 source / no .NET changes in R83"
No fresh .NET run in R83

### Step 13: Next-Format Advancement

CONFIRMED D83-20: Netpbm: HOLD_PRIMARY_FORMAT_PRIORITY, SYLK/DIF: HOLD_PRIMARY_FORMAT_PRIORITY
No real source/test advancement

## IV Result

All 20 supervisor defects independently reproduced and confirmed.

**R83_IV: COMPLETE — 20/20 CONFIRMED_CARRIED_TO_R84**
