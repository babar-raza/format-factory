# R103 Preflight — Cross-Stream Contamination and Deep Grading

Sprint: FORMAT-FACTORY-SUPERVISOR-R103-CROSS-STREAM-CONTAMINATION-AND-DEEP-GRADING-CAMPAIGN-001
Date: 2026-06-03
Stream: supervisor

## R102 Package Deficiencies Found
1. evidence-manifest.yaml lists only the declaration (1 artifact), not the 14 declared evidence artifacts
2. No reports/supervisor-r102/*.md files in the ZIP (10 reports missing)
3. No raw logs in the ZIP
4. No replay outputs in the ZIP
5. No generated next prompts from sprint reports
6. All 12 grades are ACCEPTED_VERIFIED with tests_supporting: []
7. Declaration used `test_references` field but schema expects `tests_supporting` — inspector never reads them
8. selected-product-gaps.json is stale (sprint: R98)

## Cross-Stream Contamination Status
- To be verified: context-pack latest_sprint, evidence-review sprint reference

## Fix Plan
- Wave 0: R102 reconciliation and claim classification
- Wave 1: Cross-stream contamination repair
- Wave 2: Deep grading v3 (tests_supporting field fix + content verification)
- Wave 3: Package self-containment (include sprint reports + evidence artifacts)
- Wave 4: Replay 4 packages
- Wave 5: Continuation policy hardening
- Wave 6: Stream-specific prompt generation
- Wave 7: Final IV
