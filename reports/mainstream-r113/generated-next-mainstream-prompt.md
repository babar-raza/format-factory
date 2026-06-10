# Next Mainstream Sprint Prompt (R114)

## Suggested Sprint ID
FORMAT-FACTORY-MAINSTREAM-R114-PROMPT-QUALITY-FIX-LANDED-AND-CONTINUED-PRODUCT-BREADTH-CAMPAIGN-001

## Context
R113 produced a comprehensive prompt-quality blocker packet with governance allowlist and 6 test cases for the Supervisor stream. R113 delivered 3 new .NET APIs (SortRows, GetDocumentMetadata, Tile) with 90 new tests total.

## Recommended Lanes

### Lane 1: Verify Prompt-Quality Fix
- Check if Supervisor stream has landed the `no_wrong_stream` allowlist fix
- If landed: run prompt-quality check and confirm PASS
- If not landed: escalate or produce additional evidence

### Lane 2: R113 Reconciliation
- Verify all R113 items accepted by autonomous-cycle
- Address any OVERCLAIMED/REJECTED items

### Lane 3: Commercial .NET Breadth Continuation
- FODS: Consider DeleteRow, MergeCells, or formula evaluation
- FODT: Consider InsertImage, TableOfContents, or FindReplace
- Netpbm: Consider Rotate(arbitrary angle), Composite/Blend, or ColorQuantize
- Quota: 6+ commercial .NET deliverables

### Lane 4: FOSS Deepening
- ZST: Streaming compression API
- PPM: Binary P6 write
- SYLK: Multi-sheet support
- DIF: Write capability
- Quota: 4+ FOSS deliverables

### Lane 5: Dogfood
- Continue cross-API workflow testing
- Quota: 3+ dogfood deliverables

## Hard Prohibitions (inherited)
- No git push/commit without human authorization
- No Gate 8/11 approval
- No commercial_product_ready=true
- No supervisor/acceleration tool edits from Mainstream stream
