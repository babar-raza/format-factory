---
sprint: R93
generated_by: r93-worker
train: J
---

# POC Gap Selection (Train J)

Sprint: FORMAT-FACTORY-R93-CONTEXT-PACK-SUPERVISOR-MCP-ACCELERATION-POC-PARALLEL-MEGA-TRAIN-001

## R93 Selected Product Gaps

Based on the POC matrix (poc-targets.yaml, sprint R92) and the skill registry,
the following gaps are selected for R93 product work (Trains K-P):

### Commercial .NET (Trains K-M)

| Format | Gap | Skill | Sprint |
|--------|-----|-------|--------|
| FODS .NET | Export CSV with column headers | /add-dotnet-api | R93 |
| FODT .NET | ReplaceText round-trip test | /add-roundtrip-test | R93 |
| Netpbm .NET | CopyRegion(src, dst) | /add-dotnet-api | R93 |

### FOSS Python (Trains N-P)

| Format | Gap | Skill | Sprint |
|--------|-----|-------|--------|
| ZST | Compress/decompress round-trip test | /add-python-object-model-feature | R93 |
| Python Netpbm | PPM→PGM installed workflow verification | /verify-dogfood-path | R93 |
| SYLK | SYLK write (basic round-trip) | /add-python-object-model-feature | R93 |

## Gap Selection Rationale

1. FODS: `GetSheetNames` added in R92. Next logical step: add column-header CSV export.
2. FODT: `GetHeadingParagraphs` added in R92. `ReplaceText` exists — add round-trip test.
3. Netpbm: `FillRegion` added in R92. Next: `CopyRegion` for bitmap manipulation.
4. ZST: Has compress/decompress — add formal round-trip tests.
5. Python Netpbm: PPM→PGM dogfood export exists — verify installed workflow.
6. SYLK: Has sylk_to_csv — add basic write capability.

## Status: GAPS SELECTED — READY FOR TRAINS K-P
