---
sprint: mainstream-R100
train: A (preflight)
---

# R100 Mainstream Preflight

## Baseline (from R99)
- FODS .NET: 263 tests, 25 public APIs
- FODT .NET: 249 tests, 23 public APIs
- Netpbm .NET: 172 tests, 19 public methods
- .NET total: 684
- Python total: 2633 passed, 13 skipped
- Grand total: 3317

## R100 Deep Product Plan

### Commercial .NET (GROUP 2)
| Lane | Deliverable 1 (capability) | Deliverable 2 (hardening) |
|------|---------------------------|--------------------------|
| FODS | AddSheet(string) — new sheet creation | Multi-sheet edit/save/export roundtrip tests |
| FODT | AppendParagraph(string) — paragraph mutation | Document structure after append roundtrip tests |
| Netpbm | Rotate270Cw() — counter-clockwise rotation | Transformation chain roundtrip tests |

### FOSS (GROUP 3)
| Lane | Deliverable 1 | Deliverable 2 |
|------|--------------|--------------|
| ZST | Installed example update | Probe + validate workflow tests |
| Python Netpbm | PBM->PPM->PGM chain roundtrip | Installed conversion smoke |
| SYLK | CSV export with edge cases | Malformed input diagnostics tests |

### Dogfood (GROUP 4)
| Lane | Gap to advance |
|------|---------------|
| Commercial | Netpbm .NET PGM->PPM (ToColor) dogfood proof test |
| FOSS | PBM->PPM->PGM full chain dogfood proof |

## Hard constraints
- commercial_product_ready: false (unchanged)
- No push/commit/Gate 8/Gate 11
- All src changes governed by skill registry
- 1 source change per .NET product (AddSheet, AppendParagraph, Rotate270Cw)
