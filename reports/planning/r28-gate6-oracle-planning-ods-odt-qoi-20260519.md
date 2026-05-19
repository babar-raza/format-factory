# Gate 6 Oracle Planning — ODS/ODT/QOI
# Sprint: FORMAT-FACTORY-R28-GATE5-GATE7-ORACLE-FUZZ-XCF-ZPAQ-G11-C9-PUBLICATION-HARDENING-001
# Date: 2026-05-19

## Strategy: Deterministic Expected-Value Oracle

All oracle tests compare parsed output against known expected values from:
1. Existing sample corpus files (built in Gate 3)
2. Synthetic files built in-test with known content

No external tools required for deterministic oracles.

## Blocker: Full Round-Trip Oracle
- LibreOffice-generated reference files not available in CI
- Recorded as `blocked_external_tool` in test documentation
- Does NOT block Gate 6 initial pass — deterministic oracles sufficient

## ODS Oracle Tests (6 tests)
- Known minimal-spreadsheet: Sheet1, 2 rows, Name/Value headers, Alpha/42.0 data
- Known single-cell: >= 1 non-empty cell
- Known numeric-row: [1.0, 2.0, 3.0]
- Synthetic date cell: value_type=date, value=2026-01-15
- Synthetic boolean cell: value_type=boolean, value=true
- Blocked external tool documentation

## ODT Oracle Tests (6 tests)
- Known minimal-document: "Hello, world."
- Known two-paragraphs: >= 2 paragraphs
- Known unicode-text: contains non-ASCII
- Synthetic heading: exact text + level match
- Synthetic list: Item A, Item B extraction
- Blocked external tool documentation

## QOI Oracle Tests (7 tests)
- Known 1x1-red: (255, 0, 0, 255)
- Known 2x2-black: 4 black pixels
- Known 4x1-gradient: 4 pixels
- Synthetic OP_RGB: literal (100, 150, 200, 255)
- Synthetic OP_RGBA: literal (10, 20, 30, 40)
- Synthetic OP_RUN: 3 default pixels
- Synthetic 2x2: OP_RGB + OP_RUN combination

## Results
- Total: 19/19 PASS
- No Gate 6 overclaim — initial deterministic oracles only
