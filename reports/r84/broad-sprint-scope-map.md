# R84 Broad Sprint Scope Map

**Sprint:** FORMAT-FACTORY-R84
**Date:** 2026-05-31

## Train A: R83 IV and Defect Ledger
- Reproduce all 20 supervisor defects
- Classify each
- Write defect ledger.md + .json

## Train B: Top-Level Review Package Self-Containment
- Modify build_supervisor_review_package.py: --extra-top-level-dirs parameter
- Include at top level: package-artifacts/, raw-test-logs/, raw-package-install-logs/, raw-negative-proof-logs/, raw-dotnet-logs/, product-capability-matrix/, examples-docs-readiness/, gate-readiness/, publication-readiness/, final-metadata/, validation-proofs/
- 4 new test files

## Train C: Final Metadata Closure
- 3-pass bundle protocol: no PENDING/delegated in inner final-verdict
- All metadata files finalized before final bundle build
- delivery-package-validation-summary, external-sidecar-proof-summary, final-bundle-validation-proof all real values
- 4 new test files

## Train D: Raw Proof Log Inclusion
- Generate fresh raw install logs (pip install fods/fodt wheels)
- Generate fresh raw negative proof logs
- Generate full Python test log
- Generate .NET test log
- 4 new test files

## Train E: Validator Fail-Closed Tests
- 10 new validator assertions covering R83 defect patterns

## Train F: FODS Alpha Product Proof from Top-Level
- Build fresh FODS wheel
- Installed workflow from top-level package-artifacts/
- 1 new test file

## Train G: FODS Feature Advancement
- workbook_to_csv(wb, sheet_name) — CSV export for specific sheet
- workbook_get_cell_value(wb, sheet, row, col) — read cell value
- Source changes + tests + docs

## Train H: FODT Installed Product Proof
- Build fresh FODT wheel
- Installed workflow from top-level
- 1 new test file

## Train I: FODT Feature Advancement
- document_to_text(doc) — plain text export
- document_get_paragraph_text(doc, idx) — get specific paragraph text
- Source changes + tests + docs

## Train J: ZST Dependency Policy
- Classify: DEPENDENCY_RESOLUTION_REQUIRED
- Include raw failing no-network install log
- dependency-artifacts/README.md with classification
- 2 new test files

## Train K: Fresh .NET Proof
- Run FODS .NET tests → save raw log
- Run FODT .NET tests → save raw log
- Capture fresh test count

## Train L: .NET Parity Advancement
- FODS: add workbook_sheet_count or equivalent .NET helper
- FODT: add paragraph_count equivalent
- Tests if implemented

## Train M: Netpbm Real Advancement
- PBM: add write_pbm / roundtrip test
- PGM: add write_pgm / roundtrip test
- PPM: add PPM parser basic support
- Tests

## Train N: SYLK/DIF Real Advancement
- SYLK: add sylk_to_csv export + tests
- DIF: add dif_to_csv export + tests

## Train O: Probe Package Truth
- Verify FODP/FODG/Gnumeric/ABW installed APIs
- Classify each
- One safe probe improvement

## Train P: Gate 8 Readiness Truth
- Gate 8 matrix for ODS/ODT/QOI/XCF/DIF/PPM
- 2 new security tests
- Gate 8 approved=false

## Train Q: Gate 11 Product Truth Packet
- FODS/FODT G11 status matrix
- Publication blockers
- Gate 11 approved=false

## Train R: Examples/Docs from Installed Packages
- FODS/FODT/ZST/Netpbm examples from top-level
- Docs listing supported/unsupported

## Train S: Publication Readiness
- FODS/FODT/ZST package metadata, README, blockers
- publication_authorized=false

## Train T: AI-Assisted Gap Extraction
- Run fixture AI tests
- Classify gaps
- No live AI call unless authorized

## Train U: Closeout Automation + Supervisor Loop
- Document closeout driver steps
- Print UPLOAD PRIMARY ARTIFACT path
- Trigger supervisor loop

## Train V: State/Registry/Memory/Master-Plan Sync
- Run state_snapshot.py AFTER all SHAs committed
- Update master-plan.md
- Update memory/00-index.md

## Train W: Final Adversarial IV
- Attack every claim
- 12 adversarial checks
- At most 2 repair loops
