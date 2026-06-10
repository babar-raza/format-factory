# R99 Mainstream Product Sprint — Preflight

Sprint: FORMAT-FACTORY-MAINSTREAM-R99-PRODUCT-POC-COMMERCIAL-FOSS-DOGFOOD-PARALLEL-MEGA-TRAIN-001
Mode: EXECUTION — MAINSTREAM PRODUCT STREAM ONLY
Date: 2026-06-03

## Baseline Test Counts
- FODS .NET: 255 passed
- FODT .NET: 241 passed
- Netpbm .NET: 162 passed
- .NET Total: 658
- Python: 2609 passed, 13 skipped
- Grand Total: 3267

## POC Matrix Status (from R98)
- FODS: 20 capabilities PASS, dotnet_tests 255
- FODT: 18 capabilities PASS, dotnet_tests 241
- Netpbm: 24 capabilities PASS, dotnet_tests 162
- ZST: 7 capabilities PASS
- Python Netpbm: 10 capabilities PASS
- SYLK: installed_workflow PARTIAL

## Top Product Gaps (actionable this sprint)
1. FODS: Export quality tests (CSV/HTML/JSON edge cases)
2. FODT: Heading/paragraph persistence after multiple edits
3. Netpbm: PGM-to-PPM dogfood conversion + binary write proof
4. ZST: File-based example + dependency docs
5. Python Netpbm: Cross-format conversion example
6. SYLK: Installed workflow completion

## Hard Constraints
- No ad-hoc src edits (governed skill/handoff only)
- No push/commit/Gate 8/Gate 11/publication
- commercial_product_ready remains false
- Mainstream product work only — no supervisor/acceleration infrastructure
