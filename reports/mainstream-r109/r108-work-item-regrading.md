# R108 Work Item Regrading Plan

## Source
R108 evidence declaration: `.local/evidences/mainstream-r108/evidence-declaration.yaml`

## Regrading Strategy
All 13 R108 items were ACCEPTED by autonomous-cycle but with evidence_quality_score: 0.0.
Each item will be physically verified and upgraded to ACCEPTED_VERIFIED with:
- File existence proof (ls -la on each evidence path)
- Content verification (head of each file)
- Test proof (for test-bearing items, verify test file has correct test count)
- Source diff (for governed API items, verify SHA matches ledger)

## Items to Regrade

| # | Item ID | Title | Current | Target |
|---|---------|-------|---------|--------|
| 1 | R108-LANE-A-REGRADING | R107 Evidence Regrading | ACCEPTED | ACCEPTED_VERIFIED |
| 2 | R108-LANE-B-LEDGER | Source Ledger Clean Closure | ACCEPTED | ACCEPTED_VERIFIED |
| 3 | R108-LANE-C-FODS | FODS GetColumnCount API | ACCEPTED | ACCEPTED_VERIFIED |
| 4 | R108-LANE-D-FODT | FODT ExportToMarkdownFile API | ACCEPTED | ACCEPTED_VERIFIED |
| 5 | R108-LANE-E-NETPBM | Netpbm ApplyGamma API | ACCEPTED | ACCEPTED_VERIFIED |
| 6 | R108-LANE-F-ZST | ZST Frame Inspection Tests | ACCEPTED | ACCEPTED_VERIFIED |
| 7 | R108-LANE-F-SYLK | SYLK Installed-Workflow Verification | ACCEPTED | ACCEPTED_VERIFIED |
| 8 | R108-LANE-F-PBM | PBM Edge-Case Hardening | ACCEPTED | ACCEPTED_VERIFIED |
| 9 | R108-LANE-G-FODS-DOGFOOD | FODS Save-After-Edit Dogfood | ACCEPTED | ACCEPTED_VERIFIED |
| 10 | R108-LANE-G-FODT-DOGFOOD | FODT Markdown Export Dogfood | ACCEPTED | ACCEPTED_VERIFIED |
| 11 | R108-LANE-H-PACKAGE | Package/Install Proof | ACCEPTED | ACCEPTED_VERIFIED |
| 12 | R108-LANE-I-GAPS | Fresh Mainstream Gaps | ACCEPTED | ACCEPTED_VERIFIED |
| 13 | R108-LANE-J-IV | Independent Verification | ACCEPTED | ACCEPTED_VERIFIED |
