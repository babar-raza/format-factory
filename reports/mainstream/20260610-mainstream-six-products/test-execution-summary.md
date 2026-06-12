# Test Execution Summary — Mainstream Mega-Train
# Date: 2026-06-10

## Python Test Results (selected products)
- Command: `.local/venv/Scripts/python -m pytest tests/python/{fods,fodt,csv,tsv,ndjson,pbm,pgm,ppm}`
- Result: **3001 passed, 20 skipped, 0 failed**
- Duration: 17.31s

### Per-format breakdown:
| Format | Passed | Skipped |
|--------|--------|---------|
| FODS | 211 | - |
| FODT | 248 | - |
| CSV | 38 | - |
| TSV | 373 | - |
| NDJSON | 233 | - |
| PBM | 48 | - |
| PGM | 47 | - |
| PPM | 49 | - |
| Other (shared/deepening) | ~1754 | 20 |

## .NET Test Results (all projects)
| Project | Passed | Failed | Skipped | Duration |
|---------|--------|--------|---------|----------|
| FormatFactory.Fods | 547 | 0 | 0 | 309ms |
| FormatFactory.Fodt | 520 | 0 | 0 | 352ms |
| FormatFactory.Csv | 36 | 0 | 0 | 71ms |
| FormatFactory.Ndjson | 29 | 0 | 0 | 120ms |
| FormatFactory.Tsv | 38 | 0 | 0 | 93ms |
| FormatFactory.Netpbm | 465 | 0 | 0 | 129ms |
| FormatFactory.Html | 12 | 0 | 0 | 73ms |
| FormatFactory.Markdown | 11 | 0 | 0 | 74ms |
| FormatFactory.Txt | 8 | 0 | 0 | 22ms |
| **TOTAL .NET** | **1666** | **0** | **0** | |

## Combined Total
- **Python: 3001 passed**
- **.NET: 1666 passed**
- **Grand Total: 4667 tests, 0 failures**

## New Tests This Sprint
- Python CSV writer: 19 new tests
- .NET CSV reader + document: 21 new tests
- .NET NDJSON (entire project): 29 new tests
- .NET TSV (entire project): 38 new tests
- **Total new: 107 tests**
