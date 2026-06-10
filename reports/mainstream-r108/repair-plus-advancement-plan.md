# R108 Repair + Advancement Plan

## Repair Track
1. **R107 regrading:** Verify test files exist, source diffs present, skill transcripts complete. Upgrade items from ACCEPTED_WITH_LIMITATIONS to ACCEPTED_VERIFIED where evidence is complete.
2. **Source ledger closure:** Every R107 src/ change must have ledger entry with correct SHA. Verify and fix.
3. **Git state classification:** Classify all dirty files by stream/sprint/type.

## Advancement Track
1. **FODS depth:** SaveAfterEdit proof (load, edit, save, reload, verify). Demonstrates full object-model round-trip.
2. **FODT depth:** SaveAfterReplace proof (load, replace text, save, reload, verify). Demonstrates edit workflow.
3. **Netpbm depth:** Threshold operation (convert grayscale to binary based on threshold). Completes PGM→PBM pathway.
4. **Python/FOSS:** PBM probe hardening, SYLK installed-workflow verification, ZST frame inspection.
5. **Dogfood:** Save-after-edit dogfood tests for FODS and FODT.

## Quotas
- .NET APIs: 3+ (all depth/object-model)
- FOSS: 3+ test suites
- Dogfood: 2+ pipelines
- Evidence repair: R107 regrade + ledger closure
