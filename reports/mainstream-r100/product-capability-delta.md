# R100 Product Capability Delta

Sprint: FORMAT-FACTORY-MAINSTREAM-R100-PRODUCT-POC-DEEP-COMMERCIAL-FOSS-DOGFOOD-PARALLEL-MEGA-TRAIN-001

## New Capabilities Added

### Commercial .NET
| Format | Capability | API Symbol | Tests |
|--------|-----------|-----------|-------|
| FODS | Add new sheets programmatically | AddSheet(string) | 10 |
| FODT | Append paragraphs programmatically | AppendParagraph(string) | 10 |
| Netpbm | 270-degree clockwise rotation | Rotate270Cw() | 10 |

### FOSS Python (test-only deepening, no src changes)
| Format | Capability | Tests |
|--------|-----------|-------|
| ZST | Probe/validate workflow hardening | 10 |
| Netpbm | PBM->PPM->PGM full chain verification | 8 |
| SYLK | CSV export + malformed input hardening | 9 |

## Capability Counts (cumulative)

| Product | R99 | R100 | Delta |
|---------|-----|------|-------|
| FODS .NET capabilities | 21 | 22 | +1 (add_sheet) |
| FODT .NET capabilities | 14 | 15 | +1 (append_paragraph) |
| Netpbm .NET capabilities | 24 | 25 | +1 (rotate_270_cw) |
| ZST Python capabilities | 7 | 7 | 0 (test deepening) |
| Netpbm Python capabilities | 10 | 10 | 0 (test deepening) |
| SYLK Python capabilities | 4 | 4 | 0 (test deepening) |
